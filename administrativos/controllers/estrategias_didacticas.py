import web
import sqlite3

render = web.template.render('administrativos/views/')


def conectar_bd():
    conn = sqlite3.connect('sql/conaap.db')
    conn.row_factory = sqlite3.Row
    return conn


def catalogos(cursor):
    cursor.execute(
        "SELECT DISTINCT materia FROM temas "
        "WHERE materia IS NOT NULL AND materia <> '' ORDER BY materia"
    )
    materias = [fila['materia'] for fila in cursor.fetchall()]

    cursor.execute(
        "SELECT DISTINCT grado FROM temas "
        "WHERE grado IS NOT NULL AND grado <> '' ORDER BY grado"
    )
    grados = [fila['grado'] for fila in cursor.fetchall()]

    return materias, grados


class EstrategiasDidacticasAdmin:
    def GET(self):
        data = web.input(materia='', grado='', buscar='')
        materia = data.get('materia', '').strip()
        grado = data.get('grado', '').strip()
        buscar = data.get('buscar', '').strip()

        conn = conectar_bd()
        cursor = conn.cursor()

        query = "SELECT * FROM temas WHERE 1=1"
        params = []

        if buscar:
            query += " AND LOWER(titulo) LIKE LOWER(?)"
            params.append('%' + buscar + '%')

        if materia:
            query += " AND LOWER(materia) = LOWER(?)"
            params.append(materia)

        if grado:
            query += " AND grado = ?"
            params.append(grado)

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        temas = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM temas")
        total_temas = cursor.fetchone()['total']

        lista_materias, lista_grados = catalogos(cursor)

        conn.close()

        return render.estrategias_didacticas(
            estrategias=temas,
            total=total_temas,
            materia_sel=materia,
            grado_sel=grado,
            buscar_sel=buscar,
            lista_materias=lista_materias,
            lista_grados=lista_grados
        )


class NuevaEstrategiaAdmin:
    def GET(self):
        return render.nueva_estrategia()

    def POST(self):
        data = web.input(titulo='', condicion='', materia='', grado='',
                         objetivo='', materiales='', pasos='', accion='Publicar')

        titulo = data.get('titulo', '').strip()
        condicion = data.get('condicion')
        materia = data.get('materia')
        grado = data.get('grado')
        objetivo = data.get('objetivo')
        materiales = data.get('materiales')
        paso_a_paso = data.get('pasos')
        estado = 'Publicada' if data.get('accion') == 'Publicar' else 'Borrador'

        if not titulo:
            return render.confirmacion(
                titulo='Faltan datos',
                mensaje='El titulo del tema es obligatorio.',
                volver_url='/administrativo/estrategias/nueva',
                volver_texto='Regresar al formulario',
                tipo='error'
            )

        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO temas
                (titulo, condicion, materia, grado, objetivo, materiales, paso_a_paso, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (titulo, condicion, materia, grado, objetivo, materiales, paso_a_paso, estado)
            )
            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al crear tema:", e)
            return render.confirmacion(
                titulo='No se pudo guardar',
                mensaje='Ocurrio un problema al guardar el tema en la base de datos.',
                volver_url='/administrativo/estrategias/nueva',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al crear tema:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al guardar el tema.',
                volver_url='/administrativo/estrategias/nueva',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        if estado == 'Publicada':
            mensaje = '"%s" se publico y ya es visible para los docentes.' % titulo
        else:
            mensaje = '"%s" se guardo como borrador. Todavia no lo ven los docentes.' % titulo

        return render.confirmacion(
            titulo='Tema guardado',
            mensaje=mensaje,
            volver_url='/administrativo/estrategias',
            volver_texto='Volver a la lista'
        )


class EditarEstrategiaAdmin:
    def GET(self):
        data = web.input()
        id = data.get('id')

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM temas WHERE id = ?", (id,))
        tema = cursor.fetchone()
        conn.close()

        if not tema:
            return render.confirmacion(
                titulo='Tema no encontrado',
                mensaje='No existe un tema con ese identificador.',
                volver_url='/administrativo/estrategias',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        return render.editar_estrategia(actividad=tema)

    def POST(self):
        data = web.input()
        id = data.get('id')
        titulo = data.get('titulo')
        condicion = data.get('condicion')
        objetivo = data.get('objetivo')
        materiales = data.get('materiales')
        paso_a_paso = data.get('paso_a_paso')
        materia = data.get('materia')
        grado = data.get('grado')
        estado = data.get('estado')

        if not id:
            return render.confirmacion(
                titulo='No se indico el tema',
                mensaje='No se recibio el identificador del tema a editar.',
                volver_url='/administrativo/estrategias',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE temas
                SET titulo=?, condicion=?, objetivo=?, materiales=?,
                    paso_a_paso=?, materia=?, grado=?, estado=?
                WHERE id=?
            """, (titulo, condicion, objetivo, materiales, paso_a_paso, materia, grado, estado, id))
            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al editar tema:", e)
            return render.confirmacion(
                titulo='No se guardaron los cambios',
                mensaje='Ocurrio un problema al actualizar el tema.',
                volver_url='/administrativo/estrategias/editar?id=%s' % id,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al editar tema:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al editar el tema.',
                volver_url='/administrativo/estrategias/editar?id=%s' % id,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Cambios guardados',
            mensaje='Los datos de "%s" se actualizaron correctamente.' % titulo,
            volver_url='/administrativo/estrategias',
            volver_texto='Volver a la lista'
        )


class BajaEstrategiaAdmin:
    def POST(self):
        data = web.input(id='')
        id = data.get('id')

        if not id:
            return render.confirmacion(
                titulo='No se indico el tema',
                mensaje='No se recibio el identificador del tema a eliminar.',
                volver_url='/administrativo/estrategias',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("SELECT titulo FROM temas WHERE id = ?", (id,))
            fila = cursor.fetchone()
            nombre = fila['titulo'] if fila else 'El tema'

            cursor.execute("DELETE FROM temas WHERE id = ?", (id,))
            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al eliminar tema:", e)
            return render.confirmacion(
                titulo='No se pudo eliminar',
                mensaje='Ocurrio un problema al eliminar el tema.',
                volver_url='/administrativo/estrategias',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al eliminar tema:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al eliminar el tema.',
                volver_url='/administrativo/estrategias',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Tema eliminado',
            mensaje='"%s" se elimino del repositorio y ya no lo ven los docentes.' % nombre,
            volver_url='/administrativo/estrategias',
            volver_texto='Volver a la lista'
        )