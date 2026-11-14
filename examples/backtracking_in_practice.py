"""第 21 课实战：Python 项目里“枚举 / 约束搜索”真正是怎么写的。

1. 只是枚举，没有约束 → 标准库 itertools：
   permutations（排列）、combinations（组合）、product（笛卡尔积，比如所有配置组合）。
   它们都是惰性的生成器，配合 next()、islice、any() 可以拿到想要的就停。
2. 枚举 + 过滤，规模很小（几百、几千种）→ itertools 生成全部，再用 if 过滤。最好写、最不容易错。
3. 规模大、约束多（排班、数独、选课）→ 自己写回溯生成器：每放一步就检查约束，走不通立刻退回，
   剪掉的枝根本不会被生成。

运行：uv run examples/backtracking_in_practice.py
"""

from collections.abc import Iterator
from itertools import combinations, islice, permutations, product


def build_test_matrix() -> list[dict[str, str]]:
    """CI 测试矩阵：每个维度挑一个值，所有组合都跑一遍（就是 product），再排除不支持的组合。"""
    dimensions = {"os": ["linux", "windows"], "version": ["3.11", "3.12", "3.13"], "database": ["sqlite", "postgres"]}
    matrix = [dict(zip(dimensions, values)) for values in product(*dimensions.values())]
    return [job for job in matrix if not (job["os"] == "windows" and job["database"] == "postgres")]


def pick_team(people: dict[str, set[str]], size: int, required_skills: set[str]) -> tuple[str, ...] | None:
    """从候选人里挑 size 个人，技能要覆盖 required_skills。小规模：combinations 生成 + 过滤，找到第一个就停。"""
    return next(
        (team for team in combinations(people, size) if required_skills <= set().union(*(people[name] for name in team))),
        None,
    )


def assign_shifts(
    people: list[str], shifts: list[str], unavailable: dict[str, set[str]], max_shifts_per_person: int
) -> Iterator[dict[str, str]]:
    """排班：每个班次安排一个人，避开请假，每人最多 max_shifts_per_person 个班，相邻班次不能是同一个人。

    用回溯生成器：每填一个班次就检查约束，冲突立刻换人；每找到一种完整排法就 yield 一个副本。
    """
    schedule: dict[str, str] = {}
    load = dict.fromkeys(people, 0)

    def walk(index: int) -> Iterator[dict[str, str]]:
        if index == len(shifts):
            yield dict(schedule)
            return
        shift = shifts[index]
        for person in people:
            if shift in unavailable.get(person, set()) or load[person] >= max_shifts_per_person:
                continue
            if index > 0 and schedule[shifts[index - 1]] == person:
                continue
            schedule[shift] = person
            load[person] += 1
            yield from walk(index + 1)
            load[person] -= 1
            del schedule[shift]

    yield from walk(0)


def main() -> None:
    matrix = build_test_matrix()
    assert len(matrix) == 2 * 3 * 2 - 3
    print("CI 测试矩阵：", len(matrix), "个任务，例如", matrix[0])

    orders = list(permutations(["打包", "测试", "部署"]))
    assert len(orders) == 6 and orders[0] == ("打包", "测试", "部署")
    print("三个步骤的所有顺序：", len(orders), "种")

    people = {"张": {"前端"}, "李": {"后端", "数据库"}, "王": {"前端", "测试"}, "赵": {"运维"}}
    team = pick_team(people, 2, {"前端", "后端"})
    assert team == ("张", "李")
    assert pick_team(people, 2, {"前端", "后端", "运维"}) is None
    print("能覆盖前端和后端的两人小组：", team)

    shifts = ["周一", "周二", "周三", "周四", "周五"]
    unavailable = {"张": {"周一"}, "李": {"周三", "周四"}}
    plans = assign_shifts(["张", "李", "王"], shifts, unavailable, max_shifts_per_person=2)
    first_plan = next(plans)  # 生成器：只算出第一种排法就停
    assert first_plan == {"周一": "李", "周二": "张", "周三": "王", "周四": "张", "周五": "李"}
    total = 1 + sum(1 for _ in plans)  # 想知道一共几种，再把剩下的数完
    assert total == 8  # 和用 product 暴力枚举 3^5 种再过滤的结果一致
    print("第一种排班：", first_plan, "；一共", total, "种")

    first_two_codes = list(islice(product("0123456789", repeat=6), 2))  # 10^6 种验证码，只取前两个
    assert first_two_codes == [tuple("000000"), tuple("000001")]


if __name__ == "__main__":
    main()
