import asyncio
import sys

from .core import get_matrix
from .exceptions import MatrixDownloadError, MatrixParseError

__all__ = ['get_matrix', 'MatrixDownloadError', 'MatrixParseError']


def main():
    """Точка входа для запуска из командной строки."""
    if len(sys.argv) != 2:
        print("Usage: python -m matrix_spiral <url>")
        sys.exit(1)
    url = sys.argv[1]
    try:
        result = asyncio.run(get_matrix(url))
        print(result)
    except (MatrixDownloadError, MatrixParseError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()