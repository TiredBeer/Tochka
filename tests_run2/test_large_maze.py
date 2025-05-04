import unittest
import time
import random
from typing import List
from run2 import solve


class TestLargeMaze(unittest.TestCase):
    def test_grid_100x100_with_26_keys(self) -> None:
        """
        Проверяет корректность и время выполнения на пустом поле 100×100 с 26 ключами в двух строках.
        Ожидается целочисленный результат и время работы менее 60 секунд.
        """
        n: int = 100
        grid: List[List[str]] = [['.'] * n for _ in range(n)]
        grid[0][0] = '@'
        grid[0][n - 1] = '@'
        grid[n - 1][0] = '@'
        grid[n - 1][n - 1] = '@'
        row_keys: int = n // 2 - 1
        row_doors: int = n // 2

        for i in range(26):
            key: str = chr(ord('a') + i)
            door: str = key.upper()
            col: int = 2 + i * 3
            grid[row_keys][col] = key
            grid[row_doors][col] = door

        start: float = time.time()
        result: int = solve(grid)
        duration: float = time.time() - start
        self.assertIsInstance(result, int)
        self.assertLess(duration, 60.0)

    def test_grid_100x100_with_walls_and_26_keys(self) -> None:
        """
        Тестирует алгоритм на лабиринте 100×100 с 20% случайных стен и 26 ключами.
        Проверяется, что решение возвращает int и укладывается в 60 секунд.
        """
        random.seed(0)
        n: int = 100
        grid: List[List[str]] = [['#'] * n for _ in range(n)]
        for i in range(1, n - 1):
            for j in range(1, n - 1):
                grid[i][j] = '#' if random.random() < 0.2 else '.'
        grid[1][1] = '@'
        grid[1][n - 2] = '@'
        grid[n - 2][1] = '@'
        grid[n - 2][n - 2] = '@'
        row_keys: int = n // 2 - 2
        row_doors: int = n // 2 + 1

        for idx in range(26):
            key: str = chr(ord('a') + idx)
            door: str = key.upper()
            col: int = 2 + idx * 3
            grid[row_keys][col] = key
            grid[row_doors][col] = door
            grid[row_keys - 1][col] = '.'
            grid[row_doors + 1][col] = '.'

        start: float = time.time()
        result: int = solve(grid)
        duration: float = time.time() - start
        self.assertIsInstance(result, int)
        self.assertLess(duration, 60.0)


if __name__ == "__main__":
    unittest.main()
