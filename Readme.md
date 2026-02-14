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

3.  **Запустите приложение:**
    ```bash
    python app.py
    ```

### Способ 2: Запуск через Docker

1. **Сборка образа**:
   ```bash
   docker build -t 3_backend_pyshop
   ```
2. **Запуск контейнера:**
   ```bash
   docker run --rm 3_backend-pyshop
   ```