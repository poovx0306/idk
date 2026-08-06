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

class EditarPregunta:
    def GET(self):
        datos = web.input(id=None)
        pregunta_id = datos.id
        
        conn = conectar_bd()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM preguntas WHERE id = ?', (pregunta_id,))
        pregunta = cursor.fetchone()
        
        cuestionario = None
        if pregunta:
            cursor.execute('SELECT * FROM cuestionarios WHERE id = ?', (pregunta['cuestionario_id'],))
            cuestionario = cursor.fetchone()
            
        conn.close()
        
        # Usamos claves seguras por si alguna columna tiene un nombre distinto en la BD
        p_texto = pregunta['texto'] if pregunta and 'texto' in pregunta.keys() else ''
        p_seccion = pregunta['seccion'] if pregunta and 'seccion' in pregunta.keys() else ''
        
        # Intentamos buscar el número de varias formas posibles para evitar el error de clave
        p_numero = ''
        if pregunta:
            for possible_key in ['numero', 'num', 'orden']:
                if possible_key in pregunta.keys():
                    p_numero = pregunta[possible_key]
                    break

        c_titulo = cuestionario['titulo'] if cuestionario and 'titulo' in cuestionario.keys() else ''
        c_id = pregunta['cuestionario_id'] if pregunta and 'cuestionario_id' in pregunta.keys() else 1

        return render.editar_pregunta(
            pregunta_id=pregunta_id,
            texto=p_texto,
            seccion=p_seccion,
            numero=p_numero,
            cuestionario_titulo=c_titulo,
            cuestionario_id=c_id
        )

    def POST(self):
        datos = web.input(id=None, texto='', seccion='', numero='')
        pregunta_id = datos.id
        
        conn = conectar_bd()
        cursor = conn.cursor()
        
        # Actualizamos texto, sección y el campo correcto 'numero_pregunta'
        cursor.execute('''
            UPDATE preguntas 
            SET texto = ?, seccion = ?, numero_pregunta = ?
            WHERE id = ?
        ''', (datos.texto, datos.seccion, datos.numero, pregunta_id))
        
        conn.commit()
        
        cursor.execute('SELECT cuestionario_id FROM preguntas WHERE id = ?', (pregunta_id,))
        p = cursor.fetchone()
        c_id = p['cuestionario_id'] if p and 'cuestionario_id' in p.keys() else 1
        
        conn.close()
        
        raise web.seeother(f'/administrativo/cuestionarios/ver_preguntas?id={c_id}')