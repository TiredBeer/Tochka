import itertools
import collections
import random
from run2 import solve


def naive_solve(grid):
    n, m = len(grid), len(grid[0])
    starts = []
    key_positions = {}
    for i in range(n):
        for j in range(m):
            c = grid[i][j]
            if c == '@':
                starts.append((i, j))
            elif 'a' <= c <= 'z':
                key_positions[c] = (i, j)

    keys = sorted(key_positions.keys())

    def bfs(start, target, collected):
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
        for assign in itertools.product(range(4), repeat=len(keys)):
            positions = list(starts)
            collected = set()
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


def generate_random_grid(n, m, max_keys=3, wall_prob=0.2):
    grid = [['.' for _ in range(m)] for _ in range(n)]
    for i in range(1, n - 1):
        for j in range(1, m - 1):
            if random.random() < wall_prob:
                grid[i][j] = '#'

    empties = [(i, j) for i in range(0, n - 1) for j in range(0, m - 1) if
               grid[i][j] == '.']

    random.shuffle(empties)
    starts = empties[:4]
    for x, y in starts:
        grid[x][y] = '@'

    K = random.randint(1, max_keys)
    empties = [pos for pos in empties if pos not in starts]
    random.shuffle(empties)
    key_positions = empties[:K]
    door_positions = empties[K:2 * K]
    keys = []

    for idx, (kx, ky) in enumerate(key_positions):
        key = chr(ord('a') + idx)
        door = key.upper()
        grid[kx][ky] = key
        dx, dy = door_positions[idx]
        grid[dx][dy] = door
        keys.append(key)

    return [''.join(row) for row in grid]


def run_stress_tests(number_tests=50, n=10, m=10, max_keys=3):
    print(f"Запуск {number_tests} случайных тестов")

    mismatches = 0
    for i in range(number_tests):
        lines = generate_random_grid(n, m, max_keys)
        grid = [list(line) for line in lines]
        res_fast = solve(grid)
        res_naive = naive_solve(grid)
        if res_fast != res_naive:
            mismatches += 1
            print(f"Несоответствие в тесте {i}")
            print(f"res_fast: {res_fast}\nres_naive: {res_naive}")
            for row in grid:
                print(*row)
            print()

    if mismatches == 0:
        print("Все тесты пройдены")
    else:
        print(f"Количество проваленных тестов: {mismatches}")


if __name__ == '__main__':
    run_stress_tests()
