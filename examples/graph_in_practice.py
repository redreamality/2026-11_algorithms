"""第 13 课实战：Python 项目里图的遍历真正是怎么写的。

没有专门的“图类”：一个 dict 就是邻接表，collections.deque 当队列，十来行写完。
节点直接用业务里的东西：用户名、URL、(行, 列) 坐标。
图很大、要跑很多种算法（中心度、社区发现、画图）时才引入第三方库 networkx，本项目不依赖它。

运行：uv run examples/graph_in_practice.py
"""

from collections import defaultdict, deque


def degrees_of_separation(follows: dict[str, list[str]], source: str, target: str) -> list[str] | None:
    """场景一：社交网络里 source 到 target 的最短引荐链（BFS + came_from 复原路径）。"""
    came_from: dict[str, str | None] = {source: None}
    queue = deque([source])
    while queue:
        person = queue.popleft()
        if person == target:
            chain = []
            while person is not None:
                chain.append(person)
                person = came_from[person]
            return chain[::-1]
        for friend in follows.get(person, ()):
            if friend not in came_from:
                came_from[friend] = person
                queue.append(friend)
    return None


def reachable_pages(links: dict[str, list[str]], start: str, max_depth: int) -> dict[str, int]:
    """场景二：站内爬虫只爬到第 max_depth 层。返回 {页面: 离起始页几跳}。

    BFS 天然按层走，记一下层数就能限深；用 dict 当 seen，顺便存了深度。
    """
    depth = {start: 0}
    queue = deque([start])
    while queue:
        page = queue.popleft()
        if depth[page] == max_depth:
            continue
        for linked_page in links.get(page, ()):
            if linked_page not in depth:
                depth[linked_page] = depth[page] + 1
                queue.append(linked_page)
    return depth


def flood_fill_regions(grid: list[str]) -> int:
    """场景三：地图上有几块连在一起的陆地（'#'）。节点就是 (行, 列)，邻居现算，不用先建图。"""
    rows, columns = len(grid), len(grid[0]) if grid else 0
    seen: set[tuple[int, int]] = set()
    regions = 0
    for row in range(rows):
        for column in range(columns):
            if grid[row][column] != "#" or (row, column) in seen:
                continue
            regions += 1
            stack = [(row, column)]  # DFS 用 list 当栈，不用递归，大地图也不会爆栈
            seen.add((row, column))
            while stack:
                current_row, current_column = stack.pop()
                for next_row, next_column in ((current_row + 1, current_column), (current_row - 1, current_column),
                                              (current_row, current_column + 1), (current_row, current_column - 1)):
                    if (0 <= next_row < rows and 0 <= next_column < columns
                            and grid[next_row][next_column] == "#" and (next_row, next_column) not in seen):
                        seen.add((next_row, next_column))
                        stack.append((next_row, next_column))
    return regions


def main() -> None:
    follows: defaultdict[str, list[str]] = defaultdict(list)
    for left, right in [("ann", "bob"), ("ann", "cat"), ("bob", "dan"), ("cat", "dan"), ("dan", "eve"),
                        ("fay", "gus")]:
        follows[left].append(right)
        follows[right].append(left)
    chain = degrees_of_separation(follows, "ann", "eve")
    assert chain == ["ann", "bob", "dan", "eve"]
    assert degrees_of_separation(follows, "ann", "gus") is None
    print("ann 到 eve 的引荐链：", " → ".join(chain))

    links = {
        "/": ["/docs", "/blog"],
        "/docs": ["/docs/install", "/"],
        "/blog": ["/blog/2026", "/docs"],
        "/docs/install": ["/docs/install/windows"],
    }
    depth = reachable_pages(links, "/", max_depth=2)
    assert depth == {"/": 0, "/docs": 1, "/blog": 1, "/docs/install": 2, "/blog/2026": 2}
    print("爬两层能到的页面：", sorted(depth))

    island_map = [
        "##..#",
        "#...#",
        "..#..",
        ".....",
        "##.##",
    ]
    assert flood_fill_regions(island_map) == 5
    print("地图上的陆地块数：", flood_fill_regions(island_map))


if __name__ == "__main__":
    main()
