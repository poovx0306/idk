import web
import sqlite3
import os

render = web.template.render('administrativos/views/')

def conectar_bd():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'sql', 'conaap.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

class EditarPregunta:
    def GET(self):
        datos = web.input(id=None)
        pregunta_id = datos.id
        
        conn = conectar_bd()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM preguntas WHERE id = ?', (pregunta_id,))
        pregunta = cursor.fetchone()
        
        cuestionario = None
        if pregunta:
            cursor.execute('SELECT * FROM cuestionarios WHERE id = ?', (pregunta['cuestionario_id'],))
            cuestionario = cursor.fetchone()
            
        conn.close()
        
        # Usamos claves seguras por si alguna columna tiene un nombre distinto en la BD
        p_texto = pregunta['texto'] if pregunta and 'texto' in pregunta.keys() else ''
        p_seccion = pregunta['seccion'] if pregunta and 'seccion' in pregunta.keys() else ''
        
        # Intentamos buscar el número de varias formas posibles para evitar el error de clave
        p_numero = ''
        if pregunta:
            for possible_key in ['numero', 'num', 'orden']:
                if possible_key in pregunta.keys():
                    p_numero = pregunta[possible_key]
                    break

        c_titulo = cuestionario['titulo'] if cuestionario and 'titulo' in cuestionario.keys() else ''
        c_id = pregunta['cuestionario_id'] if pregunta and 'cuestionario_id' in pregunta.keys() else 1

        return render.editar_pregunta(
            pregunta_id=pregunta_id,
            texto=p_texto,
            seccion=p_seccion,
            numero=p_numero,
            cuestionario_titulo=c_titulo,
            cuestionario_id=c_id
        )

    def POST(self):
        datos = web.input(id=None, texto='', seccion='', numero='')
        pregunta_id = datos.id
        texto = (datos.texto or '').strip()
        seccion = (datos.seccion or '').strip()
        c_id = 1
        conn = None

        if not pregunta_id or not texto:
            return render.confirmacion(
                titulo='Faltan datos',
                mensaje='El texto de la pregunta es obligatorio.',
                volver_url='/administrativo/cuestionarios/editar_pregunta?id=%s' % pregunta_id,
                volver_texto='Regresar al formulario',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute('SELECT cuestionario_id FROM preguntas WHERE id = ?', (pregunta_id,))
            fila = cursor.fetchone()

            if not fila:
                return render.confirmacion(
                    titulo='Pregunta no encontrada',
                    mensaje='No existe una pregunta con ese identificador.',
                    volver_url='/administrativo/cuestionarios',
                    volver_texto='Volver a los cuestionarios',
                    tipo='error'
                )

            c_id = fila['cuestionario_id'] if 'cuestionario_id' in fila.keys() else 1

            # Actualizamos texto, seccion y el campo correcto 'numero_pregunta'
            cursor.execute('''
                UPDATE preguntas
                SET texto = ?, seccion = ?, numero_pregunta = ?
                WHERE id = ?
            ''', (texto, seccion, datos.numero, pregunta_id))

            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al editar pregunta:", e)
            return render.confirmacion(
                titulo='No se guardaron los cambios',
                mensaje='Ocurrio un problema al actualizar la pregunta.',
                volver_url='/administrativo/cuestionarios/editar_pregunta?id=%s' % pregunta_id,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al editar pregunta:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al editar la pregunta.',
                volver_url='/administrativo/cuestionarios/editar_pregunta?id=%s' % pregunta_id,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Pregunta actualizada',
            mensaje='Los cambios de la pregunta se guardaron correctamente.',
            volver_url='/administrativo/cuestionarios/ver_preguntas?id=%s' % c_id,
            volver_texto='Volver a las preguntas'
        )