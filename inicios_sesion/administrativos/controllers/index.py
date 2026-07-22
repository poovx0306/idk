import web
import sqlite3

# Configurar el motor de plantillas apuntando a la carpeta de views
# 'views' es la carpeta y 'base' puede ser un layout común o None
render = web.template.render('inicios_sesion/views', base=None)

class InicioAdministrativos:
    def obtenerDatosInicio(self):
        """Método auxiliar para consultar la base de datos"""
        conn = None
        try:
            # Ruta a tu base de datos SQLite
            conn = sqlite3.connect('sql/conaap.db')
            cursor = conn.cursor()
            
            # Consulta de ejemplo para obtener información dinámica
            query = "SELECT * FROM administrativos;"
            cursor.execute(query)
            
            usuario = []
            for row in cursor.fetchall():
                item = {
                    'id_admin': row[0],
                    'correo': row[1],
                    'contrasena': row[2]
                }
                usuario.append(item)
                
            return usuario

        except sqlite3.Error as error:
            print(f"ERROR 100: {error.args}")
            return []
        except Exception as error:
            print(f"ERROR 101: {error.args}")
            return []
        finally:
            if conn:
                conn.close()

    def GET(self):
        """Manejador de la petición HTTP GET"""
        datos = self.obtenerDatosInicio()
        return render.inicio(datos)