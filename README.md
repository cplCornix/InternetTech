### Способ 1: Локальный запуск

1.  **Клонируйте репозиторий и перейдите в папку проекта:**
    ```bash
    git clone <ссылка-на-репозиторий>
    cd Weather_app
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

3.  **Установите необходимые библиотеки:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Настройте API-ключ:**
    Создайте в папке проекта файл с названием `.env` и добавьте в него ваш ключ от OpenWeatherMap:
    ```env
    API_KEY=ваш_секретный_ключ_здесь
    ```

5.  **Запустите сервер:**
    ```bash
    python app.py
    ```
    В консоли появится сообщение: `Сервер запускается на http://localhost:5000`.

6.  **Проверьте работу:**
    Откройте браузер и перейдите по адресу [http://localhost:5000/weather?city=Moscow](http://localhost:5000/weather?city=Moscow). Вы должны получить JSON с данными о погоде.

### Способ 2: Запуск через Docker

1.  **Соберите Docker-образ:**
    Откройте терминал в папке `Weather_app` и выполните команду:
    ```bash
    docker build -t weather-api .
    ```
    Эта команда создаст образ с именем `weather-api` согласно инструкциям в файле `Dockerfile`.

2.  **Запустите контейнер:**
    Выполните следующую команду. Она передаст ваш API-ключ из файла `.env` в контейнер и откроет доступ к порту 5000.
    ```bash
    docker run -p 5000:5000 --env-file .env weather-api
    ```

3.  **Проверьте работу:**
    Сервис будет доступен по тому же адресу: [http://localhost:5000/weather?city=Moscow](http://localhost:5000/weather?city=Moscow).
>>>>>>> 1_backend_KODE
