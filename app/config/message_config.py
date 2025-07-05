import tkinter as tk
from tkinter import ttk

# створив клас для налаштування власного діалогового вікна для повідомлень
class MessageConfig:

        def __init__(self, root):
            self.root = root

        def show_info_dialog(self, title, message):
            dialog = tk.Toplevel(self.root)
            dialog.title(title)
            dialog.geometry("400x350")

            # Зробити вікно модальним
            dialog.transient(self.root)
            dialog.grab_set()

            # Налаштування тексту повідомлення
            label = ttk.Label(dialog, text=message, font=('Comic Sans MS', 12, 'bold'), wraplength=250)
            label.pack(expand=True, pady=20)

            # Кнопка OK
            ok_button = ttk.Button(dialog, text="OK", command=dialog.destroy)
            ok_button.pack(pady=10)

            # Центрування вікна відносно головного вікна
            dialog.geometry("+{}+{}".format(
                self.root.winfo_x() + self.root.winfo_width()//2 - 150,
                self.root.winfo_y() + self.root.winfo_height()//2 - 75
            ))

            # Чекаємо закриття вікна
            self.root.wait_window(dialog)


        def show_error_dialog(self, title, message):
            dialog = tk.Toplevel(self.root)
            dialog.title(title)
            dialog.geometry("300x150")
            dialog.transient(self.root)
            dialog.grab_set()

            label = ttk.Label(dialog, text=message, font=('Comic Sans MS', 13, 'bold'),
                              wraplength=250, foreground='red')
            label.pack(expand=True, pady=20)

            ok_button = ttk.Button(dialog, text="OK", command=dialog.destroy)
            ok_button.pack(pady=10)

            dialog.geometry("+{}+{}".format(
                self.root.winfo_x() + self.root.winfo_width() // 2 - 150,
                self.root.winfo_y() + self.root.winfo_height() // 2 - 75
            ))

            self.root.wait_window(dialog)