import tkinter as tk
from database import DatabaseManager
from ui import UIManager


class LearningSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Обучающая система по информационным технологиям")
        self.root.geometry("1200x800")

        self.db = DatabaseManager("learning_system.db")
        self.db.init_db()

        self.current_user = None
        self.current_test = None
        self.test_answers = []
        self.answer_vars = []
        self.current_gif_job = None
        self.selected_topic = None

        self.ui = UIManager(self)
        self.ui.show_login_frame()

    def __del__(self):
        if hasattr(self, "db"):
            self.db.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = LearningSystem(root)
    root.mainloop()