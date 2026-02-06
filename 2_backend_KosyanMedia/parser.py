import xmltodict
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
import pandas as pd


class XMLParser:
    """Класс для парсинга XML файлов с маршрутами"""

    def __init__(self, xml_content: str):
        self.xml_content = xml_content
        self.data = None

    def parse(self) -> Dict:
        """Парсинг XML в словарь"""
        self.data = xmltodict.parse(self.xml_content)
        return self.data

    def extract_itineraries(self) -> List[Dict]:
        """Извлечение маршрутов из XML"""
        if not self.data:
            self.parse()

        itineraries = []

        # Получаем список маршрутов
        priced_itineraries = self.data.get('AirFareSearchResponse', {}).get('PricedItineraries', {})

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
                itinerary['onward_flights'] = self._process_flights(onward_flights)

            # Извлекаем рейсы "обратно" (если есть)
            return_itinerary = flight_group.get('ReturnPricedItinerary', {})
            if return_itinerary:
                return_flights = return_itinerary.get('Flights', {}).get('Flight', [])
                if not isinstance(return_flights, list):
                    return_flights = [return_flights]
                itinerary['return_flights'] = self._process_flights(return_flights)

            # Извлекаем информацию о цене
            pricing = flight_group.get('Pricing', {})
            if pricing:
                itinerary['currency'] = pricing.get('@currency')
                service_charges = pricing.get('ServiceCharges', [])
                if not isinstance(service_charges, list):
                    service_charges = [service_charges]

                for charge in service_charges:
                    if charge.get('@type') == 'SingleAdult' and charge.get('@ChargeType') == 'TotalAmount':
                        itinerary['total_amount'] = float(charge.get('#text', 0))
                        break

            # Рассчитываем время начала и конца маршрута
            itinerary['start_time'], itinerary['end_time'] = self._calculate_route_times(itinerary)

            # Генерируем уникальный ключ для маршрута
            itinerary['route_key'] = self._generate_route_key(itinerary)

            itineraries.append(itinerary)

        return itineraries

    def _process_flights(self, flights: List[Dict]) -> List[Dict]:
        """Обработка списка рейсов"""
        processed_flights = []
        for flight in flights:
            processed_flight = {
                'carrier_id': flight.get('Carrier', {}).get('@id', ''),
                'carrier_name': flight.get('Carrier', {}).get('#text', ''),
                'flight_number': flight.get('FlightNumber', ''),
                'source': flight.get('Source', ''),
                'destination': flight.get('Destination', ''),
                'departure_time': self._parse_timestamp(flight.get('DepartureTimeStamp', '')),
                'arrival_time': self._parse_timestamp(flight.get('ArrivalTimeStamp', '')),
                'class': flight.get('Class', ''),
                'stops': int(flight.get('NumberOfStops', 0))
            }
            processed_flights.append(processed_flight)
        return processed_flights

    def _parse_timestamp(self, timestamp: str) -> datetime:
        """Парсинг временной метки"""
        try:
            # Формат: 2015-10-22T0005
            if 'T' in timestamp:
                date_part, time_part = timestamp.split('T')
                if len(time_part) == 4:
                    time_part = f"{time_part[:2]}:{time_part[2:]}"
                timestamp = f"{date_part} {time_part}"
            return datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
        except:
            return datetime.min

    def _calculate_route_times(self, itinerary: Dict) -> Tuple[datetime, datetime]:
        """Расчет времени начала и конца маршрута"""
        all_flights = itinerary['onward_flights'] + itinerary['return_flights']
        if not all_flights:
            return datetime.min, datetime.min

        departure_times = [f['departure_time'] for f in all_flights]
        arrival_times = [f['arrival_time'] for f in all_flights]

        start_time = min(departure_times)
        end_time = max(arrival_times)

        return start_time, end_time

    def _generate_route_key(self, itinerary: Dict) -> str:
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

    def get_summary(self) -> Dict:
        """Получение сводной информации о файле"""
        itineraries = self.extract_itineraries()

        return {
            'total_itineraries': len(itineraries),
            'routes': [
                {
                    'id': it['id'],
                    'route_key': it['route_key'],
                    'total_flights': len(it['onward_flights']) + len(it['return_flights']),
                    'start_time': it['start_time'].strftime('%Y-%m-%d %H:%M'),
                    'end_time': it['end_time'].strftime('%Y-%m-%d %H:%M'),
                    'total_amount': it['total_amount'],
                    'currency': it['currency']
                }
                for it in itineraries
            ]
        }