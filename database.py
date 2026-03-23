import sqlite3
from datetime import datetime
from sample_data import insert_sample_data


class DatabaseManager:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def init_db(self):
        self.create_tables()
        self.ensure_default_teacher()
        self.ensure_sample_data()
        self.conn.commit()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                first_name TEXT,
                last_name TEXT,
                user_type TEXT DEFAULT 'student',
                last_test_date TEXT,
                total_score INTEGER DEFAULT 0
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                image_path TEXT,
                video_url TEXT,
                animation_path TEXT,
                audio_path TEXT,
                is_hidden INTEGER DEFAULT 0,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER,
                question_text TEXT,
                question_type TEXT,
                options TEXT,
                correct_answer TEXT,
                explanation TEXT,
                points INTEGER DEFAULT 1,
                created_by INTEGER,
                FOREIGN KEY (topic_id) REFERENCES topics (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic_id INTEGER,
                score INTEGER,
                max_score INTEGER,
                answers TEXT,
                test_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (topic_id) REFERENCES topics (id)
            )
        ''')

    def ensure_default_teacher(self):
        from hashlib import sha256

        self.cursor.execute("SELECT * FROM users WHERE username='teacher'")
        if not self.cursor.fetchone():
            hashed_password = sha256("teacher123".encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO users (username, password, first_name, last_name, user_type)
                VALUES (?, ?, ?, ?, ?)
            ''', ('teacher', hashed_password, 'Преподаватель', 'Тестовый', 'teacher'))

    def ensure_sample_data(self):
        self.cursor.execute("SELECT COUNT(*) FROM topics")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("SELECT id FROM users WHERE username='teacher'")
            teacher_id = self.cursor.fetchone()[0]
            insert_sample_data(self.cursor, teacher_id)
            self.conn.commit()

    def get_user_by_credentials(self, username, hashed_password):
        self.cursor.execute('''
            SELECT * FROM users WHERE username=? AND password=?
        ''', (username, hashed_password))
        return self.cursor.fetchone()

    def add_user(self, username, hashed_password, first_name, last_name):
        self.cursor.execute('''
            INSERT INTO users (username, password, first_name, last_name, user_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, hashed_password, first_name, last_name, 'student'))
        self.conn.commit()

    def get_topics(self, include_hidden=True):
        query = "SELECT id, title FROM topics"
        if not include_hidden:
            query += " WHERE is_hidden = 0"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_topic_by_id(self, topic_id):
        self.cursor.execute("SELECT * FROM topics WHERE id=?", (topic_id,))
        return self.cursor.fetchone()

    def get_all_topics_for_teacher(self):
        self.cursor.execute("SELECT id, title, is_hidden FROM topics")
        return self.cursor.fetchall()

    def add_topic(self, title, content, image_path, video_url, animation_path, audio_path, is_hidden, created_by):
        self.cursor.execute('''
            INSERT INTO topics (title, content, image_path, video_url, animation_path, audio_path, is_hidden, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, content, image_path, video_url, animation_path, audio_path, is_hidden, created_by))
        self.conn.commit()

    def update_topic(self, topic_id, title, content, image_path, video_url, animation_path, audio_path, is_hidden):
        self.cursor.execute('''
            UPDATE topics
            SET title=?, content=?, image_path=?, video_url=?, animation_path=?, audio_path=?, is_hidden=?
            WHERE id=?
        ''', (title, content, image_path, video_url, animation_path, audio_path, is_hidden, topic_id))
        self.conn.commit()

    def delete_topic(self, topic_id):
        self.cursor.execute("DELETE FROM questions WHERE topic_id=?", (topic_id,))
        self.cursor.execute("DELETE FROM topics WHERE id=?", (topic_id,))
        self.conn.commit()

    def get_topic_full_by_id(self, topic_id):
        self.cursor.execute("""
            SELECT title, content, image_path, video_url, animation_path, audio_path, is_hidden
            FROM topics WHERE id=?
        """, (topic_id,))
        return self.cursor.fetchone()

    def get_questions_by_topic(self, topic_id):
        self.cursor.execute('''
            SELECT id, question_text, question_type, options, correct_answer, points
            FROM questions WHERE topic_id=?
        ''', (topic_id,))
        return self.cursor.fetchall()

    def add_question(self, topic_id, question_text, question_type, options, correct_answer, explanation, points, created_by):
        self.cursor.execute('''
            INSERT INTO questions (topic_id, question_text, question_type, options, correct_answer, explanation, points, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (topic_id, question_text, question_type, options, correct_answer, explanation, points, created_by))
        self.conn.commit()

    def get_questions_short_by_topic(self, topic_id):
        self.cursor.execute(
            "SELECT id, question_type, question_text, points FROM questions WHERE topic_id=?",
            (topic_id,)
        )
        return self.cursor.fetchall()

    def get_question_by_id(self, q_id):
        self.cursor.execute('''
            SELECT id, topic_id, question_text, question_type, options, correct_answer, explanation, points
            FROM questions
            WHERE id=?
        ''', (q_id,))
        return self.cursor.fetchone()

    def update_question(self, q_id, question_text, question_type, options, correct_answer, explanation, points):
        self.cursor.execute('''
            UPDATE questions
            SET question_text=?, question_type=?, options=?, correct_answer=?, explanation=?, points=?
            WHERE id=?
        ''', (question_text, question_type, options, correct_answer, explanation, points, q_id))
        self.conn.commit()

    def delete_question(self, q_id):
        self.cursor.execute("DELETE FROM questions WHERE id=?", (q_id,))
        self.conn.commit()

    def get_question_explanation(self, q_id):
        self.cursor.execute("SELECT explanation FROM questions WHERE id=?", (q_id,))
        return self.cursor.fetchone()

    def save_test_result(self, user_id, topic_id, total_score, max_score, results_text):
        self.cursor.execute('''
            INSERT INTO test_results (user_id, topic_id, score, max_score, answers, test_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            topic_id,
            total_score,
            max_score,
            results_text,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        self.cursor.execute('''
            UPDATE users SET last_test_date=?, total_score=total_score+?
            WHERE id=?
        ''', (
            datetime.now().strftime("%Y-%m-%d"),
            total_score,
            user_id
        ))
        self.conn.commit()

    def get_student_results(self, user_id, limit=10):
        self.cursor.execute('''
            SELECT test_date, score, max_score, topic_id
            FROM test_results
            WHERE user_id=?
            ORDER BY test_date DESC
            LIMIT ?
        ''', (user_id, limit))
        return self.cursor.fetchall()

    def get_topic_title(self, topic_id):
        self.cursor.execute("SELECT title FROM topics WHERE id=?", (topic_id,))
        row = self.cursor.fetchone()
        return row[0] if row else "Неизвестно"

    def get_students(self):
        self.cursor.execute("SELECT id, first_name, last_name FROM users WHERE user_type='student'")
        return self.cursor.fetchall()

    def get_results_for_student(self, student_id):
        self.cursor.execute('''
            SELECT test_date, score, max_score, topic_id, answers
            FROM test_results
            WHERE user_id=?
            ORDER BY test_date DESC
        ''', (student_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()