from models import db, User, Movie


class DataManager:
    """
    Diese Klasse verwaltet die Datenbankoperationen für die MoviWeb-App
    unter Verwendung von SQLAlchemy ORM.
    """

    def create_user(self, name):
        """Fügt einen neuen Nutzer zur Datenbank hinzu."""
        # Erstellt ein neues User-Objekt aus dem Model
        new_user = User(name=name)
        # Fügt das neue Objekt zur aktuellen Datenbank-Session hinzu
        db.session.add(new_user)
        # Überträgt die Änderungen dauerhaft in die Datenbank
        db.session.commit()
        print(f"Nutzer '{name}' wurde erstellt.")

    def get_users(self):
        """Gibt eine Liste aller Nutzer aus der Datenbank zurück."""
        # Führt eine Abfrage aus, um alle Einträge aus der User-Tabelle zu erhalten
        users = User.query.all()
        return users

    def get_movies(self, user_id):
        """Gibt eine Liste der Lieblingsfilme für einen bestimmten Nutzer zurück."""
        # Findet den Nutzer anhand seiner ID
        user = User.query.get(user_id)
        if user:
            # Greift dank der in models.py definierten Beziehung
            # direkt auf die Liste der Lieblingsfilme zu.
            return user.favorite_movies
        # Gibt eine leere Liste zurück, wenn der Nutzer nicht gefunden wurde
        return []

    def add_movie(self, user_id, movie_data):
        """
        Fügt einen neuen Film zur Favoritenliste eines Nutzers hinzu.
        Wenn der Film noch nicht in der allgemeinen Filmdatenbank existiert, wird er erstellt.
        """
        # Finde den Nutzer, dem der Film hinzugefügt werden soll
        user = User.query.get(user_id)
        if not user:
            print(f"Fehler: Nutzer mit ID {user_id} nicht gefunden.")
            return

        # Prüfe, ob der Film bereits in der globalen 'movie'-Tabelle existiert,
        # um Duplikate zu vermeiden.
        movie = Movie.query.filter_by(name=movie_data['name'], year=movie_data['year']).first()

        # Wenn der Film nicht existiert, erstelle einen neuen Eintrag
        if not movie:
            movie = Movie(
                name=movie_data['name'],
                director=movie_data['director'],
                year=movie_data['year'],
                poster_url=movie_data.get('poster_url', '')  # .get() zur Sicherheit
            )
            db.session.add(movie)

        # Füge den Film zur Favoritenliste des Nutzers hinzu, falls er noch nicht drin ist
        if movie not in user.favorite_movies:
            user.favorite_movies.append(movie)
            # Speichere die Änderungen in der Datenbank
            db.session.commit()
            print(f"Film '{movie.name}' wurde zu den Favoriten von '{user.name}' hinzugefügt.")
        else:
            print(f"Film '{movie.name}' ist bereits in den Favoriten von '{user.name}'.")

    def update_movie(self, movie_id, new_title):
        """Aktualisiert den Titel eines bestimmten Films in der Datenbank."""
        # Finde den Film anhand seiner ID
        movie = Movie.query.get(movie_id)
        if movie:
            # Ändere das Attribut des Objekts
            movie.name = new_title
            # Übertrage die Änderung in die Datenbank
            db.session.commit()
            print(f"Filmtitel zu '{new_title}' aktualisiert.")
        else:
            print(f"Fehler: Film mit ID {movie_id} nicht gefunden.")

    def delete_movie(self, user_id, movie_id):
        """Entfernt einen Film aus der Favoritenliste eines Nutzers."""
        # Finde den Nutzer und den Film
        user = User.query.get(user_id)
        movie = Movie.query.get(movie_id)

        if user and movie:
            # Prüfe, ob der Film in der Favoritenliste des Nutzers ist
            if movie in user.favorite_movies:
                # Entferne die Verknüpfung zwischen Nutzer und Film.
                # Der Film selbst wird nicht aus der globalen Filmtabelle gelöscht.
                user.favorite_movies.remove(movie)
                db.session.commit()
                print(f"Film '{movie.name}' wurde aus den Favoriten von '{user.name}' entfernt.")
            else:
                print("Fehler: Film nicht in der Favoritenliste des Nutzers.")
        else:
            print("Fehler: Nutzer oder Film nicht gefunden.")