import web

from portal_inicio.controllers.inicio import Inicio
from inicio_docente.controllers.inicio_docente import InicioDocente

from inicios_sesion.docentes.controllers.index import LoginDocentes
from inicios_sesion.padres.controllers.index import LoginPadres
from inicios_sesion.administrativos.controllers.index import LoginAdministrativos
from inicios_sesion.cerrar_sesion import CerrarSesion

from estrategias_didacticas.controllers.estrategias_didacticas import EstrategiasDidacticas
from mi_perfil_docente.controllers.mi_perfil import MiPerfil
from deteccion_temprana.controllers.registro import RegistroPrevio
from deteccion_temprana.controllers.deteccion import DeteccionTemprana
from boton_crisis.controllers.boton_crisis import BotonCrisis, ConfirmacionCrisis
from guias_rapidas.controllers.guias_rapidas import GuiasRapidas

urls = (
    '/', 'Inicio',
    '/inicio', 'Inicio',
    '/docente/inicio', 'InicioDocente',
    '/login/docente', 'LoginDocentes',
    '/login/padre', 'LoginPadres',
    '/login/administrativo', 'LoginAdministrativos',
    '/cerrar-sesion', 'CerrarSesion',

    '/registro-nino', 'RegistroPrevio',
    '/cuestionario', 'DeteccionTemprana',
    '/deteccion-temprana/cuestionario', 'DeteccionTemprana',
    '/api/preguntas', 'deteccion_temprana.controllers.api_preguntas.ApiPreguntas',
    '/resultado', 'deteccion_temprana.controllers.resultado.Resultado',
    '/deteccion-temprana/resultado', 'deteccion_temprana.controllers.resultado.Resultado',
    '/estrategias-didacticas', 'EstrategiasDidacticas',

    '/mi-perfil', 'MiPerfil',

    '/boton-crisis', 'BotonCrisis',
    '/boton-crisis/confirmacion', 'ConfirmacionCrisis',
    '/guias-rapidas', 'GuiasRapidas',
)
app = web.application(urls, globals())

almacen = web.session.DiskStore('sessions')
sesion = web.session.Session(app, almacen, initializer={
    'id_usuario': None,
    'nombre': None,
    'rol': None,
    'id_referencia': None
})
web.config._session = sesion


if __name__ == "__main__":
    app.run()