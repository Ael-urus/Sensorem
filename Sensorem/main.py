# main.py
import customtkinter as ctk
import config
from core.views.main_window import MainWindow
from core.controllers.main_controller import MainController
from core.models.data_model import DataModel

if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    model = DataModel()
    controller = MainController(model, base_dir=config.CSV_DIR)
    app = MainWindow(controller)
    model.set_controller(controller)
    app.mainloop()