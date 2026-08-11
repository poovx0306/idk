import web
import sqlite3

render = web.template.render('mi_perfil_docente/views')


class MiPerfil:
    def GET(self):
        datos = web.input(id="1")
        id_docente = datos.id
        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT id_docente, nombre, clave_docente, correo FROM docente WHERE id_docente = ?",
            (id_docente,),
        )
        docente = cursor.fetchone()
        if not docente:
            conexion.close()
            return "Docente no encontrado"

        cursor.execute("SELECT COUNT(*) FROM infantes WHERE id_docente1 = ?", (id_docente,))
        total_alumnos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM retroalimentacion WHERE id_docente = ?", (id_docente,))
        total_evaluaciones = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(DISTINCT id_infante) FROM retroalimentacion WHERE id_docente = ?",
            (id_docente,),
        )
        total_alumnos_evaluados = cursor.fetchone()[0]

        # Temas dominados al 100%: por cada combinacion alumno+tema, se toma solo
        # el ultimo intento registrado y se cuenta si logro todos los criterios.
        cursor.execute("""
            SELECT r.id_infante, r.id_tema, r.id
            FROM retroalimentacion r
            WHERE r.id_docente = ?
            AND r.id = (
                SELECT MAX(r2.id) FROM retroalimentacion r2
                WHERE r2.id_infante = r.id_infante AND r2.id_tema = r.id_tema
            )
        """, (id_docente,))
        ultimos_intentos = cursor.fetchall()
        total_dominados = 0
        for intento in ultimos_intentos:
            cursor.execute("SELECT COUNT(*) FROM criterio_tema WHERE id_tema = ?", (intento["id_tema"],))
            total_criterios = cursor.fetchone()[0]
            cursor.execute(
                "SELECT COUNT(*) FROM retroalimentacion_criterio WHERE id_retroalimentacion = ? AND logrado = 1",
                (intento["id"],),
            )
            logrados = cursor.fetchone()[0]
            if total_criterios > 0 and logrados == total_criterios:
                total_dominados += 1

        cursor.execute("SELECT COUNT(*) FROM crisis_atendida WHERE id_docente = ?", (id_docente,))
        total_crisis = cursor.fetchone()[0]

        conexion.close()
        return render.mi_perfil(
            docente["id_docente"],
            docente["nombre"],
            docente["clave_docente"],
            docente["correo"],
            total_alumnos,
            total_evaluaciones,
            total_alumnos_evaluados,
            total_dominados,
            total_crisis,
        )
