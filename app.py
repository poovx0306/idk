import web

from portal_inicio.controllers.inicio import Inicio
from inicio_docente.controllers.inicio_docente import InicioDocente

urls = (
    '/', 'Inicio',
    '/inicio', 'Inicio',
    
    '/docente/inicio', 'InicioDocente',
    
    '/login/docente', 'LoginDocente',
    
    '/deteccion-temprana', 'DeteccionTemprana',
    '/estrategias-didacticas', 'EstrategiasDidacticas'
)
app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()