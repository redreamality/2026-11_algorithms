"""第 6 课动画的端到端测试：lo / hi / mid 在数组上移动。运行：uv run pytest tests/e2e/test_06_binary_search.py"""

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


def ptr(demo, i: int):
    return demo.locator(f'.node[data-i="{i}"] .ptr')


def search(demo, value: int, op: str):
    demo.get_by_label("值").fill(str(value))
    click(demo, f"{op}(值)")
    wait_done(demo)


def test_search_found(page: Page):
    demo = open_demo(page, "06-binary-search.html", "bsearch")
    search(demo, 12, "binary_search")
    expect(demo.locator(".caption")).to_contain_text("返回 7")
    expect(demo.locator(".box.found")).to_have_text("12")
    expect(demo.locator(".cmp")).to_have_text("3")
    click(demo, "← 上一步")  # 前一帧：区间缩成 [6, 8)
    expect(demo.locator(".range")).to_have_text("[6, 8)")
    expect(ptr(demo, 6)).to_have_text("lo")
    expect(ptr(demo, 8)).to_have_text("hi")
    expect(demo.locator(".node.fade")).to_have_count(8)


def test_search_missing(page: Page):
    demo = open_demo(page, "06-binary-search.html", "bsearch")
    search(demo, 8, "binary_search")
    expect(demo.locator(".caption")).to_contain_text("返回 -1")
    expect(demo.locator(".left")).to_have_text("0")
    expect(demo.locator(".cmp")).to_have_text("4")
    expect(demo.locator(".box.found")).to_have_count(0)


def test_lower_and_upper_bound(page: Page):
    demo = open_demo(page, "06-binary-search.html", "bsearch")
    search(demo, 7, "lower_bound")
    expect(demo.locator(".caption")).to_contain_text("lower_bound(7) = 3")
    expect(ptr(demo, 3)).to_have_text("lo / hi")
    search(demo, 7, "upper_bound")
    expect(demo.locator(".caption")).to_contain_text("upper_bound(7) = 6")
    search(demo, 99, "lower_bound")
    expect(demo.locator(".caption")).to_contain_text("lower_bound(99) = 10")
    expect(demo.locator('.node[data-i="10"] .box')).to_have_class(re.compile("found"))
