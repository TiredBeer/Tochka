import unittest
from typing import List, Dict
from run import check_capacity


class TestCheckCapacity(unittest.TestCase):
    def test_check_capacity_cases(self) -> None:
        """
        Проверяет корректность работы функции check_capacity для разных сценариев:
        """
        cases: List[tuple[str, int, List[Dict[str, str]], bool]] = [
            ("no_guests", 10, [], True),
            ("single_guest_fits", 1, [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-02"}
            ], True),
            ("single_guest_too_many", 0, [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-02"}
            ], False),
            ("non_overlapping_guests", 1, [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-03"},
                {"name": "B", "check-in": "2021-01-03",
                 "check-out": "2021-01-05"}
            ], True),
            ("overlapping_guests_fits", 3, [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-04"},
                {"name": "B", "check-in": "2021-01-02",
                 "check-out": "2021-01-05"},
                {"name": "C", "check-in": "2021-01-03",
                 "check-out": "2021-01-06"}
            ], True),
            ("overlapping_guests_too_many", 2, [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-04"},
                {"name": "B", "check-in": "2021-01-02",
                 "check-out": "2021-01-05"},
                {"name": "C", "check-in": "2021-01-03",
                 "check-out": "2021-01-06"}
            ], False),
            ("unordered_input_fits", 2, [
                {"name": "B", "check-in": "2021-01-05",
                 "check-out": "2021-01-10"},
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-03"},
                {"name": "C", "check-in": "2021-01-02",
                 "check-out": "2021-01-06"}
            ], True),
            ("unordered_input_too_many", 1, [
                {"name": "B", "check-in": "2021-01-05",
                 "check-out": "2021-01-10"},
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-03"},
                {"name": "C", "check-in": "2021-01-02",
                 "check-out": "2021-01-06"}
            ], False),
            ("edge_case_same_day_checkout_checkin", 1, [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-02"},
                {"name": "B", "check-in": "2021-01-02",
                 "check-out": "2021-01-03"}
            ], True)
        ]

        for name, max_capacity, guests, expected in cases:
            with self.subTest(case=name):
                result: bool = check_capacity(max_capacity, guests)
                self.assertEqual(
                    result,
                    expected,
                    msg=f'Case "{name}": expected {expected}, got {result}'
                )


if __name__ == "__main__":
    unittest.main()
