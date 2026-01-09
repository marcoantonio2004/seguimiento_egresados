from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection
from functools import wraps

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
    egresados = conn.execute("SELECT * FROM egresados").fetchall()
    conn.close()
    return render_template("egresados.html", egresados=egresados)


@egresados_bp.route("/egresados/registrar", methods=["GET", "POST"])
@login_required
def registrar_egresado():
    if request.method == "POST":
        datos = (
            request.form["matricula"],
            request.form["nombre"],
            request.form["carrera"],
            request.form["generacion"],
            request.form["estatus"],
            request.form["domicilio"],
            request.form["genero"],
            request.form["telefono"],
            request.form["correo"]
        )

        conn = get_connection()
        conn.execute("""
            INSERT INTO egresados 
            (matricula, nombre_completo, carrera, generacion, estatus, domicilio, genero, telefono, correo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, datos)
        conn.commit()
        conn.close()

        return redirect(url_for("egresados.listar_egresados"))

    return render_template("registrar_egresado.html")

