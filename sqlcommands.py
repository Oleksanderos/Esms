import pymysql
from urllib.parse import urlparse
from config import MYSQL_URL

# Розбираємо URL
parsed_url = urlparse(MYSQL_URL)
user = parsed_url.username
password = parsed_url.password
host = parsed_url.hostname
port = parsed_url.port
database = parsed_url.path[1:]

# Підключення до бази
connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    port=port
)

try:
    with connection.cursor() as cursor:
        # Створюємо нову таблицю users з унікальним login
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                login VARCHAR(25) UNIQUE,
                password VARCHAR(25)
            );
        """)
        connection.commit()
        print("Таблицю успішно створено з унікальним логіном та паролем!")
finally:
    connection.close()
