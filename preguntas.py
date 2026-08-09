import sqlite3

def cargar_preguntas_veanme():
    conn = sqlite3.connect('sql/conaap.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS preguntas')

    cursor.execute('''
        CREATE TABLE preguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_pregunta INTEGER NOT NULL,
            seccion TEXT NOT NULL,
            texto TEXT NOT NULL,
            puntos_casi_nunca INTEGER NOT NULL,
            puntos_a_veces INTEGER NOT NULL,
            puntos_casi_siempre INTEGER NOT NULL
        )
    ''')

    preguntas = [
        (1, 'Interacción Social', '¿A su hijo(a) le gusta recibir expresiones de afecto físico como abrazos, besos, si ud. le da los brazos él acepta ser cargado?, si se cae ¿se deja consolar?', 2, 1, 0),
        (2, 'Interacción Social', '¿A su hijo(a) le interesa jugar con otros niños(as) de su edad?', 2, 1, 0),
        (3, 'Juego e Imaginación', '¿Su hijo(a) juega imaginando a la comidita, a que habla por teléfono, o a que maneja un coche o que es un personaje de la tv?', 2, 1, 0),
        (4, 'Comunicación', '¿Su hijo(a) usa su dedo para señalar algo que necesita como leche, galletas, agua, la puerta para abrirla?', 2, 1, 0),
        (5, 'Comunicación', '¿Su hijo(a) usa su dedo para señalar algo que le gusta o le interesa como juguetes, una fuente de agua, globos?', 2, 1, 0),
        (6, 'Conductas Repetitivas / Sensorial', '¿Mientras juega, a su hijo(a) le gusta oler, lamer u observar demasiado un objeto o juguete que tiene en sus manos?', 0, 1, 2),
        (7, 'Interacción Social', '¿Su hijo(a) le trae o muestra cosas que le gustan como juguetes, objetos, dibujos, trabajos que hizo en la escuela? ¿Solo por compartir la emoción?', 2, 1, 0),
        (8, 'Comunicación / Atención', '¿Cuándo le habla a su hijo(a), él/ella voltea a mirarla por más de 2 segundos?', 2, 1, 0),
        (9, 'Interacción Social', '¿Cuándo otras personas le hablan a su hijo(a), él/ella los mira directamente a los ojos por más de dos segundos?', 2, 1, 0),
        (10, 'Conductas Repetitivas / Sensorial', '¿A su hijo(a) le alteran los ruidos fuertes de la aspiradora, licuadora, el ruido metálico del choque de cubiertos o de los carritos del supermercado?', 0, 1, 2),
        (11, 'Interacción Social', '¿Cuándo ud. sonríe a su hijo (a), él/ella le responde con una sonrisa?', 2, 1, 0),
        (12, 'Interacción Social', '¿Su hijo(a) imita actividades que usted realiza cotidianamente como peinarse, lavarse los dientes, lavar trastes, limpiar?. ¿Se ríe cuando los demás se ríen?', 2, 1, 0),
        (13, 'Comunicación', '¿Su hijo(a) responde cuando le llaman por su nombre?', 2, 1, 0),
        (14, 'Atención Conjunta', '¿Si usted señala con su dedo un juguete como un globo, objeto o situación como un avión que pasa, su hijo(a) voltea a mirarlo?', 2, 1, 0),
        (15, 'Atención Conjunta', '¿Su hijo(a) voltea a mirar las cosas o situaciones que ud está observando?', 2, 1, 0),
        (16, 'Conductas Repetitivas / Sensorial', '¿Su hijo(a) hace movimientos extraños con sus dedos como sacudirlos o mueve sus manitas o deditos enfrente de su carita? ¿Mueve su cabeza de forma especial?', 0, 1, 2),
        (17, 'Comunicación', '¿Su hijo(a) intenta atraer su atención a lo que él o ella está haciendo?', 2, 1, 0),
        (18, 'Comunicación', '¿Ha pensado que su hijo(a) no escucha bien porque al llamarlo por su nombre no responde?', 2, 1, 0),
        (19, 'Comunicación', '¿Su hijo(a) entiende órdenes o indicaciones que ud. u otras personas le dan?', 2, 1, 0),
        (20, 'Atención', '¿Su hijo(a) se queda mirando fijo, con la mirada perdida por mucho tiempo?', 0, 1, 2),
        (21, 'Conductas Repetitivas', '¿Su hijo(a) pasa mucho tiempo girando o caminando de un lado a otro sin sentido?', 0, 1, 2),
        (22, 'Interacción Social', '¿Su hijo(a) voltea a verla cuando ve algo desconocido o nuevo como escaleras eléctricas, aparatos, animales?', 2, 1, 0),
        (23, 'Atención / Interacción', '¿Su hijo(a) mira por más tiempo a cosas o juguetes que a las personas que le rodean?', 0, 1, 2),
        (24, 'Comunicación', '¿Su hijo(a) habla de una manera rara, diferente, formal, o peculiar comparado con otros niños de la misma edad?', 0, 1, 2),
        (25, 'Comunicación', '¿Su hijo(a) habla sobre él mismo en segunda persona (por ejemplo: en vez de decir: "Quiero leche" él dice: "Quieres leche")?', 0, 1, 2),
        (26, 'Comunicación / Interacción', '¿Su hijo(a) pone sus manos encima de las de usted o de otras personas con el propósito de usarlas como herramienta o para auxiliarse en sus actividades?', 0, 1, 2)
    ]

    cursor.executemany('''
    INSERT INTO preguntas
    (numero_pregunta, seccion, texto, puntos_casi_nunca, puntos_a_veces, puntos_casi_siempre, cuestionario_id)
    VALUES (?, ?, ?, ?, ?, ?, 1)
    ''', preguntas)

    conn.commit()
    conn.close()
    print("¡Preguntas guardadas con éxito en sql'!")

if __name__ == '__main__':
    cargar_preguntas_veanme()