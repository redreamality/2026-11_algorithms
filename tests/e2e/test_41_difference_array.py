"""第 41 课动画的端到端测试：差分数组每格算对、区间加只改两格、还原结果正确、拼车在第一次超载时停下。
运行：uv run pytest tests/e2e/test_41_difference_array.py"""

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


def step_back_to(demo, caption_part: str):
    """从当前帧一步步往回退，直到说明文字里出现 caption_part。"""
    for _ in range(40):
        if caption_part in demo.locator(".caption").inner_text():
            return
        click(demo, "← 上一步")
    raise AssertionError(f"没有找到说明里含 {caption_part!r} 的帧")


def test_range_add_and_restore(page: Page):
    demo = open_demo(page, "41-difference-array.html", "difference")
    click(demo, "区间加与还原")
    wait_done(demo)
    expect(demo.locator(".box.diff")).to_have_text(["3", "-2", "5", "-3", "7", "4", "-9", "4", "-3"])
    expect(demo.locator(".box.restored")).to_have_text(["3", "1", "6", "3", "10", "14", "5", "9"])
    expect(demo.locator(".best")).to_have_text("[3, 1, 6, 3, 10, 14, 5, 9]")
    expect(demo.locator(".caption")).to_contain_text("两者一样")


def test_range_add_marks_only_two_cells(page: Page):
    demo = open_demo(page, "41-difference-array.html", "difference")
    click(demo, "区间加与还原")
    wait_done(demo)
    step_back_to(demo, "下标 2～5 整体加 2")
    expect(demo.locator(".box.diff.plus")).to_have_text(["5"])
    expect(demo.locator(".box.diff.minus")).to_have_text(["-9"])
    expect(demo.locator(".box.number.range")).to_have_count(4)
    expect(demo.locator(".box.restored.empty")).to_have_count(8)  # 还没开始还原


def test_car_pooling_stops_at_first_overload(page: Page):
    demo = open_demo(page, "41-difference-array.html", "difference")
    click(demo, "拼车")
    wait_done(demo)
    expect(demo.locator(".best")).to_have_text("False")
    expect(demo.locator(".box.diff")).to_have_text(["0", "2", "0", "3", "0", "-2", "0", "-3", "0"])
    expect(demo.locator(".box.onboard.over")).to_have_text(["5"])
    expect(demo.locator(".box.onboard.done")).to_have_text(["0", "2", "2"])
    expect(demo.locator(".caption")).to_contain_text("位置 3")
