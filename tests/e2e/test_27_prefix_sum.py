"""第 27 课动画的端到端测试：前缀和数组算对、区间查询结果正确、和为 K 的子数组数对。
运行：uv run pytest tests/e2e/test_27_prefix_sum.py"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


def open_demo(page: Page, lesson: str, demo_id: str):
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    page.goto((LESSONS / lesson).as_uri() + "?fast")
    demo = page.locator(f"#{demo_id}")
    expect(demo).not_to_be_empty()
    assert not errors, errors
    return demo


def wait_done(demo):
    """等动画放到最后一帧：计数器显示成 “N / N”。"""
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def click(demo, name: str):
    demo.get_by_role("button", name=name, exact=True).click()


def test_range_sum(page: Page):
    demo = open_demo(page, "27-prefix-sum.html", "prefix")
    click(demo, "区域和查询")
    wait_done(demo)
    expect(demo.locator(".box.prefix")).to_have_text(["0", "-2", "-2", "1", "-4", "-2", "-3"])
    expect(demo.locator(".caption")).to_contain_text("sum_range(2, 5)")
    expect(demo.locator(".best")).to_have_text("-1")
    expect(demo.locator(".box.prefix.hot")).to_have_text(["-2", "-3"])


def test_subarray_sum_equals_k(page: Page):
    demo = open_demo(page, "27-prefix-sum.html", "prefix")
    click(demo, "和为 K 的子数组")
    wait_done(demo)
    expect(demo.locator(".best")).to_have_text("4")
    expect(demo.locator(".caption")).to_contain_text("一共 4 个")
    expect(demo.locator(".box.count")).to_contain_text(["0: 1", "14: 2"])
    expect(demo.locator(".box.number.done")).to_have_count(8)
