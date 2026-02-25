from typing import List

from .exceptions import MatrixParseError


def parse_matrix(text: str) -> List[List[int]]:
    """
    Преобразует текст ответа сервера в матрицу целых чисел.

    Ожидается формат с разделителями '|' и рамками из '+', '-'.
    Например:
    +-----+-----+
    |  1  |  2  |
    +-----+-----+
    |  3  |  4  |
    +-----+-----+

    Args:
        text: Сырой текст ответа.

    Returns:
        Двумерный список целых чисел (квадратная матрица).

    Raises:
        MatrixParseError: Если текст не содержит данных, не удаётся
            преобразовать числа или матрица не является квадратной.
    """
    lines = text.splitlines()
    data_lines = [line for line in lines if '|' in line]
    if not data_lines:
        raise MatrixParseError('No data lines found in response')

    matrix = []
    for line in data_lines:
        parts = line.split('|')
        row = []
        for part in parts[1:-1]:
            stripped = part.strip()
            if stripped:
                try:
                    row.append(int(stripped))
                except ValueError as err:
                    raise MatrixParseError(
                        f'Invalid number format: {stripped}',
                    ) from err
        matrix.append(row)
    size = len(matrix)
    if size == 0:
        raise MatrixParseError('Matrix is empty')
    for i, row in enumerate(matrix):
        if len(row) != size:
            raise MatrixParseError(
                f'Row {i} has length {len(row)}, expected {size}',
            )

    return matrix