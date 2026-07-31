import web
import sqlite3
import os

render = web.template.render('administrativos/views/')

def conectar_bd():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'sql', 'conaap.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

class PadresAdmin:
    def GET(self):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM padres ORDER BY id DESC")
        padres = cursor.fetchall()
        conn.close()
        
        return render.padres(padres=padres)