"""第 21 课：回溯。讲解见 lessons/21-backtracking.html

实际项目里：只是“枚举所有排列 / 组合 / 笛卡尔积”时，直接用标准库 itertools（见 examples/backtracking_in_practice.py）。
需要边走边剪枝的约束搜索（排班、数独、配置组合校验）才自己写回溯。

这里的函数都写成生成器，和 itertools 一样：每找到一个解就 yield 一个 tuple，调用方想要几个拿几个，
用 next() 取第一个解、for 循环里 break 提前停止，都不会白白算完所有解。

规则：
- 都用回溯写：选择 → 递归 → 撤销。不要用 itertools 生成答案。
- 用一个 path 列表记录当前选了什么；yield 时交出 tuple(path)，不要直接交出 path，
  不然后面的撤销会把交出去的答案也改掉。
- 递归的内部函数也是生成器，往上传结果用 yield from。
- 能提前判断“这条路走不通”就立刻 return（剪枝），别等走到底再检查。

写完后运行 uv run dsa/backtracking.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_backtracking.py。
"""

from collections.abc import Iterator, Sequence


def permutations(items: Sequence) -> Iterator[tuple]:
    """items 的全排列，顺序和 itertools.permutations(items) 完全一样（按下标的字典序）。空序列产出一个 ()。

    思路：每一层按下标从小到大，挑一个“还没用过的下标”放进 path，用一个 used 列表记录。
    items 里有相等的元素时也按下标区分，和 itertools 一样会产出看起来重复的排列。
    O(n · n!)。
    """
    raise NotImplementedError


def subsets(items: Sequence) -> Iterator[tuple]:
    """items 的所有子集，包括空集，共 2^n 个。顺序随意，测试会排序后比较。

    思路：对每个下标做一次二选一——要它，或不要它。
    每个子集内部保持 items 里原来的先后顺序。O(n · 2^n)。
    """
    raise NotImplementedError


def combination_sum(candidates: Sequence[int], target: int) -> Iterator[tuple[int, ...]]:
    """从 candidates（正整数、互不相同）里选数，和恰好等于 target，同一个数可以重复选。

    每个组合是从小到大排好的 tuple，组合之间不能重复（(2, 3) 和 (3, 2) 算同一个）。
    target 为 0 时产出一个 ()。

    提示：先把 candidates 排序（sorted，不要改传进来的数据）；递归时带一个 start，只从 start 往后选，
    就不会出现重复组合。剪枝：剩余的 target 已经小于当前候选数时，后面更大的数也不用试了，直接 break。
    """
    raise NotImplementedError


def n_queens(n: int) -> Iterator[tuple[int, ...]]:
    """n×n 棋盘放 n 个皇后，两两不在同一行、同一列、同一条斜线上。逐个产出所有解。

    每个解是一个 tuple：第 row 个数是第 row 行的皇后放在第几列。按字典序产出，
    所以 next(n_queens(4)) 是 (1, 3, 0, 2)。n = 0 时产出一个 ()（空棋盘算一种放法）。
    数解的个数：sum(1 for _ in n_queens(8)) == 92。

    思路：一行放一个，逐行往下放，每行的列从小到大试。用三个集合记录已被占的列、
    主对角线（row - column）、副对角线（row + column），判断冲突就是 O(1)。
    """
    raise NotImplementedError


def solve_sudoku(grid: list[list[int]]) -> list[list[int]] | None:
    """（选做）解 9×9 数独。grid 里 0 表示空格。返回填好的新棋盘，无解返回 None。不要改动传进来的 grid。

    规则：每行、每列、每个 3×3 宫里 1～9 各出现一次。
    思路：先复制一份棋盘，并用 9 个集合记录每行已有的数，列、宫也一样（宫的编号是 row // 3 * 3 + column // 3）。
    找到下一个空格，试 1～9 里行、列、宫都还没有的数：填上并加进集合 → 递归 → 不行就擦掉并从集合里删掉。
    进阶：每次挑“候选数最少”的空格先填，剪枝效果好得多。
    """
    raise NotImplementedError


if __name__ == "__main__":
    from itertools import islice

    def show(title, compute, expected):
        """运行一个例子，打印期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    # 端到端场景一：三位同事轮流值班周一到周三，列出前三种排法。
    show("值班排法（前 3 种）", lambda: list(islice(permutations(["张", "李", "王"]), 3)),
         [("张", "李", "王"), ("张", "王", "李"), ("李", "张", "王")])

    # 场景二：套餐里 4 种可选配件，每种要或不要，一共几种组合？
    show("配件组合有几种", lambda: sum(1 for _ in subsets(["耳机", "手环", "充电器", "保护壳"])), 16)

    # 场景三：用 20 元、30 元、50 元三种代金券恰好凑满 100 元，有哪些凑法？
    show("代金券凑 100 元", lambda: sorted(combination_sum([50, 20, 30], 100)),
         [(20, 20, 20, 20, 20), (20, 20, 30, 30), (20, 30, 50), (50, 50)])

    # 场景四：生成器可以提前停：20 个元素的全排列有 2.4×10^18 个，但第一个马上就能拿到。
    show("next(permutations(range(20)))", lambda: next(permutations(range(20))), tuple(range(20)))
    show("next(n_queens(8))", lambda: next(n_queens(8)), (0, 4, 7, 5, 2, 6, 1, 3))

    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    show("（选做）数独第一行", lambda: solve_sudoku(puzzle)[0], [5, 3, 4, 6, 7, 8, 9, 1, 2])
