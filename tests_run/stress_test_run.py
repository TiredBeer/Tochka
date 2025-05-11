import random
from datetime import datetime, timedelta
from run import check_capacity, parse_date


def naive_check_capacity(max_capacity: int,
                         guests: list[dict[str, str]]) -> bool:
    """
    Проверяет корректность работы check_capacity простым алгоритмом полного перебора:
    Для каждого момента заезда считает число гостей и сравнивает с max_capacity.
    """
    intervals: list[any] = []
    for guest in guests:
        check_in = parse_date(guest["check-in"])
        check_out = parse_date(guest["check-out"])
        intervals.append((check_in, check_out))
    for check_in, _ in intervals:
        count = 0
        for start, end in intervals:
            if start <= check_in < end:
                count += 1
            if count > max_capacity:
                return False
    return True


def generate_guests(n: int, days: int = 365) -> list[dict[str, str]]:
    """
    Генерирует список n случайных гостей с датами заезда и выезда.
    """
    base = datetime(2021, 1, 1).date()
    guests: list[dict[str, str]] = []
    for i in range(n):
        ci_offset = random.randint(0, days - 1)
        length = random.randint(1, days - ci_offset)
        ci = base + timedelta(days=ci_offset)
        co = ci + timedelta(days=length)
        guests.append({
            "name": str(i),
            "check-in": ci.isoformat(),
            "check-out": co.isoformat()
        })
    return guests


def stress_test(number_tests: int = 1000, max_n: int = 100) -> None:
    """
    Запускает серию стохастических тестов, сравнивая результаты check_capacity и naive_check_capacity.
    """
    mismatches = 0
    print(f"Запуск {number_tests} случайных тестов")

    for i in range(1, number_tests + 1):
        n = random.randint(1, max_n)
        cap = random.randint(0, n)
        guests = generate_guests(n)

        res_fast = check_capacity(cap, guests)
        res_naive = naive_check_capacity(cap, guests)

        if res_fast != res_naive:
            mismatches += 1
            print(f"Несоответствие в тесте {i}: n={n}, cap={cap}")
            print("guests =", guests)
            print("Текущий ответ:", res_fast)
            print("Предполагаемый ответ:", res_naive)
            print()

    if mismatches == 0:
        print("Все тесты пройдены")
    else:
        print(f"Количество проваленных тестов: {mismatches}")


if __name__ == '__main__':
    stress_test()
