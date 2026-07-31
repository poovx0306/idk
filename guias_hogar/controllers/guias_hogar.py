import web
import sqlite3

db_path = "sql/conaap.db"

class index:
    def GET(self):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, contenido FROM guia_rapida WHERE publico IN ('padre','ambos') ORDER BY titulo")
        guias = cur.fetchall()
        conn.close()
        return web.render.guias_hogar(seccion="guias", guias=guias)