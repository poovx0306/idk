import web
import sqlite3

render = web.template.render('administrativos/views/')

def conectar_bd():
    conn = sqlite3.connect('sql/conaap.db')
    conn.row_factory = sqlite3.Row
    return conn

class Cuestionarios:
    def GET(self):
        conn = conectar_bd()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.titulo, c.estado,
                   COUNT(p.id) as preguntas,
                   COUNT(DISTINCT p.seccion) as secciones
            FROM cuestionarios c
            LEFT JOIN preguntas p ON p.cuestionario_id = c.id
            GROUP BY c.id;
        ''')
        filas = cursor.fetchall()
        
        cuestionarios_datos = []
        for f in filas:
            cuestionarios_datos.append({
                "id": f["id"],
                "titulo": f["titulo"],
                "preguntas": f["preguntas"],
                "secciones": f["secciones"],
                "respuestas": 0,
                "estado": f["estado"]
            })
            
        conn.close()
        return render.cuestionarios(cuestionarios=cuestionarios_datos)

class EliminarCuestionario:
    def POST(self):
        data = web.input()
        cuestionario_id = data.get('id')
        
        if cuestionario_id:
            conn = conectar_bd()
            cursor = conn.cursor()
            # Elimina el cuestionario y sus preguntas correspondientes
            cursor.execute("DELETE FROM cuestionarios WHERE id = ?", (cuestionario_id,))
            cursor.execute("DELETE FROM preguntas WHERE cuestionario_id = ?", (cuestionario_id,))
            conn.commit()
            conn.close()
            
        raise web.seeother('/administrativo/cuestionarios')

class VerPreguntasCuestionario:
    def GET(self):
        data = web.input()
        cuestionario_id = data.get('id')
        
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM preguntas WHERE cuestionario_id = ?", (cuestionario_id,))
        preguntas = cursor.fetchall()
        
        cursor.execute("SELECT titulo FROM cuestionarios WHERE id = ?", (cuestionario_id,))
        cuestionario = cursor.fetchone()
        conn.close()
        
        titulo_nombre = cuestionario["titulo"] if cuestionario else f"ID {cuestionario_id}"
        return f"<h3>Vista de preguntas para: {titulo_nombre}</h3><p>Total de preguntas encontradas: {len(preguntas)}</p><a href='/administrativo/cuestionarios'>Volver</a>"

class EditarCuestionario:
    def GET(self):
        data = web.input()
        cuestionario_id = data.get('id')
        
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cuestionarios WHERE id = ?", (cuestionario_id,))
        cuestionario = cursor.fetchone()
        conn.close()
        
        if cuestionario:
            return f"<h3>Formulario de edición para: {cuestionario['titulo']} (ID: {cuestionario['id']})</h3><a href='/administrativo/cuestionarios'>Volver</a>"
        return "Cuestionario no encontrado."

class NuevoCuestionario:
    def GET(self):
        return render.nuevo_cuestionario()

    def POST(self):
        data = web.input()
        titulo = data.get('titulo')
        estado = data.get('estado', 'Activo')

        if titulo:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO cuestionarios (titulo, estado) VALUES (?, ?)", (titulo, estado))
            conn.commit()
            conn.close()

        raise web.seeother('/administrativo/cuestionarios')