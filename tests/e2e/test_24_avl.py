"""第 24 课动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"
PAGE = "24-balanced-tree.html"


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


def at_depth(demo, d):
    return demo.locator(f'.tree .box[data-depth="{d}"]')


def test_rr_left_rotation(page: Page):
    demo = open_demo(page, PAGE, "avl")
    click(demo, "插入 1, 2, 3")
    wait_done(demo)
    expect(at_depth(demo, 0)).to_have_text("2")
    expect(at_depth(demo, 1)).to_have_text(["1", "3"])
    expect(demo.locator(".tree .box.done")).to_have_text("2")
    expect(demo.locator(".height")).to_have_text("2")
    for _ in range(2):  # 退回到发现失衡的那一帧：1 的 bf 是 -2
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("失衡")
    expect(demo.locator(".tree .box.found")).to_have_text("1")
    expect(demo.locator(".tree .bf.bad")).to_have_text("-2")
    expect(demo.locator(".height")).to_have_text("3")


def test_lr_two_rotations(page: Page):
    demo = open_demo(page, PAGE, "avl")
    click(demo, "插入 3, 1, 2")
    wait_done(demo)
    expect(at_depth(demo, 0)).to_have_text("2")
    expect(at_depth(demo, 1)).to_have_text(["1", "3"])
    click(demo, "← 上一步")  # 第一次旋转后：3 → 2 → 1 变成一条直线
    expect(demo.locator(".caption")).to_contain_text("先对 1 左旋")
    expect(at_depth(demo, 0)).to_have_text("3")
    expect(at_depth(demo, 1)).to_have_text("2")
    expect(at_depth(demo, 2)).to_have_text("1")
    click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("LR")


def test_sorted_insert_stays_balanced(page: Page):
    demo = open_demo(page, PAGE, "avl")
    click(demo, "插入 1～7")
    wait_done(demo)
    expect(demo.locator(".height")).to_have_text("3")
    expect(at_depth(demo, 0)).to_have_text("4")
    expect(demo.locator(".row.out .box")).to_have_text([str(v) for v in range(1, 8)])
    demo.get_by_label("值").fill("4")
    click(demo, "insert(值)")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("重复值忽略")
