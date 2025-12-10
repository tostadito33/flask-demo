import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

app = Flask(__name__)

app.config["SECRET_KEY"] = "clave-super-secreta-para-la-practica"

# 🔧 Seleccionar base de datos según el entorno
db_uri = os.getenv("DATABASE_URL", "sqlite:///movies.db")

# Render suele dar URLs que empiezan por postgres://, pero SQLAlchemy
# prefiere postgresql:// → lo corregimos por si acaso
if db_uri.startswith("postgres://"):
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)



# 🗃️ Modelo de Película
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1–5
    added_by = db.Column(db.String(100), nullable=True)  # usuario de la sesión


# Crear tablas si no existen
# Crear tablas si no existen y añadir datos iniciales
# Crear tablas si no existen y añadir muchos datos iniciales
with app.app_context():
    db.create_all()

    # Si hay menos de 10 películas, añadimos un catálogo grande
    # (así, aunque ya tuvieras unas pocas, se añaden solo una vez)
    if Movie.query.count() < 10:
        initial_movies = [
            Movie(title="Inception", genre="Ciencia ficción", rating=5, added_by="Sistema"),
            Movie(title="El Padrino", genre="Drama", rating=5, added_by="Sistema"),
            Movie(title="Interstellar", genre="Ciencia ficción", rating=5, added_by="Sistema"),
            Movie(title="La La Land", genre="Musical", rating=4, added_by="Sistema"),
            Movie(title="Pulp Fiction", genre="Crimen", rating=5, added_by="Sistema"),
            Movie(title="Toy Story", genre="Animación", rating=4, added_by="Sistema"),
            Movie(title="El Señor de los Anillos: La Comunidad del Anillo", genre="Fantasía", rating=5, added_by="Sistema"),
            Movie(title="El Caballero Oscuro", genre="Acción", rating=5, added_by="Sistema"),
            Movie(title="Matrix", genre="Ciencia ficción", rating=5, added_by="Sistema"),
            Movie(title="Forrest Gump", genre="Drama", rating=5, added_by="Sistema"),
            Movie(title="Gladiator", genre="Acción", rating=4, added_by="Sistema"),
            Movie(title="Origen", genre="Ciencia ficción", rating=5, added_by="Sistema"),
            Movie(title="Titanic", genre="Romance", rating=4, added_by="Sistema"),
            Movie(title="Avatar", genre="Ciencia ficción", rating=4, added_by="Sistema"),
            Movie(title="Joker", genre="Drama", rating=4, added_by="Sistema"),
            Movie(title="Parásitos", genre="Thriller", rating=5, added_by="Sistema"),
            Movie(title="Coco", genre="Animación", rating=5, added_by="Sistema"),
            Movie(title="Up", genre="Animación", rating=4, added_by="Sistema"),
            Movie(title="Del revés (Inside Out)", genre="Animación", rating=5, added_by="Sistema"),
            Movie(title="Los Vengadores", genre="Acción", rating=4, added_by="Sistema"),
            Movie(title="Vengadores: Endgame", genre="Acción", rating=5, added_by="Sistema"),
            Movie(title="Spider-Man: Un nuevo universo", genre="Animación", rating=5, added_by="Sistema"),
            Movie(title="Guardianes de la Galaxia", genre="Ciencia ficción", rating=4, added_by="Sistema"),
            Movie(title="Star Wars: Una nueva esperanza", genre="Ciencia ficción", rating=5, added_by="Sistema"),
            Movie(title="Star Wars: El imperio contraataca", genre="Ciencia ficción", rating=5, added_by="Sistema"),
            Movie(title="Regreso al futuro", genre="Ciencia ficción", rating=5, added_by="Sistema"),
            Movie(title="Harry Potter y la piedra filosofal", genre="Fantasía", rating=4, added_by="Sistema"),
            Movie(title="Harry Potter y el prisionero de Azkaban", genre="Fantasía", rating=5, added_by="Sistema"),
            Movie(title="Piratas del Caribe: La maldición de la Perla Negra", genre="Aventura", rating=4, added_by="Sistema"),
            Movie(title="El Rey León", genre="Animación", rating=5, added_by="Sistema"),
            Movie(title="Shrek", genre="Animación", rating=4, added_by="Sistema"),
            Movie(title="Ratatouille", genre="Animación", rating=5, added_by="Sistema"),
            Movie(title="Buscando a Nemo", genre="Animación", rating=4, added_by="Sistema"),
            Movie(title="Braveheart", genre="Histórica", rating=4, added_by="Sistema"),
            Movie(title="La lista de Schindler", genre="Histórica", rating=5, added_by="Sistema"),
            Movie(title="La vida es bella", genre="Drama", rating=5, added_by="Sistema"),
            Movie(title="Cadena perpetua", genre="Drama", rating=5, added_by="Sistema"),
            Movie(title="Whiplash", genre="Drama", rating=5, added_by="Sistema"),
            Movie(title="Black Panther", genre="Acción", rating=4, added_by="Sistema"),
            Movie(title="Mad Max: Furia en la carretera", genre="Acción", rating=5, added_by="Sistema"),
            Movie(title="Frozen", genre="Animación", rating=4, added_by="Sistema"),
            Movie(title="Los Increíbles", genre="Animación", rating=5, added_by="Sistema"),
            Movie(title="El viaje de Chihiro", genre="Animación", rating=5, added_by="Sistema"),
            Movie(title="Your Name", genre="Animación", rating=5, added_by="Sistema"),
            Movie(title="La forma del agua", genre="Fantástico", rating=4, added_by="Sistema"),
            Movie(title="Bohemian Rhapsody", genre="Biográfica", rating=4, added_by="Sistema"),
            Movie(title="Green Book", genre="Drama", rating=4, added_by="Sistema"),
            Movie(title="Gravity", genre="Ciencia ficción", rating=4, added_by="Sistema"),
            Movie(title="Wall-E", genre="Animación", rating=5, added_by="Sistema"),
            Movie(title="Memento", genre="Thriller", rating=5, added_by="Sistema"),
        ]

        db.session.add_all(initial_movies)
        db.session.commit()




# 🏠 Página principal: lista + búsqueda + recomendación “inteligente”
@app.route("/")
def index():
    # Parámetros GET para búsqueda/filtro
    q = request.args.get("q", "", type=str)
    genre_filter = request.args.get("genre", "", type=str)

    # Construir consulta
    query = Movie.query
    if q:
        query = query.filter(Movie.title.ilike(f"%{q}%"))
    if genre_filter:
        query = query.filter(Movie.genre.ilike(f"%{genre_filter}%"))

    movies = query.order_by(Movie.rating.desc()).all()

    # “Mecanismo inteligente”:
    # Buscar el género con mejor nota media y mostrar una recomendación
    best_movie = (
        db.session.query(Movie.genre, func.avg(Movie.rating).label("avg_rating"))
        .group_by(Movie.genre)
        .order_by(func.avg(Movie.rating).desc())
        .first()
    )

    recommendation = None
    if best_movie:
        # Película mejor puntuada dentro del género top
        recommendation = (
            Movie.query.filter_by(genre=best_movie.genre)
            .order_by(Movie.rating.desc())
            .first()
        )

    username = session.get("username")

    return render_template(
        "index.html",
        movies=movies,
        q=q,
        genre_filter=genre_filter,
        recommendation=recommendation,
        username=username,
    )


# ➕ Añadir película (GET: formulario, POST: guardar)
@app.route("/add", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        title = request.form.get("title")
        genre = request.form.get("genre")
        rating = request.form.get("rating", type=int)
        added_by = session.get("username")

        if title and genre and rating:
            movie = Movie(title=title, genre=genre, rating=rating, added_by=added_by)
            db.session.add(movie)
            db.session.commit()
            return redirect(url_for("index"))

    return render_template("add_movie.html")


# 🔐 Login sencillo con sesiones
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session["username"] = username
            return redirect(url_for("index"))
    return render_template("login.html")


# 🚪 Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
