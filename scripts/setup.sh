#!/bin/bash
# Скрипт для локальной настройки проекта (Linux/macOS)

echo "Создание виртуального окружения..."
python3 -m venv venv

echo "Активация виртуального окружения..."
source venv/bin/activate

echo "Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Копирование .env.example в .env"
cp .env.example .env

echo "Настройка завершена. Запустите приложение командой: python -m app.main"