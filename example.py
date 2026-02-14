import asyncio
from matrix_spiral.core import get_matrix

async def main():
    url = "http://localhost:8000/matrix_4x4.txt"
    result = await get_matrix(url)
    print("Результат обхода:", result)

if __name__ == "__main__":
    asyncio.run(main())