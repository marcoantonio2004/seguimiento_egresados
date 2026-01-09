from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection
from functools import wraps
import psycopg2.extras

egresados_bp = Blueprint("egresados", __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

@egresados_bp.route("/egresados")
@login_required
def listar_egresados():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM egresados ORDER BY id DESC")
    egresados = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("egresados.html", egresados=egresados)

@egresados_bp.route("/egresados/registrar", methods=["GET", "POST"])
@login_required
def registrar_egresado():
    if request.method == "POST":
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO egresados
            (matricula, nombre_completo, carrera, generacion, estatus, domicilio, genero, telefono, correo)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            request.form["matricula"],
            request.form["nombre"],
            request.form["carrera"],
            request.form["generacion"],
            request.form["estatus"],
            request.form["domicilio"],
            request.form["genero"],
            request.form["telefono"],
            request.form["correo"]
        ))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("egresados.listar_egresados"))

    return render_template("registrar_egresado.html")
