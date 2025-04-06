# main.py
from core.gui.main_window import MainWindow
from core.utils.logger import LogManager

log_manager = LogManager()

def main():
    app = MainWindow(log_manager)
    app.geometry("1280x720")
    app.mainloop()

if __name__ == "__main__":
    main()