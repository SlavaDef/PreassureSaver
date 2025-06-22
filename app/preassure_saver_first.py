import sqlite3




class PressureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Моніторинг тиску")
        self.root.geometry("600x400")

        # Підключення до БД
        self.conn = sqlite3.connect('pressure.db')
        self.create_table()

        # Створення віджетів
        self.create_widgets()

        # Оновлення таблиці при запуску
        self.update_table()



    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pressure_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pressure TEXT NOT NULL,
                date DATETIME NOT NULL
            )
        ''')
        self.conn.commit()