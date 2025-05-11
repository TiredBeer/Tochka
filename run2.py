import sys
from collections import deque, defaultdict
import heapq
from dataclasses import dataclass, field


def get_input() -> list[list[str]]:
    """
    Читает входной лабиринт из стандартного ввода и возвращает список списков символов.
    """
    return [list(line.strip("\n")) for line in sys.stdin]


@dataclass(order=True)
class PriorityQueueEntry:
    """
    Элемент очереди приоритетов для A*: хранит приоритет f, текущую стоимость g и состояние.
    """
    priority: int
    cost: int = field(compare=False)
    state: tuple = field(compare=False)


def parse_grid(grid: list[list[str]]
               ) -> tuple[list[tuple[int, int]], dict[str, tuple[int, int]]]:
    """
    Находит стартовые позиции роботов и позиции ключей в сетке.
    Возвращает количество строк, количество столбцов, список стартовых позиций и словарь ключ->позиция.
    """
    num_rows = len(grid)
    num_cols = len(grid[0])
    start_positions = []
    key_positions = {}
    for row_index in range(num_rows):
        for col_index in range(num_cols):
            cell = grid[row_index][col_index]
            if cell == '@':
                start_positions.append((row_index, col_index))
            elif 'a' <= cell <= 'z':
                key_positions[cell] = (row_index, col_index)
    return start_positions, key_positions


def index_points(
        start_positions: list[tuple[int, int]],
        key_positions: dict[str, tuple[int, int]]
) -> tuple[list[tuple[int, int]], dict[tuple[int, int], int], int]:
    """
    Строит полный список точек интереса: сначала стартовые позиции, затем позиции ключей в лексикографическом порядке.
    Возвращает список точек, словарь координат->индекс и число ключей.
    """
    sorted_keys = sorted(key_positions)
    number_of_keys = len(sorted_keys)
    all_points = start_positions + [key_positions[key] for key in sorted_keys]
    coordinate_to_index = {point: index for index, point in
                           enumerate(all_points)}
    return all_points, coordinate_to_index, number_of_keys


def build_reachability_graph(
        grid: list[list[str]],
        points: list[tuple[int, int]],
        coordinate_to_index: dict[tuple[int, int], int]
) -> list[dict[int, list[tuple[int, int]]]]:
    """
    Для каждой точки рассчитывает все достижимые другие точки вместе с маской дверей и расстоянием.
    Возвращает список словарей: graph[source_index][target_index] = [(door_mask, distance), ...].
    """
    number_of_points = len(points)
    num_rows, num_cols = len(grid), len(grid[0])
    graph = [defaultdict(list) for _ in range(number_of_points)]

    for source_index, (start_row, start_col) in enumerate(points):
        visited_masks = {(start_row, start_col): [0]}
        bfs_queue = deque(
            [(start_row, start_col, 0, 0)])

        while bfs_queue:
            row, col, distance, door_mask = bfs_queue.popleft()
            target_index = coordinate_to_index.get((row, col))
            if target_index is not None and target_index != source_index:
                graph[source_index][target_index].append((door_mask, distance))

            for d_row, d_col in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                new_row, new_col = row + d_row, col + d_col
                if not (0 <= new_row < num_rows and 0 <= new_col < num_cols):
                    continue
                cell_value = grid[new_row][new_col]
                if cell_value == '#':
                    continue

                new_distance = distance + 1
                new_door_mask = door_mask
                if 'A' <= cell_value <= 'Z':
                    door_key_index = ord(cell_value.lower()) - ord('a')
                    new_door_mask |= (1 << door_key_index)

                previous_masks = visited_masks.get((new_row, new_col))
                if previous_masks:

                    if any((old_mask & new_door_mask) == old_mask for old_mask
                           in previous_masks):
                        continue

                    visited_masks[(new_row, new_col)] = [
                        mask for mask in previous_masks
                        if not ((new_door_mask & mask) == new_door_mask)]
                    visited_masks[(new_row, new_col)].append(new_door_mask)
                else:
                    visited_masks[(new_row, new_col)] = [new_door_mask]

                bfs_queue.append(
                    (new_row, new_col, new_distance, new_door_mask))

    return graph


def apply_pareto_filter(
        graph: list[dict[int, list[tuple[int, int]]]]) -> None:
    """
    Оставляет в каждой ячейке graph[source][target] только недоминируемые варианты (по двери и расстоянию).
    """
    for source_index in range(len(graph)):
        for target_index, variants in list(graph[source_index].items()):
            best_distances = {}
            for mask, distance in variants:
                if (mask not in best_distances
                        or distance < best_distances[mask]):
                    best_distances[mask] = distance

            filtered = []
            for mask, distance in best_distances.items():
                is_dominated = any(
                    other_mask != mask and
                    (other_mask & mask) == other_mask and
                    best_distances[other_mask] <= distance
                    for other_mask in best_distances
                )
                if not is_dominated:
                    filtered.append((mask, distance))

            graph[source_index][target_index] = filtered


def compute_minimum_edge_length(
        graph: list[dict[int, list[tuple[int, int]]]]) -> int:
    """
    Находит минимальное расстояние среди всех ребер графа, нужен для эвристики A*.
    """
    all_distances = [distance for adj in graph for variants in adj.values() for
                     (mask, distance) in variants]
    return min(all_distances) if all_distances else 0


def a_star_search(
        graph: list[dict[int, list[tuple[int, int]]]], num_keys: int) -> int:
    """
    Выполняет A*-поиск по состояниям роботов и собранных ключей.
    Возвращает минимальное число шагов или -1, если сбор всех ключей невозможен.
    """
    number_of_points = len(graph)
    all_keys_collected = (1 << num_keys) - 1
    start_state = (0, 1, 2, 3, 0)
    min_edge_length = compute_minimum_edge_length(graph)

    def heuristic(state):
        collected_mask = state[4]
        collected_count = bin(collected_mask).count('1')
        remaining_keys = num_keys - collected_count
        return remaining_keys * min_edge_length

    priority_queue = []
    heapq.heappush(
        priority_queue,
        PriorityQueueEntry(
            priority=heuristic(start_state),
            cost=0,
            state=start_state
        )
    )
    best_cost = {start_state: 0}

    while priority_queue:
        entry = heapq.heappop(priority_queue)
        current_cost, current_state = entry.cost, entry.state
        if current_cost > best_cost.get(current_state, float('inf')):
            continue
        if current_state[4] == all_keys_collected:
            return current_cost

        robot_positions, keys_mask = current_state[:4], current_state[4]
        for robot_index, robot_point in enumerate(robot_positions):
            for target_point in range(4, number_of_points):
                key_bit = 1 << (target_point - 4)
                if keys_mask & key_bit:
                    continue
                for required_mask, distance in graph[robot_point].get(
                        target_point, []):
                    if required_mask & ~keys_mask:
                        continue

                    new_keys_mask = keys_mask | key_bit
                    new_positions = list(robot_positions)
                    new_positions[robot_index] = target_point
                    new_state = (*new_positions, new_keys_mask)
                    tentative_cost = current_cost + distance
                    if tentative_cost < best_cost.get(new_state, float('inf')):
                        best_cost[new_state] = tentative_cost
                        heapq.heappush(
                            priority_queue,
                            PriorityQueueEntry(
                                priority=tentative_cost + heuristic(new_state),
                                cost=tentative_cost,
                                state=new_state
                            )
                        )
    return -1


def solve(grid: list[list[str]]) -> int:
    """
    Координирует разбор сетки, построение графа и запуск A*-поиска.
    """
    start_positions, key_positions = parse_grid(grid)
    points, coordinate_to_index, number_of_keys = index_points(start_positions,
                                                               key_positions)
    graph = build_reachability_graph(grid, points, coordinate_to_index)
    apply_pareto_filter(graph)
    return a_star_search(graph, number_of_keys)


def main():
    data = get_input()
    result = solve(data)
    print(result)


if __name__ == '__main__':
    main()
