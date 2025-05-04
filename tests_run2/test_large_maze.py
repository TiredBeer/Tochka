import unittest
import time
import random
from run2 import solve


class TestNoWallsLargeMaze(unittest.TestCase):
    def test_grid_100x100_with_26_keys(self):
        n = 100
        grid = [['.'] * n for _ in range(n)]
        grid[0][0] = '@'
        grid[0][n - 1] = '@'
        grid[n - 1][0] = '@'
        grid[n - 1][n - 1] = '@'
        row_keys = n // 2 - 1
        row_doors = n // 2
        for i in range(26):
            key = chr(ord('a') + i)
            door = key.upper()
            col = 2 + i * 3
            grid[row_keys][col] = key
            grid[row_doors][col] = door
        start = time.time()
        result = solve(grid)
        self.assertIsInstance(result, int)
        self.assertLess(time.time() - start, 60.0)

    def test_grid_100x100_with_walls_and_26_keys(self):
        random.seed(0)
        n = 100
        grid = [['#'] * n for _ in range(n)]

        for i in range(1, n - 1):
            for j in range(1, n - 1):
                grid[i][j] = '#' if random.random() < 0.2 else '.'

        grid[1][1] = '@'
        grid[1][n - 2] = '@'
        grid[n - 2][1] = '@'
        grid[n - 2][n - 2] = '@'
        row_keys = n // 2 - 2
        row_doors = n // 2 + 1
        for idx in range(26):
            key = chr(ord('a') + idx)
            door = key.upper()
            col = 2 + idx * 3
            grid[row_keys][col] = key
            grid[row_doors][col] = door
            grid[row_keys - 1][col] = '.'
            grid[row_doors + 1][col] = '.'

        start = time.time()
        result = solve(grid)
        self.assertIsInstance(result, int)
        self.assertLess(time.time() - start, 60.0)


if __name__ == "__main__":
    unittest.main()
