import web
import sqlite3
import os
import hashlib
from datetime import datetime

render = web.template.render('administrativos/views/')

MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


def conectar_bd():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'sql', 'conaap.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class PadresAdmin:
    def GET(self):
        padres = []
        total = 0
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT p.id,
                       p.nombre,
                       p.correo,
                       p.cuestionarios_respondidos,
                       p.miembro_desde,
                       p.estado,
                       (SELECT COUNT(*) FROM infantes i WHERE i.id_padres = p.id) AS ninos
                FROM padres p
                ORDER BY p.id DESC
            """)
            padres = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) AS total FROM padres")
            total = cursor.fetchone()['total']

        except sqlite3.Error as e:
            print("Error de base de datos en PadresAdmin:", e)
        except Exception as e:
            print("Error inesperado en PadresAdmin:", e)
        finally:
            if conn:
                conn.close()

        return render.padres(padres=padres, total=total)


class NuevoPadreAdmin:

    def encriptar(self, contrasena):
        return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()

    def GET(self):
        datos = web.input(error='')
        return render.nuevo_padre(error=datos.error)

    def POST(self):
        datos = web.input(nombre='', correo='', password='', estado='Activa')
        nombre = datos.nombre.strip()
        correo = datos.correo.strip().lower()
        password = datos.password
        estado = datos.estado.strip() or 'Activa'
        conn = None

        if not nombre or not correo or not password:
            return render.confirmacion(
                titulo='Faltan datos',
                mensaje='El nombre, el correo y la contrasena son obligatorios.',
                volver_url='/administrativo/padres/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )

        ahora = datetime.now()
        miembro_desde = '%s %s' % (MESES[ahora.month - 1], ahora.year)

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM padres WHERE LOWER(correo) = ?", (correo,))
            if cursor.fetchone():
                return render.confirmacion(
                    titulo='Correo ya registrado',
                    mensaje='Ese correo ya pertenece a otra familia.',
                    volver_url='/administrativo/padres/nuevo',
                    volver_texto='Regresar al formulario',
                    tipo='error'
                )

            cursor.execute("SELECT id_usuario FROM usuario WHERE LOWER(correo) = ?", (correo,))
            if cursor.fetchone():
                return render.confirmacion(
                    titulo='Correo ya registrado',
                    mensaje='Ese correo ya tiene una cuenta de acceso en el sistema.',
                    volver_url='/administrativo/padres/nuevo',
                    volver_texto='Regresar al formulario',
                    tipo='error'
                )

            cursor.execute(
                "INSERT INTO padres (nombre, correo, cuestionarios_respondidos, miembro_desde, estado) VALUES (?, ?, ?, ?, ?)",
                (nombre, correo, 0, miembro_desde, estado)
            )
            id_padre = cursor.lastrowid

            cursor.execute(
                "INSERT INTO usuario (correo, contrasena, rol, nombre, id_referencia) VALUES (?, ?, ?, ?, ?)",
                (correo, self.encriptar(password), 'padre', nombre, id_padre)
            )

            conn.commit()

        except sqlite3.IntegrityError as e:
            print("Correo duplicado en NuevoPadreAdmin:", e)
            return render.confirmacion(
                titulo='Correo ya registrado',
                mensaje='Ese correo ya tiene una cuenta en el sistema.',
                volver_url='/administrativo/padres/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except sqlite3.Error as e:
            print("Error de base de datos en NuevoPadreAdmin:", e)
            return render.confirmacion(
                titulo='No se pudo registrar',
                mensaje='Ocurrio un problema al guardar a la familia en la base de datos.',
                volver_url='/administrativo/padres/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado en NuevoPadreAdmin:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al registrar a la familia.',
                volver_url='/administrativo/padres/nuevo',
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Familia registrada',
            mensaje='%s se agrego correctamente y ya cuenta con acceso al portal de padres.' % nombre,
            volver_url='/administrativo/padres',
            volver_texto='Volver a la lista'
        )


class EditarPadreAdmin:

    def encriptar(self, contrasena):
        return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()

    def GET(self):
        datos = web.input(id='', error='')
        padre = None
        conn = None

        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, correo, cuestionarios_respondidos, miembro_desde, estado
                FROM padres
                WHERE id = ?
            """, (datos.id,))
            padre = cursor.fetchone()
        except sqlite3.Error as e:
            print("Error de base de datos en EditarPadreAdmin:", e)
        except Exception as e:
            print("Error inesperado en EditarPadreAdmin:", e)
        finally:
            if conn:
                conn.close()

        if not padre:
            return render.confirmacion(
                titulo='Familia no encontrada',
                mensaje='No existe una familia con ese identificador.',
                volver_url='/administrativo/padres',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        return render.editar_padre(padre=padre, error=datos.error)

    def POST(self):
        datos = web.input(id='', nombre='', correo='', estado='Activa', password='')
        id_padre = datos.id
        nombre = datos.nombre.strip()
        correo = datos.correo.strip().lower()
        estado = datos.estado.strip() or 'Activa'
        password = datos.password
        conn = None

        if not nombre or not correo:
            return render.confirmacion(
                titulo='Faltan datos',
                mensaje='El nombre y el correo son obligatorios.',
                volver_url='/administrativo/padres/editar?id=%s' % id_padre,
                volver_texto='Regresar al formulario',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM padres WHERE LOWER(correo) = ? AND id <> ?", (correo, id_padre))
            if cursor.fetchone():
                return render.confirmacion(
                    titulo='Correo en uso',
                    mensaje='Ese correo ya lo esta usando otra familia.',
                    volver_url='/administrativo/padres/editar?id=%s' % id_padre,
                    volver_texto='Regresar al formulario',
                    tipo='error'
                )

            cursor.execute(
                "UPDATE padres SET nombre = ?, correo = ?, estado = ? WHERE id = ?",
                (nombre, correo, estado, id_padre)
            )

            # Reflejar los cambios en su cuenta de acceso
            cursor.execute(
                "UPDATE usuario SET nombre = ?, correo = ? WHERE rol = 'padre' AND id_referencia = ?",
                (nombre, correo, id_padre)
            )

            # La contrasena solo se cambia si escribio una nueva
            if password:
                cursor.execute(
                    "UPDATE usuario SET contrasena = ? WHERE rol = 'padre' AND id_referencia = ?",
                    (self.encriptar(password), id_padre)
                )

            conn.commit()

        except sqlite3.Error as e:
            print("Error de base de datos al editar padre:", e)
            return render.confirmacion(
                titulo='No se guardaron los cambios',
                mensaje='Ocurrio un problema al actualizar los datos de la familia.',
                volver_url='/administrativo/padres/editar?id=%s' % id_padre,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al editar padre:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al editar a la familia.',
                volver_url='/administrativo/padres/editar?id=%s' % id_padre,
                volver_texto='Regresar al formulario',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Cambios guardados',
            mensaje='Los datos de %s se actualizaron correctamente.' % nombre,
            volver_url='/administrativo/padres',
            volver_texto='Volver a la lista'
        )


class EliminarPadreAdmin:
    def POST(self):
        datos = web.input(id='')
        id_padre = datos.id
        nombre_padre = ''
        conn = None

        if not id_padre:
            return render.confirmacion(
                titulo='No se indico la familia',
                mensaje='No se recibio el identificador de la familia a eliminar.',
                volver_url='/administrativo/padres',
                volver_texto='Volver a la lista',
                tipo='error'
            )

        try:
            conn = conectar_bd()
            cursor = conn.cursor()

            cursor.execute("SELECT nombre, correo FROM padres WHERE id = ?", (id_padre,))
            padre = cursor.fetchone()

            if not padre:
                return render.confirmacion(
                    titulo='Familia no encontrada',
                    mensaje='Esa familia ya no existe en el sistema.',
                    volver_url='/administrativo/padres',
                    volver_texto='Volver a la lista',
                    tipo='error'
                )

            nombre_padre = padre['nombre'] or padre['correo']

            cursor.execute("SELECT COUNT(*) AS total FROM infantes WHERE id_padres = ?", (id_padre,))
            ninos = cursor.fetchone()['total']

            if ninos > 0:
                return render.confirmacion(
                    titulo='No se puede eliminar',
                    mensaje='%s tiene %d nino(s) registrado(s). Reasignalos o eliminalos antes de borrar la cuenta.' % (nombre_padre, ninos),
                    volver_url='/administrativo/padres',
                    volver_texto='Volver a la lista',
                    tipo='error'
                )

            cursor.execute("DELETE FROM usuario WHERE rol = 'padre' AND id_referencia = ?", (id_padre,))
            cursor.execute("DELETE FROM padres WHERE id = ?", (id_padre,))

            conn.commit()

        except sqlite3.IntegrityError as e:
            print("No se puede eliminar por registros relacionados:", e)
            return render.confirmacion(
                titulo='No se puede eliminar',
                mensaje='Esta familia tiene registros relacionados y no puede eliminarse.',
                volver_url='/administrativo/padres',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        except sqlite3.Error as e:
            print("Error de base de datos al eliminar padre:", e)
            return render.confirmacion(
                titulo='No se pudo eliminar',
                mensaje='Ocurrio un problema al eliminar a la familia de la base de datos.',
                volver_url='/administrativo/padres',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        except Exception as e:
            print("Error inesperado al eliminar padre:", e)
            return render.confirmacion(
                titulo='Ocurrio un error',
                mensaje='Sucedio algo inesperado al eliminar a la familia.',
                volver_url='/administrativo/padres',
                volver_texto='Volver a la lista',
                tipo='error'
            )
        finally:
            if conn:
                conn.close()

        return render.confirmacion(
            titulo='Familia eliminada',
            mensaje='%s se elimino correctamente del sistema.' % nombre_padre,
            volver_url='/administrativo/padres',
            volver_texto='Volver a la lista'
        )