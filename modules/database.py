import sqlite3
from datetime import date, datetime, timedelta


def currency(amount):
    """Formatea valores numéricos como moneda."""
    return f"${amount:,.0f}".replace(",", ".")


def today_str():
    return date.today().strftime("%Y-%m-%d")


def month_bounds():
    today = date.today()
    first_day = today.replace(day=1).strftime("%Y-%m-%d")
    if today.month == 12:
        next_month = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month + 1, day=1)
    last_day = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")
    return first_day, last_day


class Database:
    def __init__(self, db_name="pos.db"):
        self.conn = sqlite3.connect(db_name)
        self._init_schema()

    def _init_schema(self):
        c = self.conn.cursor()

        # -------------------------
        # Tabla de usuarios
        # -------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            nombre TEXT,
            rol TEXT,
            activo INTEGER DEFAULT 1
        )
        """)

        # Asegurar columna 'area'
        try:
            c.execute("ALTER TABLE usuarios ADD COLUMN area TEXT")
        except sqlite3.OperationalError:
            pass

        # -------------------------
        # Tabla de productos tienda
        # -------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS productos_tienda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            nombre TEXT,
            categoria TEXT,
            precio REAL,
            stock INTEGER
        )
        """)

        # -------------------------
        # Tabla de productos restaurante
        # -------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS productos_restaurante (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            nombre TEXT,
            categoria TEXT,
            precio REAL,
            disponible INTEGER
        )
        """)

        # -------------------------
        # Tabla de ventas
        # -------------------------
        c.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            usuario_id INTEGER,
            tipo TEXT,
            total REAL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
        """)

        # -------------------------
        # Crear admin por defecto si no existe
        # -------------------------
        c.execute("SELECT * FROM usuarios WHERE username=?", ("admin",))
        if not c.fetchone():
            c.execute("""
                INSERT INTO usuarios (username, password, nombre, rol, activo, area)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("admin", "admin123", "Administrador", "administrador", 1, None))
            print("✅ Usuario admin creado (usuario: admin, contraseña: admin123)")

        self.conn.commit()
