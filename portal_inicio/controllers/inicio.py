import web
import sqlite3

# Configurar el motor de plantillas apuntando a la carpeta de views
# 'views' es la carpeta y 'base' puede ser un layout común o None
render = web.template.render('portal_inicio/views', base=None)

class Inicio:
    def obtenerDatosInicio(self):
        """Método auxiliar para consultar la base de datos"""
        conn = None
        try:
            # Ruta a tu base de datos SQLite
            conn = sqlite3.connect('sql/conaap.db')
            cursor = conn.cursor()
            
            # Consulta de ejemplo para obtener información dinámica
            query = "SELECT * FROM tarjetas_inicio;"
            cursor.execute(query)
            
            informacion = []
            for row in cursor.fetchall():
                item = {
                    'id': row[0],
                    'titulo': row[1],
                    'descripcion': row[2]
                }
                informacion.append(item)
                
            return informacion

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
        # Renderiza la plantilla portal_inicio/views/inicio.html
        return render.inicio(datos)