import sqlite3
import hashlib

BASE = 'sql/conaap.db'

INSERTAR_DEMO = True

# Numero verificado en Twilio (Verified Caller ID). Mientras tu cuenta de
# Twilio siga en modo de prueba, SOLO puedes recibir SMS reales en numeros
# que hayas verificado ahi (Phone Numbers > Manage > Verified Caller IDs,
# hasta 5 numeros). Por eso los 3 usuarios de demo comparten el mismo
# telefono: para probar la recuperacion de cualquiera de los 3, usa ese
# mismo celular. Si verificas mas numeros en Twilio, puedes darle a cada
# cuenta el suyo cambiando el cuarto valor de cada tupla.
TELEFONO_VERIFICADO = '+527205947513'

CUENTAS = [
    ('ana.martinez@conafe.gob.mx', 'docente123', 'docente', 'Ana Martinez Reyes', TELEFONO_VERIFICADO),
    ('maria.cruz@gmail.com', 'padre123', 'padre', 'Maria Cruz Hernandez', TELEFONO_VERIFICADO),
    ('admin@conafe.gob.mx', 'admin123', 'administrativo', 'Jorge Lira Uribe', TELEFONO_VERIFICADO),
    ('miguel@gmail.com','miguel123','padre','Miguel Corona', TELEFONO_VERIFICADO),
]


def encriptar(contrasena):
    """Mismo hash que usan los controladores de inicio de sesion."""
    return hashlib.sha256(contrasena.encode('utf-8')).hexdigest()


def main():
    conexion = sqlite3.connect(BASE)
    conexion.execute('PRAGMA foreign_keys = ON')
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario     INTEGER PRIMARY KEY AUTOINCREMENT,
            correo         TEXT NOT NULL UNIQUE,
            contrasena     TEXT NOT NULL,
            rol            TEXT NOT NULL,
            nombre         TEXT NOT NULL,
            id_referencia  INTEGER,
            telefono       TEXT
        )
    """)

    columnas = [c[1] for c in cursor.execute('PRAGMA table_info(usuario)')]
    if 'id_referencia' not in columnas:
        cursor.execute('ALTER TABLE usuario ADD COLUMN id_referencia INTEGER')
        print('Columna id_referencia agregada.')
    if 'telefono' not in columnas:
        cursor.execute('ALTER TABLE usuario ADD COLUMN telefono TEXT')
        print('Columna telefono agregada.')

    id_admin = None
    id_docente = None
    if INSERTAR_DEMO:
        if cursor.execute('SELECT COUNT(*) FROM administrador').fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO administrador (correo, contrasena) VALUES (?, ?)",
                ('admin@conafe.gob.mx', encriptar('admin123')))
            print('Administrador de prueba creado.')
        id_admin = cursor.execute('SELECT MIN(id_admin) FROM administrador').fetchone()[0]

        if cursor.execute('SELECT COUNT(*) FROM docente').fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO docente (clave_docente, nombre, id_admin) VALUES (?, ?, ?)",
                ('DOC-001', 'Ana Martinez Reyes', id_admin))
            print('Docente de prueba creado.')
        id_docente = cursor.execute('SELECT MIN(id_docente) FROM docente').fetchone()[0]

        if cursor.execute('SELECT COUNT(*) FROM padres').fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO padres (nombre, telefono) VALUES (?, ?)",
                ('Maria Cruz Hernandez', '7751234567'))
            print('Padre de prueba creado.')

    referencias = {
        'docente': id_docente,
        'administrativo': id_admin,
        'padre': None,
    }

    for correo, contrasena, rol, nombre, telefono in CUENTAS:
        cursor.execute("""
            INSERT INTO usuario (correo, contrasena, rol, nombre, id_referencia, telefono)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(correo) DO UPDATE SET
                contrasena    = excluded.contrasena,
                rol           = excluded.rol,
                nombre        = excluded.nombre,
                id_referencia = excluded.id_referencia,
                telefono      = excluded.telefono
        """, (correo, encriptar(contrasena), rol, nombre, referencias.get(rol), telefono))
        print('Cuenta lista:', correo, '/', contrasena, '(' + rol + ')', '- telefono:', telefono)

    conexion.commit()
    conexion.close()


if __name__ == '__main__':
    main()