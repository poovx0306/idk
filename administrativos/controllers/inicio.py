import web

render = web.template.render('administrativos/views/')


class InicioAdministrativo:
    def GET(self):
        db = web.database(dbn='sqlite', db='sql/conaap.db')

        try:
            total_alumnos = db.query('SELECT COUNT(*) as total FROM infantes')[0].total
        except Exception as e:
            print("Error al contar infantes:", e)
            total_alumnos = 0

        try:
            total_docentes = db.query('SELECT COUNT(*) as total FROM docente')[0].total
        except Exception as e:
            print("Error al contar docentes:", e)
            total_docentes = 0

        try:
            total_cuestionarios = db.query('SELECT COUNT(*) as total FROM cuestionario')[0].total
        except Exception as e:
            print("Error al contar cuestionarios:", e)
            total_cuestionarios = 0

        try:
            total_estrategias = db.query('SELECT COUNT(*) as total FROM estrategias_didacticas')[0].total
        except Exception as e:
            print("Error al contar estrategias:", e)
            total_estrategias = 0

        try:
            casos_pendientes = list(db.query("SELECT * FROM resultados WHERE nivel_riesgo = 'Alto' OR resultado = 'Alto' LIMIT 5"))
        except Exception as e:
            print("Error al consultar casos pendientes:", e)
            casos_pendientes = []

        return render.inicio(
            alumnos=total_alumnos,
            docentes=total_docentes,
            cuestionarios=total_cuestionarios,
            estrategias=total_estrategias,
            casos_pendientes=casos_pendientes
        )