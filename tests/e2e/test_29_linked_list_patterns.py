"""第 29 课动画的端到端测试：反转、找中点、删倒数第 N 个、找入环点都放到最后一帧。运行：uv run pytest tests/e2e/test_29_linked_list_patterns.py"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "29-linked-list-patterns.html").as_uri() + "?fast")
    demo = page.locator("#patterns")
    expect(demo).not_to_be_empty()
    assert not errors, errors
    return demo


def run_to_end(demo, button: str):
    demo.get_by_role("button", name=button, exact=True).click()
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def test_linked_list_patterns_final_frames(page: Page):
    demo = open_demo(page)

    run_to_end(demo, "反转链表")
    expect(demo.locator(".caption")).to_contain_text("反转完成")
    expect(demo.locator(".walk")).to_have_text("[5, 4, 3, 2, 1]")
    expect(demo.locator(".node .box")).to_have_text(["5", "4", "3", "2", "1"])

    run_to_end(demo, "找中点")
    expect(demo.locator(".caption")).to_contain_text("中点是 3")
    expect(demo.locator(".node.hot .box")).to_have_text("3")

    run_to_end(demo, "删除倒数第 N 个")
    expect(demo.locator(".walk")).to_have_text("[1, 2, 3, 5]")
    demo.get_by_label("N", exact=True).fill("5")
    run_to_end(demo, "删除倒数第 N 个")
    expect(demo.locator(".walk")).to_have_text("[2, 3, 4, 5]")

    run_to_end(demo, "判环并找入环点")
    expect(demo.locator(".caption")).to_contain_text("入环点是 3")
    expect(demo.locator(".cycle-back")).to_have_text("↩ 回到 3")
