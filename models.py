from flask_sqlalchemy import SQLAlchemy

# Erstelle ein SQLAlchemy-Datenbankobjekt
db = SQLAlchemy()

# Definiere die Assoziationstabelle für die Viele-zu-Viele-Beziehung
# zwischen Usern und Movies.
# Diese Tabelle speichert nur die IDs der verknüpften Objekte.
user_movies = db.Table('user_movies',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                       db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True)
                       )


# Definiere das User-Modell
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Definiere die Beziehung zu den Filmen
    # 'secondary' verweist auf unsere Assoziationstabelle
    # 'back_populates' stellt eine beidseitige Beziehung her, sodass
    # du von einem Filmobjekt aus auch auf die Nutzer zugreifen kannst.
    favorite_movies = db.relationship('Movie', secondary=user_movies, back_populates='favorited_by')


# Definiere das Movie-Modell
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    poster_url = db.Column(db.String(300), nullable=True)  # URL kann lang sein

    # Dies ist die andere Seite der Beziehung
    favorited_by = db.relationship('User', secondary=user_movies, back_populates='favorite_movies')