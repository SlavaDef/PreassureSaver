import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox




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


    def create_widgets(self):
        # Налаштування стилю
        style = ttk.Style()
        self.root.option_add('*Font', ('Comic Sans MS', 11, 'bold'))
        style.configure('Treeview', font=('Comic Sans MS', 10))  # Для даних у таблиці
        style.configure('Treeview.Heading', font=('Comic Sans MS', 11, 'bold'))  # Для заголовків таблиці

        # Фрейм для введення даних
        input_frame = ttk.LabelFrame(self.root, text="Введення даних", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Поля введення з шрифтом
        ttk.Label(input_frame, text="Систолічний:").grid(row=0, column=0, padx=5) # рядок, колонка , відстань по У
        self.systolic_var = tk.StringVar() # створення змінної
        self.systolic_entry = ttk.Entry(input_frame, width=5, textvariable=self.systolic_var)# привязка до поля введення
        self.systolic_entry.grid(row=0, column=1, padx=5)  # рохміщення єлемента в сітці грід

        ttk.Label(input_frame, text="Діастолічний:").grid(row=0, column=2, padx=5)
        self.diastolic_var = tk.StringVar()
        self.diastolic_entry = ttk.Entry(input_frame, width=5, textvariable=self.diastolic_var)
        self.diastolic_entry.grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Пульс:").grid(row=0, column=4, padx=5)
        self.pulse_var = tk.StringVar()
        self.pulse_entry = ttk.Entry(input_frame, width=5, textvariable=self.pulse_var)
        self.pulse_entry.grid(row=0, column=5, padx=5)

        # Кнопка зберігання з оновленим шрифтом
        save_button = ttk.Button(input_frame, text="Зберегти", command=self.save_pressure) # виклик метода
        save_button.grid(row=0, column=6, padx=10)

        # Таблиця для відображення даних
        table_frame = ttk.LabelFrame(self.root, text="Історія вимірювань", padding=10)
        table_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Створення таблиці
        columns = ('date', 'pressure', 'pulse')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        # Заголовки стовпців
        self.tree.heading('date', text='Дата')
        self.tree.heading('pressure', text='Тиск')
        self.tree.heading('pulse', text='Пульс')

        # Налаштування ширини стовпців
        self.tree.column('date', width=150)
        self.tree.column('pressure', width=100)
        self.tree.column('pulse', width=100)

        # Додавання скролбару якщо записів багато можна прокручувати колесом
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Розміщення таблиці та скролбару
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Налаштування розширення
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)


    def save_pressure(self):
        try:
            systolic = self.systolic_var.get() # отримання значення з полів введення
            diastolic = self.diastolic_var.get()
            pulse = self.pulse_var.get()

            # Перевірка чи всі поля заповнені
            if not all([systolic, diastolic, pulse]):
                messagebox.showerror("Помилка", "Будь ласка, заповніть всі поля") # меседж бокс
                return

            # Перевірка чи введені числа
            systolic = int(systolic)
            diastolic = int(diastolic)
            pulse = int(pulse)

            # Перевірка діапазонів
            if not (80 <= systolic <= 220 and
                    50 <= diastolic <= 150 and
                    40 <= pulse <= 180):
                messagebox.showerror("Помилка", "Значення поза допустимими межами")
                return

            # Формуємо рядок для збереження
            pressure = f"{systolic}/{diastolic}/{pulse}"
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Зберігаємо в БД
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO pressure_records (pressure, date) VALUES (?, ?)',
                (pressure, date)
            )
            self.conn.commit()

            # Очищаємо поля введення
            self.systolic_var.set("")
            self.diastolic_var.set("")
            self.pulse_var.set("")

            # Оновлюємо таблицю
            self.update_table()

            messagebox.showinfo("Успіх", "Дані успішно збережено!")

        except ValueError:
            messagebox.showerror("Помилка", "Будь ласка, введіть коректні числові значення")


    def update_table(self):
        # Очищаємо таблицю (всі записи з віджета Treeview)
        # якщо ви хочете оновити дані в таблиці, спочатку потрібно видалити старі записи, а потім додати нові
        for item in self.tree.get_children(): # отримує список всіх ідентифікаторів елементів, які є в таблиці

            self.tree.delete(item)

        # Отримуємо дані з БД
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT date, pressure 
            FROM pressure_records 
            ORDER BY date DESC
        ''')

        # Додаємо дані в таблицю для відображення користувачу
        for date, pressure in cursor.fetchall():
            systolic, diastolic, pulse = pressure.split('/')
            formatted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y %H:%M')
            pressure_formatted = f"{systolic}/{diastolic}"
            self.tree.insert('', 'end', values=(formatted_date, pressure_formatted, pulse))


    def __del__(self):
        self.conn.close() # закриваємо конекшн до бд


if __name__ == '__main__':
    root = tk.Tk() # Ініціалізує графічний інтерфейс Tkinter, Створює головне вікно програми
    app = PressureApp(root)
    root.mainloop()
