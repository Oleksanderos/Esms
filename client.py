import socket
import threading
import keyboard  # Для відслідковування натискання клавіші

# Імпортуємо функцію авторизації
from authdemo import login


# Функція для отримання повідомлень від сервера
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"\n{message}")
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


# Налаштування клієнта
def start_client(user_login):
    """Підключення до сервера та відправка повідомлень."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Вкажіть IP-адресу та порт сервера
    server_ip = "2.tcp.eu.ngrok.io"  # Замініть на IP сервера
    server_port = 11528

    try:
        client.connect((server_ip, server_port))
        print(f"Підключено до сервера як {user_login}")
        # Надсилаємо логін на сервер
        client.send(user_login.encode('utf-8'))
    except Exception as e:
        print(f"Не вдалося підключитися до сервера: {e}")
        exit()

    # Запускаємо потік для отримання повідомлень від сервера
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True  # Потік завершиться разом з основним
    receive_thread.start()

    # Запускаємо потік для перевірки натискання клавіші Esc
    escape_thread = threading.Thread(target=check_escape_key)
    escape_thread.daemon = True  # Щоб потік завершився разом з основним
    escape_thread.start()

    # Відправка повідомлень на сервер
    try:
        while True:
            message = input(f"{user_login} >> Введіть повідомлення: ")
            if message.strip():
                client.send(message.encode('utf-8'))
    except KeyboardInterrupt:
        print("\nВихід з програми...")
        client.close()  # Закриваємо з'єднання


if __name__ == "__main__":
    # Авторизація користувача перед підключенням до сервера
    user_login = login()

    if user_login:
        start_client(user_login)  # Якщо авторизація пройшла успішно
    else:
        print("Авторизація не вдалася. Завершення програми.")
