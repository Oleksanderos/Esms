import socket
import threading

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

# Налаштування клієнта
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Вкажіть IP-адресу та порт сервера
server_ip = "7.tcp.eu.ngrok.io"  # Замініть на IP сервера
server_port =  16486

try:
    client.connect((server_ip, server_port))
    print("Підключено до сервера")
except Exception as e:
    print(f"Не вдалося підключитися до сервера: {e}")
    exit()

# Запускаємо потік для отримання повідомлень від сервера
receive_thread = threading.Thread(target=receive_messages, args=(client,))
receive_thread.start()

# Відправка повідомлень на сервер
try:
    while True:
        message = input("Введіть повідомлення: ")
        client.send(message.encode('utf-8'))
except KeyboardInterrupt:
    print("\nВихід...")
    client.close()