import socket
import threading
import keyboard  # Для відслідковування натискання клавіші
from authdemo import login_or_register
from datetime import datetime
import pymysql
from urllib.parse import urlparse
from config import MYSQL_URL  # Імпортуємо URL з файлу config.py

# Функція для отримання поточної дати в потрібному форматі
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

# Функція для збереження повідомлень в файл
def save_message_to_history(user_login, message):
    # Створюємо назву файлу, що містить ім'я користувача і поточну дату
    filename = f"{user_login}_{get_current_date()}.txt"
    with open(filename, "a", encoding="utf-8") as file:
        file.write(message + "\n")

# Функція для отримання повідомлень від сервера
def receive_messages(client_socket, user_login):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"\n{message}")
                save_message_to_history(user_login, f"Отримано: {message}")
            else:
                break
        except Exception as e:
            print(f"Помилка під час отримання повідомлення: {e}")
            break

# Функція для перевірки натискання клавіші Esc
def check_escape_key():
    while True:
        if keyboard.is_pressed('esc'):  # Перевіряємо, чи натиснута клавіша Esc
            print("\nНатиснута клавіша Esc. Вихід з програми...")
            exit(0)

# Оновлення статусу користувача на "в мережі"
def update_web_status(cursor, connection, login):
    try:
        cursor.execute("UPDATE users SET webstatus = 1 WHERE login = %s", (login,))
        connection.commit()
        print(f"Статус користувача '{login}' оновлено на 'в мережі'.")
    except Exception as ex:
        print(f"Помилка при оновленні статусу: {ex}")

# Функція для подання скарги
def add_report_to_server(client_socket, user_login):
    try:
        reported_user = input("Введіть ім'я користувача на якого ви хочете подати скаргу: ")
        report_message = input("Введіть повідомлення скарги: ")
        if reported_user.strip() and report_message.strip():
            report_data = f"REPORT:{reported_user}:{report_message}"
            client_socket.send(report_data.encode('utf-8'))
    except Exception as e:
        print(f"Помилка під час подання скарги: {e}")

# Налаштування клієнта
def start_client(user_login):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Вкажіть IP-адресу та порт сервера
    server_ip = "0.tcp.eu.ngrok.io"  # Замініть на IP сервера
    server_port = 18462

    try:
        client.connect((server_ip, server_port))
        print(f"Підключено до сервера як {user_login}")
        client.send(user_login.encode('utf-8'))
        save_message_to_history(user_login, f"Підключено до сервера як {user_login}")
    except Exception as e:
        print(f"Не вдалося підключитися до сервера: {e}")
        exit()

    # Запускаємо потік для отримання повідомлень від сервера
    receive_thread = threading.Thread(target=receive_messages, args=(client, user_login))
    receive_thread.daemon = True
    receive_thread.start()

    # Запускаємо потік для перевірки натискання клавіші Esc
    escape_thread = threading.Thread(target=check_escape_key)
    escape_thread.daemon = True
    escape_thread.start()

    # Підключення до бази даних для оновлення статусу
    try:
        parsed_url = urlparse(MYSQL_URL)
        user = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        database = parsed_url.path[1:]

        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            update_web_status(cursor, connection, user_login)

        try:
            while True:
                message = input(f"{user_login} >> Введіть повідомлення: ")
                if message.strip() == "/report":
                    add_report_to_server(client, user_login)
                elif message.strip():
                    client.send(message.encode('utf-8'))
                    save_message_to_history(user_login, f"Відправлено: {message}")
        except KeyboardInterrupt:
            print("\nВихід з програми...")
            client.close()
    except Exception as ex:
        print(f"Помилка під час підключення до бази даних: {ex}")
        exit()

if __name__ == "__main__":
    user_login = login_or_register()
    if user_login:
        start_client(user_login)
    else:
        print("Авторизація не вдалася. Завершення програми.")
