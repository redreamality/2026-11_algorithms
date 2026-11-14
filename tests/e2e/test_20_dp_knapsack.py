"""第 20 课 DP 表动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

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


def test_knapsack_fills_to_answer(page: Page):
    demo = open_demo(page, "20-dp-knapsack.html", "dp")
    expect(cell(demo, 0, 5)).to_have_text("0")
    expect(cell(demo, 3, 5)).to_have_text("")
    click(demo, "0-1 背包")
    wait_done(demo)
    expect(cell(demo, 3, 5)).to_have_text("45")
    expect(cell(demo, 2, 4)).to_have_text("35")
    expect(demo.locator(".caption")).to_contain_text("45")


def test_knapsack_step_highlights_dependencies(page: Page):
    demo = open_demo(page, "20-dp-knapsack.html", "dp")
    click(demo, "0-1 背包")
    wait_done(demo)
    # 倒数第二帧：填 dp[3][5]，依赖上面 dp[2][5] 和 dp[2][1]
    click(demo, "← 上一步")
    expect(demo.locator("td.cur")).to_have_attribute("data-cell", "3,5")
    expect(demo.locator("td.dep")).to_have_count(2)
    expect(cell(demo, 2, 5)).to_have_class("dep")
    expect(cell(demo, 2, 1)).to_have_class("dep")


def test_lcs_traceback(page: Page):
    demo = open_demo(page, "20-dp-knapsack.html", "dp")
    click(demo, "LCS")
    wait_done(demo)
    expect(cell(demo, 4, 5)).to_have_text("3")
    expect(demo.locator(".stat")).to_have_text("LCS = BCB")
    expect(demo.locator("td.path").first).to_be_visible()
