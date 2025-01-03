import socket
import threading
import signal
import sys

# Зберігаємо список підключених клієнтів і їх логіни
clients = {}
usernames = {}  # Зберігаємо логіни користувачів, прив'язані до сокетів

# Функція для обробки клієнтів
def handle_client(client_socket, client_address):
    try:
        # Отримуємо логін від клієнта
        login = client_socket.recv(1024).decode('utf-8').strip()

        # Зберігаємо логін користувача, прив'язуючи його до сокета
        usernames[client_socket] = login

        print(f"Клієнт {client_address} підключений як {login}")
        clients[client_socket] = client_address  # Можна також зберігати адресу, якщо потрібно

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            # Виводимо повідомлення разом з логіном і айпі
            print(f"\n{login} ({client_address[0]}): {message}")

            # Відправляємо повідомлення всім клієнтам
            forward_message(message, client_socket, login)
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
def forward_message(message, sender_socket, sender_login):
    for client_socket in clients:
        if client_socket != sender_socket:  # Не відправляти повідомлення клієнту, який його надіслав
            try:
                client_socket.send(f"{sender_login}: {message}".encode('utf-8'))
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
server.bind(("127.0.0.1", 5555))  # Слухаємо на всіх інтерфейсах
server.listen(5)
print("Сервер запущений і чекає на з'єднання...")

# Приймаємо клієнтські з'єднання
while True:
    client_socket, client_address = server.accept()
    print(f"Клієнт підключений: {client_address}")
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()