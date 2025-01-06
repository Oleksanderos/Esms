import socket
import threading
import customtkinter as ctk
from datetime import datetime
import keyboard

# Функція для отримання поточної дати в потрібному форматі
def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

# Функція для збереження повідомлень в файл
def save_message_to_history(user_login, message):
    filename = f"{user_login}_{get_current_date()}.txt"
    with open(filename, "a", encoding="utf-8") as file:
        file.write(message + "\n")

# Функція для отримання повідомлень від сервера
def receive_messages(client_socket, text_area):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                text_area.configure(state="normal")
                text_area.insert(ctk.END, f"{message}\n")
                text_area.yview(ctk.END)
                text_area.configure(state="disabled")
            else:
                break
        except Exception as e:
            print(f"Помилка під час отримання повідомлення: {e}")
            break

# Функція для перевірки натискання клавіші Esc
def check_escape_key():
    while True:
        if keyboard.is_pressed('esc'):
            print("\nНатиснута клавіша Esc. Вихід з програми...")
            exit(0)

# Налаштування клієнта
def start_client(user_login, text_area):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Вкажіть IP-адресу та порт сервера
    server_ip = "0.tcp.eu.ngrok.io"
    server_port = 16229

    try:
        client.connect((server_ip, server_port))
        print(f"Підключено до сервера як {user_login}")
        client.send(user_login.encode('utf-8'))
        save_message_to_history(user_login, f"Підключено до сервера як {user_login}")
    except Exception as e:
        print(f"Не вдалося підключитися до сервера: {e}")
        exit()

    receive_thread = threading.Thread(target=receive_messages, args=(client, text_area))
    receive_thread.daemon = True
    receive_thread.start()

    escape_thread = threading.Thread(target=check_escape_key)
    escape_thread.daemon = True
    escape_thread.start()

    def send_message():
        try:
            message = message_entry.get()
            if message.strip():
                client.send(message.encode('utf-8'))
                text_area.configure(state="normal")
                text_area.insert(ctk.END, f"{user_login}: {message}\n")
                text_area.yview(ctk.END)
                save_message_to_history(user_login, f"Відправлено: {message}")
                message_entry.delete(0, ctk.END)
                text_area.configure(state="disabled")
        except Exception as e:
            print(f"Не вдалося надіслати повідомлення: {e}")

    send_button.configure(command=send_message)

# Функція для запуску інтерфейсу чату
def start_chat_interface(user_login):
    ctk.set_appearance_mode("dark")  # Зміна теми (dark/light)
    ctk.set_default_color_theme("blue")  # Колірна схема

    window = ctk.CTk()  # Головне вікно
    window.title(f"Чат - {user_login}")
    window.geometry("600x400")

    # Текстова область для виведення повідомлень
    text_area = ctk.CTkTextbox(window, width=500, height=250, state="disabled")
    text_area.grid(row=0, column=0, padx=20, pady=20, columnspan=2)

    # Поле для введення повідомлення
    global message_entry
    message_entry = ctk.CTkEntry(window, width=400, placeholder_text="Введіть повідомлення")
    message_entry.grid(row=1, column=0, padx=20, pady=10)

    # Кнопка для відправки повідомлення
    global send_button
    send_button = ctk.CTkButton(window, text="Відправити", width=100)
    send_button.grid(row=1, column=1, padx=10, pady=10)

    # Запуск клієнта
    start_client(user_login, text_area)

    # Запуск інтерфейсу
    window.mainloop()

if __name__ == "__main__":
    from authdemo import login_or_register
    user_login = login_or_register()
    if user_login:
        start_chat_interface(user_login)
    else:
        print("Авторизація не вдалася.")