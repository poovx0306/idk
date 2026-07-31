import web
import sqlite3
import hashlib
import os

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

render = web.template.render('inicios_sesion/recuperar/views')

# Credenciales de Twilio. Nunca se escriben aqui: se leen del entorno
# para no dejarlas expuestas en el repositorio.
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_VERIFY_SERVICE_SID = os.environ.get('TWILIO_VERIFY_SERVICE_SID', '')


class RecuperarContrasena:
    """Recuperacion de contrasena por SMS usando Twilio Verify.
    Paso 1: se envia el codigo al telefono que el usuario tiene registrado.
    Paso 2: se valida el codigo y se guarda la nueva contrasena.
    Twilio Verify genera el codigo y controla su vigencia; aqui no se
    guarda ningun codigo ni fecha de vencimiento.
    """

    def encriptar(self, contrasena):
        """Convierte la contrasena a un hash SHA-256.
        La contrasena nunca se guarda ni se compara en texto plano.
        """
        return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()

    def buscarTelefono(self, correo):
        """Consulta el telefono registrado a partir del correo"""
        conexion = None
        try:
            conexion = sqlite3.connect('sql/conaap.db')
            cursor = conexion.cursor()

            query = "SELECT telefono FROM usuario WHERE correo = ?"
            cursor.execute(query, (correo,))
            fila = cursor.fetchone()

            if fila is None or not fila[0]:
                return None

            return fila[0]

        except sqlite3.Error as error:
            print("ERROR 100: %s" % (error.args,))
            return None
        except Exception as error:
            print("ERROR 101: %s" % (error.args,))
            return None
        finally:
            if conexion:
                conexion.close()

    def actualizarContrasena(self, correo, contrasena):
        """Actualiza la contrasena del usuario que tiene ese correo"""
        conexion = None
        try:
            conexion = sqlite3.connect('sql/conaap.db')
            cursor = conexion.cursor()

            query = "UPDATE usuario SET contrasena = ? WHERE correo = ?"
            cursor.execute(query, (self.encriptar(contrasena), correo))
            conexion.commit()

            return cursor.rowcount > 0

        except sqlite3.Error as error:
            print("ERROR 100: %s" % (error.args,))
            return False
        except Exception as error:
            print("ERROR 101: %s" % (error.args,))
            return False
        finally:
            if conexion:
                conexion.close()

    def enviarCodigo(self, telefono):
        """Pide a Twilio Verify que genere y mande el codigo por SMS"""
        try:
            cliente = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            verificacion = (cliente.verify.v2.services(TWILIO_VERIFY_SERVICE_SID)
                             .verifications.create(to=telefono, channel='sms'))
            return verificacion.status == 'pending'
        except TwilioRestException as error:
            print("ERROR 102: %s" % (error,))
            return False

    def verificarCodigo(self, telefono, codigo):
        """Le pregunta a Twilio Verify si el codigo capturado es valido"""
        try:
            cliente = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            revision = (cliente.verify.v2.services(TWILIO_VERIFY_SERVICE_SID)
                        .verification_checks.create(to=telefono, code=codigo))
            return revision.status == 'approved'
        except TwilioRestException as error:
            print("ERROR 102: %s" % (error,))
            return False

    def GET(self):
        """Manejador de la peticion HTTP GET"""
        return render.index("", "", "1", "")

    def POST(self):
        """Manejador de la peticion HTTP POST: atiende los dos pasos
        segun el valor oculto 'paso' que trae el formulario"""
        datos = web.input(paso="1", correo="", codigo="", contrasena="", confirmar="")
        correo = datos.correo.strip().lower()

        if datos.paso == "1":
            if correo == "":
                return render.index("Captura tu correo electronico.", "", "1", "")

            telefono = self.buscarTelefono(correo)

            # Mensaje generico a proposito: no se revela si el correo
            # esta registrado o si tiene telefono.
            if telefono:
                self.enviarCodigo(telefono)

            return render.index("", "Si el correo esta registrado, te enviamos un codigo por SMS.", "2", correo)

        # paso == "2": validar codigo y guardar la nueva contrasena
        if datos.codigo == "" or datos.contrasena == "" or datos.confirmar == "":
            return render.index("Completa todos los campos.", "", "2", correo)

        if len(datos.contrasena) < 6:
            return render.index("La contrasena debe tener al menos 6 caracteres.", "", "2", correo)

        if datos.contrasena != datos.confirmar:
            return render.index("Las contrasenas no coinciden.", "", "2", correo)

        telefono = self.buscarTelefono(correo)

        if telefono is None or not self.verificarCodigo(telefono, datos.codigo):
            return render.index("El codigo no es correcto o ya vencio.", "", "2", correo)

        if not self.actualizarContrasena(correo, datos.contrasena):
            return render.index("No se pudo actualizar la contrasena. Intenta de nuevo.", "", "2", correo)

        return render.index("", "Tu contrasena se actualizo correctamente. Ya puedes iniciar sesion.", "listo", "")