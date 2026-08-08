import web
import sqlite3

render = web.template.render('mi_perfil_padre/views')

db_path = "sql/conaap.db"


class MiPerfilPadre:
    def GET(self):
        session = web.config._session
        id_padre = session.id_referencia

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT correo, nombre FROM usuario WHERE rol = 'padre' AND id_referencia = ?", (id_padre,))
        usuario = cur.fetchone()

        cur.execute("SELECT correo FROM padres WHERE id = ?", (id_padre,))
        padre = cur.fetchone()

        correo = usuario["correo"] if usuario else (padre["correo"] if padre else "sin-correo@conafe.gob.mx")
        nombre_completo = usuario["nombre"] if usuario else "Familia"

        partes_nombre = nombre_completo.split()
        apellidos_familia = " ".join(partes_nombre[1:]) if len(partes_nombre) > 1 else nombre_completo

        cur.execute("SELECT id_infante, nombre, edad FROM infantes WHERE id_padres = ?", (id_padre,))
        ninos_rows = cur.fetchall()

        ninos = []
        for nino in ninos_rows:
            cur.execute("SELECT COUNT(*) AS total FROM resultados WHERE id_infante1 = ?", (nino["id_infante"],))
            cuestionarios = cur.fetchone()["total"] or 0

            cur.execute("SELECT COUNT(*) AS total FROM actividad_casa_realizada WHERE id_infante = ?", (nino["id_infante"],))
            actividades_casa = cur.fetchone()["total"] or 0

            ninos.append({
                "nombre": nino["nombre"],
                "edad": nino["edad"],
                "cuestionarios": cuestionarios,
                "actividades_casa": actividades_casa
            })

        total_ninos = len(ninos)
        total_cuestionarios = sum(n["cuestionarios"] for n in ninos)
        total_actividades_casa = sum(n["actividades_casa"] for n in ninos)

        conn.close()

        return render.mi_perfil(
            "perfil", apellidos_familia, nombre_completo, correo, ninos, total_ninos, total_cuestionarios, total_actividades_casa
        )