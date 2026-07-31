import web


class CerrarSesion:
    def GET(self):
        sesion = web.config._session
        sesion.kill()
        raise web.HTTPError('303 See Other', {'Location': '/'})