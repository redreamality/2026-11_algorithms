"""第 25 课动画的端到端测试：盛最多水、两数之和 II、移动零都能放到最后一帧并给出正确结果。
运行：uv run pytest tests/e2e/test_25_two_pointers.py"""

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


def test_max_water(page: Page):
    demo = open_demo(page, "25-two-pointers.html", "pointers")
    click(demo, "盛最多水")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("最大面积 49，由下标 1 和 8")
    expect(demo.locator(".best")).to_have_text("49")
    expect(demo.locator(".pillar.hot")).to_have_count(2)
    pointer_texts = demo.locator(".pointer").all_inner_texts()
    assert pointer_texts[1] == "left" and pointer_texts[8] == "right"


def test_two_sum_sorted(page: Page):
    demo = open_demo(page, "25-two-pointers.html", "pointers")
    click(demo, "两数之和 II")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("返回 [1, 4]")
    expect(demo.locator(".cells .box.done")).to_have_text(["2", "8"])


def test_move_zeroes(page: Page):
    demo = open_demo(page, "25-two-pointers.html", "pointers")
    click(demo, "移动零")
    wait_done(demo)
    expect(demo.locator(".cells .box")).to_have_text(["1", "3", "12", "5", "0", "0", "0"])
    expect(demo.locator(".cells .box.done")).to_have_count(4)


def test_water_grid_pruning(page: Page):
    """搜索空间表：36 格里只算 8 格、砍掉 28 格，答案格 (1, 8) 标绿。"""
    demo = open_demo(page, "25-two-pointers.html", "water-grid")
    click(demo, "演示搜索空间")
    wait_done(demo)
    expect(demo.locator(".wg-cell.calc")).to_have_count(8)
    expect(demo.locator(".wg-cell.cut")).to_have_count(28)
    expect(demo.locator(".wg-cell.top")).to_have_attribute("data-cell", "1,8")
    expect(demo.locator(".wg-cell.top")).to_have_text("49")
    expect(demo.locator(".wg-stat")).to_contain_text("已计算 8 格　被砍掉 28 格　还没处理 0 格")


def test_water_grid_first_step_cuts_row(page: Page):
    """第一步算 (0, 8)，左边更矮，第 0 行剩下的 7 格刚被砍掉（红色）。"""
    demo = open_demo(page, "25-two-pointers.html", "water-grid")
    click(demo, "演示搜索空间")
    wait_done(demo)
    # 放完后往回退到第 2 帧（第一步），这样检查的画面是确定的
    while demo.locator(".step").inner_text() != "2 / 10":
        demo.get_by_role("button", name="← 上一步").click()
    expect(demo.locator(".wg-cell.now")).to_have_attribute("data-cell", "0,8")
    fresh = demo.locator(".wg-cell.fresh")
    expect(fresh).to_have_count(7)
    assert all(cell.startswith("0,") for cell in fresh.evaluate_all("els => els.map(e => e.dataset.cell)"))
