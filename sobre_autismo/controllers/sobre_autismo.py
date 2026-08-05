import web

render = web.template.render('sobre_autismo/views')


class SobreAutismo:
    def GET(self):
        return render.sobre_autismo()