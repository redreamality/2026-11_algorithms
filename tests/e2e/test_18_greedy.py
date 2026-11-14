"""第 18 课动画的端到端测试。页面地址带 ?fast，每帧只停 10ms。"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


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


def picked(demo):
    return demo.locator(".act.picked .act-name")


def test_by_end_time_picks_four(page: Page):
    demo = open_demo(page, "18-greedy.html", "acts")
    click(demo, "按结束时间选")
    wait_done(demo)
    expect(picked(demo)).to_have_text(["A", "D", "G", "H"])
    expect(demo.locator(".act.skipped")).to_have_count(4)
    expect(demo.locator(".count")).to_have_text("4")


def test_skip_frame_shows_conflict(page: Page):
    demo = open_demo(page, "18-greedy.html", "acts")
    click(demo, "按结束时间选")
    wait_done(demo)
    for _ in range(7):  # 退到第 3 帧：正在看 B，它和已选的 A 重叠
        click(demo, "← 上一步")
    expect(demo.locator(".step")).to_have_text("3 / 10")
    expect(demo.locator(".act.cur .act-name")).to_have_text("B")
    expect(demo.locator(".caption")).to_contain_text("跳过")
    expect(demo.locator(".act").first.locator(".endline")).to_have_attribute("style", re.compile("left: ?25%"))


def test_by_start_time_is_worse(page: Page):
    demo = open_demo(page, "18-greedy.html", "acts")
    click(demo, "按开始时间选（反例）")
    wait_done(demo)
    expect(picked(demo)).to_have_text(["C", "F", "H"])
    expect(demo.locator(".caption")).to_contain_text("比按结束时间少")
