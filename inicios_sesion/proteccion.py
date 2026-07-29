import web
RUTAS_PROTEGIDAS = {
    '/docente/inicio': 'docente',
    '/mi-perfil': 'docente',
    '/estrategias-didacticas': 'administrativo',
}

LOGIN_POR_ROL = {
    'docente': '/login/docente',
    'padre': '/login/padre',
    'administrativo': '/login/administrativo',
}


def verificar_sesion():
    ruta = web.ctx.path
    rol_requerido = RUTAS_PROTEGIDAS.get(ruta)

    if rol_requerido is None:
        return

    sesion = web.config._session

    if sesion.get('id_usuario') is None:
        raise web.seeother(LOGIN_POR_ROL[rol_requerido])

    if sesion.get('rol') != rol_requerido:
        raise web.seeother(LOGIN_POR_ROL[rol_requerido])