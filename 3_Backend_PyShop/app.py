from pprint import pprint
import random
import math
from typing import List, Dict, Tuple

TIMESTAMPS_COUNT = 50000
PROBABILITY_SCORE_CHANGED = 0.0001
PROBABILITY_HOME_SCORE = 0.45
OFFSET_MAX_STEP = 3

INITIAL_STAMP = {
    "offset": 0,
    "score": {
        "home": 0,
        "away": 0
    }
}


def generate_stamp(previous_value):
    score_changed = random.random() > 1 - PROBABILITY_SCORE_CHANGED
    home_score_change = 1 if score_changed and random.random() > 1 - \
                             PROBABILITY_HOME_SCORE else 0
    away_score_change = 1 if score_changed and not home_score_change else 0
    offset_change = math.floor(random.random() * OFFSET_MAX_STEP) + 1

    return {
        "offset": previous_value["offset"] + offset_change,
        "score": {
            "home": previous_value["score"]["home"] + home_score_change,
            "away": previous_value["score"]["away"] + away_score_change
        }
    }


def generate_game():
    stamps = [INITIAL_STAMP, ]
    current_stamp = INITIAL_STAMP
    for _ in range(TIMESTAMPS_COUNT):
        current_stamp = generate_stamp(current_stamp)
        stamps.append(current_stamp)

    return stamps


def get_score(game_stamps: List[Dict], offset: int) -> Tuple[int, int]:
    """
    Возвращает счет на момент указанного offset.

    Args:
        game_stamps: Список штампов игры, отсортированный по offset
        offset: Временная метка, для которой нужно получить счет

    Returns:
        Кортеж (home_score, away_score) на момент offset

    Особенности:
        - Если offset меньше 0, возвращает начальный счет (0, 0)
        - Если offset превышает максимальный в списке, возвращает последний известный счет
        - Использует бинарный поиск для эффективного поиска в большом списке
    """
    if not game_stamps or offset < 0:
        return 0, 0

    # Бинарный поиск для эффективности
    left, right = 0, len(game_stamps) - 1
    result_index = 0

    while left <= right:
        mid = (left + right) // 2
        current_offset = game_stamps[mid]["offset"]

        if current_offset == offset:
            result_index = mid
            break
        elif current_offset < offset:
            result_index = mid
            left = mid + 1
        else:
            right = mid - 1

    # result_index содержит индекс последнего штампа с offset <= заданному
    last_stamp = game_stamps[result_index]
    return last_stamp["score"]["home"], last_stamp["score"]["away"]


# Пример использования
if __name__ == "__main__":
    # Генерация данных
    game_stamps = generate_game()

    # Тестирование функции
    test_offsets = [0, 10, 100, 1000, 50000, 100000]

    print("Тестирование функции get_score:")
    print("-" * 40)
    for offset in test_offsets:
        home, away = get_score(game_stamps, offset)
        print(f"Offset {offset:6d}: Домашние = {home}, Гости = {away}")

    # Вывод информации о сгенерированных данных
    print(f"\nВсего штампов: {len(game_stamps)}")
    print(f"Максимальный offset: {game_stamps[-1]['offset']}")
    print(f"Финальный счет: Домашние {game_stamps[-1]['score']['home']} - "
          f"Гости {game_stamps[-1]['score']['away']}")