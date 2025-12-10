from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hola, mundo desde Flask en la nube 👋"

if __name__ == "__main__":
    # Solo para desarrollo local
    app.run(debug=True)
