"""第 35 课动画的端到端测试：岛屿数量、腐烂的橘子放到最后一帧。运行：uv run pytest tests/e2e/test_35_grid_search.py"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    page.goto((LESSONS / "35-grid-search.html").as_uri() + "?fast")
    demo = page.locator("#grid")
    expect(demo).not_to_be_empty()
    assert not errors, errors
    return demo


def wait_done(demo):
    """等动画放到最后一帧：计数器显示成 “N / N”。"""
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def test_count_islands(page: Page):
    demo = open_demo(page)
    demo.get_by_role("button", name="岛屿数量（DFS）", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".answer")).to_have_text("5")
    expect(demo.locator(".caption")).to_contain_text("一共 5 个岛屿")
    # 所有陆地都被原地标记成了某个岛，没有剩下没访问的陆地
    expect(demo.locator(".cell.land")).to_have_count(0)
    expect(demo.locator(".cell.island")).to_have_count(13)


def test_rotting_oranges(page: Page):
    demo = open_demo(page)
    demo.get_by_role("button", name="腐烂的橘子（多源 BFS）", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".answer")).to_have_text("5")
    expect(demo.locator(".caption")).to_contain_text("用了 5 分钟")
    expect(demo.locator(".cell.fresh")).to_have_count(0)
    # 左下角 (3, 0) 离两个起点最远，第 5 分钟才烂
    expect(demo.locator(".grid-board .cell").nth(3 * 5 + 0)).to_have_text("5")
