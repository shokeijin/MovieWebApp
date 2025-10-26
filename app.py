import os
import requests
from flask import Flask, render_template, request, redirect, url_for
from data_manager import DataManager
from models import db, User  # Importiere auch das User-Modell für Abfragen

# --- App- und Datenbankinitialisierung ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
data_manager = DataManager()

# --- OMDb API Konfiguration ---
# Lade den API-Schlüssel sicher, z.B. aus einer Umgebungsvariable
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "DEIN_DEFAULT_KEY")  # Ersetze DEIN_DEFAULT_KEY
OMDB_URL = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}"


# --- Routen ---

@app.route('/')
def home():
    """Startseite: Zeigt alle Nutzer und ein Formular zum Hinzufügen an."""
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    """Verarbeitet das Formular zum Hinzufügen eines neuen Nutzers."""
    name = request.form.get('name')
    if name:
        data_manager.create_user(name=name)
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def list_movies(user_id):
    """
    Diese Route hat zwei Aufgaben, basierend auf der HTTP-Methode:
    - GET: Zeigt die Lieblingsfilme eines Nutzers an.
    - POST: Fügt einen neuen Film zur Liste des Nutzers hinzu.
    """
    user = User.query.get_or_404(user_id)  # Holt den Nutzer oder gibt 404 zurück

    if request.method == 'POST':
        # --- LOGIK FÜR DAS HINZUFÜGEN EINES FILMS (POST) ---
        movie_title = request.form.get('title')
        if movie_title:
            # 1. Filminfos von OMDb abrufen
            params = {'t': movie_title}
            response = requests.get(OMDB_URL, params=params)

            if response.status_code == 200 and response.json().get('Response') == 'True':
                omdb_data = response.json()

                # 2. Movie-Objekt vorbereiten
                movie_data = {
                    'name': omdb_data.get('Title'),
                    'director': omdb_data.get('Director'),
                    'year': int(omdb_data.get('Year')),
                    'poster_url': omdb_data.get('Poster')
                }

                # 3. DataManager verwenden, um den Film hinzuzufügen
                data_manager.add_movie(user_id=user_id, movie_data=movie_data)

        return redirect(url_for('list_movies', user_id=user_id))

    else:  # request.method == 'GET'
        # --- LOGIK FÜR DAS ANZEIGEN DER FILME (GET) ---
        movies = data_manager.get_movies(user_id=user_id)
        return render_template('movies.html', user=user, movies=movies)


# --- Anwendung starten ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)