"""第 30 课动画的端到端测试：LeetCode 146 示例放到最后一帧，返回值和链表顺序对得上。运行：uv run pytest tests/e2e/test_30_lru_cache.py"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "30-lru-cache.html").as_uri() + "?fast")
    demo = page.locator("#lru")
    expect(demo).not_to_be_empty()
    assert not errors, errors
    return demo


def run_to_end(demo, button: str):
    demo.get_by_role("button", name=button, exact=True).click()
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def test_lru_example_and_eviction(page: Page):
    demo = open_demo(page)

    run_to_end(demo, "播放 LeetCode 示例")
    expect(demo.locator(".outputs")).to_have_text("[None, None, 1, None, -1, None, -1, 3, 4]")
    expect(demo.locator(".dll .box:not(.sentinel)")).to_have_text(["4:4", "3:3"])
    expect(demo.locator(".table-row .box")).to_have_count(2)

    # 已满时 put 一个新 key：淘汰最右边（最久没用）的 3，新节点放到最左边
    demo.get_by_label("key", exact=True).fill("5")
    demo.get_by_label("value", exact=True).fill("50")
    run_to_end(demo, "put(key, value)")
    expect(demo.locator(".dll .box:not(.sentinel)")).to_have_text(["5:50", "4:4"])
    demo.get_by_role("button", name="← 上一步", exact=True).click()
    expect(demo.locator(".detached")).to_contain_text("被淘汰的节点：3:3")
