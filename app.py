from flask import Flask
from data_manager import DataManager
from models import db # Importiere das db-Objekt direkt aus models

# 1. App- und Datenbankinitialisierung
# ====================================

# Erstelle eine Instanz der Flask-Anwendung
app = Flask(__name__)

# Konfiguriere die App für die Verwendung mit SQLAlchemy
# Gib den Pfad zur Datenbankdatei an. 'sqlite:///moviweb.db' bedeutet,
# dass eine Datei namens 'moviweb.db' im Hauptverzeichnis des Projekts erstellt wird.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///moviweb.db'
# Deaktiviere eine Funktion von SQLAlchemy, die wir nicht benötigen und die sonst eine Warnung ausgibt.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisiere die Datenbank innerhalb der Flask-Anwendung.
# Dies verbindet das 'db'-Objekt aus models.py mit unserer konfigurierten App.
db.init_app(app)

# Erstelle eine Instanz unseres DataManagers, um mit der Datenbank zu arbeiten.
data_manager = DataManager()


# 2. Routen einrichten
# ====================

# Definiere eine Route für die Startseite ('/')
@app.route('/')
def home():
    """Diese Funktion wird ausgeführt, wenn jemand die Haupt-URL besucht."""
    return "Welcome to MovieWeb App!"

# Hier werden später weitere Routen für Nutzer, Filme etc. hinzugefügt.
# z.B. @app.route('/users'), @app.route('/users/<int:user_id>/movies') etc.


# 3. Anwendung ausführen und Datenbank erstellen
# ============================================

# Der folgende Code-Block wird nur ausgeführt, wenn dieses Skript
# direkt mit 'python app.py' gestartet wird.
if __name__ == '__main__':
    # Erstelle die Datenbank und alle Tabellen zum ersten Mal.
    # 'with app.app_context()' stellt sicher, dass die Anwendungskonfiguration
    # geladen ist, bevor auf die Datenbank zugegriffen wird.
    with app.app_context():
        # db.create_all() liest alle Klassen, die von db.Model erben (User, Movie),
        # und erstellt die entsprechenden Tabellen in der Datenbank, falls sie noch nicht existieren.
        db.create_all()

        # Optional: Einen Test-Nutzer erstellen, wenn die Datenbank leer ist
        if not data_manager.get_users():
             print("Datenbank ist leer. Erstelle einen ersten Test-Nutzer...")
             data_manager.create_user(name="Alice")


    # Starte den Flask-Entwicklungsserver.
    # debug=True sorgt dafür, dass der Server bei Code-Änderungen automatisch neu startet
    # und detailliertere Fehlermeldungen im Browser anzeigt.
    app.run(debug=True)