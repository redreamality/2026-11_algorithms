"""第 24 课实战：Python 项目里需要“一直保持有序、又要频繁增删”时怎么写。

Python 标准库没有平衡树。按场景选：
1. 只是偶尔要有序结果 → 普通 dict / list，用的时候 sorted() 一次，O(n log n)。
2. 数据基本不变 → 排好序的 list + bisect（第 6 课讲过 bisect，第 11 课实战里用过）。
3. 边改边要有序、按排名取、按范围取 → sortedcontainers 的 SortedList / SortedDict。
   它不是平衡树，而是把数据切成很多段有序的小 list，靠二分定位；给的保证和平衡树一样
   （增删查约 O(log n)），实践中往往还更快。Java 的 TreeMap、C++ 的 std::map 用的是红黑树。

运行：uv run examples/avl_in_practice.py
"""

from sortedcontainers import SortedDict, SortedList


class Leaderboard:
    """场景：游戏排行榜。分数随时变，要能查“第几名”和“前 k 名”。

    SortedList 里存 (-分数, 玩家)，这样分数高的排前面，同分按名字排。
    """

    def __init__(self) -> None:
        self._ranking: SortedList = SortedList()
        self._score_by_player: dict[str, int] = {}

    def set_score(self, player: str, score: int) -> None:
        old_score = self._score_by_player.get(player)
        if old_score is not None:
            self._ranking.remove((-old_score, player))  # O(log n)
        self._score_by_player[player] = score
        self._ranking.add((-score, player))  # O(log n)

    def rank(self, player: str) -> int:
        """第几名（从 1 开始）。SortedList.index 是 O(log n)，不用从头数。"""
        return self._ranking.index((-self._score_by_player[player], player)) + 1

    def top(self, count: int) -> list[tuple[str, int]]:
        return [(player, -negative_score) for negative_score, player in self._ranking[:count]]


def main() -> None:
    # 有序插入：普通 BST 会退化成链表，SortedDict 不受影响
    orders = SortedDict((order_id, order_id % 97) for order_id in range(1, 10_001))
    assert orders.peekitem(0) == (1, 1)
    assert list(orders.irange(4999, 5001)) == [4999, 5000, 5001]
    for order_id in range(1, 5001):
        del orders[order_id]
    assert len(orders) == 5000 and orders.peekitem(0)[0] == 5001
    print("取消前 5000 个订单后，最早的订单号：", orders.peekitem(0)[0])

    board = Leaderboard()
    for player, score in [("alice", 90), ("bob", 75), ("carol", 90), ("dave", 60)]:
        board.set_score(player, score)
    assert board.top(3) == [("alice", 90), ("carol", 90), ("bob", 75)]
    board.set_score("dave", 95)  # dave 反超
    assert board.rank("dave") == 1
    assert board.rank("bob") == 4
    print("前三名：", board.top(3), "；bob 排第", board.rank("bob"))


if __name__ == "__main__":
    main()
