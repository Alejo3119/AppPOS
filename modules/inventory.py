import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from modules.database import currency


class InventoryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f3f4f6")
        self.controller = controller

        # Header
        header_frame = tk.Frame(self, bg="#0f172a", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame, text="📦 Inventario",
            font=("Segoe UI", 16, "bold"),
            bg="#0f172a", fg="white"
        ).pack(side="left", padx=20, pady=15)

        tk.Button(
            header_frame, text="← Volver", font=("Segoe UI", 10),
            bg="#1e293b", fg="white", relief="flat", cursor="hand2",
            command=lambda: controller.show_frame("ModernLoginPage")
        ).pack(side="left", padx=10, pady=15)

        self.user_info = tk.Label(
            header_frame, text="", font=("Segoe UI", 11),
            bg="#0f172a", fg="#cbd5e1"
        )
        self.user_info.pack(side="right", padx=20, pady=15)

        # Notebook para separar
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # Pestaña tienda
        self.tienda_tab = tk.Frame(notebook, bg="#f3f4f6")
        notebook.add(self.tienda_tab, text="Tienda")
        self._build_tienda_tab()

        # Pestaña restaurante
        self.rest_tab = tk.Frame(notebook, bg="#f3f4f6")
        notebook.add(self.rest_tab, text="Restaurante")
        self._build_rest_tab()

    # -----------------------
    # Construcción de pestañas
    # -----------------------
    def _build_tienda_tab(self):
        frame = self.tienda_tab

        btns = tk.Frame(frame, bg="#f3f4f6")
        btns.pack(fill="x", pady=5)
        tk.Button(btns, text="➕ Agregar", bg="#22c55e", fg="white",
                  relief="flat", command=self.add_tienda).pack(side="left", padx=5)
        tk.Button(btns, text="✏️ Editar", bg="#f59e0b", fg="white",
                  relief="flat", command=self.edit_tienda).pack(side="left", padx=5)
        tk.Button(btns, text="🗑️ Eliminar", bg="#ef4444", fg="white",
                  relief="flat", command=self.delete_tienda).pack(side="left", padx=5)
        tk.Button(btns, text="🔄 Actualizar", bg="#3b82f6", fg="white",
                  relief="flat", command=self.load_tienda).pack(side="left", padx=5)

        cols = ("Código", "Nombre", "Categoría", "Precio", "Stock")
        self.tienda_table = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.tienda_table.heading(c, text=c)
            self.tienda_table.column(c, anchor="center", width=100)
        self.tienda_table.column("Nombre", width=200, anchor="w")
        self.tienda_table.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_rest_tab(self):
        frame = self.rest_tab

        btns = tk.Frame(frame, bg="#f3f4f6")
        btns.pack(fill="x", pady=5)
        tk.Button(btns, text="➕ Agregar", bg="#22c55e", fg="white",
                  relief="flat", command=self.add_rest).pack(side="left", padx=5)
        tk.Button(btns, text="✏️ Editar", bg="#f59e0b", fg="white",
                  relief="flat", command=self.edit_rest).pack(side="left", padx=5)
        tk.Button(btns, text="🗑️ Eliminar", bg="#ef4444", fg="white",
                  relief="flat", command=self.delete_rest).pack(side="left", padx=5)
        tk.Button(btns, text="🔄 Actualizar", bg="#3b82f6", fg="white",
                  relief="flat", command=self.load_rest).pack(side="left", padx=5)

        cols = ("Código", "Nombre", "Categoría", "Precio", "Disponible")
        self.rest_table = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            self.rest_table.heading(c, text=c)
            self.rest_table.column(c, anchor="center", width=100)
        self.rest_table.column("Nombre", width=200, anchor="w")
        self.rest_table.pack(fill="both", expand=True, padx=10, pady=10)

    # -----------------------
    # Lógica Tienda
    # -----------------------
    def load_tienda(self):
        for i in self.tienda_table.get_children():
            self.tienda_table.delete(i)
        c = self.controller.db.conn.cursor()
        c.execute("SELECT codigo,nombre,categoria,precio,stock FROM productos_tienda")
        for r in c.fetchall():
            self.tienda_table.insert("", "end",
                                     values=(r[0], r[1], r[2], currency(r[3]), r[4]))

    def add_tienda(self):
        code = simpledialog.askstring("Código", "Código del producto:")
        name = simpledialog.askstring("Nombre", "Nombre del producto:")
        cat = simpledialog.askstring("Categoría", "Categoría:")
        price = simpledialog.askfloat("Precio", "Precio unitario:")
        stock = simpledialog.askinteger("Stock", "Cantidad en stock:")
        if not all([code, name, cat, price is not None, stock is not None]):
            return
        try:
            c = self.controller.db.conn.cursor()
            c.execute("""INSERT INTO productos_tienda (codigo,nombre,categoria,precio,stock) 
                         VALUES (?,?,?,?,?)""", (code, name, cat, price, stock))
            self.controller.db.conn.commit()
            self.load_tienda()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_tienda(self):
        sel = self.tienda_table.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un producto.")
            return
        code = self.tienda_table.item(sel[0])["values"][0]
        new_price = simpledialog.askfloat("Precio", "Nuevo precio:")
        new_stock = simpledialog.askinteger("Stock", "Nuevo stock:")
        if new_price is None or new_stock is None:
            return
        c = self.controller.db.conn.cursor()
        c.execute("UPDATE productos_tienda SET precio=?, stock=? WHERE codigo=?",
                  (new_price, new_stock, code))
        self.controller.db.conn.commit()
        self.load_tienda()

    def delete_tienda(self):
        sel = self.tienda_table.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un producto.")
            return
        code = self.tienda_table.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirmar", "¿Eliminar producto?"):
            return
        c = self.controller.db.conn.cursor()
        c.execute("DELETE FROM productos_tienda WHERE codigo=?", (code,))
        self.controller.db.conn.commit()
        self.load_tienda()

    # -----------------------
    # Lógica Restaurante
    # -----------------------
    def load_rest(self):
        for i in self.rest_table.get_children():
            self.rest_table.delete(i)
        c = self.controller.db.conn.cursor()
        c.execute("SELECT codigo,nombre,categoria,precio,disponible FROM productos_restaurante")
        for r in c.fetchall():
            disp = "Sí" if r[4] else "No"
            self.rest_table.insert("", "end",
                                   values=(r[0], r[1], r[2], currency(r[3]), disp))

    def add_rest(self):
        code = simpledialog.askstring("Código", "Código del plato:")
        name = simpledialog.askstring("Nombre", "Nombre del plato:")
        cat = simpledialog.askstring("Categoría", "Categoría:")
        price = simpledialog.askfloat("Precio", "Precio unitario:")
        disponible = messagebox.askyesno("Disponible", "¿Está disponible este plato?")
        if not all([code, name, cat, price is not None]):
            return
        try:
            c = self.controller.db.conn.cursor()
            c.execute("""INSERT INTO productos_restaurante (codigo,nombre,categoria,precio,disponible) 
                         VALUES (?,?,?,?,?)""", (code, name, cat, price, 1 if disponible else 0))
            self.controller.db.conn.commit()
            self.load_rest()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_rest(self):
        sel = self.rest_table.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un plato.")
            return
        code = self.rest_table.item(sel[0])["values"][0]
        new_price = simpledialog.askfloat("Precio", "Nuevo precio:")
        disponible = messagebox.askyesno("Disponible", "¿Disponible?")
        if new_price is None:
            return
        c = self.controller.db.conn.cursor()
        c.execute("UPDATE productos_restaurante SET precio=?, disponible=? WHERE codigo=?",
                  (new_price, 1 if disponible else 0, code))
        self.controller.db.conn.commit()
        self.load_rest()

    def delete_rest(self):
        sel = self.rest_table.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un plato.")
            return
        code = self.rest_table.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirmar", "¿Eliminar plato?"):
            return
        c = self.controller.db.conn.cursor()
        c.execute("DELETE FROM productos_restaurante WHERE codigo=?", (code,))
        self.controller.db.conn.commit()
        self.load_rest()

    # -----------------------
    # Hooks
    # -----------------------
    def on_show(self):
        if self.controller.current_user:
            u = self.controller.current_user
            self.user_info.config(text=f"{u[3]}  ·  {u[4]}")
        self.load_tienda()
        self.load_rest()
