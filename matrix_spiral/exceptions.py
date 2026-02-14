"""Пользовательские исключения для работы с матрицами."""


class MatrixError(Exception):
    """Базовое исключение для ошибок, связанных с матрицами."""


class MatrixDownloadError(MatrixError):
    """Ошибка при загрузке матрицы по сети."""


class MatrixParseError(MatrixError):
    """Ошибка при разборе текстового представления матрицы."""