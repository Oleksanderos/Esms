import customtkinter as ctk
from tkinter import messagebox
import pymysql
from client import start_chat_interface
from config import MYSQL_URL
from urllib.parse import urlparse

# Функція для отримання користувача з бази даних
def get_user(cursor, login):
    cursor.execute("SELECT * FROM users WHERE login=%s", (login,))
    return cursor.fetchone()

# Функція для додавання користувача до бази даних
def add_user(cursor, connection, login, password):
    try:
        cursor.execute("INSERT INTO users (login, password) VALUES (%s, %s)", (login, password))
        connection.commit()
    except Exception as ex:
        print(f"Помилка при додаванні користувача: {ex}")

# Функція для підключення до бази даних через MYSQL_URL
def login_or_register():
    try:
        parsed_url = urlparse(MYSQL_URL)
        connection = pymysql.connect(
            host=parsed_url.hostname,
            user=parsed_url.username,
            password=parsed_url.password,
            database=parsed_url.path[1:],
            port=parsed_url.port,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection, connection.cursor()
    except Exception as ex:
        print("З'єднання відхилено...")
        print(ex)
        return None, None

# Обробка входу користувача
def on_login():
    login = login_entry.get()
    password = password_entry.get()

    connection, cursor = login_or_register()

    if connection and cursor:
        try:
            user_data = get_user(cursor, login)
            if user_data and user_data['password'] == password:
                messagebox.showinfo("Успіх", f"Ласкаво просимо, {login}!")
                root.destroy()
                start_chat_interface(login)
            else:
                messagebox.showerror("Помилка", "Невірний логін або пароль.")
        finally:
            connection.close()
    else:
        messagebox.showerror("Помилка", "Не вдалося підключитися до бази даних.")

# Обробка реєстрації користувача
def on_register():
    login = login_entry.get()
    password = password_entry.get()

    connection, cursor = login_or_register()

    if connection and cursor:
        try:
            if get_user(cursor, login):
                messagebox.showerror("Помилка", "Користувач з таким логіном вже існує.")
            else:
                add_user(cursor, connection, login, password)
                messagebox.showinfo("Успіх", f"Користувача '{login}' успішно зареєстровано!")
                root.destroy()
                start_chat_interface(login)
        finally:
            connection.close()
    else:
        messagebox.showerror("Помилка", "Не вдалося підключитися до бази даних.")

# Створення головного вікна для авторизації
ctk.set_appearance_mode("dark")  # Темна тема
ctk.set_default_color_theme("blue")  # Колірна схема

root = ctk.CTk()
root.title("Вхід / Реєстрація")
root.geometry("350x300")

# Лейбли
ctk.CTkLabel(root, text="Логін:", font=("Arial", 14)).pack(pady=10)
login_entry = ctk.CTkEntry(root, width=250)
login_entry.pack(pady=5)

ctk.CTkLabel(root, text="Пароль:", font=("Arial", 14)).pack(pady=10)
password_entry = ctk.CTkEntry(root, width=250, show="*")
password_entry.pack(pady=5)

# Кнопки
login_button = ctk.CTkButton(root, text="Вхід", width=150, command=on_login)
login_button.pack(pady=10)

register_button = ctk.CTkButton(root, text="Реєстрація", width=150, command=on_register)
register_button.pack(pady=10)

# Запуск головного циклу
root.mainloop()