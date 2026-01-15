from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from db import get_connection
from functools import wraps
import psycopg2.extras
from psycopg2 import errors
from io import BytesIO
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
    q = request.args.get("q", "").strip()
    carrera = request.args.get("carrera", "")
    estatus = request.args.get("estatus", "")

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = "SELECT * FROM egresados WHERE 1=1"
    params = []

    if q:
        query += " AND (matricula ILIKE %s OR nombre_completo ILIKE %s)"
        params.extend([f"%{q}%", f"%{q}%"])

    if carrera:
        query += " AND carrera = %s"
        params.append(carrera)

    if estatus:
        query += " AND estatus = %s"
        params.append(estatus)

    query += " ORDER BY id DESC"

    cur.execute(query, params)
    egresados = cur.fetchall()

    # Para los selects
    cur.execute("SELECT DISTINCT carrera FROM egresados ORDER BY carrera")
    carreras = [c[0] for c in cur.fetchall()]

    cur.execute("SELECT DISTINCT estatus FROM egresados ORDER BY estatus")
    estatuses = [e[0] for e in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template(
        "egresados.html",
        egresados=egresados,
        carreras=carreras,
        estatuses=estatuses,
        q=q,
        carrera_sel=carrera,
        estatus_sel=estatus
    )

# =========================
# VER EGRESADO (NUEVA RUTA)
# =========================
@egresados_bp.route("/egresados/ver/<int:id>")
@login_required
def ver_egresado(id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("SELECT * FROM egresados WHERE id = %s", (id,))
    egresado = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not egresado:
        flash("Egresado no encontrado.", "error")
        return redirect(url_for("egresados.listar_egresados"))
    
    return render_template("ver_egresado.html", egresado=egresado)

# =========================
# REGISTRAR EGRESADO
# =========================
@egresados_bp.route("/egresados/registrar", methods=["GET", "POST"])
@login_required
def registrar_egresado():

    if request.method == "GET":
        return render_template("registrar_egresado.html", registrado=False)

    matricula = request.form["matricula"].strip()

    # Validación matrícula
    if not matricula.isdigit() or len(matricula) != 8:
        flash("La matrícula debe tener exactamente 8 dígitos.", "error")
        return redirect(url_for("egresados.registrar_egresado"))

    # Generación OTRA
    generacion = request.form["generacion"]
    if generacion == "OTRA":
        generacion = request.form.get("otra_generacion", "").strip()
        if not generacion:
            flash("Debe especificar la generación.", "error")
            return redirect(url_for("egresados.registrar_egresado"))

    conn = get_connection()
    cur = conn.cursor()

    try:
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

    except errors.UniqueViolation:
        conn.rollback()
        flash("⚠️ La matrícula ya ha sido registrada.", "error")
        return redirect(url_for("egresados.registrar_egresado"))

    finally:
        cur.close()
        conn.close()

    return render_template("registrar_egresado.html", registrado=True)

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

@egresados_bp.route("/egresados/exportar/excel")
@login_required
def exportar_excel():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            matricula,
            nombre_completo,
            carrera,
            generacion,
            estatus,
            domicilio,
            genero,
            telefono,
            correo,
            fecha_registro
        FROM egresados
        ORDER BY id
    """)
    datos = cur.fetchall()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Egresados"

    encabezados = [
        "Matrícula", "Nombre Completo", "Carrera", "Generación",
        "Estatus", "Domicilio", "Género", "Teléfono",
        "Correo", "Fecha de Registro"
    ]

    ws.append(encabezados)

    # 🎨 Estilo encabezados
    from openpyxl.styles import Font, PatternFill, Border, Side

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="0B3D1E")
    border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )

    for col in range(1, len(encabezados) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border

    # 📄 Datos
    for fila in datos:
        ws.append(fila)

    # 📐 Ajustar ancho de columnas
    for column_cells in ws.columns:
        length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
        ws.column_dimensions[column_cells[0].column_letter].width = length + 2

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    cur.close()
    conn.close()

    return send_file(
        buffer,
        as_attachment=True,
        download_name="egresados_completo.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@egresados_bp.route("/egresados/exportar/pdf")
@login_required
def exportar_pdf():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            matricula,
            nombre_completo,
            carrera,
            generacion,
            estatus,
            telefono,
            correo
        FROM egresados
        ORDER BY id
    """)
    datos = cur.fetchall()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # 🧾 Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 40, "Reporte General de Egresados")

    y = height - 80

    pdf.setFont("Helvetica-Bold", 10)
    encabezados = ["Matrícula", "Nombre", "Carrera", "Generación", "Estatus", "Teléfono", "Correo"]

    x_positions = [40, 90, 210, 330, 420, 490, 560]

    for i, h in enumerate(encabezados):
        pdf.drawString(x_positions[i], y, h)

    y -= 20
    pdf.setFont("Helvetica", 9)

    for fila in datos:
        for i, valor in enumerate(fila):
            pdf.drawString(x_positions[i], y, str(valor))
        y -= 15

        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = height - 50

    pdf.save()
    buffer.seek(0)

    cur.close()
    conn.close()

    return send_file(
        buffer,
        as_attachment=True,
        download_name="egresados_completo.pdf",
        mimetype="application/pdf"
    )