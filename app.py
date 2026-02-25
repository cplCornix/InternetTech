import os
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple

import xmltodict
from openpyxl import Workbook


def read_xml_file(filepath: str) -> str:
    """Чтение XML файла"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def parse_timestamp(timestamp: str) -> datetime:
    """Парсинг временной метки"""
    try:
        # Формат: 2015-10-22T0005
        if 'T' in timestamp:
            date_part, time_part = timestamp.split('T')
            if len(time_part) == 4:
                time_part = f"{time_part[:2]}:{time_part[2:]}"
            timestamp = f"{date_part} {time_part}"
        return datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
    except (ValueError, AttributeError):
        return datetime.min


def extract_itineraries(xml_content: str) -> List[Dict]:
    """Извлечение маршрутов из XML"""
    data = xmltodict.parse(xml_content)
    itineraries = []

    # Получаем список маршрутов
    priced_itineraries = data.get('AirFareSearchResponse', {}).get('PricedItineraries', {})

    # Обрабатываем случай, когда есть только один маршрут
    flights_list = priced_itineraries.get('Flights', [])
    if not isinstance(flights_list, list):
        flights_list = [flights_list]

    for idx, flight_group in enumerate(flights_list):
        itinerary = {
            'id': idx,
            'onward_flights': [],
            'return_flights': [],
            'pricing': {},
            'total_amount': None,
            'currency': None
        }

        # Извлекаем рейсы "туда"
        onward = flight_group.get('OnwardPricedItinerary', {})
        if onward:
            onward_flights = onward.get('Flights', {}).get('Flight', [])
            if not isinstance(onward_flights, list):
                onward_flights = [onward_flights]
            itinerary['onward_flights'] = process_flights(onward_flights)

        # Извлекаем рейсы "обратно" (если есть)
        return_itinerary = flight_group.get('ReturnPricedItinerary', {})
        if return_itinerary:
            return_flights = return_itinerary.get('Flights', {}).get('Flight', [])
            if not isinstance(return_flights, list):
                return_flights = [return_flights]
            itinerary['return_flights'] = process_flights(return_flights)

        # Извлекаем информацию о цене
        pricing = flight_group.get('Pricing', {})
        if pricing:
            itinerary['currency'] = pricing.get('@currency')
            service_charges = pricing.get('ServiceCharges', [])
            if not isinstance(service_charges, list):
                service_charges = [service_charges]

            for charge in service_charges:
                if charge.get('@type') == 'SingleAdult' and charge.get('@ChargeType') == 'TotalAmount':
                    try:
                        itinerary['total_amount'] = float(charge.get('#text', 0))
                    except (ValueError, TypeError, AttributeError):
                        itinerary['total_amount'] = None
                    break

        # Рассчитываем время начала и конца маршрута
        itinerary['start_time'], itinerary['end_time'] = calculate_route_times(itinerary)

        # Генерируем уникальный ключ для маршрута
        itinerary['route_key'] = generate_route_key(itinerary)

        itineraries.append(itinerary)

    return itineraries


def process_flights(flights: List[Dict]) -> List[Dict]:
    """Обработка списка рейсов"""
    processed_flights = []
    for flight in flights:
        processed_flight = {
            'carrier_id': flight.get('Carrier', {}).get('@id', ''),
            'carrier_name': flight.get('Carrier', {}).get('#text', ''),
            'flight_number': flight.get('FlightNumber', ''),
            'source': flight.get('Source', ''),
            'destination': flight.get('Destination', ''),
            'departure_time': parse_timestamp(flight.get('DepartureTimeStamp', '')),
            'arrival_time': parse_timestamp(flight.get('ArrivalTimeStamp', '')),
            'class': flight.get('Class', ''),
            'stops': int(flight.get('NumberOfStops', 0))
        }
        processed_flights.append(processed_flight)
    return processed_flights


def calculate_route_times(itinerary: Dict) -> Tuple[datetime, datetime]:
    """Расчет времени начала и конца маршрута"""
    all_flights = itinerary['onward_flights'] + itinerary['return_flights']
    if not all_flights:
        return datetime.min, datetime.min

    departure_times = [f['departure_time'] for f in all_flights]
    arrival_times = [f['arrival_time'] for f in all_flights]

    start_time = min(departure_times)
    end_time = max(arrival_times)

    return start_time, end_time


def generate_route_key(itinerary: Dict) -> str:
    """Генерация уникального ключа для маршрута"""
    key_parts = []

    # Добавляем информацию о рейсах "туда"
    for flight in itinerary['onward_flights']:
        flight_key = f"{flight['carrier_id']}{flight['flight_number']}_{flight['source']}_{flight['destination']}"
        key_parts.append(flight_key)

    # Добавляем разделитель для рейсов "обратно"
    if itinerary['return_flights']:
        key_parts.append('||')
        for flight in itinerary['return_flights']:
            flight_key = f"{flight['carrier_id']}{flight['flight_number']}_{flight['source']}_{flight['destination']}"
            key_parts.append(flight_key)

    return '_'.join(key_parts)


def compare_routes(itineraries1: List[Dict], itineraries2: List[Dict]) -> Dict:
    """Сравнение маршрутов из двух файлов"""
    # Создаем словари для быстрого поиска по ключу маршрута
    file1_routes = {it['route_key']: it for it in itineraries1}
    file2_routes = {it['route_key']: it for it in itineraries2}

    # Находим общие маршруты
    common_keys = set(file1_routes.keys()) & set(file2_routes.keys())

    # Находим удаленные маршруты (есть в file1, но нет в file2)
    removed_keys = set(file1_routes.keys()) - set(file2_routes.keys())

    # Находим новые маршруты (есть в file2, но нет в file1)
    new_keys = set(file2_routes.keys()) - set(file1_routes.keys())

    # Сравниваем общие маршруты
    changed_routes = []
    for key in common_keys:
        route1 = file1_routes[key]
        route2 = file2_routes[key]

        changes = compare_single_route(route1, route2)
        if changes:
            changes['route_key'] = key
            changes['id_file1'] = route1['id']
            changes['id_file2'] = route2['id']
            changed_routes.append(changes)

    # Формируем результаты
    return {
        'summary': {
            'total_file1': len(file1_routes),
            'total_file2': len(file2_routes),
            'common': len(common_keys),
            'removed': len(removed_keys),
            'new': len(new_keys),
            'changed': len(changed_routes)
        },
        'removed_routes': [
            {
                'route_key': key,
                'id': file1_routes[key]['id'],
                'start_time': file1_routes[key]['start_time'].strftime('%Y-%m-%d %H:%M'),
                'end_time': file1_routes[key]['end_time'].strftime('%Y-%m-%d %H:%M'),
                'total_amount': file1_routes[key]['total_amount'],
                'currency': file1_routes[key]['currency']
            }
            for key in removed_keys
        ],
        'new_routes': [
            {
                'route_key': key,
                'id': file2_routes[key]['id'],
                'start_time': file2_routes[key]['start_time'].strftime('%Y-%m-%d %H:%M'),
                'end_time': file2_routes[key]['end_time'].strftime('%Y-%m-%d %H:%M'),
                'total_amount': file2_routes[key]['total_amount'],
                'currency': file2_routes[key]['currency']
            }
            for key in new_keys
        ],
        'changed_routes': changed_routes
    }


def compare_single_route(route1: Dict, route2: Dict) -> Dict:
    """Сравнение двух версий одного маршрута"""
    changes = {}

    # Сравнение времени начала
    if route1['start_time'] != route2['start_time']:
        changes['start_time'] = {
            'old': route1['start_time'].strftime('%Y-%m-%d %H:%M'),
            'new': route2['start_time'].strftime('%Y-%m-%d %H:%M')
        }

    # Сравнение времени окончания
    if route1['end_time'] != route2['end_time']:
        changes['end_time'] = {
            'old': route1['end_time'].strftime('%Y-%m-%d %H:%M'),
            'new': route2['end_time'].strftime('%Y-%m-%d %H:%M')
        }

    # Сравнение цены
    if route1['total_amount'] != route2['total_amount']:
        changes['price'] = {
            'old': route1['total_amount'],
            'new': route2['total_amount'],
            'currency': route2['currency'] or route1['currency'],
            'difference': route2['total_amount'] - route1['total_amount'] if route1['total_amount'] and route2[
                'total_amount'] else None
        }

    # Сравнение валюты
    if route1['currency'] != route2['currency']:
        changes['currency'] = {
            'old': route1['currency'],
            'new': route2['currency']
        }

    # Сравнение количества рейсов
    total_flights1 = len(route1['onward_flights']) + len(route1['return_flights'])
    total_flights2 = len(route2['onward_flights']) + len(route2['return_flights'])

    if total_flights1 != total_flights2:
        changes['flight_count'] = {
            'old': total_flights1,
            'new': total_flights2
        }

    return changes if changes else {}


def print_comparison_results(results: Dict):
    """Вывод результатов сравнения в консоль"""
    print("=" * 80)
    print("СРАВНЕНИЕ МАРШРУТОВ ИЗ ДВУХ XML ФАЙЛОВ")
    print("=" * 80)

    # Сводная информация
    summary = results['summary']
    print(f"\nСВОДНАЯ ИНФОРМАЦИЯ:")
    print(f"  Всего маршрутов в первом файле: {summary['total_file1']}")
    print(f"  Всего маршрутов во втором файле: {summary['total_file2']}")
    print(f"  Общих маршрутов: {summary['common']}")
    print(f"  Удалено маршрутов: {summary['removed']}")
    print(f"  Добавлено новых маршрутов: {summary['new']}")
    print(f"  Изменено маршрутов: {summary['changed']}")

    # Новые маршруты
    if results['new_routes']:
        print(f"\nНОВЫЕ МАРШРУТЫ (добавлены во втором файле):")
        for i, route in enumerate(results['new_routes'], 1):
            print(f"\n  {i}. Ключ маршрута: {route['route_key']}")
            print(f"     ID: {route['id']}")
            print(f"     Время начала: {route['start_time']}")
            print(f"     Время окончания: {route['end_time']}")
            if route['total_amount']:
                print(f"     Цена: {route['total_amount']} {route['currency']}")

    # Удаленные маршруты
    if results['removed_routes']:
        print(f"\nУДАЛЕННЫЕ МАРШРУТЫ (были в первом, но отсутствуют во втором):")
        for i, route in enumerate(results['removed_routes'], 1):
            print(f"\n  {i}. Ключ маршрута: {route['route_key']}")
            print(f"     ID: {route['id']}")
            print(f"     Время начала: {route['start_time']}")
            print(f"     Время окончания: {route['end_time']}")
            if route['total_amount']:
                print(f"     Цена: {route['total_amount']} {route['currency']}")

    # Измененные маршруты
    if results['changed_routes']:
        print(f"\nИЗМЕНЕННЫЕ МАРШРУТЫ:")
        for i, changes in enumerate(results['changed_routes'], 1):
            print(f"\n  {i}. Ключ маршрута: {changes['route_key']}")
            print(f"     ID в первом файле: {changes['id_file1']}")
            print(f"     ID во втором файле: {changes['id_file2']}")

            for change_type, change_data in changes.items():
                if change_type in ['route_key', 'id_file1', 'id_file2']:
                    continue

                if change_type == 'start_time':
                    print(f"     Изменено время начала: {change_data['old']} → {change_data['new']}")
                elif change_type == 'end_time':
                    print(f"     Изменено время окончания: {change_data['old']} → {change_data['new']}")
                elif change_type == 'price':
                    diff = change_data['difference']
                    diff_str = f" ({diff:+.2f})" if diff is not None else ""
                    print(
                        f"     Изменена цена: {change_data['old']} → "
                        f"{change_data['new']} {change_data['currency']}{diff_str}"
                    )
                elif change_type == 'currency':
                    print(f"     Изменена валюта: {change_data['old']} → {change_data['new']}")
                elif change_type == 'flight_count':
                    print(f"     Изменено количество рейсов: {change_data['old']} → {change_data['new']}")

    print("\n" + "=" * 80)


def save_results_to_excel(results: Dict, filename: str = 'comparison_results.xlsx'):
    """Сохранение результатов в Excel файл"""
    wb = Workbook()

    # Сводная информация
    ws1 = wb.active
    ws1.title = "Summary"
    ws1.append(["Параметр", "Значение"])
    for key, value in results['summary'].items():
        ws1.append([key.replace('_', ' ').title(), value])

    # Новые маршруты
    if results['new_routes']:
        ws2 = wb.create_sheet(title="New Routes")
        headers = [
            "№", "Ключ маршрута",
            "ID в файле 1", "ID в файле 2",
            "Изменения"
        ]
        ws2.append(headers)
        for i, route in enumerate(results['new_routes'], 1):
            ws2.append([
                i,
                route['route_key'],
                route['id'],
                route['start_time'],
                route['end_time'],
                route['total_amount'] or "",
                route['currency'] or ""
            ])

    # Удаленные маршруты
    if results['removed_routes']:
        ws3 = wb.create_sheet(title="Removed Routes")
        headers = ["№", "Ключ маршрута", "ID", "Время начала", "Время окончания", "Цена", "Валюта"]
        ws3.append(headers)
        for i, route in enumerate(results['removed_routes'], 1):
            ws3.append([
                i,
                route['route_key'],
                route['id'],
                route['start_time'],
                route['end_time'],
                route['total_amount'] or "",
                route['currency'] or ""
            ])

    # Измененные маршруты
    if results['changed_routes']:
        ws4 = wb.create_sheet(title="Changed Routes")
        headers = ["№", "Ключ маршрута", "ID в файле 1", "ID в файле 2", "Изменения"]
        ws4.append(headers)
        for i, changes in enumerate(results['changed_routes'], 1):
            change_descriptions = []
            for change_type, change_data in changes.items():
                if change_type in ['route_key', 'id_file1', 'id_file2']:
                    continue

                if change_type == 'start_time':
                    change_descriptions.append(f"Время начала: {change_data['old']} → {change_data['new']}")
                elif change_type == 'end_time':
                    change_descriptions.append(f"Время окончания: {change_data['old']} → {change_data['new']}")
                elif change_type == 'price':
                    diff = change_data['difference']
                    diff_str = f" ({diff:+.2f})" if diff is not None else ""
                    change_descriptions.append(
                        f"Цена: {change_data['old']} → {change_data['new']} {change_data['currency']}{diff_str}")
                elif change_type == 'currency':
                    change_descriptions.append(f"Валюта: {change_data['old']} → {change_data['new']}")
                elif change_type == 'flight_count':
                    change_descriptions.append(f"Количество рейсов: {change_data['old']} → {change_data['new']}")

            ws4.append([
                i,
                changes['route_key'],
                changes['id_file1'],
                changes['id_file2'],
                "; ".join(change_descriptions)
            ])

    # Сохраняем файл
    wb.save(f'results/{filename}')
    print(f"\nРезультаты сохранены в файл: results/{filename}")


def save_detailed_info(itineraries1, itineraries2):
    """Сохранение детальной информации о маршрутах"""
    wb = Workbook()

    # Детальная информация о маршрутах из первого файла
    ws1 = wb.active
    ws1.title = "RS_Via-3"
    headers = ["ID", "Ключ маршрута", "Время начала", "Время окончания", "Цена", "Валюта",
               "Рейсов туда", "Рейсов обратно", "Всего рейсов"]
    ws1.append(headers)

    for it in itineraries1:
        ws1.append([
            it['id'],
            it['route_key'],
            it['start_time'].strftime('%Y-%m-%d %H:%M'),
            it['end_time'].strftime('%Y-%m-%d %H:%M'),
            it['total_amount'] or "",
            it['currency'] or "",
            len(it['onward_flights']),
            len(it['return_flights']),
            len(it['onward_flights']) + len(it['return_flights'])
        ])

    # Детальная информация о маршрутах из второго файла
    ws2 = wb.create_sheet(title="RS_ViaOW")
    ws2.append(headers)

    for it in itineraries2:
        ws2.append([
            it['id'],
            it['route_key'],
            it['start_time'].strftime('%Y-%m-%d %H:%M'),
            it['end_time'].strftime('%Y-%m-%d %H:%M'),
            it['total_amount'] or "",
            it['currency'] or "",
            len(it['onward_flights']),
            len(it['return_flights']),
            len(it['onward_flights']) + len(it['return_flights'])
        ])

    wb.save('results/routes_detailed.xlsx')
    print("✓ Детальная информация о маршрутах сохранена в results/routes_detailed.xlsx")


def main():
    """Основная функция приложения"""
    print("XML Route Comparator")
    print("=" * 60)

    # Создаем директорию для результатов, если ее нет
    os.makedirs('results', exist_ok=True)

    # Загружаем XML файлы
    print("\nЗагрузка XML файлов...")

    try:
        # Читаем содержимое файлов
        xml1_content = read_xml_file('xml_files/RS_Via-3.xml')
        xml2_content = read_xml_file('xml_files/RS_ViaOW.xml')

        print("✓ Файлы успешно загружены")

        # Парсим первый файл
        print("\nПарсинг первого файла (RS_Via-3.xml)...")
        itineraries1 = extract_itineraries(xml1_content)
        print(f"✓ Найдено маршрутов: {len(itineraries1)}")

        # Парсим второй файл
        print("Парсинг второго файла (RS_ViaOW.xml)...")
        itineraries2 = extract_itineraries(xml2_content)
        print(f"✓ Найдено маршрутов: {len(itineraries2)}")

        # Сравниваем маршруты
        print("\nСравнение маршрутов...")
        comparison_results = compare_routes(itineraries1, itineraries2)

        # Выводим результаты
        print("\n" + "=" * 60)
        print_comparison_results(comparison_results)

        # Сохраняем результаты в Excel
        print("\nСохранение результатов в Excel...")
        save_results_to_excel(comparison_results, 'route_comparison.xlsx')

        # Дополнительно сохраняем детальную информацию о маршрутах
        save_detailed_info(itineraries1, itineraries2)

        print("\n" + "=" * 60)
        print("Анализ завершен успешно!")

    except FileNotFoundError as e:
        print(f"✗ Ошибка: Файл не найден - {e}")
        print("Убедитесь, что файлы RS_Via-3.xml и RS_ViaOW.xml находятся в папке xml_files/")
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()