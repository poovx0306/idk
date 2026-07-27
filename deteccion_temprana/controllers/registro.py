import web

# Renderizador de las vistas de detección temprana
render = web.template.render('deteccion_temprana/views/')

class RegistroPrevio:
    def GET(self):
        # Muestra la pantalla del registro
        return render.registro()

    def POST(self):
        # Recibe los datos del formulario 
        datos = web.input()
        
        # mandamos directamente la pantalla del cuestionario
        return render.cuestionario()