import itertools
import collections
import random
from typing import List, Tuple
from run2 import solve


def naive_solve(grid: List[List[str]]) -> int:
    """
    Наивная реализация решения задачи о роботах в лабиринте для небольшого числа ключей (<=3).
    Перебирает все возможные порядки сбора ключей и назначения роботов.
    """
    n, m = len(grid), len(grid[0])
    starts: List[Tuple[int, int]] = []
    key_positions: dict[str, Tuple[int, int]] = {}

    for i in range(n):
        for j in range(m):
            c = grid[i][j]
            if c == '@':
                starts.append((i, j))
            elif 'a' <= c <= 'z':
                key_positions[c] = (i, j)
    keys = sorted(key_positions)
    K = len(keys)

    def bfs(start: Tuple[int, int],
            target: Tuple[int, int],
            collected: set[str]
            ) -> int | None:
        """
        Находит кратчайшее расстояние от start до target,
        учитывая собранные ключи (для прохода через двери).
        """
        sx, sy = start
        tx, ty = target
        dq = collections.deque([(sx, sy, 0)])
        visited = [[False] * m for _ in range(n)]
        visited[sx][sy] = True
        while dq:
            x, y, d = dq.popleft()
            if (x, y) == (tx, ty):
                return d
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < n and 0 <= ny < m):
                    continue
                if visited[nx][ny]:
                    continue
                cell = grid[nx][ny]
                if cell == '#':
                    continue
                if 'A' <= cell <= 'Z' and cell.lower() not in collected:
                    continue
                visited[nx][ny] = True
                dq.append((nx, ny, d + 1))
        return None

    best = float('inf')

    for order in itertools.permutations(keys):
        for assign in itertools.product(range(4), repeat=K):
            positions = list(starts)
            collected: set[str] = set()
            steps = 0
            ok = True
            for key, robot in zip(order, assign):
                dist = bfs(positions[robot], key_positions[key], collected)
                if dist is None:
                    ok = False
                    break
                steps += dist
                positions[robot] = key_positions[key]
                collected.add(key)
            if ok:
                best = min(best, steps)
    return -1 if best == float('inf') else best


def generate_random_grid(n: int,
                         m: int,
                         max_keys: int = 3,
                         wall_prob: float = 0.2
                         ) -> List[str]:
    """
    Генерирует случайный лабиринт в виде списка строк:
      - '.' — пустые клетки,
      - '#' — стены с вероятностью wall_prob,
      - '@' — четыре стартовые позиции,
      - 'a'.. — ключи, 'A'.. — двери.
    """
    grid: List[List[str]] = [['.' for _ in range(m)] for _ in range(n)]
    for i in range(1, n - 1):
        for j in range(1, m - 1):
            if random.random() < wall_prob:
                grid[i][j] = '#'

    empties = [(i, j) for i in range(n) for j in range(m) if grid[i][j] == '.']
    random.shuffle(empties)
    for x, y in empties[:4]:
        grid[x][y] = '@'

    K = random.randint(1, max_keys)
    remains = [pos for pos in empties if pos not in empties[:4]]
    random.shuffle(remains)
    key_positions = remains[:K]
    door_positions = remains[K:2 * K]
    for idx, (kx, ky) in enumerate(key_positions):
        key = chr(ord('a') + idx)
        door = key.upper()
        grid[kx][ky] = key
        dx, dy = door_positions[idx]
        grid[dx][dy] = door
    return [''.join(row) for row in grid]


def run_stress_tests(number_tests: int = 50,
                     n: int = 10,
                     m: int = 10,
                     max_keys: int = 3
                     ) -> None:
    """
    Сравнивает наивное и оптимальное решения на случайных лабиринтах.
    Выводит результаты и количество несовпадений.
    """
    print(f"Запуск {number_tests} случайных тестов")
    mismatches = 0
    for i in range(number_tests):
        lines = generate_random_grid(n, m, max_keys)
        grid = [list(line) for line in lines]
        res_fast = solve(grid)
        res_naive = naive_solve(grid)
        if res_fast != res_naive:
            mismatches += 1
            print(
                f"Несоответствие в тесте #{i}: opt={res_fast}, naive={res_naive}")
            for row in grid:
                print(''.join(row))
            print()

    if mismatches == 0:
        print("Все тесты пройдены")
    else:
        print(f"Количество проваленных тестов: {mismatches}")


if __name__ == '__main__':
    run_stress_tests()
