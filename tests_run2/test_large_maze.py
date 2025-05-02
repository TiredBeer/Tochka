import unittest
import time
from run2 import solve


class TestNoWallsLargeMaze(unittest.TestCase):
    def test_grid_100x100(self):
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
        for row in grid:
            print(*row)
        start = time.time()
        result = solve(grid)
        self.assertIsInstance(result, int)
        self.assertLess(time.time() - start, 60.0)


if __name__ == "__main__":
    unittest.main()
