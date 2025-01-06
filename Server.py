import socket
import threading
import signal
import sys
import os

# Зберігаємо список підключених клієнтів і їх логіни
clients = {}
usernames = {}  # Зберігаємо логіни користувачів, прив'язані до сокетів

# Завантаження історії чату
def load_chat_history(user1, user2):
    filename = f"chat_{min(user1, user2)}_{max(user1, user2)}.txt"
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return file.readlines()
    return []

# Збереження історії чату
def save_chat_history(user1, user2, message):
    filename = f"chat_{min(user1, user2)}_{max(user1, user2)}.txt"
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(message + "\n")

# Функція для обробки клієнтів
def handle_client(client_socket, client_address):
    try:
        # Отримуємо логін від клієнта
        login = client_socket.recv(1024).decode('utf-8').strip()

        # Зберігаємо логін користувача, прив'язуючи його до сокета
        usernames[client_socket] = login
        clients[client_socket] = client_address

        print(f"Клієнт {client_address} підключився як {login}")

        # Перевірка, чи є партнер у чату
        partner_socket = None
        partner_login = None
        for sock, user in usernames.items():
            if sock != client_socket:
                partner_socket = sock
                partner_login = user
                break

        # Завантажуємо історію, якщо знайдено партнера
        if partner_login:
            chat_history = load_chat_history(login, partner_login)
            client_socket.send("Історія чату:\n".encode('utf-8'))
            for line in chat_history:
                client_socket.send(line.encode('utf-8'))

            partner_socket.send(f"{login} приєднався до чату.".encode('utf-8'))
            print(f"{login} приєднався до чату з {partner_login}")

        # Основний цикл обміну повідомленнями
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            formatted_message = f"{login}: {message}"
            print(formatted_message)

            # Збереження історії
            if partner_login:
                save_chat_history(login, partner_login, formatted_message)

            # Відправляємо повідомлення всім клієнтам
            forward_message(formatted_message, client_socket)

    except Exception as e:
        print(f"Помилка у клієнтському підключенні: {e}")
    finally:
        print(f"Клієнт відключився: {client_address}")
        if client_socket in clients:
            del clients[client_socket]
        if client_socket in usernames:
            del usernames[client_socket]
        client_socket.close()

# Функція для пересилання повідомлень між клієнтами
def forward_message(message, sender_socket):
    for client_socket in clients:
        if client_socket != sender_socket:  # Не відправляти повідомлення клієнту, який його надіслав
            try:
                client_socket.send(message.encode('utf-8'))
                print(f"Повідомлення відправлено клієнту {clients[client_socket]}")
            except Exception as e:
                print(f"Не вдалося відправити повідомлення клієнту: {e}")

# Закриття сервера
def close_server(signal, frame):
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
server.bind(("0.0.0.0", 5555))  # Слухаємо на всіх інтерфейсах
server.listen(5)
print("Сервер запущений і чекає на з'єднання...")

# Приймаємо клієнтські з'єднання
while True:
    client_socket, client_address = server.accept()
    print(f"Клієнт підключений: {client_address}")
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()