import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from modules.database import currency, today_str


class ReportsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f3f4f6")
        self.controller = controller

        # Header
        header_frame = tk.Frame(self, bg="#0f172a", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(
            header_frame, text="📊 Reportes de Ventas",
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

        # --- Filtros ---
        filter_frame = tk.Frame(main_frame, bg="#ffffff", relief="raised", bd=1)
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(filter_frame, text="Fecha desde:", bg="#ffffff").pack(side="left", padx=5, pady=10)
        self.date_from = tk.Entry(filter_frame, width=12)
        self.date_from.insert(0, today_str())
        self.date_from.pack(side="left", padx=5)

        tk.Label(filter_frame, text="Fecha hasta:", bg="#ffffff").pack(side="left", padx=5)
        self.date_to = tk.Entry(filter_frame, width=12)
        self.date_to.insert(0, today_str())
        self.date_to.pack(side="left", padx=5)

        tk.Button(
            filter_frame, text="🔍 Buscar", bg="#3b82f6", fg="white",
            font=("Segoe UI", 9), relief="flat", command=self.load_sales
        ).pack(side="left", padx=10)
        tk.Button(
            filter_frame, text="💾 Exportar CSV", bg="#22c55e", fg="white",
            font=("Segoe UI", 9), relief="flat", command=self.export_csv
        ).pack(side="left", padx=10)

        # --- Tabla ventas ---
        table_frame = tk.Frame(main_frame, bg="#ffffff", relief="raised", bd=1)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))

        cols = ("ID", "Fecha", "Tipo", "Mesa", "Usuario", "Total", "Pago")
        self.sales_table = ttk.Treeview(table_frame, columns=cols, show="headings")
        for c in cols:
            self.sales_table.heading(c, text=c)
            self.sales_table.column(c, anchor="center", width=100)
        self.sales_table.column("Fecha", width=140)
        self.sales_table.column("Usuario", width=150, anchor="w")
        self.sales_table.column("Total", width=100, anchor="e")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.sales_table.yview)
        self.sales_table.configure(yscrollcommand=y_scroll.set)
        self.sales_table.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

        # --- Botones ---
        btn_frame = tk.Frame(main_frame, bg="#f3f4f6")
        btn_frame.pack(fill="x")
        tk.Button(
            btn_frame, text="📄 Ver Detalle", bg="#f59e0b", fg="white",
            font=("Segoe UI", 9), relief="flat", command=self.view_detail
        ).pack(side="left", padx=5)

    # -----------------------
    # Métodos
    # -----------------------
    def on_show(self):
        if self.controller.current_user:
            u = self.controller.current_user
            self.user_info.config(text=f"{u[3]}  ·  {u[4]}")
        self.load_sales()

    def load_sales(self):
        f1 = self.date_from.get().strip()
        f2 = self.date_to.get().strip()

        try:
            c = self.controller.db.conn.cursor()
            c.execute("""SELECT v.id, v.fecha, v.tipo_venta, v.mesa, u.nombre, v.total, v.tipo_pago
                         FROM ventas v
                         LEFT JOIN usuarios u ON v.usuario_id=u.id
                         WHERE date(v.fecha) BETWEEN date(?) AND date(?)
                         ORDER BY v.fecha DESC""", (f1, f2))
            rows = c.fetchall()

            for i in self.sales_table.get_children():
                self.sales_table.delete(i)
            for r in rows:
                self.sales_table.insert("", "end",
                                        values=(r[0], r[1], r[2], r[3] if r[3] else "-", r[4], currency(r[5]), r[6]))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las ventas.\n{str(e)}")

    def view_detail(self):
        sel = self.sales_table.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione una venta.")
            return
        venta_id = self.sales_table.item(sel[0])["values"][0]

        detail_win = tk.Toplevel(self)
        detail_win.title(f"Detalle Venta #{venta_id}")
        detail_win.geometry("600x400")
        detail_win.configure(bg="#ffffff")
        detail_win.transient(self)
        detail_win.grab_set()

        cols = ("Producto", "Cantidad", "Precio", "Subtotal")
        detail_table = ttk.Treeview(detail_win, columns=cols, show="headings")
        for c in cols:
            detail_table.heading(c, text=c)
            detail_table.column(c, anchor="center", width=100)
        detail_table.column("Producto", width=200, anchor="w")

        detail_table.pack(fill="both", expand=True, padx=10, pady=10)

        c = self.controller.db.conn.cursor()
        c.execute("""SELECT producto_codigo,cantidad,precio_unitario,subtotal 
                     FROM detalle_ventas WHERE venta_id=?""", (venta_id,))
        rows = c.fetchall()
        for r in rows:
            detail_table.insert("", "end",
                                values=(r[0], r[1], currency(r[2]), currency(r[3])))

    def export_csv(self):
        f1 = self.date_from.get().strip()
        f2 = self.date_to.get().strip()
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV Files", "*.csv")],
            title="Guardar Reporte CSV"
        )
        if not filename:
            return
        try:
            c = self.controller.db.conn.cursor()
            c.execute("""SELECT v.id, v.fecha, v.tipo_venta, v.mesa, u.nombre, v.total, v.tipo_pago
                         FROM ventas v
                         LEFT JOIN usuarios u ON v.usuario_id=u.id
                         WHERE date(v.fecha) BETWEEN date(?) AND date(?)
                         ORDER BY v.fecha DESC""", (f1, f2))
            rows = c.fetchall()

            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Fecha", "Tipo", "Mesa", "Usuario", "Total", "Pago"])
                for r in rows:
                    writer.writerow(r)

            messagebox.showinfo("Éxito", "Reporte exportado a CSV correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte.\n{str(e)}")
