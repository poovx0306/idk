import web
import sqlite3
import os
import hashlib

render = web.template.render('administrativos/views/')


def conectar_bd():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'sql', 'conaap.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class DocentesAdmin:
    """Lista todos los docentes registrados en la region."""

    def GET(self):
        datos = web.input(aviso='', error='')
        docentes = []
        total = 0
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM docentes ORDER BY id DESC")
            docentes = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) AS total FROM docentes")
            total = cursor.fetchone()['total']

        except sqlite3.Error as e:
            print("Error de base de datos en DocentesAdmin:", e)
        except Exception as e:
            print("Error inesperado en DocentesAdmin:", e)
        finally:
            if conn:
                conn.close()

        return render.docentes(
            docentes=docentes,
            total=total,
            aviso=datos.aviso,
            error=datos.error
        )


class NuevoDocenteAdmin:
    """Da de alta un docente y le crea su acceso al portal de inicio de sesion."""

    def encriptar(self, contrasena):
        return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()

    def GET(self):
        datos = web.input(error='')
        return render.nuevo_docente(error=datos.error)

    def POST(self):
        datos = web.input(nombre='', correo='', clave='', password='')
        nombre = datos.nombre.strip()
        correo = datos.correo.strip().lower()
        clave = datos.clave.strip()
        password = datos.password
        conn = None

        if not nombre or not correo or not clave or not password:
            raise web.seeother('/administrativo/docentes/nuevo?error=Todos+los+campos+son+obligatorios')

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # No permitir correos duplicados
            cursor.execute("SELECT id FROM docentes WHERE LOWER(correo) = ?", (correo,))
            if cursor.fetchone():
                raise web.seeother('/administrativo/docentes/nuevo?error=Ese+correo+ya+esta+registrado')

            cursor.execute(
                "INSERT INTO docentes (nombre, correo, clave, alumnos) VALUES (?, ?, ?, ?)",
                (nombre, correo, clave, 0)
            )
            id_docente = cursor.lastrowid

            # Crear tambien su usuario para que pueda entrar al login de docentes
            cursor.execute(
                "INSERT INTO usuario (correo, contrasena, rol, nombre, id_referencia) VALUES (?, ?, ?, ?, ?)",
                (correo, self.encriptar(password), 'docente', nombre, id_docente)
            )

            conn.commit()

        except web.HTTPError:
            raise
        except sqlite3.IntegrityError as e:
            print("Correo duplicado en NuevoDocenteAdmin:", e)
            raise web.seeother('/administrativo/docentes/nuevo?error=Ese+correo+ya+tiene+una+cuenta')
        except sqlite3.Error as e:
            print("Error de base de datos en NuevoDocenteAdmin:", e)
            raise web.seeother('/administrativo/docentes/nuevo?error=No+se+pudo+registrar+el+docente')
        except Exception as e:
            print("Error inesperado en NuevoDocenteAdmin:", e)
            raise web.seeother('/administrativo/docentes/nuevo?error=Ocurrio+un+error+inesperado')
        finally:
            if conn:
                conn.close()

        raise web.seeother('/administrativo/docentes?aviso=Docente+registrado+correctamente')


class EditarDocenteAdmin:
    """Muestra y guarda los cambios de un docente ya registrado."""

    def encriptar(self, contrasena):
        return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()

    def GET(self):
        datos = web.input(id='', error='')
        docente = None
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM docentes WHERE id = ?", (datos.id,))
            docente = cursor.fetchone()
        except sqlite3.Error as e:
            print("Error de base de datos en EditarDocenteAdmin:", e)
        except Exception as e:
            print("Error inesperado en EditarDocenteAdmin:", e)
        finally:
            if conn:
                conn.close()

        if not docente:
            raise web.seeother('/administrativo/docentes?error=No+se+encontro+ese+docente')

        return render.editar_docente(docente=docente, error=datos.error)

    def POST(self):
        datos = web.input(id='', nombre='', correo='', clave='', alumnos='0', password='')
        id_docente = datos.id
        nombre = datos.nombre.strip()
        correo = datos.correo.strip().lower()
        clave = datos.clave.strip()
        password = datos.password
        conn = None

        try:
            alumnos = int(datos.alumnos or 0)
        except ValueError:
            alumnos = 0

        if not nombre or not correo or not clave:
            raise web.seeother('/administrativo/docentes/editar?id=%s&error=Nombre,+correo+y+clave+son+obligatorios' % id_docente)

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            # Correo de otro docente distinto
            cursor.execute("SELECT id FROM docentes WHERE LOWER(correo) = ? AND id <> ?", (correo, id_docente))
            if cursor.fetchone():
                raise web.seeother('/administrativo/docentes/editar?id=%s&error=Ese+correo+ya+lo+usa+otro+docente' % id_docente)

            cursor.execute(
                "UPDATE docentes SET nombre = ?, correo = ?, clave = ?, alumnos = ? WHERE id = ?",
                (nombre, correo, clave, alumnos, id_docente)
            )

            # Reflejar los cambios en su cuenta de acceso
            cursor.execute(
                "UPDATE usuario SET nombre = ?, correo = ? WHERE rol = 'docente' AND id_referencia = ?",
                (nombre, correo, id_docente)
            )

            # La contrasena solo se cambia si escribio una nueva
            if password:
                cursor.execute(
                    "UPDATE usuario SET contrasena = ? WHERE rol = 'docente' AND id_referencia = ?",
                    (self.encriptar(password), id_docente)
                )

            conn.commit()

        except web.HTTPError:
            raise
        except sqlite3.Error as e:
            print("Error de base de datos al editar docente:", e)
            raise web.seeother('/administrativo/docentes/editar?id=%s&error=No+se+pudieron+guardar+los+cambios' % id_docente)
        except Exception as e:
            print("Error inesperado al editar docente:", e)
            raise web.seeother('/administrativo/docentes/editar?id=%s&error=Ocurrio+un+error+inesperado' % id_docente)
        finally:
            if conn:
                conn.close()

        raise web.seeother('/administrativo/docentes?aviso=Cambios+guardados+correctamente')


class BajaDocenteAdmin:
    """Da de baja al docente y le retira el acceso al sistema."""

    def POST(self):
        datos = web.input(id='')
        id_docente = datos.id
        conn = None

        if not id_docente:
            raise web.seeother('/administrativo/docentes?error=No+se+indico+el+docente')

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT nombre FROM docentes WHERE id = ?", (id_docente,))
            docente = cursor.fetchone()

            if not docente:
                raise web.seeother('/administrativo/docentes?error=Ese+docente+ya+no+existe')

            cursor.execute("DELETE FROM usuario WHERE rol = 'docente' AND id_referencia = ?", (id_docente,))
            cursor.execute("DELETE FROM docentes WHERE id = ?", (id_docente,))

            conn.commit()

        except web.HTTPError:
            raise
        except sqlite3.Error as e:
            print("Error de base de datos al dar de baja:", e)
            raise web.seeother('/administrativo/docentes?error=No+se+pudo+dar+de+baja+al+docente')
        except Exception as e:
            print("Error inesperado al dar de baja:", e)
            raise web.seeother('/administrativo/docentes?error=Ocurrio+un+error+inesperado')
        finally:
            if conn:
                conn.close()

        raise web.seeother('/administrativo/docentes?aviso=Docente+dado+de+baja')