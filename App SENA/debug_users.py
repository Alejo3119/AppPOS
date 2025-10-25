import sqlite3

conn = sqlite3.connect("pos.db")
c = conn.cursor()
c.execute("PRAGMA table_info(usuarios)")
print("Estructura de tabla usuarios:")
print(c.fetchall())

print("\nUsuarios existentes:")
c.execute("SELECT id, username, password, nombre, rol, activo, area FROM usuarios")
for row in c.fetchall():
    print(row)

conn.close()
