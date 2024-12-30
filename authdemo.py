import pymysql
from urllib.parse import urlparse
from config import MYSQL_URL  # Імпортуємо URL з файлу config.py


def get_user(cursor, login):
    """Перевіряє, чи існує користувач у базі даних."""
    cursor.execute("SELECT * FROM users WHERE login=%s", (login,))
    return cursor.fetchone()


def add_user(cursor, connection, login, password):
    """Додає нового користувача до бази даних."""
    try:
        cursor.execute("INSERT INTO users (login, password) VALUES (%s, %s)", (login, password))
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
                        password_input = input("Введіть пароль: ")

                        user_data = get_user(cursor, login_input)
                        if user_data and user_data['password'] == password_input:
                            print(f"Ласкаво просимо, {login_input}!")
                            return login_input  # Повертаємо логін, якщо авторизація успішна
                        else:
                            print("Невірний логін або пароль.")
                    elif choice == "2":  # Реєстрація
                        login_input = input("Введіть новий логін: ")
                        password_input = input("Введіть новий пароль: ")

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
