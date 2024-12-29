import pymysql
from config import host, user, password, db_name

def get_user(cursor, login):
    """Перевіряє, чи існує користувач у базі даних."""
    cursor.execute("SELECT * FROM users WHERE login=%s", (login,))
    return cursor.fetchone()

def login():
    """Функція авторизації користувача."""
    try:
        connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )

        print("З'єднання з базою даних успішне!")

        try:
            with connection.cursor() as cursor:
                login_input = input("Введіть логін: ")
                password_input = input("Введіть пароль: ")

                user_data = get_user(cursor, login_input)
                if user_data and user_data['password'] == password_input:
                    print(f"Ласкаво просимо, {login_input}!")
                    return login_input  # Повертаємо логін, якщо авторизація успішна
                else:
                    print("Невірний логін або пароль.")
                    return None
        finally:
            connection.close()

    except Exception as ex:
        print("З'єднання відхилено...")
        print(ex)
        return None

if __name__ == "__main__":
    login()
