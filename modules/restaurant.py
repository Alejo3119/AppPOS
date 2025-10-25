import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from modules.database import currency


class RestaurantPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f3f4f6")
        self.controller = controller

        # Header
        header_frame = tk.Frame(self, bg="#0f172a", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame, text="🍽️ Módulo Restaurante",
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

        # Main frame
        main_frame = tk.Frame(self, bg="#f3f4f6")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=2)

        # --- Productos ---
        left_frame = tk.Frame(main_frame, bg="#ffffff", relief="raised", bd=1)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_rowconfigure(1, weight=1)

        search_frame = tk.Frame(left_frame, bg="#ffffff")
        search_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        tk.Label(search_frame, text="🔍 Buscar plato:", bg="#ffffff").pack(side="left")

        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 10))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_products())

        table_frame = tk.Frame(left_frame, bg="#ffffff")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        cols = ("Código", "Nombre", "Categoría", "Precio", "Disponible")
        self.product_table = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        for c in cols:
            self.product_table.heading(c, text=c)
            self.product_table.column(c, anchor="center", width=100)
        self.product_table.column("Nombre", width=200, anchor="w")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.product_table.yview)
        self.product_table.configure(yscrollcommand=y_scroll.set)
        self.product_table.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

        btn_frame = tk.Frame(left_frame, bg="#ffffff")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        tk.Button(
            btn_frame, text="➕ Agregar a pedido", font=("Segoe UI", 10),
            bg="#22c55e", fg="white", relief="flat", command=self.add_to_cart
        ).pack(side="left", padx=5)
        tk.Button(
            btn_frame, text="🔄 Actualizar", font=("Segoe UI", 10),
            bg="#3b82f6", fg="white", relief="flat", command=self.load_products
        ).pack(side="left", padx=5)

        # --- Pedido / Carrito ---
        right_frame = tk.Frame(main_frame, bg="#ffffff", relief="raised", bd=1)
        right_frame.grid(row=0, column=1, sticky="nsew")
        tk.Label(
            right_frame, text="🧾 Pedido",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff", fg="#1e293b"
        ).pack(pady=15)

        mesa_frame = tk.Frame(right_frame, bg="#ffffff")
        mesa_frame.pack(fill="x", padx=15, pady=(0, 10))
        tk.Label(mesa_frame, text="Mesa:", font=("Segoe UI", 10), bg="#ffffff").pack(side="left")
        self.mesa_entry = tk.Entry(mesa_frame, font=("Segoe UI", 10), width=10)
        self.mesa_entry.pack(side="left", padx=10)

        cart_table_frame = tk.Frame(right_frame, bg="#ffffff")
        cart_table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        ccols = ("Producto", "Cant", "Precio", "Subtotal")
        self.cart_table = ttk.Treeview(cart_table_frame, columns=ccols, show="headings", height=10)
        for c in ccols:
            self.cart_table.heading(c, text=c)
            self.cart_table.column(c, anchor="center", width=80)
        self.cart_table.column("Producto", width=150, anchor="w")

        y_scroll2 = ttk.Scrollbar(cart_table_frame, orient="vertical", command=self.cart_table.yview)
        self.cart_table.configure(yscrollcommand=y_scroll2.set)
        self.cart_table.pack(side="left", fill="both", expand=True)
        y_scroll2.pack(side="right", fill="y")

        total_frame = tk.Frame(right_frame, bg="#ffffff")
        total_frame.pack(fill="x", padx=15, pady=(0, 15))
        self.total_label = tk.Label(
            total_frame, text="Total: $0",
            font=("Segoe UI", 14, "bold"),
            bg="#ffffff", fg="#1e293b"
        )
        self.total_label.pack(side="left")

        action_btns = tk.Frame(total_frame, bg="#ffffff")
        action_btns.pack(side="right")
        tk.Button(
            action_btns, text="✏️ Cantidad", font=("Segoe UI", 9),
            bg="#f59e0b", fg="white", relief="flat", command=self.modify_quantity
        ).pack(side="left", padx=2)
        tk.Button(
            action_btns, text="🗑️ Vaciar", font=("Segoe UI", 9),
            bg="#ef4444", fg="white", relief="flat", command=self.clear_cart
        ).pack(side="left", padx=2)
        tk.Button(
            action_btns, text="💰 Cobrar", font=("Segoe UI", 9),
            bg="#22c55e", fg="white", relief="flat", command=self.finish_sale
        ).pack(side="left", padx=2)

        # Estado
        self.cart = []
        self.total = 0.0

    # -----------------------
    # Métodos
    # -----------------------
    def on_show(self):
        if self.controller.current_user:
            u = self.controller.current_user
            self.user_info.config(text=f"{u[3]}  ·  {u[4]}")
        self.load_products()
        self.cart = []
        self.update_cart()

    def load_products(self):
        q = self.search_entry.get().strip().lower()
        c = self.controller.db.conn.cursor()
        if q:
            c.execute("""SELECT codigo,nombre,categoria,precio,disponible 
                         FROM productos_restaurante 
                         WHERE (LOWER(nombre) LIKE ? OR LOWER(categoria) LIKE ?)""",
                      (f"%{q}%", f"%{q}%"))
        else:
            c.execute("SELECT codigo,nombre,categoria,precio,disponible FROM productos_restaurante")
        rows = c.fetchall()

        for i in self.product_table.get_children():
            self.product_table.delete(i)
        for r in rows:
            disp = "Sí" if r[4] else "No"
            self.product_table.insert("", "end",
                                      values=(r[0], r[1], r[2], currency(r[3]), disp))

    def add_to_cart(self):
        sel = self.product_table.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un plato.")
            return
        code, name, cat, price_disp, disponible = self.product_table.item(sel[0])["values"]
        if disponible != "Sí":
            messagebox.showwarning("Aviso", "Este plato no está disponible.")
            return
        price = float(str(price_disp).replace('$', '').replace(',', ''))

        for p in self.cart:
            if p["codigo"] == code:
                p["cantidad"] += 1
                self.update_cart()
                return

        self.cart.append({"codigo": code, "nombre": name, "precio": price, "cantidad": 1})
        self.update_cart()

    def modify_quantity(self):
        sel = self.cart_table.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un ítem del pedido.")
            return

        item_name = self.cart_table.item(sel[0])["values"][0]
        for p in self.cart:
            if p["nombre"] == item_name:
                nueva = simpledialog.askinteger(
                    "Cantidad",
                    f"Nueva cantidad para {p['nombre']}",
                    minvalue=0, initialvalue=p['cantidad']
                )
                if nueva is None:
                    return
                if nueva == 0:
                    self.cart = [x for x in self.cart if x["nombre"] != item_name]
                else:
                    self.cart[self.cart.index(p)]["cantidad"] = nueva
                self.update_cart()
                return

    def update_cart(self):
        for i in self.cart_table.get_children():
            self.cart_table.delete(i)
        self.total = 0.0
        for p in self.cart:
            sub = p['cantidad'] * p['precio']
            self.total += sub
            self.cart_table.insert("", "end",
                                   values=(p['nombre'], p['cantidad'],
                                           currency(p['precio']), currency(sub)))
        self.total_label.config(text=f"Total: {currency(self.total)}")

    def clear_cart(self):
        if not self.cart:
            return
        if messagebox.askyesno("Confirmar", "¿Vaciar pedido?"):
            self.cart = []
            self.update_cart()

    def finish_sale(self):
        if not self.cart:
            messagebox.showwarning("Aviso", "Pedido vacío.")
            return
        mesa = self.mesa_entry.get().strip()
        if not mesa:
            messagebox.showwarning("Aviso", "Ingrese número de mesa.")
            return

        payment_window = tk.Toplevel(self)
        payment_window.title("Método de Pago")
        payment_window.geometry("300x200")
        payment_window.configure(bg="#ffffff")
        payment_window.resizable(False, False)
        payment_window.transient(self)
        payment_window.grab_set()

        tk.Label(payment_window, text="Seleccione método de pago:",
                 font=("Segoe UI", 12), bg="#ffffff").pack(pady=20)
        payment_var = tk.StringVar(value="efectivo")
        for txt, val in [("💵 Efectivo", "efectivo"),
                         ("💳 Tarjeta", "tarjeta"),
                         ("📱 Transferencia", "transferencia")]:
            tk.Radiobutton(payment_window, text=txt, variable=payment_var,
                           value=val, font=("Segoe UI", 11), bg="#ffffff").pack(anchor="w", padx=50, pady=5)

        def process_payment():
            payment_window.destroy()
            self.process_sale(payment_var.get(), mesa)

        tk.Button(payment_window, text="Procesar Pago", font=("Segoe UI", 11, "bold"),
                  bg="#22c55e", fg="white", relief="flat", command=process_payment).pack(pady=20)

    def process_sale(self, metodo, mesa):
        try:
            c = self.controller.db.conn.cursor()
            c.execute("""INSERT INTO ventas (total,tipo_pago,usuario_id,tipo_venta,mesa)
                         VALUES (?,?,?,?,?)""",
                      (self.total, metodo, self.controller.current_user[0], "restaurante", mesa))
            venta_id = c.lastrowid

            for p in self.cart:
                sub = p['cantidad'] * p['precio']
                c.execute("""INSERT INTO detalle_ventas 
                             (venta_id,producto_codigo,cantidad,precio_unitario,subtotal) 
                             VALUES (?,?,?,?,?)""",
                          (venta_id, p['codigo'], p['cantidad'], p['precio'], sub))

            self.controller.db.conn.commit()
            messagebox.showinfo("Éxito",
                                f"Pedido registrado!\nMesa {mesa}\nTotal: {currency(self.total)}")
            self.cart = []
            self.update_cart()
            self.load_products()

        except Exception as e:
            self.controller.db.conn.rollback()
            messagebox.showerror("Error", f"Error al procesar el pedido: {str(e)}")
