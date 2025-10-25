import tkinter as tk
from tkinter import messagebox

# --- Módulos propios ---
from modules.database import Database
from modules.login import ModernLoginPage
from modules.store import StorePage
from modules.restaurant import RestaurantPage
from modules.report import ReportsPage
from modules.inventory import InventoryPage

# Admin (opcional): si no existe admin.py, usamos un placeholder
try:
    from modules.admin import SettingsPage
except Exception:
    class SettingsPage(tk.Frame):
        def __init__(self, parent, controller):
            super().__init__(parent, bg="#f3f4f6")
            tk.Label(self, text="⚙️ Configuración (por agregar)",
                     font=("Segoe UI", 14, "bold"),
                     bg="#f3f4f6", fg="#334155").pack(pady=20)
        def on_show(self): pass


INACTIVITY_TIMEOUT_MS = 5 * 60 * 1000  # 5 minutos


class ModuleSelector(tk.Frame):
    """
    Pantalla de selección de módulo (Tienda / Restaurante) post-login.
    Se adapta a los permisos del rol.
    """
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e5e7eb")
        self.controller = controller

        wrapper = tk.Frame(self, bg="#e5e7eb")
        wrapper.pack(expand=True)

        title = tk.Label(
            wrapper, text="Selecciona un módulo",
            font=("Segoe UI", 18, "bold"), bg="#e5e7eb", fg="#0f172a"
        )
        title.grid(row=0, column=0, columnspan=3, pady=(10, 20))

        # Botones principales
        self.btn_store = tk.Button(
            wrapper, text="🛒 Tienda", width=18, height=3,
            font=("Segoe UI", 12, "bold"),
            bg="#2563eb", fg="white", relief="flat", cursor="hand2",
            command=lambda: controller.show_frame("StorePage")
        )
        self.btn_store.grid(row=1, column=0, padx=10, pady=10)

        self.btn_rest = tk.Button(
            wrapper, text="🍽️ Restaurante", width=18, height=3,
            font=("Segoe UI", 12, "bold"),
            bg="#059669", fg="white", relief="flat", cursor="hand2",
            command=lambda: controller.show_frame("RestaurantPage")
        )
        self.btn_rest.grid(row=1, column=1, padx=10, pady=10)

        self.btn_reports = tk.Button(
            wrapper, text="📊 Reportes", width=18, height=3,
            font=("Segoe UI", 12, "bold"),
            bg="#f59e0b", fg="white", relief="flat", cursor="hand2",
            command=lambda: controller.show_frame("ReportsPage")
        )
        self.btn_reports.grid(row=2, column=0, padx=10, pady=10)

        self.btn_inventory = tk.Button(
            wrapper, text="📦 Inventario", width=18, height=3,
            font=("Segoe UI", 12, "bold"),
            bg="#0ea5e9", fg="white", relief="flat", cursor="hand2",
            command=lambda: controller.show_frame("InventoryPage")
        )
        self.btn_inventory.grid(row=2, column=1, padx=10, pady=10)

        self.btn_admin = tk.Button(
            wrapper, text="⚙️ Configuración", width=18, height=3,
            font=("Segoe UI", 12, "bold"),
            bg="#64748b", fg="white", relief="flat", cursor="hand2",
            command=lambda: controller.show_frame("SettingsPage")
        )
        self.btn_admin.grid(row=3, column=0, padx=10, pady=10)

        self.btn_logout = tk.Button(
            wrapper, text="⎋ Cerrar sesión", width=18, height=3,
            font=("Segoe UI", 12, "bold"),
            bg="#ef4444", fg="white", relief="flat", cursor="hand2",
            command=controller.logout
        )
        self.btn_logout.grid(row=3, column=1, padx=10, pady=10)

        self.user_info = tk.Label(
            wrapper, text="", font=("Segoe UI", 11),
            bg="#e5e7eb", fg="#475569"
        )
        self.user_info.grid(row=4, column=0, columnspan=3, pady=(10, 0))

    def on_show(self):
        # Actualizar info y permisos por rol
        u = self.controller.current_user
        name = u[3] if u else ""
        role = (u[4] if u else "").lower()
        self.user_info.config(text=f"Sesión: {name} · Rol: {role}")

        # Reset: habilitar todo
        for b in (self.btn_store, self.btn_rest, self.btn_reports, self.btn_inventory, self.btn_admin):
            b.configure(state="normal")

        # Permisos por rol
        if role == "cajero":
            # Por requerimiento: cajero solo debe ver lo necesario.
            # En esta fase: solo Tienda. (Si quieres que algunos cajeros vayan a Restaurante,
            # luego añadimos un campo 'area' por usuario y lo habilitamos acá).
            self.btn_rest.configure(state="disabled")
            self.btn_reports.configure(state="disabled")
            self.btn_inventory.configure(state="disabled")
            self.btn_admin.configure(state="disabled")
        elif role == "gerente":
            # Gerente: todo menos configuración del sistema
            self.btn_admin.configure(state="disabled")
        elif role == "administrador":
            # Todo habilitado
            pass
        else:
            # Rol desconocido: permitir solo logout
            for b in (self.btn_store, self.btn_rest, self.btn_reports, self.btn_inventory, self.btn_admin):
                b.configure(state="disabled")


class ModernPOSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema POS - Restaurante & Tienda")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        self.configure(bg="#f3f4f6")

        # --- DB y sesión ---
        self.db = Database()
        self.current_user = None

        # --- Contenedor principal ---
        container = tk.Frame(self, bg="#f3f4f6")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.container = container

        # --- Registrar frames ---
        self.frames = {}
        for F in (ModernLoginPage, ModuleSelector, StorePage, RestaurantPage,
                  ReportsPage, InventoryPage, SettingsPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # --- Mostrar login al inicio ---
        self.show_frame("ModernLoginPage")

        # --- Bloqueo por inactividad ---
        self._inactivity_after_id = None
        self._bind_activity_events()
        self._schedule_inactivity_check()

    # -------- Navegación --------
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

    def login_success(self, user_row):
        self.current_user = user_row
        rol = user_row[4]   # campo 'rol'
        area = None
        try:
            area = user_row[6]  # campo 'area' (puede ser None)
        except IndexError:
            pass

        # Administrador → va a configuración general o selector
        if rol == "administrador":
            self.show_frame("SettingsPage")

        # Cajero → depende del área
        elif rol == "cajero":
            if area == "restaurante":
                self.show_frame("RestaurantPage")
            else:
                self.show_frame("StorePage")

        # Gerente → por ahora lo mandamos a tienda
        elif rol == "gerente":
            self.show_frame("StorePage")

        # Por defecto
        else:
            self.show_frame("StorePage")

    def logout(self):
        # Cerrar completamente la sesión
        self.current_user = None
        login_frame = self.frames.get("ModernLoginPage")
        if login_frame and hasattr(login_frame, "clear_inputs"):
            login_frame.clear_inputs()
        self.show_frame("ModernLoginPage")
        messagebox.showinfo("Sesión finalizada", "Has cerrado sesión correctamente.")

    def get_user_role(self):
        if not self.current_user:
            return None
        return (self.current_user[4] or "").lower()

    # -------- Inactividad --------
    def _bind_activity_events(self):
        events = ["<Any-KeyPress>", "<Any-Button>", "<Motion>"]
        for ev in events:
            self.bind_all(ev, self._on_user_activity, add="+")
        # Nota: no hacemos logout inmediato en foco-perdido; solo por tiempo.

    def _on_user_activity(self, event=None):
        # Reinicia el temporizador de inactividad
        self._schedule_inactivity_check()

    def _schedule_inactivity_check(self):
        if self._inactivity_after_id:
            self.after_cancel(self._inactivity_after_id)
        self._inactivity_after_id = self.after(INACTIVITY_TIMEOUT_MS, self._auto_logout)

    def _auto_logout(self):
        if self.current_user:
            messagebox.showwarning(
                "Sesión bloqueada",
                "Se cerró la sesión por inactividad."
            )
            self.logout()

    # -------- Utilidad --------
    def require_role(self, allowed_roles):
        """
        Úsalo desde páginas para validar permisos:
        if not controller.require_role({'gerente','administrador'}): return
        """
        role = self.get_user_role()
        if role not in {r.lower() for r in allowed_roles}:
            messagebox.showerror("Permiso denegado", "No tienes acceso a este módulo.")
            self.show_frame("ModuleSelector")
            return False
        return True


if __name__ == "__main__":
    app = ModernPOSApp()
    app.mainloop()