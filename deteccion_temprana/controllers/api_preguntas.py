import web
import sqlite3
import json

class ApiPreguntas:
    def GET(self):
        web.header('Content-Type', 'application/json')

        try:
            conn = sqlite3.connect('sql/conaap.db')
            cursor = conn.cursor()

            # obtener el cuestionario activo
            cursor.execute("SELECT id FROM cuestionarios WHERE estado = 'Activo' LIMIT 1")
            cuestionario = cursor.fetchone()

            if not cuestionario:
                conn.close()
                return json.dumps({'status': 'error', 'mensaje': 'No hay cuestionario activo'})

            cuestionario_id = cuestionario[0]

            cursor.execute('''
                SELECT id, numero_pregunta, seccion, texto,
                       puntos_casi_nunca, puntos_a_veces, puntos_casi_siempre
                FROM preguntas
                WHERE cuestionario_id = ?
                ORDER BY numero_pregunta ASC
            ''', (cuestionario_id,))

            filas = cursor.fetchall()
            conn.close()

            lista_preguntas = []
            for fila in filas:
                lista_preguntas.append({
                    'id': fila[0],
                    'numero': fila[1],
                    'seccion': fila[2],
                    'texto': fila[3],
                    'puntos': {
                        'Casi nunca': fila[4],
                        'A veces': fila[5],
                        'Casi siempre': fila[6]
                    }
                })

            return json.dumps({'status': 'ok', 'preguntas': lista_preguntas})

        except Exception as e:
            return json.dumps({'status': 'error', 'mensaje': str(e)})