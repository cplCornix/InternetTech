"""Модуль для работы с базой данных PostgreSQL."""
import os
from typing import List, Tuple, Any

import psycopg2
from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

from app.data import EMPLOYEE_DATA

load_dotenv()


def get_connection() -> PgConnection:
    """Создаёт и возвращает подключение к PostgreSQL."""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'employee_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
    )


def init_database(conn: PgConnection) -> None:
    """
    Инициализирует таблицу employee и заполняет её тестовыми данными.

    Если таблица уже существует и содержит записи, данные не перезаписываются.
    """
    with conn.cursor() as cur:
        # Создание таблицы, если её нет
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employee (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                department VARCHAR(255) NOT NULL,
                salary INTEGER NOT NULL
            );
        """)
        conn.commit()

        # Проверяем, есть ли уже данные
        cur.execute("SELECT COUNT(*) FROM employee;")
        count = cur.fetchone()[0]
        if count == 0:
            # Вставка данных
            insert_query = """
                INSERT INTO employee (id, name, department, salary)
                VALUES (%s, %s, %s, %s);
            """
            cur.executemany(insert_query, EMPLOYEE_DATA)
            conn.commit()
            print(f"Загружено {len(EMPLOYEE_DATA)} записей в таблицу employee.")
        else:
            print(f"Таблица employee уже содержит {count} записей. Пропускаем загрузку.")


def execute_query(conn: PgConnection, query: str) -> List[Tuple[Any, ...]]:
    """Выполняет SQL-запрос и возвращает все строки результата."""
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()