from flask import Flask, render_template, redirect, url_for, session
from auth import auth_bp
from egresados import egresados_bp

app = Flask(__name__)
app.secret_key = "clave_secreta_egresados"

app.register_blueprint(auth_bp)
app.register_blueprint(egresados_bp)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html")
