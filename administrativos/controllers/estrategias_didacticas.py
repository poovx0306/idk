import web
import sqlite3
import os

render = web.template.render('administrativos/views/')

def conectar_bd():
    conn = sqlite3.connect('sql/conaap.db')
    conn.row_factory = sqlite3.Row
    return conn

class EstrategiasDidacticasAdmin:
    def GET(self):
        data = web.input(materia='', grado='')
        materia = data.get('materia', '').strip()
        grado = data.get('grado', '').strip()

        conn = conectar_bd()
        cursor = conn.cursor()

        query = "SELECT * FROM actividad_asignada WHERE 1=1"
        params = []

        if materia:
            query += " AND LOWER(materia) = LOWER(?)"
            params.append(materia)

        if grado:
            query += " AND grado = ?"
            params.append(grado)

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        estrategias = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM actividad_asignada")
        total_estrategias = cursor.fetchone()['total']

        conn.close()
        return render.estrategias_didacticas(
            estrategias=estrategias, 
            total=total_estrategias,
            materia_sel=materia, 
            grado_sel=grado
        )

class NuevaEstrategiaAdmin:
    def GET(self):
        return render.nueva_estrategia()

    def POST(self):
        data = web.input(titulo='', condicion='', materia='', grado='', 
                        objetivo='', materiales='', pasos='', accion='Publicar')

        titulo = data.get('titulo')
        descripcion = data.get('condicion')  # condicion va en descripcion
        materia = data.get('materia')
        grado = data.get('grado')
        objetivo = data.get('objetivo')
        materiales = data.get('materiales')
        paso_a_paso = data.get('pasos')
        estado = 'Publicada' if data.get('accion') == 'Publicar' else 'Borrador'

        import datetime
        fecha = datetime.date.today().isoformat()

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO actividad_asignada 
            (titulo, descripcion, objetivo, materiales, paso_a_paso, materia, grado, fecha_asignacion, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (titulo, descripcion, objetivo, materiales, paso_a_paso, materia, grado, fecha, estado)
        )
        conn.commit()
        conn.close()

        raise web.seeother('/administrativo/estrategias')
    
class EditarEstrategiaAdmin:
    def GET(self):
        data = web.input()
        id = data.get('id')

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM actividad_asignada WHERE id = ?", (id,))
        actividad = cursor.fetchone()
        conn.close()

        if not actividad:
            raise web.seeother('/administrativo/estrategias')

        return render.editar_estrategia(actividad=actividad)

    def POST(self):
        data = web.input()
        id = data.get('id')
        titulo = data.get('titulo')
        descripcion = data.get('descripcion')
        objetivo = data.get('objetivo')
        materiales = data.get('materiales')
        paso_a_paso = data.get('paso_a_paso')
        materia = data.get('materia')
        grado = data.get('grado')
        grupo = data.get('grupo')
        estado = data.get('estado')

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE actividad_asignada
            SET titulo=?, descripcion=?, objetivo=?, materiales=?,
                paso_a_paso=?, materia=?, grado=?, grupo=?, estado=?
            WHERE id=?
        """, (titulo, descripcion, objetivo, materiales, paso_a_paso, materia, grado, grupo, estado, id))
        conn.commit()
        conn.close()

        raise web.seeother('/administrativo/estrategias')

def GET(self):
        data = web.input(materia='', grado='', buscar='')
        materia = data.get('materia', '').strip()
        grado = data.get('grado', '').strip()
        buscar = data.get('buscar', '').strip()

        conn = conectar_bd()
        cursor = conn.cursor()

        query = "SELECT * FROM actividad_asignada WHERE 1=1"
        params = []

        if buscar:
            query += " AND LOWER(titulo) LIKE LOWER(?)"
            params.append(f"%{buscar}%")

        if materia:
            query += " AND LOWER(materia) = LOWER(?)"
            params.append(materia)

        if grado:
            query += " AND grado = ?"
            params.append(grado)

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        estrategias = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM actividad_asignada")
        total_estrategias = cursor.fetchone()['total']

        conn.close()

        return render.estrategias_didacticas(
            estrategias=estrategias,
            total=total_estrategias,
            materia_sel=materia,
            grado_sel=grado,
            buscar_sel=buscar
        )