import web

from portal_inicio.controllers.inicio import Inicio
from inicio_docente.controllers.inicio_docente import InicioDocente
from inicios_sesion.docentes.controllers.index import LoginDocentes
from inicios_sesion.padres.controllers.index import LoginPadres
from inicios_sesion.administrativos.controllers.index import LoginAdministrativos
from inicios_sesion.cerrar_sesion import CerrarSesion


urls = (
    '/', 'Inicio',
    '/inicio', 'Inicio',
    '/docente/inicio', 'InicioDocente',
    '/login/docente', 'LoginDocentes',
    '/login/padre', 'LoginPadres',
    '/login/administrativo', 'LoginAdministrativos',
    '/cerrar-sesion', 'CerrarSesion'
)

app = web.application(urls, globals())

almacen = web.session.DiskStore('sessions')
sesion = web.session.Session(app, almacen, initializer={
    'id_usuario': None,
    'nombre': None,
    'rol': None
})
web.config._session = sesion

if __name__ == "__main__":
    app.run()