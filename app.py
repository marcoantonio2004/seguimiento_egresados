from flask import Flask, render_template, redirect, url_for, session
from auth import auth_bp
from egresados import egresados_bp
from db import get_connection
import psycopg2.extras

app = Flask(__name__)
app.secret_key = "clave_secreta_egresados"

app.register_blueprint(auth_bp)
app.register_blueprint(egresados_bp)

@app.route("/")
def index():
    return render_template("index.html")

# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Alumnos totales
    cur.execute("SELECT COUNT(*) FROM egresados")
    alumnos_totales = cur.fetchone()[0]

    # Egresados
    cur.execute("SELECT COUNT(*) FROM egresados WHERE estatus = 'Egresado'")
    total_egresados = cur.fetchone()[0]

    # Titulados
    cur.execute("SELECT COUNT(*) FROM egresados WHERE estatus = 'Titulado'")
    total_titulados = cur.fetchone()[0]

    # En seguimiento
    cur.execute("SELECT COUNT(*) FROM egresados WHERE estatus = 'En seguimiento'")
    total_seguimiento = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        "dashboard.html",
        alumnos_totales=alumnos_totales,
        total_egresados=total_egresados,
        total_titulados=total_titulados,
        total_seguimiento=total_seguimiento
    )

if __name__ == "__main__":
    app.run(debug=True)
