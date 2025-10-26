import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from data_manager import DataManager
from models import db, User

# === 1. INITIALISIERUNG UND KONFIGURATION ===

app = Flask(__name__)

# Lade den Secret Key sicher, wichtig für 'flash' Nachrichten
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ein-sehr-geheimer-schluessel')

# Datenbank-Konfiguration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisiere die Datenbank und den DataManager
db.init_app(app)
data_manager = DataManager()

# --- OMDb API Konfiguration ---
# HINWEIS: Ihr API-Schlüssel wurde hier direkt eingetragen.
# Für eine Produktionsumgebung wird dringend empfohlen, stattdessen Umgebungsvariablen zu verwenden.
OMDB_API_KEY = "ab436000"  # <--- IHR API-SCHLÜSSEL IST HIER EINGEFÜGT
OMDB_URL = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}"


# === 2. FEHLERHANDLER ===

@app.errorhandler(404)
def page_not_found(e):
    """Rendert eine benutzerdefinierte Seite für 404-Fehler."""
    return render_template('404.html'), 404


# === 3. ROUTEN ===

@app.route('/')
def home():
    """Startseite: Zeigt alle Nutzer an."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    """Verarbeitet das Formular zum Hinzufügen eines neuen Nutzers."""
    name = request.form.get('name')
    if name:
        data_manager.create_user(name=name)
        flash(f"Nutzer '{name}' erfolgreich erstellt!", "success")
    else:
        flash("Der Name darf nicht leer sein.", "error")
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def list_movies(user_id):
    """Zeigt die Lieblingsfilme eines bestimmten Nutzers an."""
    user = User.query.get_or_404(user_id)
    movies = data_manager.get_movies(user_id=user_id)
    return render_template('movies.html', user=user, movies=movies)


@app.route('/users/<int:user_id>/add_movie', methods=['POST'])
def add_movie(user_id):
    """Verarbeitet das Hinzufügen eines neuen Films zur Liste eines Nutzers."""
    User.query.get_or_404(user_id)  # Stellt sicher, dass der Nutzer existiert
    movie_title = request.form.get('title')

    if not movie_title:
        flash("Bitte geben Sie einen Filmtitel ein.", "error")
        return redirect(url_for('list_movies', user_id=user_id))

    # 1. Externe API aufrufen
    response = requests.get(OMDB_URL, params={'t': movie_title})

    # 2. Antwort der API verarbeiten
    if response.status_code == 200 and response.json().get('Response') == 'True':
        omdb_data = response.json()

        # Sicherstellen, dass das Jahr korrekt extrahiert wird (z.B. aus "2014-2018")
        year_str = omdb_data.get('Year', '0').split('–')[0]

        movie_data = {
            'name': omdb_data.get('Title'),
            'director': omdb_data.get('Director'),
            'year': int("".join(filter(str.isdigit, year_str))),  # Nur Ziffern extrahieren
            'poster_url': omdb_data.get('Poster')
        }

        # 3. DataManager mit fertigen Daten aufrufen
        if data_manager.add_movie(user_id=user_id, movie_data=movie_data):
            flash(f"Film '{movie_data['name']}' wurde hinzugefügt!", "success")
        else:
            flash("Film konnte nicht hinzugefügt werden (Datenbankfehler).", "error")
    else:
        flash(f"Film '{movie_title}' konnte auf OMDb nicht gefunden werden.", "error")

    return redirect(url_for('list_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """Löscht einen Film aus der Favoritenliste eines Nutzers."""
    if data_manager.delete_movie(user_id, movie_id):
        flash("Film erfolgreich entfernt.", "success")
    else:
        flash("Film konnte nicht entfernt werden.", "error")
    return redirect(url_for('list_movies', user_id=user_id))


# === 4. ANWENDUNG STARTEN ===

if __name__ == '__main__':
    with app.app_context():
        # Erstellt die Datenbanktabellen, falls sie noch nicht existieren
        db.create_all()
    # Startet den Flask-Entwicklungsserver im Debug-Modus
    app.run(debug=True)