import web
# Importamos el controller Inicio desde la carpeta controllers
from portal_inicio.controllers.inicio import Inicio
from 

# Mapeo de URLs -> Clases
urls = (
    '/', 'Inicio',
    '/inicio', 'Inicio'
)

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()