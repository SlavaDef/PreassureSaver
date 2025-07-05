from tkinter import messagebox



class PressureService:

    def __init__(self, conn, message_config):
        self.conn = conn
        self.message_config = message_config



    # статистика за весь час (за замовч), за тиждень, за місяць
    def get_pressure_statistics(self, period=None):
            cursor = self.conn.cursor()
            # cursor.execute('SELECT pressure FROM pressure_records')

            # SQL запити для різних періодів, словник SQL запитів
            sql_queries = {
                'week': '''
                       SELECT pressure 
                       FROM pressure_records 
                       WHERE date >= datetime('now', '-7 days')
                   ''',
                'month': '''
                       SELECT pressure 
                       FROM pressure_records 
                       WHERE date >= datetime('now', '-30 days')
                   ''',
                'all': 'SELECT pressure FROM pressure_records'
            }

            # Вибираємо потрібний запит
            # sql_queries['all'] - це значення за замовчуванням в методі get() якщо значення не передано
            query = sql_queries.get(period, sql_queries['all'])
            cursor.execute(query)

            records = cursor.fetchall()  # [('150/80/77',), ('125/85/90',), ('125/85/75',)....] масив кортеджів

            total = len(records)
            critical = 0
            # `(pressure,)` - це розпакування кортежу. Кома після `pressure` вказує Python, що це саме кортеж з одним елементом
            for (pressure,) in records:
                sys, dia, pulse = map(int, pressure.split(
                    '/'))  # `map(int, перетворить три рядка на числа бо split('/') верне масив з трех рядків
                if sys > 180 or dia > 120 or pulse > 140:
                    critical += 1

            if total > 0:
                percentage = (critical / total) * 100
                # знову словник для message
                period_text = {
                    'week': 'за тиждень',
                    'month': 'за місяць',
                    'all': 'за весь період'
                }.get(period, 'за весь період')

                message = (f"Статистика {period_text}:\n"
                           f"Загальна кількість вимірювань: {total}\n"
                           f"Кількість критичних показників: {critical}\n"
                           f"Відсоток критичних показників: {percentage:.1f}%\n")

                if critical >= 2:
                    message += "\nРекомендуємо звернутися до лікаря!"

                messagebox.showinfo("Статистика тиску", message)
            else:
                messagebox.showinfo("Статистика тиску", "Немає записів для аналізу")



    def get_pressure_extremes(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT pressure, date FROM pressure_records')
        records = cursor.fetchall()

        if not records:
            self.message_config.show_info_dialog("Статистика", "Немає записів для аналізу")
            return

        max_pressure = {'sys': 0, 'dia': 0, 'pulse': 0, 'date': ''}
        min_pressure = {'sys': 999, 'dia': 999, 'pulse': 0, 'date': ''}
        max_pulse = {'value': 0, 'sys': 0, 'dia': 0, 'date': ''}
        min_pulse = {'value': 999, 'sys': 0, 'dia': 0, 'date': ''}

        for pressure, date in records:
            sys, dia, pulse = map(int, pressure.split('/'))

            # Перевірка максимального тиску
            if sys > max_pressure['sys'] or (sys == max_pressure['sys'] and dia > max_pressure['dia']):
                max_pressure.update({'sys': sys, 'dia': dia, 'pulse': pulse, 'date': date})

            # Перевірка мінімального тиску
            if sys < min_pressure['sys'] or (sys == min_pressure['sys'] and dia < min_pressure['dia']):
                min_pressure.update({'sys': sys, 'dia': dia, 'pulse': pulse, 'date': date})

            # Перевірка максимального пульсу
            if pulse > max_pulse['value']:
                max_pulse.update({'value': pulse, 'sys': sys, 'dia': dia, 'date': date})

            # Перевірка мінімального пульсу
            if pulse < min_pulse['value']:
                min_pulse.update({'value': pulse, 'sys': sys, 'dia': dia, 'date': date})

            # Повідомлення про тиск
        pressure_message = (
            f"Максимальний тиск: {max_pressure['sys']}/{max_pressure['dia']} "
            f"(пульс: {max_pressure['pulse']}, дата: {max_pressure['date']})\n\n"
            f"Мінімальний тиск: {min_pressure['sys']}/{min_pressure['dia']} "
            f"(пульс: {min_pressure['pulse']}, дата: {min_pressure['date']})"
        )

        # Повідомлення про пульс
        pulse_message = (
            f"Максимальний пульс: {max_pulse['value']} "
            f"(тиск: {max_pulse['sys']}/{max_pulse['dia']}, дата: {max_pulse['date']})\n\n"
            f"Мінімальний пульс: {min_pulse['value']} "
            f"(тиск: {min_pulse['sys']}/{min_pulse['dia']}, дата: {min_pulse['date']})"
        )

        self.message_config.show_info_dialog("Екстремальні показники тиску", pressure_message)
        self.message_config.show_info_dialog("Екстремальні показники пульсу", pulse_message)



    def check_weekly_critical_pressure(self):
        cursor = self.conn.cursor()
        # Отримуємо записи за останній тиждень
        cursor.execute('''
            SELECT pressure, date 
            FROM pressure_records 
            WHERE date >= datetime('now', '-7 days')
            ORDER BY date DESC
        ''')

        critical_count = 0
        for pressure, date in cursor.fetchall():
            sys, dia, pulse = map(int, pressure.split('/'))

            # Перевіряємо критичні показники
            if sys > 180 or dia > 120 or pulse > 140:
                critical_count += 1

            # Якщо знайдено 2 або більше критичних записів
            if critical_count >= 2:
                messagebox.showwarning(
                    "Важливе попередження",
                    "За останній тиждень у вас було декілька випадків підвищеного тиску/пульсу. "
                    "Наполегливо рекомендуємо звернутися до лікаря!"
                )
                break