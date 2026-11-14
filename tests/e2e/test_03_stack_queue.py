"""第 3 课动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"
PAGE = "03-stack-queue.html"


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


def test_stack_lifo_and_empty_pop(page: Page):
    demo = open_demo(page, PAGE, "stack")
    click(demo, "push")
    wait_done(demo)
    expect(demo.locator(".row.data .box")).to_have_text(["1", "2", "3", "4"])
    for _ in range(4):
        click(demo, "pop")
        wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("pop() 返回 1")
    click(demo, "pop")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("IndexError")


def queue_cells(demo):
    return demo.locator(".row.data .box")


def test_queue_enqueue_wraps_to_zero(page: Page):
    demo = open_demo(page, PAGE, "cqueue")
    expect(queue_cells(demo)).to_have_text(["·", "·", "3", "4"])
    click(demo, "enqueue")
    wait_done(demo)
    expect(queue_cells(demo)).to_have_text(["5", "·", "3", "4"])
    expect(demo.locator(".caption")).to_contain_text("回绕到 0")
    ptrs = demo.locator(".row.data .tag.ptr")
    expect(ptrs.nth(1)).to_have_text("tail")
    expect(ptrs.nth(2)).to_have_text("head")
    expect(demo.locator(".row.data .node.hot .box")).to_have_text(["5"])


def test_queue_grows_in_queue_order(page: Page):
    demo = open_demo(page, PAGE, "cqueue")
    for _ in range(3):  # 5 回绕到 0，6 填满，7 触发扩容
        click(demo, "enqueue")
        wait_done(demo)
    expect(demo.locator(".cap")).to_have_text("8")
    expect(demo.locator(".head")).to_have_text("0")
    expect(queue_cells(demo)).to_have_text(["3", "4", "5", "6", "7", "·", "·", "·"])
    for _ in range(2):  # 退回到搬家中途：旧数组也显示出来
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("旧[1] → 新[3]")
    expect(demo.locator(".row.old .node.hot .box")).to_have_text(["6"])

    click(demo, "dequeue")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("dequeue() 返回 3")
