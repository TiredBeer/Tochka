import unittest
from run import check_capacity


class TestCheckCapacity(unittest.TestCase):
    cases = [
        {
            "name": "no guests",
            "max_capacity": 10,
            "guests": [],
            "expected": True
        },
        {
            "name": "single guest fits",
            "max_capacity": 1,
            "guests": [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-02"}
            ],
            "expected": True
        },
        {
            "name": "single guest too many",
            "max_capacity": 0,
            "guests": [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-02"}
            ],
            "expected": False
        },
        {
            "name": "non overlapping guests",
            "max_capacity": 1,
            "guests": [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-03"},
                {"name": "B", "check-in": "2021-01-03",
                 "check-out": "2021-01-05"},
            ],
            "expected": True
        },
        {
            "name": "overlapping guests fits",
            "max_capacity": 3,
            "guests": [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-04"},
                {"name": "B", "check-in": "2021-01-02",
                 "check-out": "2021-01-05"},
                {"name": "C", "check-in": "2021-01-03",
                 "check-out": "2021-01-06"},
            ],
            "expected": True
        },
        {
            "name": "overlapping guests too many",
            "max_capacity": 2,
            "guests": [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-04"},
                {"name": "B", "check-in": "2021-01-02",
                 "check-out": "2021-01-05"},
                {"name": "C", "check-in": "2021-01-03",
                 "check-out": "2021-01-06"},
            ],
            "expected": False
        },
        {
            "name": "unordered input fits",
            "max_capacity": 2,
            "guests": [
                {"name": "B", "check-in": "2021-01-05",
                 "check-out": "2021-01-10"},
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-03"},
                {"name": "C", "check-in": "2021-01-02",
                 "check-out": "2021-01-06"},
            ],
            "expected": True
        },
        {
            "name": "unordered input too many",
            "max_capacity": 1,
            "guests": [
                {"name": "B", "check-in": "2021-01-05",
                 "check-out": "2021-01-10"},
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-03"},
                {"name": "C", "check-in": "2021-01-02",
                 "check-out": "2021-01-06"},
            ],
            "expected": False
        },
        {
            "name": "edge case same day checkout and checkin",
            "max_capacity": 1,
            "guests": [
                {"name": "A", "check-in": "2021-01-01",
                 "check-out": "2021-01-02"},
                {"name": "B", "check-in": "2021-01-02",
                 "check-out": "2021-01-03"},
            ],
            "expected": True
        }
    ]

    def test_check_capacity(self):
        for case in self.cases:
            with self.subTest(case=case["name"]):
                result = check_capacity(case["max_capacity"], case["guests"])
                self.assertEqual(
                    result,
                    case["expected"],
                    msg=f'Failed case "{case["name"]}": '
                        f'got {result}, expected {case["expected"]}'
                )


if __name__ == "__main__":
    unittest.main()
