from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db import get_connection
from functools import wraps
import psycopg2.extras

egresados_bp = Blueprint("egresados", __name__)

# =========================
# DECORADOR LOGIN
# =========================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

# =========================
# LISTAR EGRESADOS
# =========================
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

# =========================
# REGISTRAR EGRESADO
# =========================
@egresados_bp.route("/egresados/registrar", methods=["GET", "POST"])
@login_required
def registrar_egresado():

    # 👉 GET: solo mostrar formulario
    if request.method == "GET":
        return render_template(
            "registrar_egresado.html",
            registrado=False
        )

    # 👉 POST: guardar egresado
    matricula = request.form["matricula"].strip()

    # Validación matrícula
    if not matricula.isdigit() or len(matricula) != 8:
        flash("La matrícula debe tener exactamente 8 dígitos.", "error")
        return redirect(url_for("egresados.registrar_egresado"))

    # Generación "OTRA"
    generacion = request.form["generacion"]
    if generacion == "OTRA":
        generacion = request.form.get("otra_generacion", "").strip()
        if not generacion:
            flash("Debe especificar la generación.", "error")
            return redirect(url_for("egresados.registrar_egresado"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO egresados
        (matricula, nombre_completo, carrera, generacion, estatus,
         domicilio, genero, telefono, correo)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        matricula,
        request.form["nombre"],
        request.form["carrera"],
        generacion,
        request.form["estatus"],
        request.form.get("domicilio"),
        request.form.get("genero"),
        request.form.get("telefono"),
        request.form.get("correo")
    ))

    conn.commit()
    cur.close()
    conn.close()

    # 👉 MOSTRAR FORMULARIO CON MENSAJE DE ÉXITO
    return render_template(
        "registrar_egresado.html",
        registrado=True
    )

# =========================
# EDITAR EGRESADO
# =========================
@egresados_bp.route("/egresados/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_egresado(id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == "POST":

        generacion = request.form["generacion"]
        if generacion == "OTRA":
            generacion = request.form.get("otra_generacion", "").strip()

        cur.execute("""
            UPDATE egresados
            SET matricula = %s,
                nombre_completo = %s,
                carrera = %s,
                generacion = %s,
                estatus = %s,
                domicilio = %s,
                genero = %s,
                telefono = %s,
                correo = %s
            WHERE id = %s
        """, (
            request.form["matricula"],
            request.form["nombre"],
            request.form["carrera"],
            generacion,
            request.form["estatus"],
            request.form.get("domicilio"),
            request.form.get("genero"),
            request.form.get("telefono"),
            request.form.get("correo"),
            id
        ))

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("egresados.listar_egresados"))

    # GET
    cur.execute("SELECT * FROM egresados WHERE id = %s", (id,))
    egresado = cur.fetchone()
    cur.close()
    conn.close()

    return render_template("editar_egresado.html", egresado=egresado)

# =========================
# ELIMINAR EGRESADO
# =========================
@egresados_bp.route("/egresados/eliminar/<int:id>")
@login_required
def eliminar_egresado(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM egresados WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("egresados.listar_egresados"))
