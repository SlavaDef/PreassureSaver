import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from config.message_config import MessageConfig
from service.service import PressureService


class PressureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Моніторинг тиску") # назва вікна
        self.root.geometry("750x600") # розмір по координаті х і у
        self.root.attributes('-alpha', 0.85) # прозорість
        self.message_config = MessageConfig(root) # не стандартне налаштування вікна

        # Підключення до БД
        self.conn = sqlite3.connect('pressure3.db')

        # Створення екземпляру сервісного класу
        self.service = PressureService(self.conn, self.message_config)

        self.create_table()

        # Створення віджетів
        self.create_widgets()

        # Оновлення таблиці при запуску
        self.update_table()

        # Перевірка критичних показників при запуску
        self.service.check_weekly_critical_pressure()


    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pressure_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pressure TEXT NOT NULL,
                date DATETIME NOT NULL,
                notes TEXT
            )
        ''')
        self.conn.commit()


    def create_widgets(self):

        # Налаштування стилю
        style = ttk.Style()
        self.root.option_add('*Font', ('Comic Sans MS', 11, 'bold'))
        #self.root.option_add('*Dialog.msg.font', ('Comic Sans MS', 13, 'bold'))
        style.configure('Treeview', font=('Comic Sans MS', 10))  # Для даних у таблиці
        style.configure('Treeview.Heading', font=('Comic Sans MS', 11, 'bold'))  # Для заголовків таблиці
        style.configure('TButton', font=('Comic Sans MS', 10))  # Для кнопок
        style.configure('TLabelframe.Label', font=('Comic Sans MS', 10)) # шрифт для тексту заголовку

        # Фрейм для введення даних
        input_frame = ttk.LabelFrame(self.root, text="Введення даних",  padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        style.configure('TLabelframe.Label', font=('Comic Sans MS', 10))



        # Створюємо фрейм для кнопок
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=8, pady=5)

        # Створюємо фрейм для кнопок статистики
        stat_button_frame = ttk.Frame(input_frame)
        stat_button_frame.grid(row=3, column=0, columnspan=8, pady=5)

        style = ttk.Style() # стилі для кнопок, далі цей стиль додаемо до налаштувань самої кнопки
        style.configure('Custom.TButton', buttoncolor='sky blue', background='green', foreground='black',  borderwidth=5,
        relief="raised", padding=(10, 5))


        # Поля введення з шрифтом
        ttk.Label(input_frame, text="Систолічний:").grid(row=0, column=0, padx=5) # рядок, колонка , відстань по У
        self.systolic_var = tk.StringVar() # створення змінної
        self.systolic_entry = ttk.Entry(input_frame, width=5, textvariable=self.systolic_var)# привязка до поля введення
        self.systolic_entry.grid(row=0, column=1, padx=5)  # рохміщення єлемента в сітці грід

        ttk.Label(input_frame, text="Діастолічний:").grid(row=0, column=2, padx=5)
        self.diastolic_var = tk.StringVar()  # змінна для збереження введеного тексту
        self.diastolic_entry = ttk.Entry(input_frame, width=5, textvariable=self.diastolic_var) #Створюємо поле введення для пульсу
        self.diastolic_entry.grid(row=0, column=3, padx=5) # Розміщуємо поле введення у вікні

        ttk.Label(input_frame, text="Пульс:").grid(row=0, column=4, padx=5)
        self.pulse_var = tk.StringVar()
        self.pulse_entry = ttk.Entry(input_frame, width=5, textvariable=self.pulse_var)
        self.pulse_entry.grid(row=0, column=5, padx=5)

        # Додаємо поле для заміток
        ttk.Label(input_frame, text="Замітки:").grid(row=1, column=0, padx=5, pady=5)
        self.notes_var = tk.StringVar()
        self.notes_entry = ttk.Entry(input_frame, width=40, textvariable=self.notes_var)
        self.notes_entry.grid(row=1, column=1, columnspan=5, padx=5, pady=5)

        # Розміщуємо кнопки у фреймі
        save_button = ttk.Button(button_frame, text="Зберегти", style='Custom.TButton', command=self.save_pressure)
        save_button.pack(side='left', padx=5)

        edit_button = ttk.Button(button_frame, text="Редагувати", style='Custom.TButton', command=self.edit_selected)
        edit_button.pack(side='left', padx=5)

        #statistic_button = ttk.Button(button_frame, text="Статистика", command=self.get_pressure_statistics)
        #statistic_button.pack(side='left', padx=5)

        statistic_button = ttk.Button(stat_button_frame, text="Загальна статистика",
                                      command=lambda: self.service.get_pressure_statistics('all'))
        statistic_button.pack(side='left', padx=5)

        week_stat_button = ttk.Button(stat_button_frame, text="Статистика за тиждень",
                                      command=lambda: self.service.get_pressure_statistics('week'))
        week_stat_button.pack(side='left', padx=5)

        month_stat_button = ttk.Button(stat_button_frame, text="Статистика за місяць",
                                       command=lambda: self.service.get_pressure_statistics('month'))
        month_stat_button.pack(side='left', padx=5)


        ex_button = ttk.Button(stat_button_frame, text="Екстремальні показники",
                                  command=self.service.get_pressure_extremes)
        ex_button.pack(side='left', padx=5)


        # Таблиця для відображення даних
        table_frame = ttk.LabelFrame(self.root, text="Історія вимірювань", padding=10)
        table_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Створення таблиці
        columns = ('id', 'date', 'pressure', 'pulse', 'notes')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        # Заголовки стовпців
        self.tree.heading('id', text='ID')
        self.tree.heading('date', text='Дата')
        self.tree.heading('pressure', text='Тиск')
        self.tree.heading('pulse', text='Пульс')
        self.tree.heading('notes', text='Замітки')

        # Налаштування ширини стовпців
        self.tree.column('id', width=0, stretch=False)
        self.tree.column('date', width=150)
        self.tree.column('pressure', width=100)
        self.tree.column('pulse', width=100)
        self.tree.column('notes', width=200)

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
            notes = self.notes_var.get()

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
                'INSERT INTO pressure_records (pressure, date, notes) VALUES (?, ?, ?)',
                (pressure, date, notes)
            )
            self.conn.commit()

            # Очищаємо поля введення
            self.systolic_var.set("")
            self.diastolic_var.set("")
            self.pulse_var.set("")
            self.notes_var.set("")

            # Оновлюємо таблицю
            self.update_table()

            messagebox.showinfo("Успіх", "Дані успішно збережено!")

        except ValueError:
            messagebox.showerror("Помилка", "Будь ласка, введіть коректні числові значення")


    def edit_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Попередження", "Будь ласка, виберіть запис для редагування")
            return

        item = self.tree.item(selected_item[0])
        values = item['values']
        record_id = values[0]  # ID запису
        date_str = values[1]  # Дата
        pressure = values[2]  # Тиск
        pulse = values[3]  # Пульс
        notes = values[4] if values[4] else ""  # Замітки

        # Створюємо вікно редагування
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редагування запису")
        edit_window.geometry("700x300")

        # Отримуємо значення тиску
        sys, dia = pressure.split('/')

        # Додаємо поле для дати
        ttk.Label(edit_window, text="Дата (дд.мм.рррр):").grid(row=0, column=0, padx=5, pady=5)
        date_var = tk.StringVar(value=date_str.split()[0])
        date_entry = ttk.Entry(edit_window, textvariable=date_var, width=12)
        date_entry.grid(row=0, column=1, padx=5)

        # Додаємо поле для часу
        ttk.Label(edit_window, text="Час (гг:хх):").grid(row=0, column=2, padx=5)
        time_var = tk.StringVar(value=date_str.split()[1])
        time_entry = ttk.Entry(edit_window, textvariable=time_var, width=8)
        time_entry.grid(row=0, column=3, padx=5)

        # Створюємо поля введення
        ttk.Label(edit_window, text="Систолічний:").grid(row=1, column=0, padx=5, pady=5)
        sys_var = tk.StringVar(value=sys)
        sys_entry = ttk.Entry(edit_window, textvariable=sys_var, width=5)
        sys_entry.grid(row=1, column=1, padx=5)

        ttk.Label(edit_window, text="Діастолічний:").grid(row=1, column=2, padx=5)
        dia_var = tk.StringVar(value=dia)
        dia_entry = ttk.Entry(edit_window, textvariable=dia_var, width=5)
        dia_entry.grid(row=1, column=3, padx=5)

        ttk.Label(edit_window, text="Пульс:").grid(row=1, column=4, padx=5)
        pulse_var = tk.StringVar(value=pulse)
        pulse_entry = ttk.Entry(edit_window, textvariable=pulse_var, width=5)
        pulse_entry.grid(row=1, column=5, padx=5)

        ttk.Label(edit_window, text="Замітки:").grid(row=2, column=0, padx=5, pady=5)
        notes_var = tk.StringVar(value=notes)
        notes_entry = ttk.Entry(edit_window, textvariable=notes_var, width=40)
        notes_entry.grid(row=2, column=1, columnspan=5, padx=5)


        def save_changes(): # це внутрышня функція в функції edit_selected()
            try:
                new_sys = int(sys_var.get())
                new_dia = int(dia_var.get())
                new_pulse = int(pulse_var.get())
                new_date = date_var.get()
                new_notes = notes_var.get()
                new_time = time_var.get()

                # Перевірка коректності дати та часу
                try:
                    datetime_str = f"{new_date} {new_time}"
                    formatted_date = datetime.strptime(datetime_str, '%d.%m.%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    messagebox.showerror("Помилка", "Некоректний формат дати або часу")
                    return

                if not (80 <= new_sys <= 220 and 50 <= new_dia <= 150 and 40 <= new_pulse <= 180):
                    messagebox.showerror("Помилка", "Значення поза допустимими межами")
                    return

                if  new_sys > 180 or  new_dia > 120 or new_pulse > 140:
                    messagebox.showwarning("Попередження", "Вам краще випити пігулку чи звернутися до лікаря")


                # Оновлюємо запис в БД
                cursor = self.conn.cursor()
                new_pressure = f"{new_sys}/{new_dia}/{new_pulse}"

                cursor.execute('''
                    UPDATE pressure_records 
                    SET pressure = ?, notes = ?, date = ?
                    WHERE id = ?
                ''', (new_pressure, new_notes, formatted_date, record_id))
                self.conn.commit()

                self.update_table()
                edit_window.destroy()
                messagebox.showinfo("Успіх", "Зміни збережено!")

            except ValueError:
                messagebox.showerror("Помилка", "Будь ласка, введіть коректні числові значення")
        # У параметрі `command=save_changes` ми вказуємо, яка функція повинна виконатися при натисканні на кнопку
        ttk.Button(edit_window, text="Зберегти зміни", command=save_changes).grid(row=3, column=0, columnspan=6,
                                                                                  pady=20)

    def update_table(self):
        # Очищаємо таблицю (всі записи з віджета Treeview)
        # якщо ви хочете оновити дані в таблиці, спочатку потрібно видалити старі записи, а потім додати нові
        for item in self.tree.get_children(): # отримує список всіх ідентифікаторів елементів, які є в таблиці

            self.tree.delete(item)

        # Отримуємо дані з БД
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, date, pressure, notes 
            FROM pressure_records 
            ORDER BY date DESC
        ''')

        # Додаємо дані в таблицю для відображення користувачу
        for id_, date, pressure, notes in cursor.fetchall():
            systolic, diastolic, pulse = pressure.split('/')
            formatted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y %H:%M')
            pressure_formatted = f"{systolic}/{diastolic}"
            self.tree.insert('', 'end', values=(id_, formatted_date, pressure_formatted, pulse, notes))




    def __del__(self):
        self.conn.close() # закриваємо конекшн до бд


if __name__ == '__main__':
    root = tk.Tk() # Ініціалізує графічний інтерфейс Tkinter, Створює головне вікно програми
    app = PressureApp(root)
    root.mainloop()