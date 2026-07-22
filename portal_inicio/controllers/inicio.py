import web

render = web.template.render('portal_inicio/views')

class Inicio:
    def GET(self):
        texto = "¡Hola! Tu servidor en Python y web.py están funcionando bien."
        
        return render.inicio(texto)