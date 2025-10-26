import os
import requests
# Wichtig: render_template, request, redirect und url_for importieren
from flask import Flask, render_template, request, redirect, url_for
from data_manager import DataManager
from models import db, User

# --- App- und Datenbankinitialisierung (bleibt gleich) ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
data_manager = DataManager()


# ... (OMDb Konfiguration bleibt hier)

# --- Routen-Implementierung ---

@app.route('/')
def home():
    """
    Diese Funktion wird bei einer GET-Anfrage an die Startseite ('/') aufgerufen.
    Sie holt alle Nutzer und rendert das index.html-Template mit diesen Daten.
    """
    # 1. Rufe die Liste aller Nutzer vom DataManager ab
    users = data_manager.get_users()
    # 2. Gib das Template zurück und übergebe die Nutzerliste an Jinja2
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def add_user():
    """
    Diese Funktion wird aufgerufen, wenn das "Nutzer hinzufügen"-Formular
    abgeschickt wird (POST-Anfrage an /users).
    """
    # 1. Hole den Namen aus den Formulardaten. 'name' entspricht dem name-Attribut im <input>-Tag.
    name = request.form.get('name')
    # 2. Stelle sicher, dass ein Name eingegeben wurde
    if name:
        # 3. Nutze den DataManager, um den neuen Nutzer in der Datenbank zu speichern
        data_manager.create_user(name=name)
    # 4. Leite den Browser zurück zur Startseite. Dort wird home() erneut aufgerufen
    #    und die aktualisierte Nutzerliste angezeigt (Post-Redirect-Get-Pattern).
    return redirect(url_for('home'))


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def list_movies(user_id):
    """
    Diese Route bleibt für die Anzeige und das Hinzufügen von Filmen zuständig.
    """
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # ... (Logik zum Hinzufügen eines Films)
        # ... (bleibt unverändert)
        pass  # Platzhalter

    # GET-Request
    movies = data_manager.get_movies(user_id=user_id)
    return render_template('movies.html', user=user, movies=movies)


# --- Anwendung starten (bleibt gleich) ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)