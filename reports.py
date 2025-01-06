import pymysql
from urllib.parse import urlparse  # Додано імпорт urlparse
from config import MYSQL_URL

def get_db_connection():
    try:
        parsed_url = urlparse(MYSQL_URL)
        user = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port
        database = parsed_url.path[1:]

        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as ex:
        print(f"Помилка при підключенні до БД: {ex}")
        return None

def view_reports():
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM reports WHERE resolved = FALSE")
                reports = cursor.fetchall()
                for report in reports:
                    print(f"ID: {report['id']}, Повідомлення: {report['message']}, Від: {report['reported_by']}, На: {report['reported_user']}")
        finally:
            connection.close()

def close_report(report_id):
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE reports SET resolved = 1 WHERE id = %s", (report_id,))
                connection.commit()
                print(f"Скаргу з ID {report_id} закрито.")
        finally:
            connection.close()

def check_user_exists(username):
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE login = %s", (username,))
                user = cursor.fetchone()
                return user is not None
        finally:
            connection.close()
    return False

def ban_user(username):
    if check_user_exists(username):
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE users SET ban = 1 WHERE login = %s", (username,))
                    connection.commit()
                    print(f"Користувача {username} заблоковано.")
            finally:
                connection.close()
    else:
        print(f"Користувача з логіном {username} не існує.")

if __name__ == "__main__":
    while True:
        print("1. Переглянути скарги")
        print("2. Закрити скаргу")
        print("3. Заблокувати користувача")
        print("4. Вихід")
        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            view_reports()
        elif choice == "2":
            report_id = input("Введіть ID скарги для закриття: ").strip()
            close_report(report_id)
        elif choice == "3":
            username = input("Введіть логін користувача для блокування: ").strip()
            ban_user(username)
        elif choice == "4":
            break
        else:
            print("Неправильний вибір.")
