import web


class CerrarSesion:
    """Cierra la sesion activa y regresa al inicio de sesion."""

    def GET(self):
        sesion = web.config._session
        sesion.kill()
        raise web.seeother('/login/docente')