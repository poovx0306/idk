import web

render = web.template.render('deteccion_temprana/views/')

class Resultado:
    def GET(self):
        session = web.config._session
        es_padre = getattr(session, 'rol', None) == 'padre'
        return render.resultado(es_padre)