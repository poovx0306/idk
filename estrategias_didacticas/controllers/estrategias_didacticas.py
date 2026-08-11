import web
import sqlite3
import datetime

render = web.template.render('estrategias_didacticas/views')


def obtener_docente(cursor, id_docente):
    cursor.execute("""
        SELECT docente.nombre, usuario.correo
        FROM docente
        JOIN usuario ON usuario.id_referencia = docente.id_docente AND usuario.rol = 'docente'
        WHERE docente.id_docente = ?
    """, (id_docente,))
    fila = cursor.fetchone()
    nombre = fila["nombre"] if fila else "Docente"
    correo = fila["correo"] if fila else "sin-correo@conafe.gob.mx"
    return nombre, correo


class EstrategiasDidacticas:
    def GET(self):
        datos = web.input(id="1", condicion="Autismo (TEA)", materia="", grado="")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        nombre_docente, correo_docente = obtener_docente(cursor, id_docente)

        consulta = "SELECT * FROM temas WHERE estado = 'Publicada'"
        parametros = []

        if datos.condicion:
            consulta += " AND condicion = ?"
            parametros.append(datos.condicion)
        if datos.materia:
            consulta += " AND materia = ?"
            parametros.append(datos.materia)
        if datos.grado:
            consulta += " AND grado = ?"
            parametros.append(datos.grado)

        consulta += " ORDER BY materia, titulo"

        cursor.execute(consulta, parametros)
        estrategias = cursor.fetchall()

        cursor.execute(
            "SELECT DISTINCT materia FROM temas "
            "WHERE estado = 'Publicada' AND materia IS NOT NULL AND materia <> '' "
            "ORDER BY materia"
        )
        lista_materias = [fila["materia"] for fila in cursor.fetchall()]

        cursor.execute(
            "SELECT DISTINCT grado FROM temas "
            "WHERE estado = 'Publicada' AND grado IS NOT NULL AND grado <> '' "
            "ORDER BY grado"
        )
        lista_grados = [fila["grado"] for fila in cursor.fetchall()]

        conexion.close()

        return render.estrategias_didacticas(
            id_docente, nombre_docente, correo_docente, estrategias,
            datos.condicion, datos.materia, datos.grado,
            lista_materias, lista_grados
        )


class FichaActividad:
    def GET(self):
        datos = web.input(id_estrategia="", id="1", id_alumno="", guardado="")
        id_docente = datos.id

        conexion = sqlite3.connect("sql/conaap.db")
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        nombre_docente, correo_docente = obtener_docente(cursor, id_docente)

        cursor.execute("SELECT * FROM temas WHERE id = ?", (datos.id_estrategia,))
        estrategia = cursor.fetchone()

        if not estrategia:
            conexion.close()
            raise web.notfound()

        texto_pasos = estrategia["paso_a_paso"] or ""
        pasos = [p.strip() for p in texto_pasos.split("|") if p.strip()]

        cursor.execute(
            "SELECT * FROM criterio_tema WHERE id_tema = ? ORDER BY id",
            (datos.id_estrategia,)
        )
        criterios = cursor.fetchall()

        cursor.execute(
            "SELECT id_infante, nombre FROM infantes WHERE id_docente1 = ? ORDER BY nombre",
            (id_docente,)
        )
        alumnos = cursor.fetchall()

        marcados = []
        observaciones = ""
        fecha_previa = ""

        try:
            id_alumno_sel = int(datos.id_alumno) if datos.id_alumno else ""
        except ValueError:
            id_alumno_sel = ""

        if id_alumno_sel:
            cursor.execute("""
                SELECT id, fecha, observaciones FROM retroalimentacion
                WHERE id_tema = ? AND id_infante = ?
                ORDER BY id DESC LIMIT 1
            """, (datos.id_estrategia, id_alumno_sel))
            previa = cursor.fetchone()

            if previa:
                fecha_previa = previa["fecha"]
                observaciones = previa["observaciones"] or ""
                cursor.execute("""
                    SELECT id_criterio FROM retroalimentacion_criterio
                    WHERE id_retroalimentacion = ? AND logrado = 1
                """, (previa["id"],))
                marcados = [fila["id_criterio"] for fila in cursor.fetchall()]

        conexion.close()

        return render.ficha_actividad(
            id_docente, nombre_docente, correo_docente, estrategia, pasos,
            criterios, alumnos, id_alumno_sel, marcados, observaciones,
            fecha_previa, datos.guardado
        )


class GuardarRetroalimentacion:
    def POST(self):
        datos = web.input(id_estrategia="", id="1", id_alumno="",
                          observaciones="", criterio=[])
        id_docente = datos.id
        id_tema = datos.id_estrategia
        id_alumno = datos.id_alumno

        volver = "/estrategias-didacticas/ficha?id_estrategia=%s&id=%s" % (id_tema, id_docente)

        if not id_alumno:
            raise web.HTTPError('303 See Other', {'Location': volver})

        marcados = datos.criterio
        if not isinstance(marcados, list):
            marcados = [marcados]

        conexion = None
        try:
            conexion = sqlite3.connect("sql/conaap.db")
            cursor = conexion.cursor()

            fecha = datetime.date.today().isoformat()

            cursor.execute("""
                INSERT INTO retroalimentacion
                (id_tema, id_infante, id_docente, fecha, observaciones)
                VALUES (?, ?, ?, ?, ?)
            """, (id_tema, id_alumno, id_docente, fecha, datos.observaciones))

            id_retro = cursor.lastrowid

            cursor.execute("SELECT id FROM criterio_tema WHERE id_tema = ?", (id_tema,))
            todos = [fila[0] for fila in cursor.fetchall()]

            for id_criterio in todos:
                logrado = 1 if str(id_criterio) in [str(m) for m in marcados] else 0
                cursor.execute("""
                    INSERT INTO retroalimentacion_criterio
                    (id_retroalimentacion, id_criterio, logrado)
                    VALUES (?, ?, ?)
                """, (id_retro, id_criterio, logrado))

            conexion.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al guardar retroalimentacion:", e)
        except Exception as e:
            print("Error inesperado al guardar retroalimentacion:", e)
        finally:
            if conexion:
                conexion.close()

        destino = "%s&id_alumno=%s&guardado=1" % (volver, id_alumno)
        raise web.HTTPError('303 See Other', {'Location': destino})