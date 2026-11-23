"""第 44 课动画的端到端测试：分配任务填 best[mask]、旅行商填 shortest[mask][last]。
运行：uv run pytest tests/e2e/test_44_bitmask_dp.py"""

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


def cell(demo, key: str):
    return demo.locator(f'td[data-cell="{key}"]')


def test_assignment_fills_masks_in_order(page: Page):
    demo = open_demo(page, "44-bitmask-dp.html", "bitmask-dp")
    click(demo, "分配任务")
    wait_done(demo)
    expect(demo.locator(".step")).to_have_text("10 / 10")
    assert [cell(demo, f"{mask},1").inner_text() for mask in range(8)] == ["0", "9", "2", "8", "7", "12", "5", "9"]
    expect(cell(demo, "7,1")).to_have_class("best")
    # 倒推出的分法：骑手 0 → 单 1，骑手 1 → 单 0，骑手 2 → 单 2
    for key in ("c0,1", "c1,0", "c2,2"):
        expect(cell(demo, key)).to_have_class("best")
    expect(demo.locator(".stat")).to_have_text("答案 = 9")
    # 倒数第二帧：填 111，最后一个骑手 2 送单 2，用到 best[011]
    click(demo, "← 上一步")
    expect(demo.locator("td.cur")).to_have_attribute("data-cell", "7,1")
    expect(cell(demo, "3,1")).to_have_class("dep")
    expect(cell(demo, "c2,2")).to_have_class("dep")


def test_assignment_steps_go_by_increasing_mask(page: Page):
    demo = open_demo(page, "44-bitmask-dp.html", "bitmask-dp")
    click(demo, "分配任务")
    wait_done(demo)
    for _ in range(8):
        click(demo, "← 上一步")
    expect(demo.locator("td.cur")).to_have_attribute("data-cell", "0,1")  # 第 2 帧：初始值
    for mask in range(1, 8):
        click(demo, "下一步 →")
        expect(demo.locator("td.cur")).to_have_attribute("data-cell", f"{mask},1")


def test_traveling_salesman(page: Page):
    demo = open_demo(page, "44-bitmask-dp.html", "bitmask-dp")
    click(demo, "旅行商")
    wait_done(demo)
    expect(demo.locator(".step")).to_have_text("15 / 15")
    assert [cell(demo, f"15,{last}").inner_text() for last in range(4)] == ["", "16", "9", "11"]
    assert [cell(demo, f"7,{last}").inner_text() for last in range(4)] == ["", "15", "8", ""]
    # 8 行 × 4 列 = 32 格，有意义的只有 13 格
    expect(demo.locator("td.off")).to_have_count(19)
    expect(demo.locator("td.best")).to_have_count(2)  # 停在 1 和停在 2 回站都是 18
    expect(demo.locator(".stat")).to_have_text("答案 = 18")
    expect(demo.locator(".caption")).to_contain_text("0 → 1 → 3 → 2 → 0")
    # 倒数第二帧：填 shortest[1111][3]。上一站是 1 要 15 + 4 = 19，是 2 只要 8 + 3 = 11，所以用到 (0111, 2)
    click(demo, "← 上一步")
    expect(demo.locator("td.cur")).to_have_attribute("data-cell", "15,3")
    expect(cell(demo, "7,2")).to_have_class("dep")
    expect(cell(demo, "d2,3")).to_have_class("dep")
