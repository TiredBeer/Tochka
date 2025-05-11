import json
from datetime import datetime


def parse_date(date_str: str) -> datetime.date:
    """
    Парсит строку в формате YYYY-MM-DD в объект datetime.date.
    """
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def check_capacity(max_capacity: int, guests: list) -> bool:
    """
    Проверяет, не превышает ли число одновременно проживающих гостей заданную вместимость.
    """
    events = []
    for guest in guests:
        check_in = parse_date(guest["check-in"])
        check_out = parse_date(guest["check-out"])
        events.append((check_in, 1))
        events.append((check_out, -1))
    events.sort()

    current = 0
    for date, delta in events:
        current += delta
        if current > max_capacity:
            return False
    return True


if __name__ == "__main__":
    max_capacity = int(input())
    n = int(input())

    guests = []
    for _ in range(n):
        guest_json = input()
        guest_data = json.loads(guest_json)
        guests.append(guest_data)

    result = check_capacity(max_capacity, guests)
    print(result)
