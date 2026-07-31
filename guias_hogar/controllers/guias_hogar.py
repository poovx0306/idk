import web
import sqlite3

render = web.template.render('guias_hogar/views')

db_path = "sql/conaap.db"

class GuiasHogar:
    def GET(self):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, contenido FROM guia_rapida WHERE publico IN ('padre','ambos') ORDER BY titulo")
        guias = cur.fetchall()
        conn.close()
        return render.guias_hogar("guias", guias)