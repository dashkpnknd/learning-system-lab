import os
import sys
import subprocess
import webbrowser
from tkinter import messagebox


def open_file_external(path):
    try:
        if not os.path.exists(path):
            messagebox.showerror("Ошибка", f"Файл не найден:\n{path}")
            return

        ext = os.path.splitext(path)[1].lower()

        if os.name == 'nt':
            os.startfile(path)
        elif sys.platform == 'darwin':
            if ext == ".mp3":
                subprocess.Popen(["open", "-a", "QuickTime Player", path])
            else:
                subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")


def open_video(video_path):
    try:
        if not video_path:
            messagebox.showerror("Ошибка", "Ссылка или путь к видео не указан")
            return

        if video_path.startswith("http://") or video_path.startswith("https://"):
            webbrowser.open(video_path)
        else:
            full_path = os.path.abspath(video_path)
            webbrowser.open(f"file://{full_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть видео:\n{e}")