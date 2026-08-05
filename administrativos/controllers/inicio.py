import web

render = web.template.render('administrativos/views/')

class InicioAdministrativo:
    def GET(self):
        db = web.database(dbn='sqlite', db='sql/conaap.db')
        
        # Total de infantes (alumnos registrados)
        try:
            total_alumnos = db.query('SELECT COUNT(*) as total FROM infantes')[0].total
        except:
            total_alumnos = 0
        
        # Total de docentes
        try:
            total_docentes = db.query('SELECT COUNT(*) as total FROM docente')[0].total
        except:
            try:
                total_docentes = db.query('SELECT COUNT(*) as total FROM docentes')[0].total
            except:
                total_docentes = 0
        
# Total de cuestionarios respondidos
        try:
            total_cuestionarios = db.query('SELECT COUNT(*) as total FROM resultados_cuestionarios')[0].total
        except:
            total_cuestionarios = 0
            
        # Total de estrategias didácticas
        try:
            total_estrategias = db.query('SELECT COUNT(*) as total FROM estrategias_didacticas')[0].total
        except:
            total_estrategias = 0

        # Casos pendientes o en rojo (ajusta la condición según el campo de tu tabla resultados, por ejemplo: nivel, puntaje o estatus)
        try:
            casos_pendientes = list(db.query("SELECT * FROM resultados WHERE nivel_riesgo = 'Alto' OR resultado = 'Alto' LIMIT 5"))
        except:
            casos_pendientes = []

        return render.inicio(
            alumnos=total_alumnos,
            docentes=total_docentes,
            cuestionarios=total_cuestionarios,
            estrategias=total_estrategias,
            casos_pendientes=casos_pendientes
        )