import web
import sqlite3

render = web.template.render('actividades_guardadas/views')


class ActividadesGuardadas:
    """Lista las actividades asignadas por el docente, con filtros."""

    def GET(self):
        datos = web.input(id="1", grado="", grupo="", materia="")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        consulta = "SELECT * FROM actividad_asignada WHERE id_docente = ?"
        parametros = [id_docente]

        if datos.grado:
            consulta += " AND grado = ?"
            parametros.append(datos.grado)
        if datos.grupo:
            consulta += " AND grupo = ?"
            parametros.append(datos.grupo)
        if datos.materia:
            consulta += " AND materia = ?"
            parametros.append(datos.materia)

        consulta += " ORDER BY fecha_asignacion DESC"

        cursor.execute(consulta, parametros)
        actividades = cursor.fetchall()
        conexion.close()

        return render.actividades_guardadas(
            id_docente, actividades, datos.grado, datos.grupo, datos.materia
        )


def _cargar_ficha(id_docente, id_actividad):
    """Arma todo lo que necesita la plantilla de la ficha. La usan GET y los dos POST,
    para nunca depender de un redirect."""
    conexion = sqlite3.connect("sql/conaap.db")
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT a.*, d.nombre AS nombre_docente
        FROM actividad_asignada a
        JOIN docente d ON d.id_docente = a.id_docente
        WHERE a.id = ?
    """, (id_actividad,))
    actividad = cursor.fetchone()

    cursor.execute(
        "SELECT 1 FROM actividad_favorita WHERE id_docente = ? AND id_actividad = ?",
        (id_docente, id_actividad),
    )
    guardada = cursor.fetchone() is not None

    conexion.close()

    if not actividad:
        raise web.notfound()

    texto_materiales = actividad["materiales"] or ""
    materiales = [m.strip() for m in texto_materiales.split("·") if m.strip()]

    texto_pasos = actividad["paso_a_paso"] or ""
    pasos = [p.strip() for p in texto_pasos.split("|") if p.strip()]

    return render.ficha_actividad_asignada(id_docente, actividad, materiales, pasos, guardada)


class FichaActividadAsignada:
    """Detalle de una actividad asignada: objetivo, materiales y pasos."""

    def GET(self):
        datos = web.input(id="1", id_actividad="")
        return _cargar_ficha(datos.id, datos.id_actividad)


class MarcarActividad:
    """Cambia el estado de una actividad entre Pendiente y Completada (persistido en BD)."""

    def POST(self):
        datos = web.input(id="1", id_actividad="")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        cursor = conexion.cursor()

        cursor.execute("SELECT estado FROM actividad_asignada WHERE id = ?", (datos.id_actividad,))
        fila = cursor.fetchone()
        estado_actual = fila[0] if fila else "Pendiente"
        nuevo_estado = "Pendiente" if estado_actual == "Completada" else "Completada"

        cursor.execute(
            "UPDATE actividad_asignada SET estado = ? WHERE id = ?",
            (nuevo_estado, datos.id_actividad),
        )
        conexion.commit()
        conexion.close()

        return _cargar_ficha(id_docente, datos.id_actividad)


class GuardarActividad:
    """Guarda o quita una actividad de los favoritos personales del docente."""

    def POST(self):
        datos = web.input(id="1", id_actividad="")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT 1 FROM actividad_favorita WHERE id_docente = ? AND id_actividad = ?",
            (id_docente, datos.id_actividad),
        )
        ya_guardada = cursor.fetchone() is not None

        if ya_guardada:
            cursor.execute(
                "DELETE FROM actividad_favorita WHERE id_docente = ? AND id_actividad = ?",
                (id_docente, datos.id_actividad),
            )
        else:
            cursor.execute(
                "INSERT INTO actividad_favorita (id_docente, id_actividad) VALUES (?, ?)",
                (id_docente, datos.id_actividad),
            )
        conexion.commit()
        conexion.close()

class MisActividadesGuardadas:
    """Lista solo las actividades que el docente marco como guardadas (favoritas)."""

    def GET(self):
        datos = web.input(id="1")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT a.*
            FROM actividad_favorita f
            JOIN actividad_asignada a ON a.id = f.id_actividad
            WHERE f.id_docente = ?
            ORDER BY a.fecha_asignacion DESC
        """, (id_docente,))
        guardadas = cursor.fetchall()
        conexion.close()

        return render.mis_actividades_guardadas(id_docente, guardadas)

        return _cargar_ficha(id_docente, datos.id_actividad)