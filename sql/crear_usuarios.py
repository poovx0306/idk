import sqlite3
import hashlib

BASE = 'sql/conaap.db'

INSERTAR_DEMO = True

CUENTAS = [
    ('ana.martinez@conafe.gob.mx', 'docente123', 'docente', 'Ana Martinez Reyes'),
    ('maria.cruz@gmail.com', 'padre123', 'padre', 'Maria Cruz Hernandez'),
    ('admin@conafe.gob.mx', 'admin123', 'administrativo', 'Jorge Lira Uribe'),
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
            id_referencia  INTEGER
        )
    """)

    columnas = [c[1] for c in cursor.execute('PRAGMA table_info(usuario)')]
    if 'id_referencia' not in columnas:
        cursor.execute('ALTER TABLE usuario ADD COLUMN id_referencia INTEGER')
        print('Columna id_referencia agregada.')

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

    for correo, contrasena, rol, nombre in CUENTAS:
        cursor.execute("""
            INSERT INTO usuario (correo, contrasena, rol, nombre, id_referencia)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(correo) DO UPDATE SET
                contrasena    = excluded.contrasena,
                rol           = excluded.rol,
                nombre        = excluded.nombre,
                id_referencia = excluded.id_referencia
        """, (correo, encriptar(contrasena), rol, nombre, referencias.get(rol)))
        print('Cuenta lista:', correo, '/', contrasena, '(' + rol + ')')

    conexion.commit()
    conexion.close()


if __name__ == '__main__':
    main()