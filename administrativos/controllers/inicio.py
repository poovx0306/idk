import web

render = web.template.render('administrativos/views/')

class InicioAdministrativo:
    def GET(self):
        return render.inicio()