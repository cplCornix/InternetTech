from typing import Dict, List, Any, Tuple
import pandas as pd
from datetime import datetime


class RouteComparator:
    """Класс для сравнения маршрутов из двух XML файлов"""

    def __init__(self, file1_itineraries: List[Dict], file2_itineraries: List[Dict]):
        self.file1_itineraries = file1_itineraries
        self.file2_itineraries = file2_itineraries
        self.comparison_results = {}

    def compare(self) -> Dict:
        """Основной метод сравнения"""
        # Создаем словари для быстрого поиска по ключу маршрута
        file1_routes = {it['route_key']: it for it in self.file1_itineraries}
        file2_routes = {it['route_key']: it for it in self.file2_itineraries}

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

            changes = self._compare_single_route(route1, route2)
            if changes:
                changes['route_key'] = key
                changes['id_file1'] = route1['id']
                changes['id_file2'] = route2['id']
                changed_routes.append(changes)

        # Формируем результаты
        self.comparison_results = {
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

        return self.comparison_results

    def _compare_single_route(self, route1: Dict, route2: Dict) -> Dict:
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

    def print_comparison_results(self):
        """Вывод результатов сравнения в консоль"""
        results = self.comparison_results

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
                            f"     Изменена цена: {change_data['old']} → {change_data['new']} {change_data['currency']}{diff_str}")
                    elif change_type == 'currency':
                        print(f"     Изменена валюта: {change_data['old']} → {change_data['new']}")
                    elif change_type == 'flight_count':
                        print(f"     Изменено количество рейсов: {change_data['old']} → {change_data['new']}")

        print("\n" + "=" * 80)

    def save_results_to_excel(self, filename: str = 'comparison_results.xlsx'):
        """Сохранение результатов в Excel файл"""
        results = self.comparison_results

        with pd.ExcelWriter(f'results/{filename}', engine='openpyxl') as writer:
            # Сводная информация
            summary_df = pd.DataFrame([results['summary']])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Новые маршруты
            if results['new_routes']:
                new_df = pd.DataFrame(results['new_routes'])
                new_df.to_excel(writer, sheet_name='New Routes', index=False)

            # Удаленные маршруты
            if results['removed_routes']:
                removed_df = pd.DataFrame(results['removed_routes'])
                removed_df.to_excel(writer, sheet_name='Removed Routes', index=False)

            # Измененные маршруты
            if results['changed_routes']:
                # Преобразуем сложную структуру в плоскую таблицу
                flat_changes = []
                for change in results['changed_routes']:
                    flat_change = {
                        'route_key': change['route_key'],
                        'id_file1': change['id_file1'],
                        'id_file2': change['id_file2']
                    }

                    for change_type, change_data in change.items():
                        if change_type in ['route_key', 'id_file1', 'id_file2']:
                            continue

                        if isinstance(change_data, dict):
                            for key, value in change_data.items():
                                flat_change[f"{change_type}_{key}"] = value

                    flat_changes.append(flat_change)

                changed_df = pd.DataFrame(flat_changes)
                changed_df.to_excel(writer, sheet_name='Changed Routes', index=False)

        print(f"\nРезультаты сохранены в файл: results/{filename}")