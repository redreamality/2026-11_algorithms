"""第 26 课动画的端到端测试：三道滑动窗口题都能放到最后一帧，并且最终答案和高亮对得上。
运行：uv run pytest tests/e2e/test_26_sliding_window.py"""

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


def test_longest_substring(page: Page):
    demo = open_demo(page, "26-sliding-window.html", "window")
    click(demo, "无重复最长子串")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text('"abc"，长度 3')
    expect(demo.locator(".cells .box.done")).to_have_text(["a", "b", "c"])


def test_min_window(page: Page):
    demo = open_demo(page, "26-sliding-window.html", "window")
    click(demo, "最小覆盖子串")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text('"BANC"')
    expect(demo.locator(".best")).to_contain_text("长度 4")
    expect(demo.locator(".cells .box.done")).to_have_text(["B", "A", "N", "C"])


def test_min_subarray(page: Page):
    demo = open_demo(page, "26-sliding-window.html", "window")
    click(demo, "长度最小的子数组")
    wait_done(demo)
    expect(demo.locator(".best")).to_have_text("2")
    expect(demo.locator(".cells .box.done")).to_have_text(["4", "3"])
