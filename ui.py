import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import hashlib
import sqlite3
from PIL import Image, ImageTk, ImageSequence
from media_utils import open_file_external, open_video


class UIManager:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.db = app.db

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_frame(self):
        self.clear_frame()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Обучающая система по ИТ", font=("Arial", 20, "bold"))
        title_label.pack(pady=20)

        login_frame = ttk.LabelFrame(main_frame, text="Вход в систему", padding="15")
        login_frame.pack(pady=20)

        ttk.Label(login_frame, text="Имя пользователя:").grid(row=0, column=0, sticky=tk.W, pady=5)
        username_entry = ttk.Entry(login_frame, width=30)
        username_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(login_frame, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=5)
        password_entry = ttk.Entry(login_frame, width=30, show="*")
        password_entry.grid(row=1, column=1, pady=5, padx=5)

        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="Войти",
                   command=lambda: self.login(username_entry.get(), password_entry.get())).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Регистрация",
                   command=self.show_register_frame).pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack()

        password_entry.bind('<Return>', lambda e: self.login(username_entry.get(), password_entry.get()))

    def login(self, username, password):
        if not username or not password:
            self.status_label.config(text="Заполните все поля")
            return

        user = self.db.get_user_by_credentials(username, self.hash_password(password))

        if user:
            self.app.current_user = {
                'id': user[0],
                'username': user[1],
                'first_name': user[3],
                'last_name': user[4],
                'user_type': user[5]
            }
            self.show_main_menu()
        else:
            self.status_label.config(text="Неверное имя пользователя или пароль")

    def show_register_frame(self):
        self.clear_frame()

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Регистрация нового пользователя", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        register_frame = ttk.LabelFrame(main_frame, text="Данные пользователя", padding="15")
        register_frame.pack(pady=20)

        fields = [
            ("Имя пользователя:", "username_entry"),
            ("Пароль:", "password_entry", "*"),
            ("Подтверждение пароля:", "confirm_entry", "*"),
            ("Имя:", "first_name_entry"),
            ("Фамилия:", "last_name_entry")
        ]

        entries = {}
        for i, (label, name, *args) in enumerate(fields):
            ttk.Label(register_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            show_char = args[0] if args else ""
            entry = ttk.Entry(register_frame, width=30, show=show_char)
            entry.grid(row=i, column=1, pady=5, padx=5)
            entries[name] = entry

        button_frame = ttk.Frame(register_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="Зарегистрироваться",
                   command=lambda: self.register(entries)).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Назад",
                   command=self.show_login_frame).pack(side=tk.LEFT, padx=5)

        self.reg_status_label = ttk.Label(main_frame, text="", foreground="red")
        self.reg_status_label.pack()

    def register(self, entries):
        username = entries["username_entry"].get()
        password = entries["password_entry"].get()
        confirm = entries["confirm_entry"].get()
        first_name = entries["first_name_entry"].get()
        last_name = entries["last_name_entry"].get()

        if not all([username, password, confirm, first_name, last_name]):
            self.reg_status_label.config(text="Заполните все поля")
            return

        if password != confirm:
            self.reg_status_label.config(text="Пароли не совпадают")
            return

        try:
            self.db.add_user(username, self.hash_password(password), first_name, last_name)
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            self.show_login_frame()
        except sqlite3.IntegrityError:
            self.reg_status_label.config(text="Пользователь с таким именем уже существует")

    def show_main_menu(self):
        self.clear_frame()

        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        user_info = f"Пользователь: {self.app.current_user['first_name']} {self.app.current_user['last_name']} ({self.app.current_user['user_type']})"
        ttk.Label(top_frame, text=user_info, font=("Arial", 10)).pack(side=tk.LEFT)

        ttk.Button(top_frame, text="Выход", command=self.show_login_frame).pack(side=tk.RIGHT)

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Главное меню", font=("Arial", 18, "bold"))
        title_label.pack(pady=20)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(expand=True)

        ttk.Button(button_frame, text="📚 Изучение теории",
                   command=self.show_theory_module, width=30).pack(pady=10)

        ttk.Button(button_frame, text="✍️ Проверь себя",
                   command=self.show_test_module, width=30).pack(pady=10)

        if self.app.current_user['user_type'] == 'teacher':
            ttk.Button(button_frame, text="⚙️ Панель преподавателя",
                       command=self.show_teacher_panel, width=30).pack(pady=10)

    def show_theory_module(self):
        self.clear_frame()

        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame, text="← На главную", command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(top_frame, text="Модуль: Изучение теории", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=20)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame, width=220)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        left_frame.pack_propagate(False)

        ttk.Label(left_frame, text="Темы:", font=("Arial", 10, "bold")).pack(anchor=tk.W)

        topics_listbox = tk.Listbox(left_frame, height=20, font=("Arial", 10))
        topics_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)

        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def resize_scrollable_frame(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_scrollable_frame)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        include_hidden = self.app.current_user['user_type'] != 'student'
        topics = self.db.get_topics(include_hidden=include_hidden)

        topics_dict = {}
        for topic in topics:
            topics_listbox.insert(tk.END, topic[1])
            topics_dict[topic[1]] = topic[0]

        self.app.current_gif_job = None

        def stop_animation():
            if self.app.current_gif_job is not None:
                try:
                    self.root.after_cancel(self.app.current_gif_job)
                except Exception:
                    pass
                self.app.current_gif_job = None

        def display_topic(topic_id):
            stop_animation()

            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            topic_data = self.db.get_topic_by_id(topic_id)

            if topic_data:
                title_label = ttk.Label(scrollable_frame, text=topic_data[1], font=("Arial", 16, "bold"))
                title_label.pack(pady=10)

                text_frame = ttk.LabelFrame(scrollable_frame, text="Теоретический материал", padding="10")
                text_frame.pack(fill=tk.X, pady=5, padx=5)

                theory_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=15, font=("Arial", 10))
                theory_text.pack(fill=tk.X)
                theory_text.insert(1.0, topic_data[2])
                theory_text.config(state=tk.DISABLED)

                if topic_data[3]:
                    img_frame = ttk.LabelFrame(scrollable_frame, text="Рисунок", padding="10")
                    img_frame.pack(fill=tk.X, pady=5, padx=5)

                    if os.path.exists(topic_data[3]):
                        try:
                            img = Image.open(topic_data[3])
                            img.thumbnail((700, 400), Image.Resampling.LANCZOS)
                            photo = ImageTk.PhotoImage(img)

                            img_label = ttk.Label(img_frame, image=photo)
                            img_label.image = photo
                            img_label.pack()
                        except Exception as e:
                            ttk.Label(img_frame, text=f"Ошибка загрузки изображения:\n{e}").pack()
                    else:
                        ttk.Label(img_frame, text=f"Файл изображения не найден:\n{topic_data[3]}").pack()

                if topic_data[4]:
                    video_frame = ttk.LabelFrame(scrollable_frame, text="Видеоматериал", padding="10")
                    video_frame.pack(fill=tk.X, pady=5, padx=5)

                    ttk.Label(video_frame, text="Учебное видео:", font=("Arial", 9, "bold")).pack()

                    video_display = ttk.Frame(video_frame)
                    video_display.pack(fill=tk.X, pady=5)

                    ttk.Label(video_display, text="🎥 Видео доступно для просмотра", font=("Arial", 10)).pack()

                    ttk.Button(video_display, text="Открыть видео",
                               command=lambda path=topic_data[4]: open_video(path)).pack(pady=5)

                if topic_data[5]:
                    anim_frame = ttk.LabelFrame(scrollable_frame, text="Анимация", padding="10")
                    anim_frame.pack(fill=tk.X, pady=5, padx=5)

                    if os.path.exists(topic_data[5]):
                        try:
                            gif = Image.open(topic_data[5])

                            frames = []
                            for frame in ImageSequence.Iterator(gif):
                                frame_copy = frame.copy().convert("RGBA")
                                frame_copy.thumbnail((700, 400), Image.Resampling.LANCZOS)
                                frames.append(ImageTk.PhotoImage(frame_copy))

                            if frames:
                                gif_label = ttk.Label(anim_frame)
                                gif_label.pack()

                                def animate(index=0):
                                    gif_label.configure(image=frames[index])
                                    gif_label.image = frames[index]
                                    next_index = (index + 1) % len(frames)
                                    self.app.current_gif_job = self.root.after(150, lambda: animate(next_index))

                                animate(0)
                            else:
                                ttk.Label(anim_frame, text="Не удалось прочитать кадры GIF").pack()
                        except Exception:
                            ttk.Label(
                                anim_frame,
                                text=f"Анимация: {os.path.basename(topic_data[5])}\nНе удалось встроить GIF, можно открыть отдельно."
                            ).pack()
                            ttk.Button(anim_frame, text="Открыть анимацию",
                                       command=lambda path=topic_data[5]: open_file_external(path)).pack(pady=5)
                    else:
                        ttk.Label(anim_frame, text=f"Файл анимации не найден:\n{topic_data[5]}").pack()

                if topic_data[6]:
                    audio_frame = ttk.LabelFrame(scrollable_frame, text="Аудиоматериал", padding="10")
                    audio_frame.pack(fill=tk.X, pady=5, padx=5)

                    if os.path.exists(topic_data[6]):
                        ttk.Label(audio_frame, text="🎵 Аудиолекция:", font=("Arial", 9, "bold")).pack()

                        audio_player_frame = ttk.Frame(audio_frame)
                        audio_player_frame.pack(fill=tk.X, pady=5)

                        ttk.Button(audio_player_frame, text="▶ Воспроизвести",
                                   command=lambda path=topic_data[6]: open_file_external(path)).pack(side=tk.LEFT, padx=5)

                        ttk.Label(audio_player_frame,
                                  text=f"Файл: {os.path.basename(topic_data[6])}").pack(side=tk.LEFT, padx=10)
                    else:
                        ttk.Label(audio_frame, text=f"Файл аудио не найден:\n{topic_data[6]}").pack()

        def on_topic_select(event):
            selection = topics_listbox.curselection()
            if selection:
                topic_title = topics_listbox.get(selection[0])
                topic_id = topics_dict[topic_title]
                display_topic(topic_id)

        topics_listbox.bind('<<ListboxSelect>>', on_topic_select)

        if topics:
            topics_listbox.selection_set(0)
            display_topic(topics[0][0])
        else:
            ttk.Label(scrollable_frame, text="Нет доступных тем. Обратитесь к преподавателю.").pack()

    def show_test_module(self):
        self.clear_frame()

        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame, text="← На главную", command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(top_frame, text="Модуль: Проверь себя", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=20)

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        select_frame = ttk.LabelFrame(main_frame, text="Выберите тему для тестирования", padding="10")
        select_frame.pack(fill=tk.X, pady=10)

        include_hidden = self.app.current_user['user_type'] != 'student'
        topics = self.db.get_topics(include_hidden=include_hidden)

        if not topics:
            ttk.Label(select_frame, text="Нет доступных тем для тестирования").pack(pady=10)
            return

        self.app.selected_topic = tk.StringVar()
        topic_combo = ttk.Combobox(
            select_frame,
            textvariable=self.app.selected_topic,
            values=[topic[1] for topic in topics],
            width=40
        )
        topic_combo.pack(pady=5)
        topic_combo.set("Выберите тему")

        ttk.Button(select_frame, text="Начать тестирование",
                   command=lambda: self.start_test(topics)).pack(pady=10)

        if self.app.current_user['user_type'] == 'student':
            results_frame = ttk.LabelFrame(main_frame, text="Мои результаты", padding="10")
            results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            self.show_student_results(results_frame)

    def start_test(self, topics):
        selected_title = self.app.selected_topic.get()
        if selected_title == "Выберите тему" or not selected_title:
            messagebox.showwarning("Предупреждение", "Выберите тему для тестирования")
            return

        topic_id = None
        for topic in topics:
            if topic[1] == selected_title:
                topic_id = topic[0]
                break

        if topic_id:
            self.app.current_test = topic_id
            self.show_test_questions(topic_id)

    def show_test_questions(self, topic_id):
        self.clear_frame()

        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame, text="← Назад к выбору темы", command=self.show_test_module).pack(side=tk.LEFT)
        ttk.Label(top_frame, text="Тестирование", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=20)

        questions = self.db.get_questions_by_topic(topic_id)

        if not questions:
            messagebox.showinfo("Информация", "Для этой темы нет вопросов")
            self.show_test_module()
            return

        selected_questions = random.sample(questions, min(3, len(questions)))

        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def resize_scrollable(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_scrollable)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.app.test_answers = []
        self.app.answer_vars = []

        for i, q in enumerate(selected_questions, 1):
            q_id, q_text, q_type, options, correct, points = q
            points = points if points else 1

            q_frame = ttk.LabelFrame(scrollable_frame, text=f"Вопрос {i} (баллов: {points})", padding="10")
            q_frame.pack(fill=tk.X, pady=10, padx=10)

            ttk.Label(q_frame, text=q_text, wraplength=800, font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)

            answer_var = None
            answer_frame = ttk.Frame(q_frame)
            answer_frame.pack(fill=tk.X, pady=5)

            if q_type == "text":
                answer_var = tk.StringVar()
                entry = ttk.Entry(answer_frame, textvariable=answer_var, width=50)
                entry.pack(anchor=tk.W)

            elif q_type == "multiple":
                answer_var = tk.StringVar()
                options_list = options.split(';')
                for opt in options_list:
                    ttk.Radiobutton(answer_frame, text=opt, variable=answer_var, value=opt).pack(anchor=tk.W)

            elif q_type == "match":
                answer_var = {}
                parts = options.split('|')
                if len(parts) == 2:
                    left_items = parts[0].split(';')
                    right_items = parts[1].split(';')

                    match_frame = ttk.Frame(answer_frame)
                    match_frame.pack()

                    for j, left in enumerate(left_items):
                        ttk.Label(match_frame, text=left + ":").grid(row=j, column=0, sticky=tk.W, pady=2)
                        combo = ttk.Combobox(match_frame, values=right_items, width=30)
                        combo.grid(row=j, column=1, padx=10, pady=2)
                        answer_var[left] = combo

            self.app.answer_vars.append((q_id, q_type, answer_var, correct, points))

        submit_frame = ttk.Frame(scrollable_frame)
        submit_frame.pack(pady=20)

        ttk.Button(submit_frame, text="Завершить тест и проверить ответы",
                   command=self.check_test_results).pack()

    def check_test_results(self):
        total_score = 0
        max_score = 0
        results = []

        for q_id, q_type, answer_var, correct, points in self.app.answer_vars:
            max_score += points
            is_correct = False

            if q_type == "text":
                user_answer = answer_var.get().strip()
                is_correct = user_answer.lower() == correct.lower()

            elif q_type == "multiple":
                user_answer = answer_var.get()
                is_correct = user_answer == correct

            elif q_type == "match":
                user_answer = {}
                correct_dict = {}
                for match in correct.split(';'):
                    key, val = match.split('-')
                    correct_dict[key.strip()] = val.strip()

                all_correct = True
                for key, combo in answer_var.items():
                    user_answer[key] = combo.get()
                    if combo.get() != correct_dict.get(key, ""):
                        all_correct = False

                is_correct = all_correct

            if is_correct:
                total_score += points
                results.append(f"✓ Вопрос {q_id}: верно (+{points} баллов)")
            else:
                results.append(f"✗ Вопрос {q_id}: неверно (0 баллов)")
                explanation = self.db.get_question_explanation(q_id)
                if explanation:
                    results.append(f"  Пояснение: {explanation[0]}")
            results.append("")

        results_text = "\n".join(results)
        self.db.save_test_result(
            self.app.current_user['id'],
            self.app.current_test,
            total_score,
            max_score,
            results_text
        )

        result_text = f"Ваш результат: {total_score} из {max_score} баллов\n\n{results_text}"
        messagebox.showinfo("Результаты тестирования", result_text)
        self.show_test_module()

    def show_student_results(self, parent_frame):
        results = self.db.get_student_results(self.app.current_user['id'])

        if results:
            columns = ("Дата", "Тема", "Результат")
            tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=5)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=180)

            tree.pack(fill=tk.X, pady=5)

            for result in results:
                topic_title = self.db.get_topic_title(result[3])
                tree.insert("", tk.END, values=(result[0], topic_title, f"{result[1]}/{result[2]}"))
        else:
            ttk.Label(parent_frame, text="Нет результатов тестирования").pack()

    def show_teacher_panel(self):
        self.clear_frame()

        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame, text="← На главную", command=self.show_main_menu).pack(side=tk.LEFT)
        ttk.Label(top_frame, text="Панель преподавателя", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=20)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        topics_frame = ttk.Frame(notebook)
        notebook.add(topics_frame, text="Управление темами")
        self.teacher_topics_panel(topics_frame)

        questions_frame = ttk.Frame(notebook)
        notebook.add(questions_frame, text="Управление вопросами")
        self.teacher_questions_panel(questions_frame)

        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Результаты студентов")
        self.teacher_results_panel(results_frame)

    def teacher_topics_panel(self, parent):
        form_frame = ttk.LabelFrame(parent, text="Добавить/Редактировать тему", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(form_frame, text="Название темы:").grid(row=0, column=0, sticky=tk.W, pady=5)
        title_entry = ttk.Entry(form_frame, width=50)
        title_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Содержание:").grid(row=1, column=0, sticky=tk.W, pady=5)
        content_text = scrolledtext.ScrolledText(form_frame, width=60, height=10)
        content_text.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Путь к рисунку:").grid(row=2, column=0, sticky=tk.W, pady=5)
        image_entry = ttk.Entry(form_frame, width=50)
        image_entry.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Ссылка/путь к видео:").grid(row=3, column=0, sticky=tk.W, pady=5)
        video_entry = ttk.Entry(form_frame, width=50)
        video_entry.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Путь к анимации (GIF):").grid(row=4, column=0, sticky=tk.W, pady=5)
        anim_entry = ttk.Entry(form_frame, width=50)
        anim_entry.grid(row=4, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Путь к аудио (MP3):").grid(row=5, column=0, sticky=tk.W, pady=5)
        audio_entry = ttk.Entry(form_frame, width=50)
        audio_entry.grid(row=5, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Скрыть от студентов:").grid(row=6, column=0, sticky=tk.W, pady=5)
        is_hidden_var = tk.BooleanVar()
        ttk.Checkbutton(form_frame, text="Скрыть тему", variable=is_hidden_var).grid(row=6, column=1, sticky=tk.W)

        list_frame = ttk.LabelFrame(parent, text="Существующие темы", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("ID", "Название", "Скрыта")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=180)

        tree.pack(fill=tk.BOTH, expand=True)

        def load_topics():
            for item in tree.get_children():
                tree.delete(item)

            for topic in self.db.get_all_topics_for_teacher():
                hidden_status = "Да" if topic[2] else "Нет"
                tree.insert("", tk.END, values=(topic[0], topic[1], hidden_status))

        load_topics()

        button_frame = ttk.Frame(list_frame)
        button_frame.pack(pady=10)

        def add_topic():
            title = title_entry.get()
            content = content_text.get(1.0, tk.END).strip()
            is_hidden = 1 if is_hidden_var.get() else 0

            if not title or not content:
                messagebox.showwarning("Предупреждение", "Заполните название и содержание")
                return

            self.db.add_topic(
                title, content, image_entry.get(), video_entry.get(),
                anim_entry.get(), audio_entry.get(), is_hidden, self.app.current_user['id']
            )
            messagebox.showinfo("Успех", "Тема добавлена")
            load_topics()

            title_entry.delete(0, tk.END)
            content_text.delete(1.0, tk.END)
            image_entry.delete(0, tk.END)
            video_entry.delete(0, tk.END)
            anim_entry.delete(0, tk.END)
            audio_entry.delete(0, tk.END)
            is_hidden_var.set(False)

        def edit_topic():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Предупреждение", "Выберите тему для редактирования")
                return

            item = tree.item(selected[0])
            topic_id = item['values'][0]
            title = title_entry.get()
            content = content_text.get(1.0, tk.END).strip()
            is_hidden = 1 if is_hidden_var.get() else 0

            if not title or not content:
                messagebox.showwarning("Предупреждение", "Заполните название и содержание")
                return

            self.db.update_topic(
                topic_id, title, content, image_entry.get(), video_entry.get(),
                anim_entry.get(), audio_entry.get(), is_hidden
            )
            messagebox.showinfo("Успех", "Тема обновлена")
            load_topics()

        def delete_topic():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Предупреждение", "Выберите тему для удаления")
                return

            if messagebox.askyesno("Подтверждение", "Удалить тему? Все вопросы по этой теме также будут удалены."):
                item = tree.item(selected[0])
                topic_id = item['values'][0]
                self.db.delete_topic(topic_id)
                messagebox.showinfo("Успех", "Тема удалена")
                load_topics()

        def on_tree_select(event):
            selected = tree.selection()
            if selected:
                item = tree.item(selected[0])
                topic_id = item['values'][0]
                topic = self.db.get_topic_full_by_id(topic_id)

                if topic:
                    title_entry.delete(0, tk.END)
                    title_entry.insert(0, topic[0])

                    content_text.delete(1.0, tk.END)
                    content_text.insert(1.0, topic[1])

                    image_entry.delete(0, tk.END)
                    image_entry.insert(0, topic[2] if topic[2] else "")

                    video_entry.delete(0, tk.END)
                    video_entry.insert(0, topic[3] if topic[3] else "")

                    anim_entry.delete(0, tk.END)
                    anim_entry.insert(0, topic[4] if topic[4] else "")

                    audio_entry.delete(0, tk.END)
                    audio_entry.insert(0, topic[5] if topic[5] else "")

                    is_hidden_var.set(bool(topic[6]))

        tree.bind('<<TreeviewSelect>>', on_tree_select)

        ttk.Button(button_frame, text="Добавить", command=add_topic).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=edit_topic).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=delete_topic).pack(side=tk.LEFT, padx=5)

    def teacher_questions_panel(self, parent):
        topic_frame = ttk.LabelFrame(parent, text="Выберите тему", padding="10")
        topic_frame.pack(fill=tk.X, padx=10, pady=10)

        topics = self.db.get_topics(include_hidden=True)
        topic_combo = ttk.Combobox(topic_frame, values=[topic[1] for topic in topics], width=40, state="readonly")
        topic_combo.pack()

        form_frame = ttk.LabelFrame(parent, text="Добавить / Редактировать вопрос", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(form_frame, text="Тип вопроса:").grid(row=0, column=0, sticky=tk.W, pady=5)
        q_type_var = tk.StringVar(value="text")
        q_type_combo = ttk.Combobox(form_frame, textvariable=q_type_var, values=["text", "multiple", "match"], width=20, state="readonly")
        q_type_combo.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)

        ttk.Label(form_frame, text="Текст вопроса:").grid(row=1, column=0, sticky=tk.W, pady=5)
        q_text = scrolledtext.ScrolledText(form_frame, width=60, height=4)
        q_text.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)

        ttk.Label(form_frame, text="Варианты ответов (через ;):").grid(row=2, column=0, sticky=tk.W, pady=5)
        options_entry = ttk.Entry(form_frame, width=60)
        options_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)

        ttk.Label(form_frame, text="Правильный ответ:").grid(row=3, column=0, sticky=tk.W, pady=5)
        correct_entry = ttk.Entry(form_frame, width=60)
        correct_entry.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)

        ttk.Label(form_frame, text="Пояснение:").grid(row=4, column=0, sticky=tk.W, pady=5)
        explanation_text = scrolledtext.ScrolledText(form_frame, width=60, height=3)
        explanation_text.grid(row=4, column=1, pady=5, padx=5, sticky=tk.W)

        ttk.Label(form_frame, text="Баллы:").grid(row=5, column=0, sticky=tk.W, pady=5)
        points_entry = ttk.Entry(form_frame, width=20)
        points_entry.grid(row=5, column=1, pady=5, padx=5, sticky=tk.W)
        points_entry.insert(0, "1")

        selected_question_id = tk.StringVar(value="")

        def clear_form():
            selected_question_id.set("")
            q_type_var.set("text")

            q_text.delete(1.0, tk.END)
            options_entry.delete(0, tk.END)
            correct_entry.delete(0, tk.END)
            explanation_text.delete(1.0, tk.END)

            points_entry.delete(0, tk.END)
            points_entry.insert(0, "1")

        def get_selected_topic_id():
            topic_title = topic_combo.get()
            if not topic_title:
                return None

            for topic in topics:
                if topic[1] == topic_title:
                    return topic[0]
            return None

        def load_questions():
            for item in questions_tree.get_children():
                questions_tree.delete(item)

            topic_id = get_selected_topic_id()
            if topic_id is None:
                return

            questions = self.db.get_questions_short_by_topic(topic_id)
            for q in questions:
                questions_tree.insert("", tk.END, values=(q[0], q[1], q[2][:80], q[3]))

        def add_question():
            topic_id = get_selected_topic_id()
            if topic_id is None:
                messagebox.showwarning("Предупреждение", "Выберите тему")
                return

            q_type = q_type_var.get()
            question_text = q_text.get(1.0, tk.END).strip()
            options = options_entry.get().strip()
            correct = correct_entry.get().strip()
            explanation = explanation_text.get(1.0, tk.END).strip()

            try:
                points = int(points_entry.get()) if points_entry.get() else 1
            except ValueError:
                messagebox.showwarning("Предупреждение", "Баллы должны быть числом")
                return

            if not question_text or not correct:
                messagebox.showwarning("Предупреждение", "Заполните текст вопроса и правильный ответ")
                return

            self.db.add_question(
                topic_id, question_text, q_type, options, correct,
                explanation, points, self.app.current_user['id']
            )
            messagebox.showinfo("Успех", "Вопрос добавлен")
            clear_form()
            load_questions()

        def edit_question():
            q_id = selected_question_id.get()
            if not q_id:
                messagebox.showwarning("Предупреждение", "Выберите вопрос для редактирования")
                return

            q_type = q_type_var.get()
            question_text = q_text.get(1.0, tk.END).strip()
            options = options_entry.get().strip()
            correct = correct_entry.get().strip()
            explanation = explanation_text.get(1.0, tk.END).strip()

            try:
                points = int(points_entry.get()) if points_entry.get() else 1
            except ValueError:
                messagebox.showwarning("Предупреждение", "Баллы должны быть числом")
                return

            if not question_text or not correct:
                messagebox.showwarning("Предупреждение", "Заполните текст вопроса и правильный ответ")
                return

            self.db.update_question(
                int(q_id), question_text, q_type, options, correct, explanation, points
            )
            messagebox.showinfo("Успех", "Вопрос обновлен")
            clear_form()
            load_questions()

        def delete_question():
            selected = questions_tree.selection()
            if not selected:
                messagebox.showwarning("Предупреждение", "Выберите вопрос для удаления")
                return

            if messagebox.askyesno("Подтверждение", "Удалить вопрос?"):
                item = questions_tree.item(selected[0])
                q_id = item['values'][0]
                self.db.delete_question(q_id)
                clear_form()
                load_questions()
                messagebox.showinfo("Успех", "Вопрос удален")

        def on_question_select(event):
            selected = questions_tree.selection()
            if not selected:
                return

            item = questions_tree.item(selected[0])
            q_id = item['values'][0]
            question = self.db.get_question_by_id(q_id)

            if question:
                selected_question_id.set(str(question[0]))

                q_text.delete(1.0, tk.END)
                q_text.insert(1.0, question[2])

                q_type_var.set(question[3] if question[3] else "text")

                options_entry.delete(0, tk.END)
                options_entry.insert(0, question[4] if question[4] else "")

                correct_entry.delete(0, tk.END)
                correct_entry.insert(0, question[5] if question[5] else "")

                explanation_text.delete(1.0, tk.END)
                explanation_text.insert(1.0, question[6] if question[6] else "")

                points_entry.delete(0, tk.END)
                points_entry.insert(0, str(question[7] if question[7] else 1))

        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=10)

        ttk.Button(buttons_frame, text="Добавить вопрос", command=add_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Редактировать вопрос", command=edit_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Очистить форму", command=clear_form).pack(side=tk.LEFT, padx=5)

        list_frame = ttk.LabelFrame(parent, text="Существующие вопросы", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        questions_tree = ttk.Treeview(
            list_frame,
            columns=("ID", "Тип", "Вопрос", "Баллы"),
            show="headings",
            height=10
        )
        questions_tree.heading("ID", text="ID")
        questions_tree.heading("Тип", text="Тип")
        questions_tree.heading("Вопрос", text="Вопрос")
        questions_tree.heading("Баллы", text="Баллы")

        questions_tree.column("ID", width=60, anchor=tk.CENTER)
        questions_tree.column("Тип", width=120, anchor=tk.CENTER)
        questions_tree.column("Вопрос", width=700, anchor=tk.W)
        questions_tree.column("Баллы", width=100, anchor=tk.CENTER)

        questions_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        list_buttons_frame = ttk.Frame(list_frame)
        list_buttons_frame.pack(fill=tk.X)

        ttk.Button(list_buttons_frame, text="Обновить список", command=load_questions).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_buttons_frame, text="Удалить вопрос", command=delete_question).pack(side=tk.LEFT, padx=5)

        topic_combo.bind('<<ComboboxSelected>>', lambda e: (clear_form(), load_questions()))
        questions_tree.bind('<<TreeviewSelect>>', on_question_select)

        if topics:
            topic_combo.current(0)
            load_questions()

    def teacher_results_panel(self, parent):
        student_frame = ttk.LabelFrame(parent, text="Выберите студента", padding="10")
        student_frame.pack(fill=tk.X, padx=10, pady=10)

        students = self.db.get_students()
        student_names = [f"{s[1]} {s[2]}" for s in students]

        selected_student = tk.StringVar()
        student_combo = ttk.Combobox(student_frame, textvariable=selected_student, values=student_names, width=40)
        student_combo.pack()

        results_frame = ttk.LabelFrame(parent, text="Результаты тестирования", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ("Дата", "Тема", "Результат")
        results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)

        for col in columns:
            results_tree.heading(col, text=col)
            results_tree.column(col, width=180)

        results_tree.pack(fill=tk.BOTH, expand=True)

        details_frame = ttk.LabelFrame(results_frame, text="Детали ответов", padding="10")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        details_text = scrolledtext.ScrolledText(details_frame, height=10, wrap=tk.WORD)
        details_text.pack(fill=tk.BOTH, expand=True)

        def load_results():
            for item in results_tree.get_children():
                results_tree.delete(item)

            selected_name = selected_student.get()
            if selected_name:
                student_id = None
                for student in students:
                    if f"{student[1]} {student[2]}" == selected_name:
                        student_id = student[0]
                        break

                if student_id:
                    for result in self.db.get_results_for_student(student_id):
                        topic_title = self.db.get_topic_title(result[3])
                        results_tree.insert(
                            "",
                            tk.END,
                            values=(result[0], topic_title, f"{result[1]}/{result[2]}"),
                            tags=(result[4],)
                        )

        def show_details(event):
            selected = results_tree.selection()
            if selected:
                item = results_tree.item(selected[0])
                details = item.get('tags', [''])[0]
                details_text.delete(1.0, tk.END)
                details_text.insert(1.0, details)

        results_tree.bind('<<TreeviewSelect>>', show_details)
        student_combo.bind('<<ComboboxSelected>>', lambda e: load_results())