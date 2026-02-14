import math
import os
import time
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request

app = Flask(__name__)
load_dotenv()

# Константы
API_KEY = os.getenv('API_KEY')
CACHE_DURATION = 1800  # секунд
REQUEST_TIMEOUT = 5  # секунд
API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Кэш погоды: ключ — название города (в нижнем регистре), значение — словарь с данными
weather_cache: Dict[str, Dict[str, Any]] = {}


def get_weather_from_api(city: str) -> Dict[str, Any]:
    """
    Получает данные о погоде от OpenWeatherMap.

    Аргументы:
        city: название города.

    Возвращает:
        Словарь с ключами: temperature, pressure, wind_speed, city, timestamp.

    Исключения:
        ValueError: если город не найден или API вернул ошибку.
        requests.RequestException: при проблемах сети.
        KeyError: если ответ API не содержит ожидаемых полей.
    """
    params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
    try:
        response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT)
        data = response.json()
    except requests.RequestException as e:
        raise requests.RequestException(f"Ошибка соединения: {e}") from e

    if response.status_code != 200:
        message = data.get('message', 'Unknown error')
        raise ValueError(f"Город не найден: {message}")

    # Проверка наличия необходимых ключей в ответе
    try:
        temperature = data['main']['temp']
        pressure_hpa = data['main']['pressure']
        wind_speed = data['wind']['speed']
        city_name = data['name']
    except KeyError as e:
        raise KeyError(f"Неожиданный формат ответа API: отсутствует ключ {e}") from e

    # Преобразование давления: hPa -> мм рт.ст.
    pressure_mmhg = math.ceil(pressure_hpa / 1.333)

    return {
        'temperature': temperature,
        'pressure': pressure_mmhg,
        'wind_speed': wind_speed,
        'city': city_name,
        'timestamp': int(time.time()),
    }


@app.route('/weather', methods=['GET'])
def get_weather() -> tuple:
    """
    Обрабатывает GET-запрос к /weather.

    Параметры запроса:
        city (обязательный): название города.

    Возвращает:
        JSON с данными о погоде или сообщением об ошибке.
    """
    city_name = request.args.get('city')
    if not city_name:
        return jsonify({'error': 'Укажите параметр ?city='}), 400

    normalized_city = city_name.lower()
    current_time = time.time()

    # Проверка кэша
    cached = weather_cache.get(normalized_city)
    if cached and (current_time - cached['timestamp']) < CACHE_DURATION:
        cached['source'] = 'cache'
        return jsonify(cached), 200

    try:
        weather_data = get_weather_from_api(city_name)
    except ValueError as e:
        # Город не найден или ошибка API
        app.logger.info("Ошибка получения данных для города %s: %s", city_name, e)
        return jsonify({'error': str(e)}), 404
    except requests.RequestException as e:
        # Проблемы сети
        app.logger.error("Сетевая ошибка при запросе к API: %s", e)
        return jsonify({'error': 'Ошибка соединения с сервисом погоды'}), 503
    except KeyError as e:
        # Неверный формат ответа
        app.logger.error("Ошибка формата данных от API: %s", e)
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

    # Успешное получение данных
    weather_data['source'] = 'openweathermap'
    weather_cache[normalized_city] = weather_data
    return jsonify(weather_data), 200


if __name__ == '__main__':
    app.logger.info("Сервер запускается на http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)