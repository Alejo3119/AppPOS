import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib


class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f3f4f6")
        self.controller = controller

        # Header
        header_frame = tk.Frame(self, bg="#0f172a", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame, text="⚙️ Administración de Usuarios",
            font=("Segoe UI", 16, "bold"),
            bg="#0f172a", fg="white"
        ).pack(side="left", padx=20, pady=15)

        tk.Button(
            header_frame, text="← Volver", font=("Segoe UI", 10),
            bg="#1e293b", fg="white", relief="flat", cursor="hand2",
            command=lambda: controller.show_frame("ModuleSelector")
        ).pack(side="left", padx=10, pady=15)

        self.user_info = tk.Label(
            header_frame, text="", font=("Segoe UI", 11),
            bg="#0f172a", fg="#cbd5e1"
        )
        self.user_info.pack(side="right", padx=20, pady=15)

        # Tabla de usuarios
        main_frame = tk.Frame(self, bg="#f3f4f6")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        btns = tk.Frame(main_frame, bg="#f3f4f6")
        btns.pack(fill="x", pady=5)
        tk.Button(btns, text="➕ Agregar", bg="#22c55e", fg="white",
                  relief="flat", command=self.add_user).pack(side="left", padx=5)
        tk.Button(btns, text="✏️ Editar", bg="#f59e0b", fg="white",
                  relief="flat", command=self.edit_user).pack(side="left", padx=5)
        tk.Button(btns, text="🗑️ Eliminar", bg="#ef4444", fg="white",
                  relief="flat", command=self.delete_user).pack(side="left", padx=5)
        tk.Button(btns, text="🔄 Actualizar", bg="#3b82f6", fg="white",
                  relief="flat", command=self.load_users).pack(side="left", padx=5)

        cols = ("ID", "Usuario", "Nombre", "Rol", "Área", "Activo")
        self.table = ttk.Treeview(main_frame, columns=cols, show="headings")
        for c in cols:
            self.table.heading(c, text=c)
            self.table.column(c, anchor="center", width=100)
        self.table.column("Nombre", width=180, anchor="w")
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

    # -----------------------
    # Hooks
    # -----------------------
    def on_show(self):
        if not self.controller.require_role({"administrador"}):
            return
        u = self.controller.current_user
        self.user_info.config(text=f"{u[3]}  ·  {u[4]}")
        self.load_users()

    # -----------------------
    # Funciones CRUD usuarios
    # -----------------------
    def load_users(self):
        for i in self.table.get_children():
            self.table.delete(i)
        c = self.controller.db.conn.cursor()
        try:
            c.execute("SELECT id, username, nombre, rol, area, activo FROM usuarios")
            for r in c.fetchall():
                self.table.insert("", "end", values=(
                    r[0], r[1], r[2], r[3], r[4] if r[4] else "-", "Sí" if r[5] else "No"
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_user(self):
        username = simpledialog.askstring("Usuario", "Nombre de usuario:")
        nombre = simpledialog.askstring("Nombre", "Nombre completo:")
        password = simpledialog.askstring("Contraseña", "Contraseña inicial:")
        rol = simpledialog.askstring("Rol", "Rol (cajero / gerente / administrador):")
        area = None
        if rol and rol.lower() == "cajero":
            area = simpledialog.askstring("Área", "Área (tienda / restaurante):")
        if not all([username, nombre, password, rol]):
            return
        hashed = hashlib.sha256(password.encode()).hexdigest()
        try:
            c = self.controller.db.conn.cursor()
            c.execute("""INSERT INTO usuarios (username,password,nombre,rol,area,activo)
                         VALUES (?,?,?,?,?,1)""", (username, hashed, nombre, rol.lower(), area))
            self.controller.db.conn.commit()
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_user(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un usuario.")
            return
        uid = self.table.item(sel[0])["values"][0]
        new_name = simpledialog.askstring("Nombre", "Nuevo nombre (vacío = no cambiar):")
        new_pass = simpledialog.askstring("Contraseña", "Nueva contraseña (vacío = no cambiar):")
        new_rol = simpledialog.askstring("Rol", "Nuevo rol (cajero / gerente / administrador):")
        new_area = None
        if new_rol and new_rol.lower() == "cajero":
            new_area = simpledialog.askstring("Área", "Área (tienda / restaurante):")
        c = self.controller.db.conn.cursor()
        if new_name:
            c.execute("UPDATE usuarios SET nombre=? WHERE id=?", (new_name, uid))
        if new_pass:
            hashed = hashlib.sha256(new_pass.encode()).hexdigest()
            c.execute("UPDATE usuarios SET password=? WHERE id=?", (hashed, uid))
        if new_rol:
            c.execute("UPDATE usuarios SET rol=?, area=? WHERE id=?", (new_rol.lower(), new_area, uid))
        self.controller.db.conn.commit()
        self.load_users()

    def delete_user(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un usuario.")
            return
        uid = self.table.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirmar", "¿Eliminar usuario?"):
            return
        c = self.controller.db.conn.cursor()
        c.execute("DELETE FROM usuarios WHERE id=?", (uid,))
        self.controller.db.conn.commit()
        self.load_users()
