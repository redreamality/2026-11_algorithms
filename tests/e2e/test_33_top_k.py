"""第 33 课动画的端到端测试：双堆求数据流的中位数。运行：uv run pytest tests/e2e/test_33_top_k.py"""

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


def test_example_stream_then_add_one(page: Page):
    demo = open_demo(page, "33-top-k.html", "two-heaps")
    click(demo, "播放示例数据流")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("中位数 = 7.5")
    expect(demo.locator(".smaller-half .box")).to_have_text(["1", "3", "5", "7"])
    expect(demo.locator(".larger-half .box")).to_have_text(["8", "9", "10", "15"])
    expect(demo.locator(".box.top")).to_have_text(["7", "8"])
    expect(demo.locator(".median")).to_have_text("7.5")

    # 再加入 2：7 先被送到右边，右边多了，再把 7 挪回左边
    demo.get_by_label("值").fill("2")
    click(demo, "加入")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("中位数 = 7")
    expect(demo.locator(".smaller-half .box")).to_have_text(["1", "2", "3", "5", "7"])
    expect(demo.locator(".larger-half .box")).to_have_text(["8", "9", "10", "15"])
    click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("把它的堆顶（最小值）7 挪回较小的一半")
    expect(demo.locator(".box.moving")).to_have_text("7")
