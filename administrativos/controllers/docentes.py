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
            return render.confirmacion(
                titulo='Faltan datos',
                mensaje='Todos los campos del formulario son obligatorios.',
                volver_url='/administrativo/docentes/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT id_docente FROM docente WHERE LOWER(correo) = ?", (correo,))
            if cursor.fetchone():
                return render.confirmacion(
                    titulo='Correo ya registrado',
                    mensaje='Ese correo ya pertenece a otro docente.',
                    volver_url='/administrativo/docentes/nuevo',
                    volver_texto='Regresar al formulario',
                    tipo='error'
                )

            cursor.execute("SELECT id_usuario FROM usuario WHERE LOWER(correo) = ?", (correo,))
            if cursor.fetchone():
                return render.confirmacion(
                    titulo='Correo ya registrado',
                    mensaje='Ese correo ya tiene una cuenta de acceso en el sistema.',
                    volver_url='/administrativo/docentes/nuevo',
                    volver_texto='Regresar al formulario',
                    tipo='error'
                )

            cursor.execute("SELECT id_admin FROM administrador LIMIT 1")
            fila_admin = cursor.fetchone()
            if not fila_admin:
                return render.confirmacion(
                    titulo='No hay administrador',
                    mensaje='No existe un administrador registrado para asociar al docente.',
                    volver_url='/administrativo/docentes/nuevo',
                    volver_texto='Regresar al formulario',
                    tipo='error'
                )
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

        except sqlite3.IntegrityError as e:
            print("Correo duplicado en NuevoDocenteAdmin:", e)
            return render.confirmacion(
                titulo='Correo ya registrado',
                mensaje='Ese correo ya tiene una cuenta en el sistema.',
                volver_url='/administrativo/docentes/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except sqlite3.Error as e:
            print("Error de base de datos en NuevoDocenteAdmin:", e)
            return render.confirmacion(
                titulo='No se pudo registrar',
                mensaje='Ocurrio un problema al guardar al docente en la base de datos.',
                volver_url='/administrativo/docentes/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado en NuevoDocenteAdmin:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al registrar al docente.',
                volver_url='/administrativo/docentes/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Docente registrado',
            mensaje='%s se agrego correctamente y ya cuenta con acceso al portal.' % nombre,
            volver_url='/administrativo/docentes',
            volver_texto='Volver a la lista'
        )


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
            return render.confirmacion(
                titulo='Docente no encontrado',
                mensaje='No existe un docente con ese identificador.',
                volver_url='/administrativo/docentes',
                volver_texto='Volver a la lista',
                tipo='error'
            )

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
            return render.confirmacion(
                titulo='Faltan datos',
                mensaje='El nombre, el correo y la clave son obligatorios.',
                volver_url='/administrativo/docentes/editar?id=%s' % id_docente,
                volver_texto='Regresar al formulario',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT id_docente FROM docente WHERE LOWER(correo) = ? AND id_docente <> ?", (correo, id_docente))
            if cursor.fetchone():
                return render.confirmacion(
                    titulo='Correo en uso',
                    mensaje='Ese correo ya lo esta usando otro docente.',
                    volver_url='/administrativo/docentes/editar?id=%s' % id_docente,
                    volver_texto='Regresar al formulario',
                    tipo='error'
                )

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

        except sqlite3.Error as e:
            print("Error de base de datos al editar docente:", e)
            return render.confirmacion(
                titulo='No se guardaron los cambios',
                mensaje='Ocurrio un problema al actualizar los datos del docente.',
                volver_url='/administrativo/docentes/editar?id=%s' % id_docente,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al editar docente:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al editar al docente.',
                volver_url='/administrativo/docentes/editar?id=%s' % id_docente,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Cambios guardados',
            mensaje='Los datos de %s se actualizaron correctamente.' % nombre,
            volver_url='/administrativo/docentes',
            volver_texto='Volver a la lista'
        )


class BajaDocenteAdmin:

    def POST(self):
        datos = web.input(id='')
        id_docente = datos.id
        nombre_docente = ''
        conn = None

        if not id_docente:
            return render.confirmacion(
                titulo='No se indico el docente',
                mensaje='No se recibio el identificador del docente a dar de baja.',
                volver_url='/administrativo/docentes',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT nombre FROM docente WHERE id_docente = ?", (id_docente,))
            docente = cursor.fetchone()

            if not docente:
                return render.confirmacion(
                    titulo='Docente no encontrado',
                    mensaje='Ese docente ya no existe en el sistema.',
                    volver_url='/administrativo/docentes',
                    volver_texto='Volver a la lista',
                    tipo='error'
                )

            nombre_docente = docente['nombre']

            cursor.execute("SELECT COUNT(*) AS total FROM infantes WHERE id_docente1 = ?", (id_docente,))
            if cursor.fetchone()['total'] > 0:
                return render.confirmacion(
                    titulo='No se puede dar de baja',
                    mensaje='%s tiene alumnos asignados. Reasignalos a otro docente antes de darlo de baja.' % nombre_docente,
                    volver_url='/administrativo/docentes',
                    volver_texto='Volver a la lista',
                    tipo='error'
                )

            cursor.execute("DELETE FROM usuario WHERE rol = 'docente' AND id_referencia = ?", (id_docente,))
            cursor.execute("DELETE FROM docente WHERE id_docente = ?", (id_docente,))

            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al dar de baja:", e)
            return render.confirmacion(
                titulo='No se pudo dar de baja',
                mensaje='Ocurrio un problema al eliminar al docente de la base de datos.',
                volver_url='/administrativo/docentes',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al dar de baja:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al dar de baja al docente.',
                volver_url='/administrativo/docentes',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Docente dado de baja',
            mensaje='%s fue eliminado del sistema y ya no tiene acceso al portal.' % nombre_docente,
            volver_url='/administrativo/docentes',
            volver_texto='Volver a la lista'
        )