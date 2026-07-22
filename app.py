import web
# Importamos el controller Inicio desde la carpeta controllers
from portal_inicio.controllers.inicio import Inicio
from inicio_docente.controllers.inicio_docente import InicioDocente

# Mapeo de URLs -> Clases
urls = (
    '/', 'Inicio',
    '/inicio', 'Inicio'
    '/docente/inicio', 'InicioDocente'
)

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()