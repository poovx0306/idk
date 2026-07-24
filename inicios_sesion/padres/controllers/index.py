import web
import sqlite3
import hashlib

render = web.template.render('inicios_sesion/padres/views')


class LoginPadres:
    """Inicio de sesion de las madres, padres de familia y tutores."""

    def encriptar(self, contrasena):
        """Convierte la contrasena a un hash SHA-256.
        La contrasena nunca se guarda ni se compara en texto plano.
        """
        return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()

    def buscarUsuario(self, correo, contrasena):
        """Consulta al usuario por su correo y su contrasena encriptada"""
        conexion = None
        try:
            conexion = sqlite3.connect('sql/conaap.db')
            cursor = conexion.cursor()

            query = "SELECT id_usuario, nombre FROM usuario WHERE correo = ? AND contrasena = ? AND rol = 'padre'"
            cursor.execute(query, (correo, self.encriptar(contrasena)))
            fila = cursor.fetchone()

            if fila is None:
                return None

            return {
                'id_usuario': fila[0],
                'nombre': fila[1]
            }

        except sqlite3.Error as error:
            print(f"ERROR 100: {error.args}")
            return None
        except Exception as error:
            print(f"ERROR 101: {error.args}")
            return None
        finally:
            if conexion:
                conexion.close()

    def GET(self):
        """Manejador de la peticion HTTP GET"""
        return render.index("")

    def POST(self):
        """Manejador de la peticion HTTP POST: valida el inicio de sesion"""
        datos = web.input(correo="", contrasena="")

        if datos.correo == "" or datos.contrasena == "":
            return render.index("Captura tu correo y tu contrasena.")

        usuario = self.buscarUsuario(datos.correo, datos.contrasena)

        if usuario is None:
            return render.index("El correo o la contrasena no son correctos.")

        sesion = web.config._session
        sesion.id_usuario = usuario['id_usuario']
        sesion.nombre = usuario['nombre']
        sesion.rol = 'padre'

        raise web.seeother('/deteccion-temprana')