import socket
import threading
import signal
import sys
import os

# Зберігаємо список підключених клієнтів і їх логіни
clients = {}
usernames = {}  # Зберігаємо логіни користувачів, прив'язані до сокетів

# Лок на доступ до консолі для уникнення накладання тексту
console_lock = threading.Lock()


# Функція для перевірки існування історії між двома користувачами
def load_chat_history_for_pair(login1, login2):
    file_path = f"{login1}_{login2}_chat.txt"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    return []


# Функція для збереження історії чату для пари користувачів
def save_chat_history_for_pair(login1, login2, message):
    file_path = f"{login1}_{login2}_chat.txt"
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(message + "\n")


# Функція для обробки клієнтів
def handle_client(client_socket, client_address):
    try:
        # Отримуємо логін від клієнта
        login = client_socket.recv(1024).decode('utf-8').strip()

        # Перевіряємо чи є цей логін
        if login in usernames.values():
            with console_lock:
                print(f"Клієнт {client_address} з логіном {login} вже підключений.")
            client_socket.send(f"Логін {login} вже використовується!".encode('utf-8'))
            client_socket.close()
            return

        # Завантажуємо історію чату для цього користувача
        chat_history = load_chat_history(login)

        # Відправляємо історію чату клієнту
        if chat_history:
            for line in chat_history:
                client_socket.send(line.encode('utf-8'))

        # Зберігаємо логін користувача, прив'язуючи його до сокета
        usernames[client_socket] = login

        with console_lock:
            print(f"Клієнт {client_address} підключений як {login}")
        clients[client_socket] = client_address  # Можна також зберігати адресу, якщо потрібно

        # Перевіряємо історію з іншими користувачами
        for other_socket, other_login in usernames.items():
            if other_login != login:  # Історія з іншими підключеними користувачами
                chat_history_for_pair = load_chat_history_for_pair(login, other_login)
                for line in chat_history_for_pair:
                    client_socket.send(line.encode('utf-8'))

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            # Виводимо повідомлення разом з логіном і айпі
            with console_lock:
                print(f"\n{login} ({client_address[0]}): {message}")

            # Зберігаємо повідомлення в історії чату для всіх пар
            for other_socket, other_login in usernames.items():
                if other_login != login:  # Для кожної пари, яка взаємодіяла
                    save_chat_history_for_pair(login, other_login, f"{login}: {message}")
                    save_chat_history_for_pair(other_login, login, f"{login}: {message}")

            # Відправляємо повідомлення всім клієнтам
            forward_message(message, client_socket, login)
    except Exception as e:
        with console_lock:
            print(f"Помилка у клієнтському підключенні: {e}")
    finally:
        with console_lock:
            print(f"Клієнт відключився: {client_address}")
        if client_socket in clients:
            del clients[client_socket]
        if client_socket in usernames:
            del usernames[client_socket]
        client_socket.close()


# Функція для пересилання повідомлень між клієнтами
def forward_message(message, sender_socket, sender_login):
    for client_socket in clients:
        if client_socket != sender_socket:  # Не відправляти повідомлення клієнту, який його надіслав
            try:
                client_socket.send(f"{sender_login}: {message}".encode('utf-8'))
            except Exception as e:
                with console_lock:
                    print(f"Не вдалося відправити повідомлення клієнту: {e}")


# Закриття сервера
def close_server(signal, frame):
    with console_lock:
        print("\nЗакриття сервера...")
    for client_socket in clients:
        client_socket.close()
    server.close()
    sys.exit(0)


# Обробка сигналу закриття
signal.signal(signal.SIGINT, close_server)

# Налаштування сервера
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 5555))  # Слухаємо на всіх інтерфейсах
server.listen(5)
with console_lock:
    print("Сервер запущений і чекає на з'єднання...")

# Приймаємо клієнтські з'єднання
while True:
    client_socket, client_address = server.accept()
    with console_lock:
        print(f"Клієнт підключений: {client_address}")
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.daemon = True
    client_thread.start()