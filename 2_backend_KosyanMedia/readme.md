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

4.  **Убедитесь в наличии файлов ```RS_Via-3.xml``` и ```RS_ViaOW.xml``` в папке ```xml_files/``` или скопируйте их в указанную папку**

5.  **Запустите приложение:**
    ```bash
    python app.py
    ```
6. **После выполнения в папке ```results``` будут созданы результаты:
    ```route_comparison.xlsx``` содержащее три листа: ```Summary``` - сводная информация о сравнении,
    ```New Routes``` - с перечислением новых маршрутов во втором файле и
    ```Removed Routes``` - с маршрутами, удаленными в втором файле и будет создан файл ```routes_detailed``` со всеми маршрутами из обоих файлов**

### Способ 2: Запуск через Docker

1. **Сборка образа**:
   ```bash
   docker build -t xml-route-comparator
   ```
2. **Запуск контейнера:**
   ```bash
   docker run -v $(pwd)/xml_files:/app/xml_files \
           -v $(pwd)/results:/app/results \
           xml-route-comparator
   ```