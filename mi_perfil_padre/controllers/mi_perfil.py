import web
import sqlite3

render = web.template.render('mi_perfil_padre/views')

db_path = "sql/conaap.db"


class MiPerfilPadre:
    def GET(self):
        session = web.config._session
        id_padre = session.id_referencia

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT correo, nombre FROM usuario WHERE rol = 'padre' AND id_referencia = ?", (id_padre,))
        usuario = cur.fetchone()

        cur.execute("SELECT correo, miembro_desde, cuestionarios_respondidos, estado FROM padres WHERE id = ?", (id_padre,))
        padre = cur.fetchone()
        conn.close()

        correo = usuario["correo"] if usuario else (padre["correo"] if padre else "sin-correo@conafe.gob.mx")
        nombre = usuario["nombre"] if usuario else "Familia"
        miembro_desde = padre["miembro_desde"] if padre and padre["miembro_desde"] else "No disponible"

        return render.mi_perfil("perfil", nombre, correo, miembro_desde)