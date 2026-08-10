import web
import sqlite3
import os

render = web.template.render('administrativos/views/')


def conectar_bd():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'sql', 'conaap.db')

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # OJO: aqui NO se activa PRAGMA foreign_keys.
    # La tabla 'cuestionario' (singular, sin uso) declara una llave foranea
    # rota hacia preguntas(id_pregunta), columna que no existe. Con el PRAGMA
    # encendido, SQLite rechaza cualquier DELETE sobre preguntas con el error
    # "foreign key mismatch". Se deja apagado hasta que esa tabla se corrija.
    return conn


class Cuestionarios:
    def GET(self):
        cuestionarios_datos = []
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute('SELECT id, titulo, estado FROM cuestionarios')
            filas = cursor.fetchall()

            for f in filas:
                cuestionario_id = f["id"]

                # Contar cuantas preguntas pertenecen a este cuestionario
                cursor.execute(
                    'SELECT COUNT(*) AS total FROM preguntas WHERE cuestionario_id = ?',
                    (cuestionario_id,)
                )
                conteo = cursor.fetchone()
                total_preguntas = conteo['total'] if conteo else 0

                # Contar cuantas secciones unicas hay
                cursor.execute(
                    'SELECT COUNT(DISTINCT seccion) AS total FROM preguntas WHERE cuestionario_id = ?',
                    (cuestionario_id,)
                )
                conteo_secciones = cursor.fetchone()
                total_secciones = conteo_secciones['total'] if conteo_secciones else 0

                # Contar cuantas respuestas/resultados se han guardado
                cursor.execute('SELECT COUNT(*) AS total FROM resultados')
                conteo_respuestas = cursor.fetchone()
                total_respuestas = conteo_respuestas['total'] if conteo_respuestas else 0

                cuestionarios_datos.append({
                    "id": f["id"],
                    "titulo": f["titulo"],
                    "preguntas": total_preguntas,
                    "secciones": total_secciones,
                    "respuestas": total_respuestas,
                    "estado": f["estado"]
                })

        except sqlite3.Error as e:
            print("Error de base de datos en Cuestionarios:", e)
        except Exception as e:
            print("Error inesperado en Cuestionarios:", e)
        finally:
            if conn:
                conn.close()

        return render.cuestionarios(cuestionarios=cuestionarios_datos)


class NuevoCuestionario:
    def GET(self):
        return render.nuevo_cuestionario()

    def POST(self):
        data = web.input(titulo='', estado='Activo')
        titulo = (data.titulo or '').strip()
        estado = (data.estado or 'Activo').strip()
        conn = None

        if not titulo:
            return render.confirmacion(
                titulo='Faltan datos',
                mensaje='El titulo del cuestionario es obligatorio.',
                volver_url='/administrativo/cuestionarios/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cuestionarios (titulo, estado) VALUES (?, ?)",
                (titulo, estado)
            )
            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al crear cuestionario:", e)
            return render.confirmacion(
                titulo='No se pudo crear',
                mensaje='Ocurrio un problema al guardar el cuestionario en la base de datos.',
                volver_url='/administrativo/cuestionarios/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al crear cuestionario:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al crear el cuestionario.',
                volver_url='/administrativo/cuestionarios/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Cuestionario creado',
            mensaje='"%s" se agrego correctamente y quedo como %s.' % (titulo, estado),
            volver_url='/administrativo/cuestionarios',
            volver_texto='Volver a la lista'
        )


class EditarCuestionario:
    def GET(self):
        data = web.input(id='')
        cuestionario_id = data.id
        cuestionario = None
        preguntas = []
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM cuestionarios WHERE id = ?", (cuestionario_id,))
            cuestionario = cursor.fetchone()

            cursor.execute("SELECT * FROM preguntas WHERE cuestionario_id = ?", (cuestionario_id,))
            preguntas = cursor.fetchall()

        except sqlite3.Error as e:
            print("Error de base de datos en EditarCuestionario:", e)
        except Exception as e:
            print("Error inesperado en EditarCuestionario:", e)
        finally:
            if conn:
                conn.close()

        if not cuestionario:
            return render.confirmacion(
                titulo='Cuestionario no encontrado',
                mensaje='No existe un cuestionario con ese identificador.',
                volver_url='/administrativo/cuestionarios',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        return render.editar_cuestionario(cuestionario=cuestionario, preguntas=preguntas)

    def POST(self):
        data = web.input(cuestionario_id='', titulo_cuestionario='',
                         texto_pregunta='', seccion='General', numero_pregunta='1')
        cuestionario_id = data.cuestionario_id
        titulo = (data.titulo_cuestionario or '').strip()
        texto_pregunta = (data.texto_pregunta or '').strip()
        seccion = (data.seccion or 'General').strip()
        numero_pregunta = data.numero_pregunta
        pregunta_agregada = False
        conn = None

        if not cuestionario_id:
            return render.confirmacion(
                titulo='No se indico el cuestionario',
                mensaje='No se recibio el identificador del cuestionario a editar.',
                volver_url='/administrativo/cuestionarios',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # 1. Actualizar el titulo del cuestionario
            if titulo:
                cursor.execute(
                    "UPDATE cuestionarios SET titulo = ? WHERE id = ?",
                    (titulo, cuestionario_id)
                )

            # 2. Si escribio una nueva pregunta, insertarla
            if texto_pregunta:
                cursor.execute('''
                    INSERT INTO preguntas (cuestionario_id, numero_pregunta, seccion, texto,
                                           puntos_casi_nunca, puntos_a_veces, puntos_casi_siempre)
                    VALUES (?, ?, ?, ?, 2, 1, 0)
                ''', (cuestionario_id, numero_pregunta, seccion, texto_pregunta))
                pregunta_agregada = True

            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al editar cuestionario:", e)
            return render.confirmacion(
                titulo='No se guardaron los cambios',
                mensaje='Ocurrio un problema al actualizar el cuestionario.',
                volver_url='/administrativo/cuestionarios/editar?id=%s' % cuestionario_id,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al editar cuestionario:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al editar el cuestionario.',
                volver_url='/administrativo/cuestionarios/editar?id=%s' % cuestionario_id,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        if pregunta_agregada:
            mensaje = 'Los cambios se guardaron y la pregunta nueva se agrego al cuestionario.'
        else:
            mensaje = 'Los cambios del cuestionario se guardaron correctamente.'

        return render.confirmacion(
            titulo='Cambios guardados',
            mensaje=mensaje,
            volver_url='/administrativo/cuestionarios',
            volver_texto='Volver a la lista'
        )


class EliminarCuestionario:
    def POST(self):
        data = web.input(id='')
        cuestionario_id = data.id
        titulo_cuestionario = ''
        conn = None

        if not cuestionario_id:
            return render.confirmacion(
                titulo='No se indico el cuestionario',
                mensaje='No se recibio el identificador del cuestionario a eliminar.',
                volver_url='/administrativo/cuestionarios',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT titulo FROM cuestionarios WHERE id = ?", (cuestionario_id,))
            fila = cursor.fetchone()

            if not fila:
                return render.confirmacion(
                    titulo='Cuestionario no encontrado',
                    mensaje='Ese cuestionario ya no existe en el sistema.',
                    volver_url='/administrativo/cuestionarios',
                    volver_texto='Volver a la lista',
                    tipo='error'
                )

            titulo_cuestionario = fila['titulo']

            # Elimina el cuestionario y sus preguntas correspondientes
            cursor.execute("DELETE FROM cuestionarios WHERE id = ?", (cuestionario_id,))
            cursor.execute("DELETE FROM preguntas WHERE cuestionario_id = ?", (cuestionario_id,))
            conn.commit()

        except sqlite3.IntegrityError as e:
            print("No se puede eliminar el cuestionario por registros relacionados:", e)
            return render.confirmacion(
                titulo='No se puede eliminar',
                mensaje='Este cuestionario tiene resultados registrados y no puede eliminarse.',
                volver_url='/administrativo/cuestionarios',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        except sqlite3.Error as e:
            print("Error de base de datos al eliminar cuestionario:", e)
            return render.confirmacion(
                titulo='No se pudo eliminar',
                mensaje='Ocurrio un problema al eliminar el cuestionario de la base de datos.',
                volver_url='/administrativo/cuestionarios',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al eliminar cuestionario:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al eliminar el cuestionario.',
                volver_url='/administrativo/cuestionarios',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Cuestionario eliminado',
            mensaje='"%s" se elimino junto con sus preguntas.' % titulo_cuestionario,
            volver_url='/administrativo/cuestionarios',
            volver_texto='Volver a la lista'
        )


class VerPreguntasCuestionario:
    def GET(self):
        data = web.input(id='')
        cuestionario_id = data.id
        cuestionario = None
        preguntas = []
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # Obtener titulo e informacion del cuestionario
            cursor.execute("SELECT * FROM cuestionarios WHERE id = ?", (cuestionario_id,))
            cuestionario = cursor.fetchone()

            # Obtener la lista de preguntas
            cursor.execute(
                "SELECT * FROM preguntas WHERE cuestionario_id = ? ORDER BY numero_pregunta ASC",
                (cuestionario_id,)
            )
            preguntas = cursor.fetchall()

        except sqlite3.Error as e:
            print("Error de base de datos en VerPreguntasCuestionario:", e)
        except Exception as e:
            print("Error inesperado en VerPreguntasCuestionario:", e)
        finally:
            if conn:
                conn.close()

        if not cuestionario:
            return render.confirmacion(
                titulo='Cuestionario no encontrado',
                mensaje='No existe un cuestionario con ese identificador.',
                volver_url='/administrativo/cuestionarios',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        return render.ver_preguntas(cuestionario=cuestionario, preguntas=preguntas)


class ToggleEstadoCuestionario:
    def POST(self):
        data = web.input(id='', estado='')
        cuestionario_id = data.id
        nuevo_estado = (data.estado or '').strip()  # 'Activo' o 'Inactivo'
        conn = None

        if not cuestionario_id or not nuevo_estado:
            return render.confirmacion(
                titulo='Faltan datos',
                mensaje='No se recibio el cuestionario o el estado que se le quiere asignar.',
                volver_url='/administrativo/cuestionarios',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # Si se va a activar, primero desactivar TODOS los demas
            if nuevo_estado == 'Activo':
                cursor.execute(
                    "UPDATE cuestionarios SET estado = 'Inactivo' WHERE id != ?",
                    (cuestionario_id,)
                )

            # Actualizar el estado del cuestionario seleccionado
            cursor.execute(
                "UPDATE cuestionarios SET estado = ? WHERE id = ?",
                (nuevo_estado, cuestionario_id)
            )
            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al cambiar el estado:", e)
            return render.confirmacion(
                titulo='No se pudo cambiar el estado',
                mensaje='Ocurrio un problema al actualizar el estado del cuestionario.',
                volver_url='/administrativo/cuestionarios',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al cambiar el estado:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al cambiar el estado del cuestionario.',
                volver_url='/administrativo/cuestionarios',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        if nuevo_estado == 'Activo':
            mensaje = ('El cuestionario quedo como Activo. '
                       'Los demas se pasaron a Inactivo para que solo haya uno en uso.')
        else:
            mensaje = 'El cuestionario quedo como Inactivo y ya no se aplicara a los padres.'

        return render.confirmacion(
            titulo='Estado actualizado',
            mensaje=mensaje,
            volver_url='/administrativo/cuestionarios',
            volver_texto='Volver a la lista'
        )


class EliminarPregunta:
    def POST(self):
        data = web.input(id='', cuestionario_id='')
        pregunta_id = data.id
        cuestionario_id = data.cuestionario_id
        volver_url = '/administrativo/cuestionarios/ver_preguntas?id=%s' % cuestionario_id
        texto_pregunta = ''
        conn = None

        if not pregunta_id:
            return render.confirmacion(
                titulo='No se indico la pregunta',
                mensaje='No se recibio el identificador de la pregunta a eliminar.',
                volver_url=volver_url,
                volver_texto='Volver a las preguntas',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT texto FROM preguntas WHERE id = ?", (pregunta_id,))
            fila = cursor.fetchone()

            if not fila:
                return render.confirmacion(
                    titulo='Pregunta no encontrada',
                    mensaje='Esa pregunta ya no existe en el cuestionario.',
                    volver_url=volver_url,
                    volver_texto='Volver a las preguntas',
                    tipo='error'
                )

            texto_pregunta = fila['texto']

            cursor.execute("DELETE FROM preguntas WHERE id = ?", (pregunta_id,))
            conn.commit()

        except sqlite3.IntegrityError as e:
            print("No se puede eliminar la pregunta por registros relacionados:", e)
            return render.confirmacion(
                titulo='No se puede eliminar',
                mensaje='Esta pregunta ya tiene respuestas registradas y no puede eliminarse.',
                volver_url=volver_url,
                volver_texto='Volver a las preguntas',
                tipo='error'
            )
        except sqlite3.Error as e:
            print("Error de base de datos al eliminar pregunta:", e)
            return render.confirmacion(
                titulo='No se pudo eliminar',
                mensaje='Ocurrio un problema al eliminar la pregunta de la base de datos.',
                volver_url=volver_url,
                volver_texto='Volver a las preguntas',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al eliminar pregunta:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al eliminar la pregunta.',
                volver_url=volver_url,
                volver_texto='Volver a las preguntas',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        resumen = texto_pregunta if len(texto_pregunta) <= 60 else texto_pregunta[:60] + '...'

        return render.confirmacion(
            titulo='Pregunta eliminada',
            mensaje='Se elimino la pregunta: "%s"' % resumen,
            volver_url=volver_url,
            volver_texto='Volver a las preguntas'
        )