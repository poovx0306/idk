import web
import sqlite3
import os

render = web.template.render('administrativos/views/')

def conectar_bd():
    conn = sqlite3.connect('sql/conaap.db')
    conn.row_factory = sqlite3.Row
    return conn

class EstrategiasDidacticasAdmin:
    def GET(self):
        data = web.input(materia='', grado='')
        materia = data.get('materia', '').strip()
        grado = data.get('grado', '').strip()

        conn = conectar_bd()
        cursor = conn.cursor()

        query = "SELECT * FROM actividad_asignada WHERE 1=1"
        params = []

        if materia:
            query += " AND LOWER(materia) = LOWER(?)"
            params.append(materia)

        if grado:
            query += " AND grado = ?"
            params.append(grado)

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        estrategias = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM actividad_asignada")
        total_estrategias = cursor.fetchone()['total']

        conn.close()
        return render.estrategias_didacticas(
            estrategias=estrategias, 
            total=total_estrategias,
            materia_sel=materia, 
            grado_sel=grado
        )

class NuevaEstrategiaAdmin:
    def GET(self):
        return render.nueva_estrategia()

    def POST(self):
        data = web.input(titulo='', condicion='', materia='', grado='', 
                        objetivo='', materiales='', pasos='', accion='Publicar')

        titulo = data.get('titulo')
        descripcion = data.get('condicion')  # condicion va en descripcion
        materia = data.get('materia')
        grado = data.get('grado')
        objetivo = data.get('objetivo')
        materiales = data.get('materiales')
        paso_a_paso = data.get('pasos')
        estado = 'Publicada' if data.get('accion') == 'Publicar' else 'Borrador'

        import datetime
        fecha = datetime.date.today().isoformat()

        if not titulo:
            return render.confirmacion(
                titulo='Faltan datos',
                mensaje='El titulo de la estrategia es obligatorio.',
                volver_url='/administrativo/estrategias/nueva',
                volver_texto='Regresar al formulario',
                tipo='error'
            )

        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO actividad_asignada
                (titulo, descripcion, objetivo, materiales, paso_a_paso, materia, grado, fecha_asignacion, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (titulo, descripcion, objetivo, materiales, paso_a_paso, materia, grado, fecha, estado)
            )
            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al crear estrategia:", e)
            return render.confirmacion(
                titulo='No se pudo guardar',
                mensaje='Ocurrio un problema al guardar la estrategia en la base de datos.',
                volver_url='/administrativo/estrategias/nueva',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al crear estrategia:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al guardar la estrategia.',
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
            mensaje = '"%s" se guardo como borrador. Todavia no la ven los docentes.' % titulo

        return render.confirmacion(
            titulo='Estrategia guardada',
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
        cursor.execute("SELECT * FROM actividad_asignada WHERE id = ?", (id,))
        actividad = cursor.fetchone()
        conn.close()

        if not actividad:
            return render.confirmacion(
                titulo='Estrategia no encontrada',
                mensaje='No existe una estrategia con ese identificador.',
                volver_url='/administrativo/estrategias',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        return render.editar_estrategia(actividad=actividad)

    def POST(self):
        data = web.input()
        id = data.get('id')
        titulo = data.get('titulo')
        descripcion = data.get('descripcion')
        objetivo = data.get('objetivo')
        materiales = data.get('materiales')
        paso_a_paso = data.get('paso_a_paso')
        materia = data.get('materia')
        grado = data.get('grado')
        grupo = data.get('grupo')
        estado = data.get('estado')

        if not id:
            return render.confirmacion(
                titulo='No se indico la estrategia',
                mensaje='No se recibio el identificador de la estrategia a editar.',
                volver_url='/administrativo/estrategias',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        conn = None
        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE actividad_asignada
                SET titulo=?, descripcion=?, objetivo=?, materiales=?,
                    paso_a_paso=?, materia=?, grado=?, grupo=?, estado=?
                WHERE id=?
            """, (titulo, descripcion, objetivo, materiales, paso_a_paso, materia, grado, grupo, estado, id))
            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al editar estrategia:", e)
            return render.confirmacion(
                titulo='No se guardaron los cambios',
                mensaje='Ocurrio un problema al actualizar la estrategia.',
                volver_url='/administrativo/estrategias/editar?id=%s' % id,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al editar estrategia:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al editar la estrategia.',
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