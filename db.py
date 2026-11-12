
import os
import mysql.connector
from dotenv import load_dotenv

# Đọc các biến cấu hình từ file .env
load_dotenv()

# Hàm tạo kết nối đến MySQL
def get_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return conn
