# main.py
# Point d'entrée principal pour l'application Sensorem
import customtkinter as ctk
from core.views.main_window import MainWindow

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    app = MainWindow()
    app.mainloop()