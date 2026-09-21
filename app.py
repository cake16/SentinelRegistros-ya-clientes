import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder="sources", static_url_path="/sources")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")

# En local usa SQLite; en Render/producción define DATABASE_URL (Postgres de Neon/Supabase).
db_url = os.environ.get("DATABASE_URL", "sqlite:///registro.db")
if db_url.startswith("postgres://"):
    # SQLAlchemy moderno requiere el prefijo postgresql://
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from dotenv import load_dotenv
load_dotenv()


class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    empresa = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(200), nullable=False, unique=True)   
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
  


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/registrar", methods=["POST"])
def registrar():
    nombre = request.form.get("nombre", "").strip()
    empresa = request.form.get("empresa", "").strip()
    telefono = request.form.get("telefono", "").strip()
    correo = request.form.get("correo", "").strip().lower()

    if not nombre or not empresa or not telefono or not correo:
        flash("Todos los campos son obligatorios.")
        return redirect(url_for("index"))

    existente = Registro.query.filter_by(correo=correo).first()
    if existente:
        flash("Ese correo ya está registrado.")
        return redirect(url_for("index"))

    nuevo = Registro(
        nombre=nombre,
        empresa=empresa,
        telefono=telefono,
        correo=correo,
    )
    db.session.add(nuevo)
    db.session.commit()


    return render_template("exito.html", nombre=nombre)




with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
