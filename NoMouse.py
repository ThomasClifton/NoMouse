from gesture_processor import GestureProcessor
from app_ui import Application
from config_manager import load_config


def run_app():
    config_data = load_config()
    processor = GestureProcessor()
    app = Application(processor)
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()


if __name__ == "__main__":
    run_app()