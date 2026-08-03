import web
import sqlite3

render = web.template.render('mi_perfil_padres/views')

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

        cur.execute("SELECT nombre, telefono FROM padres WHERE id_padres = ?", (id_padre,))
        padre = cur.fetchone()
        conn.close()

        correo = usuario["correo"] if usuario else "sin-correo@conafe.gob.mx"
        nombre = usuario["nombre"] if usuario else (padre["nombre"] if padre else "Familia")
        telefono = padre["telefono"] if padre and padre["telefono"] else "No registrado"

        return render.mi_perfil("perfil", nombre, correo, telefono)