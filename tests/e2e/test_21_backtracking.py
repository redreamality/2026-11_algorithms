"""第 21 课动画的端到端测试：4 皇后的放置、冲突、撤销。运行：uv run pytest tests/e2e/test_21_backtracking.py"""

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


def queen_cols(demo, n=4):
    """每行皇后所在的列。"""
    cells = demo.locator(".board .cell")
    texts = cells.all_inner_texts()
    return [texts[r * n:(r + 1) * n].index("♛") for r in range(n)]


def test_first_solution(page: Page):
    demo = open_demo(page, "21-backtracking.html", "queens")
    click(demo, "找第一个解")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("[1, 3, 0, 2]")
    expect(demo.locator(".board .queen")).to_have_count(4)
    assert queen_cols(demo) == [1, 3, 0, 2]
    expect(demo.locator(".solutions")).to_have_text("1")


def test_conflict_and_undo_frames(page: Page):
    demo = open_demo(page, "21-backtracking.html", "queens")
    click(demo, "找第一个解")
    wait_done(demo)
    for _ in range(int(demo.locator(".step").inner_text().split(" / ")[1]) - 3):
        click(demo, "← 上一步")
    # 第 3 帧：第 1 行第 0 列和第 0 行的皇后同列，被剪掉
    expect(demo.locator(".step")).to_have_text(re.compile(r"^3 / "))
    expect(demo.locator(".caption")).to_contain_text("同一列")
    expect(demo.locator(".board .found")).to_have_text("×")
    expect(demo.locator(".board .queen")).to_have_count(1)


def test_all_solutions(page: Page):
    demo = open_demo(page, "21-backtracking.html", "queens")
    click(demo, "找全部解")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("共 2 个解")
    expect(demo.locator(".solutions")).to_have_text("2")
    expect(demo.locator(".board .queen")).to_have_count(0)
    demo.get_by_label("n").fill("5")
    click(demo, "找全部解")
    wait_done(demo)
    expect(demo.locator(".solutions")).to_have_text("10")
