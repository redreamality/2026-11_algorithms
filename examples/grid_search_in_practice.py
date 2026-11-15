"""第 35 课实战：Python 项目里“网格搜索”真正是怎么写的。

网格就是隐式的图，业务里常见三种用法：
1. 画图软件的油漆桶（flood fill）：从点到的像素出发，把相连的同色像素都换成新颜色。
   用显式栈或 deque 写，不用递归：一张 1000×1000 的图，递归必然超过 Python 的递归上限。
2. 扫雷点开空白格：BFS 一圈圈往外翻，碰到“周围有雷”的格子只翻开它、不再往外扩。
3. 仓库机器人 / 游戏寻路的最短步数：BFS，第一次走到终点时的步数就是最短的。
   有不同地形代价时换成 Dijkstra（heapq），要更快就上 A*；专门的库有 networkx、scipy.ndimage.label，本项目不引入。

运行：uv run examples/grid_search_in_practice.py
"""

from collections import deque

DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 上、下、左、右
ALL_EIGHT_DIRECTIONS = [(row_step, col_step) for row_step in (-1, 0, 1) for col_step in (-1, 0, 1)
                        if (row_step, col_step) != (0, 0)]


def flood_fill(image: list[list[str]], start_row: int, start_col: int, new_color: str) -> int:
    """油漆桶：把 (start_row, start_col) 所在的同色连通区域原地换成 new_color，返回换了几个像素。"""
    old_color = image[start_row][start_col]
    if old_color == new_color:
        return 0  # 不判断的话，换完的像素还是“旧颜色”，会死循环
    row_count, col_count = len(image), len(image[0])
    image[start_row][start_col] = new_color
    stack = [(start_row, start_col)]
    painted_count = 0
    while stack:
        row, col = stack.pop()
        painted_count += 1
        for row_step, col_step in DIRECTIONS:
            next_row, next_col = row + row_step, col + col_step
            if 0 <= next_row < row_count and 0 <= next_col < col_count and image[next_row][next_col] == old_color:
                image[next_row][next_col] = new_color  # 入栈时就涂色，等于标记已访问
                stack.append((next_row, next_col))
    return painted_count


def mines_around(mines: set[tuple[int, int]], row: int, col: int) -> int:
    # in 的结果是 True / False，sum 时 True 当 1、False 当 0，加起来就是周围的雷数
    return sum((row + row_step, col + col_step) in mines for row_step, col_step in ALL_EIGHT_DIRECTIONS)


def reveal(mines: set[tuple[int, int]], row_count: int, col_count: int,
           click_row: int, click_col: int) -> dict[tuple[int, int], int]:
    """扫雷点开一格（假设不是雷）。返回所有被翻开的格子 → 它周围的雷数。

    周围雷数为 0 的格子会继续往八个方向翻；不为 0 的格子只翻开自己，是这片区域的边界。
    """
    revealed = {(click_row, click_col): mines_around(mines, click_row, click_col)}
    queue = deque([(click_row, click_col)])
    while queue:
        row, col = queue.popleft()
        if revealed[(row, col)] != 0:
            continue
        for row_step, col_step in ALL_EIGHT_DIRECTIONS:
            next_cell = (row + row_step, col + col_step)
            if (0 <= next_cell[0] < row_count and 0 <= next_cell[1] < col_count
                    and next_cell not in revealed and next_cell not in mines):
                revealed[next_cell] = mines_around(mines, *next_cell)
                queue.append(next_cell)
    return revealed


def shortest_route(warehouse: list[str], start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]] | None:
    """仓库地图里 "#" 是货架，"." 是通道。返回从 start 到 goal 的最短路线（含两端），走不到返回 None。

    BFS 一层层往外扩，第一次碰到 goal 时就是最少步数。came_from 记下每格是从哪一格走来的，倒着走回去就是路线。
    """
    row_count, col_count = len(warehouse), len(warehouse[0])
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        if cell == goal:
            route = []
            while cell is not None:
                route.append(cell)
                cell = came_from[cell]
            return route[::-1]
        row, col = cell
        for row_step, col_step in DIRECTIONS:
            next_cell = (row + row_step, col + col_step)
            if (0 <= next_cell[0] < row_count and 0 <= next_cell[1] < col_count
                    and warehouse[next_cell[0]][next_cell[1]] == "." and next_cell not in came_from):
                came_from[next_cell] = cell
                queue.append(next_cell)
    return None


def main() -> None:
    image = [list(row) for row in [
        "WWWBB",
        "WBWBB",
        "WBWWW",
        "BBBBW",
    ]]
    assert flood_fill(image, 0, 0, "R") == 10
    assert ["".join(row) for row in image] == ["RRRBB", "RBRBB", "RBRRR", "BBBBR"]
    assert flood_fill(image, 0, 0, "R") == 0  # 新旧颜色相同，什么都不做
    print("油漆桶之后：", ["".join(row) for row in image])

    big_image = [["W"] * 600 for _ in range(600)]
    assert flood_fill(big_image, 0, 0, "R") == 360_000  # 递归版在这里会 RecursionError
    print("600×600 的整张图也能一次填满：", 360_000, "个像素")

    mines = {(0, 3), (2, 1)}
    revealed = reveal(mines, 4, 4, 3, 3)
    assert revealed == {  # 手算核对过：只有 (2, 3)、(3, 3) 周围没雷，会继续往外翻
        (1, 2): 2, (1, 3): 1,
        (2, 2): 1, (2, 3): 0,
        (3, 2): 1, (3, 3): 0,
    }
    assert reveal(mines, 4, 4, 1, 1) == {(1, 1): 1}  # 周围有雷：只翻开自己
    print("扫雷点开右下角，翻开了", len(revealed), "格")

    warehouse = [
        "....#",
        ".##.#",
        ".#...",
        "...#.",
    ]
    route = shortest_route(warehouse, (0, 0), (3, 4))
    assert route is not None and len(route) - 1 == 7  # 7 步
    assert route[0] == (0, 0) and route[-1] == (3, 4)
    assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(route, route[1:]))  # 每步只走一格
    assert shortest_route([".#", "#."], (0, 0), (1, 1)) is None  # 被货架隔断
    print("机器人最短路线：", route)


if __name__ == "__main__":
    main()
