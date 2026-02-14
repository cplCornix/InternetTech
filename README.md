### Способ 1: Локальный запуск

1.  **Клонируйте репозиторий и перейдите в папку проекта:**
    ```bash
    git clone <ссылка-на-репозиторий>
    ```

2.  **Создайте и активируйте виртуальное окружение:**
    *На Windows:*
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
    *На Linux/macOS:*
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *После активации в начале строки терминала должно появится `(venv)`.*

3.  **Установить необходимые пакеты:**
    ```bash
    pip install aiohttp pytest pytest-asyncio aioresponses
    ```
4. **Для быстрой проверки работоспособности в папке tests есть матрица 4x4 и файл example.py с ссылкой на файл с этой матрицей. Для быстрой проверки перейти в терминале в папку с матрицей и запустить сервер:**
    ```bash
    cd tests
    python -m http.server 8000
   ```
   
5. **Запустить второй терминал и запустить example.py:**
    ```bash
    py example.py
   ```
   *Будет возращен List[int] тестовой матрицы с обходом по спирали против часовой стрелки, начиная из верхнего левого угла*

### Способ 2: Запуск через Docker

1. **Сборка образа**:
   ```bash
   docker build -t matrix-spiral . 
   ```
2. **Запуск контейнера:**
   ```bash
   docker run --rm matrix-spiral
   ```
   
3. **Модифицировать файл example.py**
   Заменить
    ```bash
    async def main():
      url = "http://localhost:8000/matrix_4x4.txt"
   ```
   на
    ```bash
    async def main(): 
      url = os.getenv('MATRIX_URL', 'http://localhost:8000/matrix.txt')
   ```

4. **Запустить проект**
    ```bash
    docker-compose up --build
    ```
>>>>>>> 4_Backend_AvitoTech
