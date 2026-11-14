"""第 36 课动画的端到端测试：子集 II 的同层去重放到最后一帧。运行：uv run pytest tests/e2e/test_36_backtracking_patterns.py"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    page.goto((LESSONS / "36-backtracking-patterns.html").as_uri() + "?fast")
    demo = page.locator("#subsets")
    expect(demo).not_to_be_empty()
    assert not errors, errors
    return demo


def wait_done(demo):
    """等动画放到最后一帧：计数器显示成 “N / N”。"""
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def test_remove_duplicates_prunes_same_level(page: Page):
    demo = open_demo(page)
    demo.get_by_role("button", name="去重（同层跳过）", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".answer-count")).to_have_text("6")
    expect(demo.locator(".duplicate-count")).to_have_text("0")
    expect(demo.locator(".pruned-count")).to_have_text("2")
    # 按 DFS 顺序，先剪掉 [1] 下面的第二个 [1, 2]，再剪掉根下面的第二个 [2]
    expect(demo.locator(".tree-node.pruned .box")).to_have_text(["[1, 2]", "[2]"])
    expect(demo.locator(".answers .box")).to_have_text(["[]", "[1]", "[1, 2]", "[1, 2, 2]", "[2]", "[2, 2]"])


def test_without_rule_collects_duplicates(page: Page):
    demo = open_demo(page)
    demo.get_by_role("button", name="不去重（对照）", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".answer-count")).to_have_text("8")
    expect(demo.locator(".duplicate-count")).to_have_text("2")
    expect(demo.locator(".caption")).to_contain_text("2 个是重复的")


def test_unsorted_input_is_sorted_first(page: Page):
    demo = open_demo(page)
    demo.get_by_label("输入").select_option("2, 1, 2")
    demo.get_by_role("button", name="去重（同层跳过）", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".nums .box")).to_have_text(["1", "2", "2"])
    expect(demo.locator(".answer-count")).to_have_text("6")
