import web
#pruebas
from administrativos.controllers.cuestionarios import (
    Cuestionarios, 
    NuevoCuestionario, 
    EliminarCuestionario, 
    EditarCuestionario,
    VerPreguntasCuestionario
)
#cosas de alejandro (no tocar)
from administrativos.controllers.inicio import InicioAdministrativo
from administrativos.controllers.resultados import Resultados
from administrativos.controllers.estrategias_didacticas import EstrategiasDidacticasAdmin, NuevaEstrategiaAdmin
from administrativos.controllers.docentes import DocentesAdmin, NuevoDocenteAdmin, EditarDocenteAdmin, BajaDocenteAdmin
from administrativos.controllers.alumnos import AlumnosAdmin
from administrativos.controllers.alumnos import AlumnosAdmin, NuevoAlumnoAdmin
from administrativos.controllers.padres import PadresAdmin

from portal_inicio.controllers.inicio import Inicio
from sobre_autismo.controllers.sobre_autismo import SobreAutismo
from inicio_docente.controllers.inicio_docente import InicioDocente

from inicios_sesion.docentes.controllers.index import LoginDocentes
from inicios_sesion.padres.controllers.index import LoginPadres
from inicios_sesion.administrativos.controllers.index import LoginAdministrativos
from inicios_sesion.recuperar.controllers.index import RecuperarContrasena
from inicios_sesion.cerrar_sesion import CerrarSesion

from estrategias_didacticas.controllers.estrategias_didacticas import EstrategiasDidacticas, FichaActividad
from mi_perfil_docente.controllers.mi_perfil import MiPerfil
from deteccion_temprana.controllers.registro import RegistroPrevio
from deteccion_temprana.controllers.deteccion import DeteccionTemprana
from deteccion_temprana.controllers.seleccionar_nino import SeleccionarNino, ElegirNino
from deteccion_temprana.controllers.guardar_resultado import GuardarResultadoAPI
from boton_crisis.controllers.boton_crisis import BotonCrisis, ConfirmacionCrisis
from guias_rapidas.controllers.guias_rapidas import GuiasRapidas
from actividades_guardadas.controllers.actividades_guardadas import ActividadesGuardadas, FichaActividadAsignada, MarcarActividad, GuardarActividad, MisActividadesGuardadas
from inicio_padres.controllers.inicio_padres import InicioPadres
from guias_hogar.controllers.guias_hogar import GuiasHogar
from actividades_postcrisis.controllers.actividades_postcrisis import ActividadesPostcrisis, MarcarActividadPostcrisis
from avance_infante.controllers.avance_infante import AvanceInfante
from mi_perfil_padre.controllers.mi_perfil import MiPerfilPadre

urls = (
    '/', 'Inicio',
    '/sobre-autismo', 'SobreAutismo',

    #pruebas
    '/administrativo/inicio', 'InicioAdministrativo',
    '/administrativo/cuestionarios', 'Cuestionarios',
    '/administrativo/cuestionarios/nuevo', 'NuevoCuestionario',
    '/administrativo/cuestionarios/editar', 'EditarCuestionario',
    '/administrativo/cuestionarios/eliminar', 'EliminarCuestionario',
    '/administrativo/cuestionarios/ver_preguntas', 'VerPreguntasCuestionario',
    # Resultados
    '/administrativo/resultados', 'Resultados',
    '/administrativo/estrategias', 'EstrategiasDidacticasAdmin',
    '/administrativo/estrategias/nueva', 'NuevaEstrategiaAdmin',
    '/administrativo/docentes', 'DocentesAdmin',
    '/administrativo/docentes/nuevo', 'NuevoDocenteAdmin',
    '/administrativo/docentes/editar', 'EditarDocenteAdmin',
    '/administrativo/docentes/baja', 'BajaDocenteAdmin',
    '/administrativo/alumnos', 'AlumnosAdmin',
    '/administrativo/alumnos/nuevo', 'NuevoAlumnoAdmin',
    '/administrativo/padres', 'PadresAdmin',

    '/inicio', 'Inicio',
    '/docente/inicio', 'InicioDocente',
    '/login/docente', 'LoginDocentes',
    '/login/padre', 'LoginPadres',
    '/login/administrativo', 'LoginAdministrativos',
    '/recuperar-contrasena', 'RecuperarContrasena',
    '/cerrar-sesion', 'CerrarSesion',

    '/registro-nino', 'RegistroPrevio',
    '/cuestionario', 'DeteccionTemprana',
    '/deteccion-temprana/cuestionario', 'DeteccionTemprana',
    '/api/preguntas', 'deteccion_temprana.controllers.api_preguntas.ApiPreguntas',
    '/resultado', 'deteccion_temprana.controllers.resultado.Resultado',
#no mover esta linea ni la de arriba alv
    '/deteccion-temprana/resultado', 'deteccion_temprana.controllers.resultado.Resultado',

    '/estrategias-didacticas', 'EstrategiasDidacticas',
    '/estrategias-didacticas/ficha', 'FichaActividad',
    '/actividades-guardadas', 'ActividadesGuardadas',
    '/actividades-guardadas/ficha', 'FichaActividadAsignada',
    '/actividades-guardadas/completar', 'MarcarActividad',
    '/actividades-guardadas/guardar', 'GuardarActividad',
    '/actividades-guardadas/guardadas', 'MisActividadesGuardadas',

    '/padre/inicio', 'InicioPadres',
    '/padre/guias', 'GuiasHogar',
    '/padre/postcrisis', 'ActividadesPostcrisis',
    '/padre/postcrisis/marcar', 'MarcarActividadPostcrisis',
    '/padre/avance', 'AvanceInfante',
    '/padre/perfil', 'MiPerfilPadre',
    '/padre/seleccionar-nino', 'SeleccionarNino',
    '/padre/elegir-nino', 'ElegirNino',
    '/api/guardar-resultado', 'GuardarResultadoAPI',

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
    'id_referencia': None,
    'id_infante_actual': None
})
web.config._session = sesion


if __name__ == "__main__":
    app.run()