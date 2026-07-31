import sqlite3

conexion = sqlite3.connect('sql/conaap.db')
conexion.execute("UPDATE usuario SET telefono = ? WHERE correo = ?", ('+527205947513', 'admin@conafe.gob.mx'))
conexion.commit()
conexion.close()
print("Telefono asignado.")