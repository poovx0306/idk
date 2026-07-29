import web


class CerrarSesion:
    """Cierra la sesion activa y regresa al portal de inicio."""

    def GET(self):
        sesion = web.config._session
        sesion.kill()
        raise web.seeother('/')