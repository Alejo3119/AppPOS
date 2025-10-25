# modules/login.py
import tkinter as tk
from tkinter import messagebox
import hashlib


class ModernLoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#06b6d4")
        self.controller = controller

        # Frame principal centrado
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_frame = tk.Frame(self, bg="#06b6d4")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Card de login
        card_frame = tk.Frame(main_frame, bg="#ffffff", relief="raised", bd=1)
        card_frame.grid(row=0, column=0, padx=20, pady=20)
        card_frame.grid_rowconfigure(4, weight=1)

        logo_frame = tk.Frame(card_frame, bg="#ffffff")
        logo_frame.grid(row=0, column=0, padx=30, pady=(30, 20))

        logo_icon = tk.Label(logo_frame, text="💰", font=("Segoe UI", 32), bg="#ffffff")
        logo_icon.grid(row=0, column=0, pady=(0, 10))

        title_label = tk.Label(logo_frame, text="Sistema POS", font=("Segoe UI", 20, "bold"),
                               bg="#ffffff", fg="#1e293b")
        title_label.grid(row=1, column=0)
        subtitle_label = tk.Label(logo_frame, text="Restaurante & Tienda",
                                  font=("Segoe UI", 11), bg="#ffffff", fg="#64748b")
        subtitle_label.grid(row=2, column=0, pady=(0, 20))

        form_frame = tk.Frame(card_frame, bg="#ffffff")
        form_frame.grid(row=1, column=0, padx=30, pady=(0, 20))

        tk.Label(form_frame, text="👤 Usuario", bg="#ffffff",
                 font=("Segoe UI", 10), anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.user_entry = tk.Entry(form_frame, font=("Segoe UI", 11), bg="#f8fafc",
                                   relief="flat", width=25)
        self.user_entry.grid(row=1, column=0, pady=(0, 15))

        tk.Label(form_frame, text="🔒 Contraseña", bg="#ffffff",
                 font=("Segoe UI", 10), anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.pass_entry = tk.Entry(form_frame, font=("Segoe UI", 11), show="*",
                                   bg="#f8fafc", relief="flat", width=25)
        self.pass_entry.grid(row=3, column=0, pady=(0, 20))

        login_btn = tk.Button(form_frame, text="Ingresar →", font=("Segoe UI", 11, "bold"),
                              bg="#2563eb", fg="white", relief="flat", cursor="hand2",
                              command=self.check_login, width=20, height=2)
        login_btn.grid(row=4, column=0, pady=(0, 20))

        footer_frame = tk.Frame(card_frame, bg="#ffffff")
        footer_frame.grid(row=2, column=0, padx=30, pady=(0, 20))
        tk.Label(footer_frame, text="© 2024 Sistema POS - Desarrollado para SENA",
                 font=("Segoe UI", 9), bg="#ffffff", fg="#94a3b8").pack()

        self.pass_entry.bind("<Return>", lambda e: self.check_login())

    def clear_inputs(self):
        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)

    def check_login(self):
        user = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        if not user or not pwd:
            messagebox.showerror("Error", "Complete usuario y contraseña.")
            return

        c = self.controller.db.conn.cursor()
        # Primero obtenemos la contraseña almacenada (si existe y está activo)
        c.execute("SELECT password FROM usuarios WHERE username=? AND activo=1", (user,))
        res = c.fetchone()
        if not res:
            messagebox.showerror("Acceso denegado", "Usuario no encontrado o inactivo.")
            return

        stored = str(res[0])  # contraseña en BD (puede ser texto plano o SHA256)

        # Comparamos: aceptamos si coincide el texto plano o el hash SHA256
        hashed = hashlib.sha256(pwd.encode()).hexdigest()
        if stored == pwd or stored == hashed:
            # recuperar fila completa y pasarla al controlador
            c.execute("SELECT * FROM usuarios WHERE username=? AND activo=1", (user,))
            row = c.fetchone()
            if row:
                self.controller.login_success(row)
                self.clear_inputs()
                return

        # Si llega acá, la contraseña no coincide
        messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
