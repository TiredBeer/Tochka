import json
from datetime import datetime


def check_capacity(max_capacity: int, guests: list) -> bool:
    events = []
    for g in guests:
        check_in = datetime.strptime(g["check-in"], "%Y-%m-%d").date()
        check_out = datetime.strptime(g["check-out"], "%Y-%m-%d").date()
        events.append((check_in, 1))
        events.append((check_out, -1))
    events.sort(key=lambda x: (x[0], x[1]))

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
