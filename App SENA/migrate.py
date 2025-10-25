import sqlite3

conn = sqlite3.connect("pos.db")
c = conn.cursor()
try:
    c.execute("ALTER TABLE usuarios ADD COLUMN area TEXT")
    print("Columna 'area' agregada.")
except Exception as e:
    print("Posiblemente ya existía:", e)
conn.commit()
conn.close()
