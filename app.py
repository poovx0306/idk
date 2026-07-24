import web

from portal_inicio.controllers.inicio import Inicio
from inicio_docente.controllers.inicio_docente import InicioDocente
from estrategias_didacticas.controllers.estrategias_didacticas import EstrategiasDidacticas

urls = (
    '/', 'Inicio',
    '/inicio', 'Inicio',

    '/docente/inicio', 'InicioDocente',

    '/login/docente', 'LoginDocente',

    '/deteccion-temprana', 'DeteccionTemprana',
    '/estrategias-didacticas', 'EstrategiasDidacticas'
)
app = web.application(urls, globals())

if __name__=="__main__":
    app.run()