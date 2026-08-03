import web

render = web.template.render('administrativos/views/')

class InicioAdministrativo:
    def GET(self):
        db = web.database(dbn='sqlite', db='sql/conaap.db')
        
        total_alumnos = db.query('SELECT COUNT(*) as total FROM infantes')[0].total
        total_docentes = db.query('SELECT COUNT(*) as total FROM docente')[0].total
        
        try:
            total_cuestionarios = db.query('SELECT COUNT(*) as total FROM cuestionarios')[0].total
        except:
            total_cuestionarios = 0
            
        try:
            total_estrategias = db.query('SELECT COUNT(*) as total FROM estrategias_didacticas')[0].total
        except:
            total_estrategias = 0

        return render.inicio(
            alumnos=total_alumnos,
            docentes=total_docentes,
            cuestionarios=total_cuestionarios,
            estrategias=total_estrategias
        )