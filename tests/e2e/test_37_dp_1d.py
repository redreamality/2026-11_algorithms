"""第 37 课动画的端到端测试：打家劫舍填表、最长递增子序列的 smallest_tail、最大子数组和。
运行：uv run pytest tests/e2e/test_37_dp_1d.py"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


def open_demo(page: Page, lesson: str, demo_id: str):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
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


def cell(demo, i, j):
    return demo.locator(f'td[data-cell="{i},{j}"]')


def test_rob_houses_fills_table_and_marks_houses(page: Page):
    demo = open_demo(page, "37-dp-1d.html", "dp1d")
    click(demo, "打家劫舍")
    wait_done(demo)
    assert [cell(demo, 1, j).inner_text() for j in range(5)] == ["2", "7", "11", "11", "12"]
    expect(demo.locator("td.pick")).to_have_count(3)
    for j in (0, 2, 4):
        expect(cell(demo, 0, j)).to_have_class("pick")
    expect(demo.locator(".caption")).to_contain_text("最多偷 12")
    # 倒数第二帧：填 i = 4，依赖 i = 3 和 i = 2
    click(demo, "← 上一步")
    expect(demo.locator("td.cur")).to_have_attribute("data-cell", "1,4")
    expect(cell(demo, 1, 3)).to_have_class("dep")
    expect(cell(demo, 1, 2)).to_have_class("dep")


def test_lis_smallest_tail(page: Page):
    demo = open_demo(page, "37-dp-1d.html", "dp1d")
    click(demo, "最长递增子序列")
    wait_done(demo)
    expect(demo.locator(".tails .box")).to_have_text(["2", "3", "7", "18"])
    expect(demo.locator(".stat")).to_have_text("答案 = 4")


def test_max_subarray_sum(page: Page):
    demo = open_demo(page, "37-dp-1d.html", "dp1d")
    click(demo, "最大子数组和")
    wait_done(demo)
    expect(cell(demo, 2, 8)).to_have_text("6")
    expect(demo.locator("td.pick")).to_have_text(["4", "-1", "2", "1"])
    expect(demo.locator(".caption")).to_contain_text("[4, -1, 2, 1]")
