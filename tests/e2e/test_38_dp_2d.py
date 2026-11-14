"""第 38 课动画的端到端测试：最小路径和、编辑距离、最长回文子串。
运行：uv run pytest tests/e2e/test_38_dp_2d.py"""

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


def cell(demo, key):
    return demo.locator(f'td[data-cell="{key}"]')


def test_edit_distance_table_and_operations(page: Page):
    demo = open_demo(page, "38-dp-2d.html", "dp2d")
    click(demo, "编辑距离")
    wait_done(demo)
    expected_rows = [[0, 1, 2, 3], [1, 1, 2, 3], [2, 2, 1, 2], [3, 2, 2, 2], [4, 3, 3, 2], [5, 4, 4, 3]]
    for i, row in enumerate(expected_rows):
        assert [cell(demo, f"{i},{j}").inner_text() for j in range(4)] == [str(v) for v in row]
    expect(demo.locator(".caption")).to_contain_text("把 h 换成 r，删掉 r，删掉 e")
    # 倒数第二帧：填右下角，三格都是依赖
    click(demo, "← 上一步")
    expect(demo.locator("td.cur")).to_have_attribute("data-cell", "5,3")
    expect(demo.locator("td.dep")).to_have_count(3)
    for key in ("4,2", "4,3", "5,2"):
        expect(cell(demo, key)).to_have_class("dep")


def test_min_path_sum(page: Page):
    demo = open_demo(page, "38-dp-2d.html", "dp2d")
    click(demo, "最小路径和")
    wait_done(demo)
    expect(cell(demo, "2,2")).to_have_text("7")
    expect(demo.locator(".caption")).to_contain_text("1 → 3 → 1 → 1 → 1")


def test_longest_palindrome(page: Page):
    demo = open_demo(page, "38-dp-2d.html", "dp2d")
    click(demo, "最长回文子串")
    wait_done(demo)
    expect(cell(demo, "0,2")).to_have_text("✓")
    expect(cell(demo, "0,2")).to_have_class("path")
    expect(cell(demo, "0,4")).to_have_text("✗")
    expect(cell(demo, "2,0")).to_have_class("off")
    expect(demo.locator(".stat")).to_have_text("答案 = bab")
