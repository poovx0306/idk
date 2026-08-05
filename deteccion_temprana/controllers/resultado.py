import web

render = web.template.render('deteccion_temprana/views/')

class Resultado:
    def GET(self):
        return render.resultado()