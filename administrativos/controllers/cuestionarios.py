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

class Cuestionarios:
    def GET(self):
        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute('SELECT id, titulo, estado FROM cuestionarios')
        filas = cursor.fetchall()

        cuestionarios_datos = []
        for f in filas:
            cuestionario_id = f["id"]

            # Contar cuántas preguntas pertenecen a este cuestionario
            cursor.execute('SELECT COUNT(*) AS total FROM preguntas WHERE cuestionario_id = ?', (cuestionario_id,))
            conteo = cursor.fetchone()
            total_preguntas = conteo["total"] if conteo else 0

            cuestionarios_datos.append({
                "id": f["id"],
                "titulo": f["titulo"],
                "preguntas": total_preguntas,  # <--- Aquí va el conteo real
                "secciones": 0,
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
        
        # Obtener datos del cuestionario
        cursor.execute("SELECT * FROM cuestionarios WHERE id = ?", (cuestionario_id,))
        cuestionario = cursor.fetchone()
        
        # Obtener sus preguntas
        cursor.execute("SELECT * FROM preguntas WHERE cuestionario_id = ?", (cuestionario_id,))
        preguntas = cursor.fetchall()
        
        conn.close()
        
        if cuestionario:
            return render.editar_cuestionario(cuestionario=cuestionario, preguntas=preguntas)
        else:
            raise web.seeother('/administrativo/cuestionarios')

    def POST(self):
        data = web.input()
        cuestionario_id = data.get('cuestionario_id')
        titulo = data.get('titulo_cuestionario')
        texto_pregunta = data.get('texto_pregunta')
        seccion = data.get('seccion', 'General')
        numero_pregunta = data.get('numero_pregunta', 1)

        conn = conectar_bd()
        cursor = conn.cursor()

        # 1. Actualizar el título del cuestionario
        if titulo and cuestionario_id:
            cursor.execute("UPDATE cuestionarios SET titulo = ? WHERE id = ?", (titulo, cuestionario_id))

        # 2. Si escribió una nueva pregunta, insertarla
        if texto_pregunta and cuestionario_id:
            cursor.execute('''
                INSERT INTO preguntas (cuestionario_id, numero_pregunta, seccion, texto, puntos_casi_nunca, puntos_a_veces, puntos_casi_siempre)
                VALUES (?, ?, ?, ?, 2, 1, 0)
            ''', (cuestionario_id, numero_pregunta, seccion, texto_pregunta))

        conn.commit()
        conn.close()

        raise web.seeother('/administrativo/cuestionarios')

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

class VerPreguntasCuestionario:
    def GET(self):
        data = web.input()
        cuestionario_id = data.get('id')

        conn = conectar_bd()
        cursor = conn.cursor()

        # Obtener título e información del cuestionario
        cursor.execute("SELECT * FROM cuestionarios WHERE id = ?", (cuestionario_id,))
        cuestionario = cursor.fetchone()

        # Obtener la lista de preguntas
        cursor.execute("SELECT * FROM preguntas WHERE cuestionario_id = ? ORDER BY numero_pregunta ASC", (cuestionario_id,))
        preguntas = cursor.fetchall()

        conn.close()

        if cuestionario:
            return render.ver_preguntas(cuestionario=cuestionario, preguntas=preguntas)
        else:
            raise web.seeother('/administrativo/cuestionarios')