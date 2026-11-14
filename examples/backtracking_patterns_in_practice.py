"""第 36 课实战：“列出所有方案”在 Python 项目里真正是怎么写的。

先看标准库 itertools 能不能直接做：
1. 每一项各选一个、全部搭配（测试矩阵、SKU 规格组合）→ itertools.product。
2. 从 n 个里挑 k 个、不计顺序（抽评审人、选组合）→ itertools.combinations。
3. 排出先后顺序 → itertools.permutations。注意有重复元素时它会产出重复结果。
itertools 是“先全部生成、再过滤”。约束很多、组合数很大时（排班、排课），
大部分组合在前几步就已经违反约束，这时要手写回溯，走不通就立刻回头（剪枝）。

运行：uv run examples/backtracking_patterns_in_practice.py
"""

from itertools import combinations, permutations, product


def test_matrix(versions: list[str], systems: list[str], databases: list[str],
                excluded: set[tuple[str, str]]) -> list[tuple[str, str, str]]:
    """场景一：CI 测试矩阵。三个维度全搭配，去掉已知不支持的（系统, 数据库）组合。"""
    return [
        (version, system, database)
        for version, system, database in product(versions, systems, databases)
        if (system, database) not in excluded
    ]


def reviewer_pairs(team: list[str], author: str) -> list[tuple[str, str]]:
    """场景二：从团队里挑两个人评审，作者自己不能评审。顺序无所谓，用 combinations。"""
    candidates = [member for member in team if member != author]
    return list(combinations(candidates, 2))


def distinct_orders(items: list[str]) -> list[tuple[str, ...]]:
    """场景三：有重复元素时，permutations 会把“两个相同的东西换位置”也算一种，要用 set 去重。

    元素少时这样写没问题；元素多时会先生成 n! 个再丢掉大部分，这就是第 36 课手写同层去重的意义。
    """
    return sorted(set(permutations(items)))


def schedule_shifts(shifts: list[str], available: dict[str, set[str]],
                    max_shifts_per_person: int) -> tuple[dict[str, str] | None, int]:
    """场景四：排班。每个班次派一个人；只能派有空的人；每人最多上 max_shifts_per_person 个班；
    同一天（班次名的前缀相同，如 "周一早"、"周一晚"）一个人只能上一个班。

    返回 (一种排法, 尝试过的分配次数)，排不出来时排法是 None。
    用 product 要先生成 人数^班次数 种排法再逐个检查；回溯在违反约束的那一步就回头。
    """
    assignment: dict[str, str] = {}
    shift_count = {person: 0 for person in available}
    attempts = 0

    def backtrack(index: int) -> bool:
        nonlocal attempts
        if index == len(shifts):
            return True
        shift = shifts[index]
        day = shift[:2]
        for person in sorted(available):
            if shift not in available[person] or shift_count[person] >= max_shifts_per_person:
                continue  # 剪枝：没空，或者已经排满
            if any(other_shift[:2] == day and assigned == person
                   for other_shift, assigned in assignment.items()):
                continue  # 剪枝：同一天已经有班
            attempts += 1
            assignment[shift] = person  # ① 选择
            shift_count[person] += 1
            if backtrack(index + 1):  # ② 递归
                return True
            del assignment[shift]  # ③ 撤销
            shift_count[person] -= 1
        return False

    found = backtrack(0)
    return (dict(assignment) if found else None), attempts


def main() -> None:
    matrix = test_matrix(["3.11", "3.12"], ["linux", "windows"], ["postgres", "sqlite"],
                         excluded={("windows", "postgres")})
    assert len(matrix) == 2 * 2 * 2 - 2
    assert ("3.12", "windows", "sqlite") in matrix
    print("测试矩阵共", len(matrix), "项，例如", matrix[0])

    pairs = reviewer_pairs(["alice", "bob", "carol", "dave"], author="bob")
    assert pairs == [("alice", "carol"), ("alice", "dave"), ("carol", "dave")]
    print("评审人组合：", pairs)

    orders = distinct_orders(["红", "红", "蓝"])
    assert orders == [("红", "红", "蓝"), ("红", "蓝", "红"), ("蓝", "红", "红")]
    print("两红一蓝的不同排列：", len(orders), "种（permutations 生成了 6 个）")

    shifts = ["周一早", "周一晚", "周二早", "周二晚", "周三早", "周三晚"]
    available = {
        "alice": {"周一早", "周二早", "周三早"},
        "bob": {"周一早", "周一晚", "周二晚", "周三晚"},
        "carol": {"周一晚", "周二早", "周二晚", "周三早", "周三晚"},
    }
    plan, attempts = schedule_shifts(shifts, available, max_shifts_per_person=2)
    assert plan is not None and set(plan) == set(shifts)
    for person in available:
        days = [shift[:2] for shift, assigned in plan.items() if assigned == person]
        assert len(days) == len(set(days)) <= 2
        assert all(shift in available[person] for shift, assigned in plan.items() if assigned == person)
    print("排班：", plan)
    print(f"回溯只试了 {attempts} 次分配；用 product 要检查 {len(available) ** len(shifts)} 种完整排法")

    impossible, _ = schedule_shifts(shifts, available, max_shifts_per_person=1)
    assert impossible is None  # 6 个班 3 个人，每人最多 1 个班，排不满
    print("每人最多 1 个班时：排不出来")


if __name__ == "__main__":
    main()
