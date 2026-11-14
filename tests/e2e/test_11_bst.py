"""第 11 课动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"
PAGE = "11-bst.html"


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


def inorder(demo):
    return demo.locator(".row.out .box")


def test_insert_follows_path(page: Page):
    demo = open_demo(page, PAGE, "bst")
    expect(inorder(demo)).to_have_text(["1", "3", "4", "5", "6", "7", "8", "9"])
    demo.get_by_label("值").fill("2")
    click(demo, "insert(值)")
    wait_done(demo)
    expect(inorder(demo)).to_have_text(["1", "2", "3", "4", "5", "6", "7", "8", "9"])
    expect(demo.locator(".tree .box.path")).to_have_text(["5", "3", "1"])  # 走过的路：5 → 3 → 1
    expect(demo.locator(".tree .box.hot")).to_have_text("2")
    expect(demo.locator(".size")).to_have_text("9")

    click(demo, "insert(值)")  # 再插一次 2：重复值忽略
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("重复值忽略")
    expect(demo.locator(".size")).to_have_text("9")


def test_remove_two_children_uses_successor(page: Page):
    demo = open_demo(page, PAGE, "bst")
    demo.get_by_label("值").fill("5")
    click(demo, "remove(值)")
    wait_done(demo)
    expect(inorder(demo)).to_have_text(["1", "3", "4", "6", "7", "8", "9"])
    expect(demo.locator('.tree .box[data-depth="0"]')).to_have_text("6")
    click(demo, "← 上一步")  # 复制完、还没删掉旧后继：树里有两个 6
    expect(demo.locator(".caption")).to_contain_text("复制")
    expect(demo.locator(".tree .box.done")).to_have_text("6")
    expect(demo.locator(".tree .box.found")).to_have_text("6")
    click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("它就是后继")
    expect(demo.locator(".tree .box.found")).to_have_text("5")


def test_remove_one_child_and_sorted_insert(page: Page):
    demo = open_demo(page, PAGE, "bst")
    demo.get_by_label("值").fill("7")
    click(demo, "remove(值)")  # 7 只有左孩子 6
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("6 接替了 7")
    expect(demo.locator(".size")).to_have_text("7")

    click(demo, "有序插入 1～7")
    wait_done(demo)
    expect(inorder(demo)).to_have_text([str(v) for v in range(1, 8)])
    expect(demo.locator(".height")).to_have_text("7")
    expect(demo.locator(".caption")).to_contain_text("退化成链表")
