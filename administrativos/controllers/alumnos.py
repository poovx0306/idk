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
                       d.nombre AS docente_asignado
                FROM infantes i
                LEFT JOIN docente d ON d.id_docente = i.id_docente1
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
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("SELECT id_docente, nombre FROM docente ORDER BY nombre")
            lista_docentes = cursor.fetchall()
        except sqlite3.Error as e:
            print("Error de base de datos en NuevoAlumnoAdmin:", e)
        except Exception as e:
            print("Error inesperado en NuevoAlumnoAdmin:", e)
        finally:
            if conn:
                conn.close()

        return render.nuevo_alumno(lista_docentes=lista_docentes, error=datos.error)

    def POST(self):
        datos = web.input(nombre='', edad='', condicion='', id_docente1='', grado='')
        nombre = datos.nombre.strip()
        condicion = datos.condicion.strip()
        grado = datos.grado.strip()
        id_docente1 = datos.id_docente1.strip()
        conn = None

        try:
            edad = int(datos.edad or 0)
        except ValueError:
            edad = 0

        if not nombre or not id_docente1:
            raise web.seeother('/administrativo/alumnos/nuevo?error=El+nombre+y+el+docente+son+obligatorios')

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO infantes (nombre, edad, id_docente1, condicion, grado) VALUES (?, ?, ?, ?, ?)",
                (nombre, edad, id_docente1, condicion, grado)
            )
            conn.commit()

        except web.HTTPError:
            raise
        except sqlite3.Error as e:
            print("Error de base de datos al registrar alumno:", e)
            raise web.seeother('/administrativo/alumnos/nuevo?error=No+se+pudo+registrar+al+alumno')
        except Exception as e:
            print("Error inesperado al registrar alumno:", e)
            raise web.seeother('/administrativo/alumnos/nuevo?error=Ocurrio+un+error+inesperado')
        finally:
            if conn:
                conn.close()

        raise web.seeother('/administrativo/alumnos?aviso=Alumno+registrado+correctamente')


class EditarAlumnoAdmin:
    def GET(self):
        datos = web.input(id='', error='')
        alumno = None
        lista_docentes = []
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
                       id_docente1
                FROM infantes
                WHERE id_infante = ?
            """, (datos.id,))
            alumno = cursor.fetchone()

            cursor.execute("SELECT id_docente, nombre FROM docente ORDER BY nombre")
            lista_docentes = cursor.fetchall()

        except sqlite3.Error as e:
            print("Error de base de datos en EditarAlumnoAdmin:", e)
        except Exception as e:
            print("Error inesperado en EditarAlumnoAdmin:", e)
        finally:
            if conn:
                conn.close()

        if not alumno:
            raise web.seeother('/administrativo/alumnos?error=No+se+encontro+ese+alumno')

        return render.editar_alumno(alumno=alumno, lista_docentes=lista_docentes, error=datos.error)

    def POST(self):
        datos = web.input(id='', nombre='', edad='', condicion='', id_docente1='', grado='')
        id_alumno = datos.id
        nombre = datos.nombre.strip()
        condicion = datos.condicion.strip()
        grado = datos.grado.strip()
        id_docente1 = datos.id_docente1.strip()
        conn = None

        try:
            edad = int(datos.edad or 0)
        except ValueError:
            edad = 0

        if not nombre or not id_docente1:
            raise web.seeother('/administrativo/alumnos/editar?id=%s&error=El+nombre+y+el+docente+son+obligatorios' % id_alumno)

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE infantes SET nombre = ?, edad = ?, id_docente1 = ?, condicion = ?, grado = ? WHERE id_infante = ?",
                (nombre, edad, id_docente1, condicion, grado, id_alumno)
            )
            conn.commit()

        except web.HTTPError:
            raise
        except sqlite3.Error as e:
            print("Error de base de datos al editar alumno:", e)
            raise web.seeother('/administrativo/alumnos/editar?id=%s&error=No+se+pudieron+guardar+los+cambios' % id_alumno)
        except Exception as e:
            print("Error inesperado al editar alumno:", e)
            raise web.seeother('/administrativo/alumnos/editar?id=%s&error=Ocurrio+un+error+inesperado' % id_alumno)
        finally:
            if conn:
                conn.close()

        raise web.seeother('/administrativo/alumnos?aviso=Cambios+guardados+correctamente')


class EliminarAlumnoAdmin:
    def POST(self):
        datos = web.input(id='')
        id_alumno = datos.id
        conn = None

        if not id_alumno:
            raise web.seeother('/administrativo/alumnos?error=No+se+indico+el+alumno')

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT nombre FROM infantes WHERE id_infante = ?", (id_alumno,))
            alumno = cursor.fetchone()

            if not alumno:
                raise web.seeother('/administrativo/alumnos?error=Ese+alumno+ya+no+existe')

            cursor.execute("DELETE FROM infantes WHERE id_infante = ?", (id_alumno,))
            conn.commit()

        except web.HTTPError:
            raise
        except sqlite3.IntegrityError as e:
            print("No se puede eliminar por registros relacionados:", e)
            raise web.seeother('/administrativo/alumnos?error=No+se+puede+eliminar:+tiene+registros+relacionados')
        except sqlite3.Error as e:
            print("Error de base de datos al eliminar alumno:", e)
            raise web.seeother('/administrativo/alumnos?error=No+se+pudo+eliminar+al+alumno')
        except Exception as e:
            print("Error inesperado al eliminar alumno:", e)
            raise web.seeother('/administrativo/alumnos?error=Ocurrio+un+error+inesperado')
        finally:
            if conn:
                conn.close()

        raise web.seeother('/administrativo/alumnos?aviso=Alumno+eliminado+correctamente')