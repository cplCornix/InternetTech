@echo off
REM Скрипт для локальной настройки проекта (Windows)

echo Создание виртуального окружения...
python -m venv venv

echo Активация виртуального окружения...
call venv\Scripts\activate

echo Установка зависимостей...
pip install --upgrade pip
pip install -r requirements.txt

echo Копирование .env.example в .env
copy .env.example .env

echo Настройка завершена. Запустите приложение командой: python -m app.main