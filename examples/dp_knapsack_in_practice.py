"""第 20 课实战：Python 项目里“背包与序列 DP”真正是怎么写的。

1. 比较两段文本 / 两个文件 → 标准库 difflib。unified_diff 生成和 git diff 一样的补丁，
   SequenceMatcher 给出相似度和对齐的块。它背后就是“最长公共子序列”这一类 DP。
2. 拼写纠错、模糊搜索 → difflib.get_close_matches（按相似度挑最接近的几个）。
3. 预算内挑一组东西（迭代排需求、广告位投放）→ 标准库没有现成的。几十件、预算几千以内，
   直接写 0-1 背包 DP，并且要回溯出“选了哪些”；规模再大就上整数规划求解器。
   千万别按“性价比”贪心：会漏掉更好的组合（见下面的反例）。

运行：uv run examples/dp_knapsack_in_practice.py
"""

import difflib
from typing import NamedTuple


class Campaign(NamedTuple):
    name: str
    cost: int  # 投放花费（千元）
    expected_clicks: int


def plan_campaigns(campaigns: list[Campaign], budget: int) -> list[Campaign]:
    """0-1 背包：预算内让预计点击最多。一维表 + 记录每格是否“拿了第 i 件”，最后回溯出方案。"""
    best = [0] * (budget + 1)
    took = [[False] * (budget + 1) for _ in campaigns]
    for index, campaign in enumerate(campaigns):
        for remaining in range(budget, campaign.cost - 1, -1):  # 倒着循环，每件只拿一次
            with_it = best[remaining - campaign.cost] + campaign.expected_clicks
            if with_it > best[remaining]:
                best[remaining] = with_it
                took[index][remaining] = True
    chosen, remaining = [], budget
    for index in range(len(campaigns) - 1, -1, -1):
        if took[index][remaining]:
            chosen.append(campaigns[index])
            remaining -= campaigns[index].cost
    return chosen[::-1]


def plan_by_ratio(campaigns: list[Campaign], budget: int) -> list[Campaign]:
    """反面教材：按“每千元点击数”贪心。"""
    chosen, remaining = [], budget
    for campaign in sorted(campaigns, key=lambda c: c.expected_clicks / c.cost, reverse=True):
        if campaign.cost <= remaining:
            chosen.append(campaign)
            remaining -= campaign.cost
    return chosen


def main() -> None:
    old_config = ["host=db1", "port=5432", "user=app", "timeout=30"]
    new_config = ["host=db2", "port=5432", "user=app", "timeout=30", "pool=10"]
    patch = list(difflib.unified_diff(old_config, new_config, "old.conf", "new.conf", lineterm=""))
    assert "-host=db1" in patch and "+host=db2" in patch and "+pool=10" in patch
    print("配置文件 diff：")
    print("\n".join(patch))

    similarity = difflib.SequenceMatcher(None, "receive", "recieve").ratio()
    assert 0.8 < similarity < 1
    print(f"receive 和 recieve 的相似度：{similarity:.2f}")

    commands = ["status", "commit", "checkout", "branch", "merge", "rebase"]
    suggestions = difflib.get_close_matches("comit", commands, n=2)
    assert suggestions[0] == "commit"
    print("你是不是想输入：", suggestions)

    campaigns = [
        Campaign("搜索广告", 5, 500),
        Campaign("信息流", 4, 300),
        Campaign("开屏", 6, 660),
        Campaign("短信", 2, 100),
        Campaign("邮件", 5, 500),
    ]
    plan = plan_campaigns(campaigns, 10)
    assert [campaign.name for campaign in plan] == ["搜索广告", "邮件"]
    assert sum(campaign.expected_clicks for campaign in plan) == 1000
    greedy = plan_by_ratio(campaigns, 10)
    assert sum(campaign.expected_clicks for campaign in greedy) == 960
    print("预算 10 千元的投放方案：", [campaign.name for campaign in plan], "预计点击 1000")
    print("按性价比贪心：", [campaign.name for campaign in greedy], "预计点击 960")


if __name__ == "__main__":
    main()
