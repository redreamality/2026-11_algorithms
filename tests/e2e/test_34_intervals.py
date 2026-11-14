"""第 34 课动画的端到端测试：合并区间、会议室 II 放到最后一帧。运行：uv run pytest tests/e2e/test_34_intervals.py"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    page.goto((LESSONS / "34-intervals.html").as_uri() + "?fast")
    demo = page.locator("#intervals")
    expect(demo).not_to_be_empty()
    assert not errors, errors
    return demo


def wait_done(demo):
    """等动画放到最后一帧：计数器显示成 “N / N”。"""
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def test_merge_intervals(page: Page):
    demo = open_demo(page)
    demo.get_by_role("button", name="合并区间", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".answer")).to_have_text("[[1, 6], [8, 12], [15, 18]]")
    expect(demo.locator(".caption")).to_contain_text("合并结果")
    expect(demo.locator(".act.result .seg")).to_have_count(3)


def test_meeting_rooms(page: Page):
    demo = open_demo(page)
    demo.get_by_role("button", name="会议室 II", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".answer")).to_have_text("4")
    expect(demo.locator(".caption")).to_contain_text("至少需要 4 间会议室")
    # D 接着用 B 腾出的会议室 2，E 接着用 A 腾出的会议室 1
    expect(demo.locator('[data-name="D"] .room-tag')).to_have_text("会议室 2")
    expect(demo.locator('[data-name="E"] .room-tag')).to_have_text("会议室 1")
