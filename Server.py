import socket
import threading
import signal
import sys

# Зберігаємо список підключених клієнтів
clients = []

# Функція для обробки клієнтів
def handle_client(client_socket, client_address):
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break

            print(f"\nПовідомлення від {client_address}: {message}")
            # Відправляємо повідомлення всім клієнтам
            forward_message(message, client_socket)
    except Exception as e:
        print(f"Помилка у клієнтському підключенні: {e}")
    finally:
        print(f"Клієнт відключився: {client_address}")
        clients.remove(client_socket)
        client_socket.close()

# Функція для пересилання повідомлень між клієнтами
def forward_message(message, sender_socket):
    for client in clients:
        if client != sender_socket:  # Не відправляти повідомлення клієнту, який його надіслав
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Не вдалося відправити повідомлення клієнту: {e}")

# Закриття сервера
def close_server(signal, frame):
    print("\nЗакриття сервера...")
    for client in clients:
        client.close()
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
    clients.append(client_socket)
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
