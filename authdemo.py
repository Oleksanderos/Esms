import pymysql
from urllib.parse import urlparse
from config import MYSQL_URL  # Імпортуємо URL з файлу config.py
import sys
import keyboard  # Потрібно встановити через `pip install keyboard`
import hashlib  # Для хешування паролів


def hash_password(password):
    """Хешує пароль за допомогою SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def input_with_asterisks(prompt=""):
    """Функція для введення пароля із зірочками, ігноруючи пробіли."""
    print(prompt, end="", flush=True)
    password = ""
    allowed_keys = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  # Дозволені символи

    while True:
        key = keyboard.read_event(suppress=True)  # Чекаємо на натискання клавіші
        if key.event_type == "down":  # Обробляємо тільки натискання
            if key.name == "enter":  # Якщо натиснуто Enter
                print()  # Переходимо на новий рядок
                break
            elif key.name == "backspace":  # Якщо натиснуто Backspace
                if len(password) > 0:
                    password = password[:-1]
                    # Видаляємо останній символ з консолі
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif key.name in allowed_keys:  # Дозволяємо лише певні символи
                password += key.name
                sys.stdout.write("*")
                sys.stdout.flush()
            # Усі інші клавіші (включаючи пробіли) ігноруються
    return password


def input_password_open(prompt=""):
    """Функція для відкритого введення пароля, ігноруючи пробіли."""
    print(prompt, end="", flush=True)
    password = ""
    allowed_keys = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  # Дозволені символи

    while True:
        key = keyboard.read_event(suppress=True)  # Чекаємо на натискання клавіші
        if key.event_type == "down":  # Обробляємо тільки натискання
            if key.name == "enter":  # Якщо натиснуто Enter
                print()  # Переходимо на новий рядок
                break
            elif key.name == "backspace":  # Якщо натиснуто Backspace
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write("\b \b")  # Видаляємо останній символ
                    sys.stdout.flush()
            elif key.name in allowed_keys:  # Дозволяємо лише певні символи
                password += key.name
                sys.stdout.write(key.name)  # Виводимо введений символ
                sys.stdout.flush()
            # Усі інші клавіші (включаючи пробіли) ігноруються
    return password


def get_user(cursor, login):
    """Перевіряє, чи існує користувач у базі даних та перевіряє його бан статус."""
    cursor.execute("SELECT * FROM users WHERE login=%s", (login,))
    user = cursor.fetchone()

    if user and user['ban'] == 1:  # Якщо бан статус 1, то повертаємо повідомлення
        return None  # Повертаємо None, щоб не дозволити підключення
    return user


def add_user(cursor, connection, login, password):
    """Додає нового користувача до бази даних."""
    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (login, password) VALUES (%s, %s)", (login, hashed_password))
        connection.commit()  # Підтверджуємо зміни
        print(f"Користувача '{login}' успішно зареєстровано!")
    except Exception as ex:
        print(f"Помилка при додаванні користувача: {ex}")


def login_or_register():
    """Функція для вибору між входом і реєстрацією."""
    try:
        # Розбираємо URL для отримання компонентів
        parsed_url = urlparse(MYSQL_URL)

        # Отримуємо деталі підключення
        user = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        database = parsed_url.path[1:]  # Видаляємо перший символ '/' з імені бази даних

        # Підключаємося до MySQL через URL
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            cursorclass=pymysql.cursors.DictCursor
        )

        print("З'єднання з базою даних успішне!")

        try:
            with connection.cursor() as cursor:
                while True:
                    choice = input("Виберіть дію: (1) Вхід, (2) Реєстрація: ").strip()
                    if choice == "1":  # Вхід
                        login_input = input("Введіть логін: ")
                        password_input = input_with_asterisks("Введіть пароль: ")
                        hashed_password = hash_password(password_input)

                        user_data = get_user(cursor, login_input)

                        if user_data is None:
                            print("\033[31mВаш аккаунт заблокований.\033[0m")
                            continue  # Пропускаємо далі, якщо аккаунт заблокований

                        if user_data and user_data['password'] == hashed_password:
                            print(f"Ласкаво просимо, {login_input}!")
                            return login_input  # Повертаємо логін, якщо авторизація успішна
                        else:
                            print("Невірний логін або пароль.")
                    elif choice == "2":  # Реєстрація
                        login_input = input("Введіть новий логін: ")

                        while True:  # Цикл для повторного введення пароля, якщо є помилки
                            password_input = input_password_open("Введіть новий пароль: ")

                            # Перевіряємо довжину пароля
                            if len(password_input) < 4:
                                print("Пароль повинен містити хоча б 4 символи. Спробуйте ще раз.")
                                continue

                            # Якщо всі перевірки пройдені, виходимо з циклу
                            break

                        # Перевіряємо, чи користувач вже існує
                        if get_user(cursor, login_input):
                            print("Користувач з таким логіном вже існує. Спробуйте інший.")
                        else:
                            add_user(cursor, connection, login_input, password_input)
                    else:
                        print("Невірний вибір. Спробуйте ще раз.")
        finally:
            connection.close()

    except Exception as ex:
        print("З'єднання відхилено...")
        print(ex)
        return None
