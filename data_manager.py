from models import db, User, Movie
from sqlalchemy.exc import SQLAlchemyError


class DataManager:
    """
    Verwaltet alle Datenbankoperationen (CRUD) für die MoviWeb-App.
    Diese Klasse ist die einzige Schicht, die direkt mit der Datenbank interagiert.
    """

    def get_users(self):
        """Gibt eine Liste aller Nutzer aus der Datenbank zurück."""
        try:
            return User.query.order_by(User.name).all()
        except SQLAlchemyError as e:
            print(f"Datenbankfehler beim Abrufen der Nutzer: {e}")
            return []

    def get_movies(self, user_id):
        """Gibt eine Liste der Lieblingsfilme für einen bestimmten Nutzer zurück."""
        try:
            user = User.query.get(user_id)
            if user:
                return user.favorite_movies
            return []
        except SQLAlchemyError as e:
            print(f"Datenbankfehler beim Abrufen der Filme: {e}")
            return []

    def create_user(self, name):
        """Fügt einen neuen Nutzer sicher zur Datenbank hinzu."""
        try:
            new_user = User(name=name)
            db.session.add(new_user)
            db.session.commit()
            print(f"Nutzer '{name}' wurde erstellt.")
            return new_user
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Datenbankfehler beim Erstellen des Nutzers: {e}")
            return None

    def add_movie(self, user_id, movie_data):
        """
        Fügt einen neuen Film zur Favoritenliste eines Nutzers hinzu.
        Erhält ein Dictionary mit fertigen Filmdaten.
        """
        user = User.query.get(user_id)
        if not user:
            print(f"Fehler: Nutzer mit ID {user_id} nicht gefunden.")
            return False

        try:
            # Duplikate in der globalen Movie-Tabelle vermeiden
            movie = Movie.query.filter_by(name=movie_data['name'], year=movie_data['year']).first()
            if not movie:
                movie = Movie(
                    name=movie_data['name'],
                    director=movie_data['director'],
                    year=movie_data['year'],
                    poster_url=movie_data.get('poster_url', '')
                )
                db.session.add(movie)

            if movie not in user.favorite_movies:
                user.favorite_movies.append(movie)

            db.session.commit()
            print(f"Film '{movie.name}' wurde zu den Favoriten von '{user.name}' hinzugefügt.")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Datenbankfehler beim Hinzufügen des Films: {e}")
            return False

    def update_movie(self, movie_id, new_title):
        """Aktualisiert den Titel eines bestimmten Films in der Datenbank."""
        try:
            movie = Movie.query.get(movie_id)
            if movie:
                movie.name = new_title
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Datenbankfehler beim Aktualisieren des Films: {e}")
            return False

    def delete_movie(self, user_id, movie_id):
        """Entfernt einen Film aus der Favoritenliste eines Nutzers."""
        try:
            user = User.query.get(user_id)
            movie = Movie.query.get(movie_id)
            if user and movie and movie in user.favorite_movies:
                user.favorite_movies.remove(movie)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Datenbankfehler beim Löschen des Films: {e}")
            return False