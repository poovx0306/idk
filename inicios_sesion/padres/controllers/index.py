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
        """Consulta al usuario por su correo y su contrasena encriptada.
        El rol viaja dentro de la consulta, asi una persona no puede
        entrar por una pantalla que no le corresponde.
        """
        conexion = None
        try:
            conexion = sqlite3.connect('sql/conaap.db')
            cursor = conexion.cursor()

            query = ("SELECT id_usuario, nombre, id_referencia FROM usuario "
                    "WHERE correo = ? AND contrasena = ? AND rol = 'padre'")
            cursor.execute(query, (correo, self.encriptar(contrasena)))
            fila = cursor.fetchone()

            if fila is None:
                return None

            return {
                'id_usuario': fila[0],
                'nombre': fila[1],
                'id_referencia': fila[2]
            }

        except sqlite3.Error as error:
            print("ERROR 100: %s" % (error.args,))
            return None
        except Exception as error:
            print("ERROR 101: %s" % (error.args,))
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
        correo = datos.correo.strip().lower()
        contrasena = datos.contrasena

        if correo == "" or contrasena == "":
            return render.index("Captura tu correo y tu contrasena.")

        usuario = self.buscarUsuario(correo, contrasena)

        # Mensaje generico a proposito: no se le dice al atacante
        # si fallo el correo o si fallo la contrasena.
        if usuario is None:
            return render.index("El correo o la contrasena no son correctos.")

        sesion = web.config._session
        sesion.id_usuario = usuario['id_usuario']
        sesion.nombre = usuario['nombre']
        sesion.rol = 'padre'
        sesion.id_referencia = usuario['id_referencia']

        raise web.HTTPError('303 See Other', {'Location': '/registro-nino'})