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
    def GET(self):
        datos = web.input(aviso='', error='')
        docente = []
        total = 0
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT d.id_docente AS id,
                       d.nombre,
                       d.correo,
                       d.clave_docente AS clave,
                       (SELECT COUNT(*) FROM infantes i WHERE i.id_docente1 = d.id_docente) AS alumnos
                FROM docente d
                ORDER BY d.id_docente DESC
            """)
            docente = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) AS total FROM docente")
            total = cursor.fetchone()['total']

        except sqlite3.Error as e:
            print("Error de base de datos en DocentesAdmin:", e)
        except Exception as e:
            print("Error inesperado en DocentesAdmin:", e)
        finally:
            if conn:
                conn.close()

        return render.docentes(
            docente=docente,
            total=total,
            aviso=datos.aviso,
            error=datos.error
        )


class NuevoDocenteAdmin:

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

            cursor.execute("SELECT id_docente FROM docente WHERE LOWER(correo) = ?", (correo,))
            if cursor.fetchone():
                raise web.seeother('/administrativo/docentes/nuevo?error=Ese+correo+ya+esta+registrado')

            cursor.execute("SELECT id_usuario FROM usuario WHERE LOWER(correo) = ?", (correo,))
            if cursor.fetchone():
                raise web.seeother('/administrativo/docentes/nuevo?error=Ese+correo+ya+tiene+una+cuenta+en+el+sistema')

            cursor.execute("SELECT id_admin FROM administrador LIMIT 1")
            fila_admin = cursor.fetchone()
            if not fila_admin:
                raise web.seeother('/administrativo/docentes/nuevo?error=No+hay+administrador+registrado')
            id_admin = fila_admin['id_admin']

            cursor.execute(
                "INSERT INTO docente (clave_docente, nombre, id_admin, correo, contrasena) VALUES (?, ?, ?, ?, ?)",
                (clave, nombre, id_admin, correo, self.encriptar(password))
            )
            id_docente = cursor.lastrowid

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

    def encriptar(self, contrasena):
        return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()

    def GET(self):
        datos = web.input(id='', error='')
        docente = None
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id_docente AS id,
                       d.nombre,
                       d.correo,
                       d.clave_docente AS clave,
                       (SELECT COUNT(*) FROM infantes i WHERE i.id_docente1 = d.id_docente) AS alumnos
                FROM docente d
                WHERE d.id_docente = ?
            """, (datos.id,))
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
        datos = web.input(id='', nombre='', correo='', clave='', password='')
        id_docente = datos.id
        nombre = datos.nombre.strip()
        correo = datos.correo.strip().lower()
        clave = datos.clave.strip()
        password = datos.password
        conn = None

        if not nombre or not correo or not clave:
            raise web.seeother('/administrativo/docentes/editar?id=%s&error=Nombre,+correo+y+clave+son+obligatorios' % id_docente)

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT id_docente FROM docente WHERE LOWER(correo) = ? AND id_docente <> ?", (correo, id_docente))
            if cursor.fetchone():
                raise web.seeother('/administrativo/docentes/editar?id=%s&error=Ese+correo+ya+lo+usa+otro+docente' % id_docente)

            cursor.execute(
                "UPDATE docente SET nombre = ?, correo = ?, clave_docente = ? WHERE id_docente = ?",
                (nombre, correo, clave, id_docente)
            )

            # Reflejar los cambios en su cuenta de acceso
            cursor.execute(
                "UPDATE usuario SET nombre = ?, correo = ? WHERE rol = 'docente' AND id_referencia = ?",
                (nombre, correo, id_docente)
            )

            # La contrasena solo se cambia si escribio una nueva
            if password:
                cursor.execute(
                    "UPDATE docente SET contrasena = ? WHERE id_docente = ?",
                    (self.encriptar(password), id_docente)
                )
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

    def POST(self):
        datos = web.input(id='')
        id_docente = datos.id
        conn = None

        if not id_docente:
            raise web.seeother('/administrativo/docentes?error=No+se+indico+el+docente')

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT nombre FROM docente WHERE id_docente = ?", (id_docente,))
            docente = cursor.fetchone()

            if not docente:
                raise web.seeother('/administrativo/docentes?error=Ese+docente+ya+no+existe')

            cursor.execute("DELETE FROM usuario WHERE rol = 'docente' AND id_referencia = ?", (id_docente,))
            cursor.execute("DELETE FROM docente WHERE id_docente = ?", (id_docente,))

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