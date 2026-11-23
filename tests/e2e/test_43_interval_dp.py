"""第 43 课动画的端到端测试：石子合并按区间长度填表、最长回文子序列。
运行：uv run pytest tests/e2e/test_43_interval_dp.py"""

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


def test_merge_stones_fills_by_length(page: Page):
    demo = open_demo(page, "43-interval-dp.html", "interval-dp")
    click(demo, "石子合并")
    wait_done(demo)
    # 2 帧开场 + 6 个区间 + 1 帧答案
    expect(demo.locator(".step")).to_have_text("9 / 9")
    assert [cell(demo, 0, j).inner_text() for j in range(4)] == ["0", "7", "15", "26"]
    assert [cell(demo, 1, j).inner_text() for j in range(1, 4)] == ["0", "6", "16"]
    expect(demo.locator("td.off")).to_have_count(6)
    expect(cell(demo, 0, 3)).to_have_class("best")
    expect(demo.locator(".stat")).to_have_text("答案 = 26")
    # 倒数第二帧：填 0..3，最好的分割点 k = 1，用到 (0, 1) 和 (2, 3)，整排石子都在区间里
    click(demo, "← 上一步")
    expect(demo.locator("td.cur")).to_have_attribute("data-cell", "0,3")
    expect(cell(demo, 0, 1)).to_have_class("dep")
    expect(cell(demo, 2, 3)).to_have_class("dep")
    expect(demo.locator(".items .box.hot")).to_have_count(4)
    expect(demo.locator(".caption")).to_contain_text("最小的是 k = 1")


def test_merge_stones_order_is_by_length(page: Page):
    demo = open_demo(page, "43-interval-dp.html", "interval-dp")
    click(demo, "石子合并")
    wait_done(demo)
    # 退回第 2 帧（对角线），再一步步往前走：第 3～5 帧是长度 2 的三个区间，第 6～7 帧是长度 3
    for _ in range(7):
        click(demo, "← 上一步")
    expected = ["0,1", "1,2", "2,3", "0,2", "1,3", "0,3"]
    for key in expected:
        click(demo, "下一步 →")
        expect(demo.locator("td.cur")).to_have_attribute("data-cell", key)
        i, j = map(int, key.split(","))
        expect(demo.locator(".items .box.hot")).to_have_count(j - i + 1)


def test_longest_palindromic_subsequence(page: Page):
    demo = open_demo(page, "43-interval-dp.html", "interval-dp")
    click(demo, "最长回文子序列")
    wait_done(demo)
    assert [cell(demo, 0, j).inner_text() for j in range(5)] == ["1", "2", "3", "3", "4"]
    expect(cell(demo, 0, 4)).to_have_class("best")
    expect(demo.locator(".stat")).to_have_text("答案 = 4")
    # 倒数第二帧：text[0..4] = "bbbab" 两端都是 b，用到中间 1..3
    click(demo, "← 上一步")
    expect(demo.locator("td.cur")).to_have_attribute("data-cell", "0,4")
    expect(cell(demo, 1, 3)).to_have_class("dep")
    expect(demo.locator(".caption")).to_contain_text("两端都是 b")
