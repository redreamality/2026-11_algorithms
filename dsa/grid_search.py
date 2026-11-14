"""第 35 课：网格搜索。讲解见 lessons/35-grid-search.html

规则：
- 网格是列表的列表：grid[row][col]，row 是第几行（从上往下），col 是第几列（从左往右）。
  row_count = len(grid)，col_count = len(grid[0])。网格可能是空的（[]），先判断。
- 相邻只算上、下、左、右四个方向，斜着不算。建议在函数里写一个方向数组：
  directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]，
  然后用 for row_step, col_step in directions 依次算出 next_row、next_col。
- 走到新格子之前，先检查 0 <= next_row < row_count 且 0 <= next_col < col_count，再读它的值。
- count_islands、max_island_area、minutes_until_all_rotten 可以原地修改传进来的网格，
  用来标记“已经访问过”（例如把陆地改成水），这样就不需要额外的 visited 集合。
- capture_surrounded_regions 要求原地修改 board，不返回任何东西。
- 递归写 DFS 时，网格很大可能超过 Python 默认的递归深度；本课的例子都很小，不用担心，
  想更稳妥可以改用自己维护的栈或队列。
- 写完后运行 uv run dsa/grid_search.py，看每个例子的“期望”和“实际”是否一致。
"""


def count_islands(grid: list[list[str]]) -> int:
    """grid 里 "1" 是陆地，"0" 是水。上下左右相连的陆地组成一个岛屿，返回岛屿的个数。（LeetCode 200. 岛屿数量）

    例子：
        ["1", "1", "0", "0"]
        ["1", "0", "0", "1"]
        ["0", "0", "1", "1"]
    → 2（左上角三格是一个岛，右下角三格是另一个岛）。

    思路：从上到下、从左到右扫每一格。遇到一块还没访问过的陆地，就说明发现了一个新岛屿，
    island_count 加一，然后从这格出发做 DFS 或 BFS，把和它相连的陆地全部标记成已访问
    （直接改成 "0" 最省事），这样同一个岛不会被数第二次。

    目标复杂度：时间 O(row_count × col_count)，每格最多被访问一次；
    额外空间 O(row_count × col_count)（最坏情况下递归栈或队列的大小）。
    """
    raise NotImplementedError


def max_island_area(grid: list[list[int]]) -> int:
    """grid 里 1 是陆地，0 是水。岛屿的面积是它包含的陆地格子数，返回最大的岛屿面积，没有岛屿返回 0。（LeetCode 695. 岛屿的最大面积）

    例子：
        [1, 1, 0, 0]
        [1, 0, 0, 1]
        [0, 0, 1, 1]
        [0, 0, 1, 0]
    → 4（右下角的岛有 4 格，左上角的岛只有 3 格）。

    思路：和 count_islands 一样扫描并淹没岛屿，只是 DFS 要返回“这次淹没了几格”：
    当前格算 1，再加上四个方向各自递归回来的面积。用 largest_area 记录见过的最大值。

    目标复杂度：时间 O(row_count × col_count)，额外空间 O(row_count × col_count)。
    """
    raise NotImplementedError


def minutes_until_all_rotten(grid: list[list[int]]) -> int:
    """grid 里 0 是空格，1 是新鲜橘子，2 是腐烂的橘子。每过一分钟，腐烂橘子上下左右相邻的新鲜橘子都会腐烂。
    返回所有橘子都腐烂需要的最少分钟数；如果有橘子永远不会腐烂，返回 -1；一开始就没有新鲜橘子，返回 0。
    （LeetCode 994. 腐烂的橘子）

    例子：
        [2, 1, 1]
        [1, 1, 0]
        [0, 1, 1]
    → 4（第 1 分钟烂到 (0, 1)、(1, 0)，第 2 分钟 (0, 2)、(1, 1)，第 3 分钟 (2, 1)，第 4 分钟 (2, 2)）。

    思路：多源 BFS。一开始把所有腐烂橘子的位置都放进 rotten_queue（多个起点同时出发），
    并数出新鲜橘子的个数 fresh_count。然后一层一层地处理队列：每一层就是一分钟，
    这一层的每个橘子把相邻的新鲜橘子变成 2、放进队列、fresh_count 减一。
    队列空了以后，fresh_count 还大于 0 就返回 -1，否则返回经过的分钟数。

    目标复杂度：时间 O(row_count × col_count)，额外空间 O(row_count × col_count)。
    """
    raise NotImplementedError


def capture_surrounded_regions(board: list[list[str]]) -> None:
    """board 里只有 "X" 和 "O"。把所有被 "X" 完全围住的 "O" 改成 "X"，原地修改，不返回。（LeetCode 130. 被围绕的区域）

    “被围住”的意思是：这片相连的 "O" 里没有任何一格在边界上（第一行、最后一行、第一列、最后一列）。
    和边界上的 "O" 相连的 "O" 逃得出去，要保留。

    例子：
        ["X", "X", "X", "X"]        ["X", "X", "X", "X"]
        ["X", "O", "O", "X"]   →    ["X", "X", "X", "X"]
        ["X", "X", "O", "X"]        ["X", "X", "X", "X"]
        ["X", "O", "X", "X"]        ["X", "O", "X", "X"]
    （中间三个 "O" 被围住，改成 "X"；最下面那个 "O" 在边界上，保留。）

    思路：反过来想，不去找“被围住的”，而是找“逃得出去的”。
    1. 从边界上的每个 "O" 出发做 DFS 或 BFS，把和它相连的 "O" 都临时改成一个记号，比如 "S"（safe，安全）；
    2. 再扫一遍整个 board：剩下的 "O" 都是被围住的，改成 "X"；"S" 改回 "O"。

    目标复杂度：时间 O(row_count × col_count)，额外空间 O(row_count × col_count)。
    """
    raise NotImplementedError


if __name__ == "__main__":
    import copy

    def show(function, grid, expected):
        """调用 function(grid 的副本)，打印输入、期望和实际结果。原地修改型的函数比较修改后的网格。"""
        working_copy = copy.deepcopy(grid)
        try:
            returned = function(working_copy)
            actual = working_copy if returned is None else returned
            verdict = "通过" if actual == expected else "不对"
        except NotImplementedError:
            actual, verdict = "（还没写）", "未完成"
        print(f"[{verdict}] {function.__name__}，输入：")
        for row in grid:
            print(f"        {row}")
        print(f"        期望：{expected!r}")
        print(f"        实际：{actual!r}")

    show(count_islands, [
        ["1", "1", "0", "0"],
        ["1", "0", "0", "1"],
        ["0", "0", "1", "1"],
    ], 2)
    show(count_islands, [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "1"],
    ], 3)
    show(count_islands, [["0", "0"], ["0", "0"]], 0)
    show(count_islands, [], 0)

    show(max_island_area, [
        [1, 1, 0, 0],
        [1, 0, 0, 1],
        [0, 0, 1, 1],
        [0, 0, 1, 0],
    ], 4)
    show(max_island_area, [[0, 0, 0, 0, 0]], 0)
    show(max_island_area, [
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1],
    ], 1)

    show(minutes_until_all_rotten, [
        [2, 1, 1],
        [1, 1, 0],
        [0, 1, 1],
    ], 4)
    show(minutes_until_all_rotten, [
        [2, 1, 1],
        [0, 1, 1],
        [1, 0, 1],
    ], -1)
    show(minutes_until_all_rotten, [[0, 2]], 0)
    show(minutes_until_all_rotten, [
        [2, 1, 1, 1, 2],
        [1, 1, 0, 1, 1],
    ], 2)

    show(capture_surrounded_regions, [
        ["X", "X", "X", "X"],
        ["X", "O", "O", "X"],
        ["X", "X", "O", "X"],
        ["X", "O", "X", "X"],
    ], [
        ["X", "X", "X", "X"],
        ["X", "X", "X", "X"],
        ["X", "X", "X", "X"],
        ["X", "O", "X", "X"],
    ])
    show(capture_surrounded_regions, [
        ["O", "O", "X"],
        ["X", "O", "X"],
        ["X", "X", "X"],
    ], [
        ["O", "O", "X"],
        ["X", "O", "X"],
        ["X", "X", "X"],
    ])
    show(capture_surrounded_regions, [["X"]], [["X"]])
