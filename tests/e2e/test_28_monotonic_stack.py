"""第 28 课动画的端到端测试：单调栈的三道题都放到最后一帧，答案对得上。运行：uv run pytest tests/e2e/test_28_monotonic_stack.py"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "28-monotonic-stack.html").as_uri() + "?fast")
    demo = page.locator("#monotonic")
    expect(demo).not_to_be_empty()
    assert not errors, errors
    return demo


def run_to_end(demo, problem: str):
    demo.get_by_label("题目").select_option(label=problem)
    demo.get_by_role("button", name="开始", exact=True).click()
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def test_monotonic_stack_final_frames(page: Page):
    demo = open_demo(page)

    run_to_end(demo, "每日温度")
    expect(demo.locator(".result")).to_have_text("[1, 1, 4, 2, 1, 1, 0, 0]")
    expect(demo.locator(".stack-row .box")).to_have_count(2)  # 第 6、7 天一直没等到

    run_to_end(demo, "最大矩形")
    expect(demo.locator(".result")).to_have_text("10")
    expect(demo.locator(".caption")).to_contain_text("最大矩形面积 = 10")

    run_to_end(demo, "接雨水")
    expect(demo.locator(".result")).to_have_text("6")
    expect(demo.locator(".caption")).to_contain_text("一共接到 6 格水")
