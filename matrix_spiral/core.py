import asyncio
from typing import List

import aiohttp

from .exceptions import MatrixDownloadError, MatrixParseError
from .parser import parse_matrix
from .spiral import spiral_traverse

DEFAULT_TIMEOUT = 10


async def get_matrix(url: str, timeout: int = DEFAULT_TIMEOUT) -> List[int]:
    """
    Загружает матрицу с удалённого сервера и возвращает результат её обхода.

    Args:
        url: Адрес ресурса, возвращающего текстовое представление матрицы.
        timeout: Максимальное время ожидания ответа (в секундах).

    Returns:
        Список чисел, полученный при обходе матрицы по спирали
        против часовой стрелки, начиная с левого верхнего угла.

    Raises:
        MatrixDownloadError: При сетевых ошибках или статусе ответа != 200.
        MatrixParseError: Если не удаётся разобрать полученные данные как
            квадратную матрицу.
    """
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    try:
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise MatrixDownloadError(
                        f'HTTP error {response.status}',
                    )
                text = await response.text()
    except aiohttp.ClientError as err:
        raise MatrixDownloadError(f'Network error: {err}') from err
    except asyncio.TimeoutError as err:
        raise MatrixDownloadError(f'Timeout after {timeout}s') from err

    matrix = parse_matrix(text)
    return spiral_traverse(matrix)