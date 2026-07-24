import web
render = web.template.render('deteccion_temprana/views/')

class DeteccionTemprana:
    def GET(self):
        return render.cuestionario()
    def POST (self):
        datos = web.input()

        puntuacion = 0
        for clave, valor in datos.items():
            if valor == "a_veces":
                puntuacion += 1
            elif valor == "raro":
                puntuacion += 2
        return render.resultado(puntuacion)