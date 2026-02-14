from typing import List


def spiral_traverse(matrix: List[List[int]]) -> List[int]:
    """
    Выполняет обход квадратной матрицы по спирали против часовой стрелки,
    начиная с левого верхнего угла.

    Args:
        matrix: Квадратная матрица чисел.

    Returns:
        Список чисел в порядке обхода.
    """
    if not matrix:
        return []

    result: List[int] = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1

    while top <= bottom and left <= right:
        # Вниз по левому столбцу
        for i in range(top, bottom + 1):
            result.append(matrix[i][left])
        left += 1
        if left > right:
            break

        # Вправо по нижней строке
        for i in range(left, right + 1):
            result.append(matrix[bottom][i])
        bottom -= 1
        if top > bottom:
            break

        # Вверх по правому столбцу
        for i in range(bottom, top - 1, -1):
            result.append(matrix[i][right])
        right -= 1
        if left > right:
            break

        # Влево по верхней строке
        for i in range(right, left - 1, -1):
            result.append(matrix[top][i])
        top += 1

    return result