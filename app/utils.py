"""Вспомогательные функции для форматирования вывода."""
from typing import List, Tuple, Any


def print_results(rows: List[Tuple[Any, ...]], description: str) -> None:
    """
    Красиво выводит результаты запроса.

    Args:
        rows: Список кортежей с данными.
        description: Описание запроса (заголовок).
    """
    if not rows:
        print(f"\n{description}: нет данных")
        return

    # Определяем заголовки на основе первого элемента (если это DictRow)
    # Упрощённо: для DictCursor можно получить имена колонок
    if hasattr(rows[0], 'keys'):
        headers = list(rows[0].keys())
    else:
        # Если простые кортежи, попытаемся определить по количеству полей
        # В наших запросах известны поля, но для общности оставим заглушку
        headers = [f"col{i}" for i in range(len(rows[0]))]

    # Вычисляем ширину колонок
    col_widths = []
    for i, header in enumerate(headers):
        max_len = len(header)
        for row in rows:
            val = row[i] if isinstance(row, (tuple, list)) else row[header]
            max_len = max(max_len, len(str(val)))
        col_widths.append(max_len)

    # Формируем разделитель
    separator = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'

    print(f"\n{description}")
    print(separator)
    # Заголовок
    header_line = '|'
    for i, header in enumerate(headers):
        header_line += f" {header:<{col_widths[i]}} |"
    print(header_line)
    print(separator)

    # Строки данных
    for row in rows:
        line = '|'
        for i, header in enumerate(headers):
            val = row[i] if isinstance(row, (tuple, list)) else row[header]
            line += f" {str(val):<{col_widths[i]}} |"
        print(line)
    print(separator)