import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError, DatabaseError
from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

print("DB_PASSWORD:", os.getenv('DB_PASSWORD'))
print("DB_USER:", os.getenv('DB_USER'))

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    print("Подключение успешно!")
    conn.close()
except OperationalError as e:
    print(f"OperationalError: {e}")
    # Попробуем извлечь детали, если они есть в e.pgcode или e.pgerror
    if hasattr(e, 'pgerror'):
        print(f"PG Error: {e.pgerror}")
    if hasattr(e, 'pgcode'):
        print(f"PG Code: {e.pgcode}")
except DatabaseError as e:
    print(f"DatabaseError: {e}")