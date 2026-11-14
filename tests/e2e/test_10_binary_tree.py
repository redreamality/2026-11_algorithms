"""第 10 课动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"
PAGE = "10-binary-tree.html"


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


@pytest.mark.parametrize("name, expected", [
    ("前序", ["1", "2", "4", "5", "3", "6"]),
    ("中序", ["4", "2", "5", "1", "3", "6"]),
    ("后序", ["4", "5", "2", "6", "3", "1"]),
    ("层序", ["1", "2", "3", "4", "5", "6"]),
])
def test_traversal_output(page: Page, name, expected):
    demo = open_demo(page, PAGE, "btree")
    click(demo, name)
    wait_done(demo)
    expect(demo.locator(".row.out .box")).to_have_text(expected)
    expect(demo.locator(".tree .box.done")).to_have_count(6)


def test_inorder_step_shows_stack(page: Page):
    demo = open_demo(page, PAGE, "btree")
    click(demo, "中序")
    wait_done(demo)
    for _ in range(100):  # 退回到第一次输出：一路向左走到 4
        if "输出 4" in demo.locator(".caption").inner_text():
            break
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_have_text("输出 4。")
    expect(demo.locator(".row.stack .box")).to_have_text(["1", "2", "4"])
    expect(demo.locator(".tree .box.hot")).to_have_text("4")
    expect(demo.locator(".row.out .box")).to_have_text(["4"])


def test_level_order_queue(page: Page):
    demo = open_demo(page, PAGE, "btree")
    click(demo, "层序")
    wait_done(demo)
    click(demo, "← 上一步")
    while "把它的孩子 4、5" not in demo.locator(".caption").inner_text():
        click(demo, "← 上一步")
    expect(demo.locator(".row.queue .box")).to_have_text(["3", "4", "5"])
    expect(demo.locator(".tree .box.hot")).to_have_text("2")
