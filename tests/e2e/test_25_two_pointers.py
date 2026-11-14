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
