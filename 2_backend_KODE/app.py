import time
import math
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import requests

app = Flask(__name__)
load_dotenv()

API_KEY = os.getenv('API_KEY')
CACHE_DURATION = 1800

weather_cache = {}

def get_weather_from_api(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if response.status_code == 200:
            return {
                'temperature': data['main']['temp'],
                'pressure': math.ceil(data['main']['pressure'] / 1.333),  # hPa -> мм рт.ст.
                'wind_speed': data['wind']['speed'],
                'city': data['name'],
                'timestamp': int(time.time())
            }
        else:
            return {'error': f"Город не найден: {data.get('message', 'Unknown error')}"}
    except Exception as e:
        return {'error': f"Ошибка соединения: {str(e)}"}

@app.route('/weather', methods=['GET'])
def get_weather():
    city_name = request.args.get('city')
    if not city_name:
        return jsonify({'error': 'Укажите параметр ?city='}), 400

    city_name = city_name.lower()
    now = time.time()

    cached = weather_cache.get(city_name)
    if cached and (now - cached['timestamp']) < CACHE_DURATION:
        cached['source'] = 'cache'
        return jsonify(cached)

    weather_data = get_weather_from_api(city_name)

    if 'error' in weather_data:
        return jsonify(weather_data), 404

    weather_data['source'] = 'openweathermap'
    weather_cache[city_name] = weather_data

    return jsonify(weather_data)

if __name__ == '__main__':
    print("Сервер запускается на http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)