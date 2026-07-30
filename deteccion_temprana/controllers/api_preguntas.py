import web
import sqlite3
import json

class ApiPreguntas:
    def GET(self):
        # Establecemos encabezado JSON (embellecedor)
        web.header('Content-Type', 'application/json')
        
        try:
            conn = sqlite3.connect('sql/conaap.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, numero_pregunta, seccion, texto, 
                       puntos_casi_nunca, puntos_a_veces, puntos_casi_siempre 
                FROM preguntas 
                ORDER BY numero_pregunta ASC
            ''')
            
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