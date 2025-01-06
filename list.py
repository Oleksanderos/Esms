import pymysql
from urllib.parse import urlparse
from config import MYSQL_URL  # Імпортуємо URL із файлу config.py

# Функція для визначення статусу за кодом
def get_status(webstatus):
    status_mapping = {
        0: ("Не в мережі", "\033[90m"),  # Сірий
        1: ("В мережі", "\033[92m"),  # Зелений
        2: ("Не на місці", "\033[93m"),  # Жовтий
        3: ("Не турбувати", "\033[95m"),  # Фіолетовий
    }
    status_text, color_code = status_mapping.get(webstatus, ("Невідомий статус", "\033[0m"))
    return color_code + status_text + "\033[0m"

# Функція для визначення статусу бану
def get_ban_status(ban):
    if ban == 1:
        return "\033[91mЗабанено\033[0m"  # Червоний
    else:
        return "\033[92mАктивний\033[0m"  # Зелений

# Функція для бану користувача
def ban_user(cursor, connection, user_id):
    """Забанити користувача."""
    try:
        cursor.execute("UPDATE users SET ban = 1 WHERE id = %s", (user_id,))
        connection.commit()
        print(f"Користувача з ID {user_id} заблоковано.")
    except Exception as ex:
        print(f"Помилка при бані користувача: {ex}")

# Функція для розбану користувача
def unban_user(cursor, connection, user_id):
    """Розбанити користувача."""
    try:
        cursor.execute("UPDATE users SET ban = 0 WHERE id = %s", (user_id,))
        connection.commit()
        print(f"Користувача з ID {user_id} розблоковано.")
    except Exception as ex:
        print(f"Помилка при розбані користувача: {ex}")

def fetch_users():
    """Отримує список користувачів і статусів із бази даних, а також дає можливість банити/розбанювати."""
    try:
        # Розбираємо URL для отримання деталей підключення
        parsed_url = urlparse(MYSQL_URL)

        # Отримуємо деталі підключення
        user = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        database = parsed_url.path[1:]  # Видаляємо перший символ '/' з імені бази даних

        # Підключаємося до бази даних
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
                # Виконуємо SQL-запит для отримання користувачів
                cursor.execute("SELECT id, login, webstatus, ban FROM users")
                users = cursor.fetchall()

                # Виводимо список користувачів із статусами
                print("Список користувачів:")
                for user in users:
                    user_id = user['id']
                    login = user['login']
                    webstatus = user['webstatus']
                    ban = user['ban']

                    status = get_status(webstatus)
                    ban_status = get_ban_status(ban)

                    print(f"ID: {user_id}, Логін: {login}, Статус: {status}, Бан: {ban_status}")

                # Дія з користувачем
                user_id_to_modify = input("Введіть ID користувача для зміни статусу (або '0' для виходу): ")
                if user_id_to_modify != '0':
                    action = input("Виберіть дію: (1) Забанити, (2) Розбанити: ").strip()
                    if action == '1':
                        ban_user(cursor, connection, user_id_to_modify)
                    elif action == '2':
                        unban_user(cursor, connection, user_id_to_modify)
                    else:
                        print("Невірний вибір.")

        finally:
            connection.close()

    except Exception as ex:
        print("Помилка при підключенні до бази даних або виконанні запиту:")
        print(ex)

# Виконуємо функцію
if __name__ == "__main__":
    fetch_users()
