import web
import sqlite3
import os

render = web.template.render('administrativos/views/')


def conectar_bd():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'sql', 'conaap.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class AlumnosAdmin:
    def GET(self):
        data = web.input(docente='', grado='', aviso='', error='')
        docente = data.docente.strip()
        grado = data.grado.strip()

        alumnos = []
        lista_docentes = []
        total = 0
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            query = """
                SELECT i.id_infante AS id,
                       i.nombre,
                       i.edad,
                       i.condicion,
                       i.grado,
                       i.id_docente1,
                       d.nombre AS docente_asignado,
                       p.nombre AS familia_nombre,
                       p.correo AS familia_correo
                FROM infantes i
                LEFT JOIN docente d ON d.id_docente = i.id_docente1
                LEFT JOIN padres p ON p.id = i.id_padres
                WHERE 1=1
            """
            params = []

            if docente:
                query += " AND i.id_docente1 = ?"
                params.append(docente)

            if grado:
                query += " AND i.grado = ?"
                params.append(grado)

            query += " ORDER BY i.id_infante DESC"

            cursor.execute(query, params)
            alumnos = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) AS total FROM infantes")
            total = cursor.fetchone()['total']

            cursor.execute("SELECT id_docente, nombre FROM docente ORDER BY nombre")
            lista_docentes = cursor.fetchall()

            cursor.execute(
                "SELECT id, nombre, correo FROM padres ORDER BY nombre, correo"
            )
            lista_padres = cursor.fetchall()

        except sqlite3.Error as e:
            print("Error de base de datos en AlumnosAdmin:", e)
        except Exception as e:
            print("Error inesperado en AlumnosAdmin:", e)
        finally:
            if conn:
                conn.close()

        return render.alumnos(
            alumnos=alumnos,
            total=total,
            docente_sel=docente,
            grado_sel=grado,
            lista_docentes=lista_docentes,
            aviso=data.aviso,
            error=data.error
        )


class NuevoAlumnoAdmin:
    def GET(self):
        datos = web.input(error='')
        lista_docentes = []
        lista_padres = []
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("SELECT id_docente, nombre FROM docente ORDER BY nombre")
            lista_docentes = cursor.fetchall()

            cursor.execute(
                "SELECT id, nombre, correo FROM padres ORDER BY nombre, correo"
            )
            lista_padres = cursor.fetchall()
        except sqlite3.Error as e:
            print("Error de base de datos en NuevoAlumnoAdmin:", e)
        except Exception as e:
            print("Error inesperado en NuevoAlumnoAdmin:", e)
        finally:
            if conn:
                conn.close()

        return render.nuevo_alumno(lista_docentes=lista_docentes, lista_padres=lista_padres, error=datos.error)

    def POST(self):
        datos = web.input(nombre='', edad='', condicion='', id_docente1='', grado='', id_padres='')
        nombre = datos.nombre.strip()
        condicion = datos.condicion.strip()
        grado = datos.grado.strip()
        id_docente1 = datos.id_docente1.strip()
        id_padres = datos.id_padres.strip()
        conn = None

        try:
            edad = int(datos.edad or 0)
        except ValueError:
            edad = 0

        if not nombre or not id_docente1 or not id_padres:
            return render.confirmacion(
                titulo='Faltan datos',
                mensaje='El nombre, el docente asignado y la familia son obligatorios.',
                volver_url='/administrativo/alumnos/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO infantes (nombre, edad, id_docente1, id_padres, condicion, grado) VALUES (?, ?, ?, ?, ?, ?)",
                (nombre, edad, id_docente1, id_padres, condicion, grado)
            )
            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al registrar alumno:", e)
            return render.confirmacion(
                titulo='No se pudo registrar',
                mensaje='Ocurrio un problema al guardar al alumno en la base de datos.',
                volver_url='/administrativo/alumnos/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al registrar alumno:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al registrar al alumno.',
                volver_url='/administrativo/alumnos/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Alumno registrado',
            mensaje='%s se agrego correctamente a la lista de alumnos.' % nombre,
            volver_url='/administrativo/alumnos',
            volver_texto='Volver a la lista'
        )


class EditarAlumnoAdmin:
    def GET(self):
        datos = web.input(id='', error='')
        alumno = None
        lista_docentes = []
        lista_padres = []
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id_infante AS id,
                       nombre,
                       edad,
                       condicion,
                       grado,
                       id_docente1,
                       id_padres
                FROM infantes
                WHERE id_infante = ?
            """, (datos.id,))
            alumno = cursor.fetchone()

            cursor.execute("SELECT id_docente, nombre FROM docente ORDER BY nombre")
            lista_docentes = cursor.fetchall()

            cursor.execute(
                "SELECT id, nombre, correo FROM padres ORDER BY nombre, correo"
            )
            lista_padres = cursor.fetchall()

        except sqlite3.Error as e:
            print("Error de base de datos en EditarAlumnoAdmin:", e)
        except Exception as e:
            print("Error inesperado en EditarAlumnoAdmin:", e)
        finally:
            if conn:
                conn.close()

        if not alumno:
            return render.confirmacion(
                titulo='Alumno no encontrado',
                mensaje='No existe un alumno con ese identificador.',
                volver_url='/administrativo/alumnos',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        return render.editar_alumno(alumno=alumno, lista_docentes=lista_docentes, lista_padres=lista_padres, error=datos.error)

    def POST(self):
        datos = web.input(id='', nombre='', edad='', condicion='', id_docente1='', grado='', id_padres='')
        id_alumno = datos.id
        nombre = datos.nombre.strip()
        condicion = datos.condicion.strip()
        grado = datos.grado.strip()
        id_docente1 = datos.id_docente1.strip()
        id_padres = datos.id_padres.strip()
        conn = None

        try:
            edad = int(datos.edad or 0)
        except ValueError:
            edad = 0

        if not nombre or not id_docente1 or not id_padres:
            return render.confirmacion(
                titulo='Faltan datos',
                mensaje='El nombre, el docente asignado y la familia son obligatorios.',
                volver_url='/administrativo/alumnos/editar?id=%s' % id_alumno,
                volver_texto='Regresar al formulario',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE infantes SET nombre = ?, edad = ?, id_docente1 = ?, id_padres = ?, condicion = ?, grado = ? WHERE id_infante = ?",
                (nombre, edad, id_docente1, id_padres, condicion, grado, id_alumno)
            )
            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al editar alumno:", e)
            return render.confirmacion(
                titulo='No se guardaron los cambios',
                mensaje='Ocurrio un problema al actualizar los datos del alumno.',
                volver_url='/administrativo/alumnos/editar?id=%s' % id_alumno,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al editar alumno:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al editar al alumno.',
                volver_url='/administrativo/alumnos/editar?id=%s' % id_alumno,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Cambios guardados',
            mensaje='Los datos de %s se actualizaron correctamente.' % nombre,
            volver_url='/administrativo/alumnos',
            volver_texto='Volver a la lista'
        )


class EliminarAlumnoAdmin:
    def POST(self):
        datos = web.input(id='')
        id_alumno = datos.id
        nombre_alumno = ''
        conn = None

        if not id_alumno:
            return render.confirmacion(
                titulo='No se indico el alumno',
                mensaje='No se recibio el identificador del alumno a eliminar.',
                volver_url='/administrativo/alumnos',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT nombre FROM infantes WHERE id_infante = ?", (id_alumno,))
            alumno = cursor.fetchone()

            if not alumno:
                return render.confirmacion(
                    titulo='Alumno no encontrado',
                    mensaje='Ese alumno ya no existe en el sistema.',
                    volver_url='/administrativo/alumnos',
                    volver_texto='Volver a la lista',
                    tipo='error'
                )

            nombre_alumno = alumno['nombre']

            cursor.execute("DELETE FROM infantes WHERE id_infante = ?", (id_alumno,))
            conn.commit()

        except sqlite3.IntegrityError as e:
            print("No se puede eliminar por registros relacionados:", e)
            return render.confirmacion(
                titulo='No se puede eliminar',
                mensaje='Este alumno tiene registros relacionados (cuestionarios o actividades) y no puede eliminarse.',
                volver_url='/administrativo/alumnos',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        except sqlite3.Error as e:
            print("Error de base de datos al eliminar alumno:", e)
            return render.confirmacion(
                titulo='No se pudo eliminar',
                mensaje='Ocurrio un problema al eliminar al alumno de la base de datos.',
                volver_url='/administrativo/alumnos',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al eliminar alumno:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al eliminar al alumno.',
                volver_url='/administrativo/alumnos',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Alumno eliminado',
            mensaje='%s se elimino correctamente del sistema.' % nombre_alumno,
            volver_url='/administrativo/alumnos',
            volver_texto='Volver a la lista'
        )