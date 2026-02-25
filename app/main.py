"""Главный модуль приложения."""
import sys

from app.db import get_connection, init_database, execute_query
from app.queries import QUERY_ALL_MAX, QUERY_ONE_MAX
from app.utils import print_results


def main() -> None:
    """Точка входа в программу."""
    try:
        # Подключаемся к БД
        conn = get_connection()
        print("Подключение к базе данных установлено.")

        # Инициализируем таблицу и загружаем данные
        init_database(conn)

        # Выполняем первый запрос (все максимальные зарплаты)
        rows_all = execute_query(conn, QUERY_ALL_MAX)
        print_results(rows_all, "Все сотрудники с максимальной зарплатой в отделе")

        # Выполняем второй запрос (по одному сотруднику на отдел)
        rows_one = execute_query(conn, QUERY_ONE_MAX)
        print_results(rows_one, "По одному сотруднику с максимальной зарплатой в отделе")

        conn.close()
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()