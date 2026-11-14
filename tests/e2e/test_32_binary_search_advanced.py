"""第 32 课动画的端到端测试：搜索旋转排序数组、二分答案。运行：uv run pytest tests/e2e/test_32_binary_search_advanced.py"""

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


def test_search_rotated_found(page: Page):
    demo = open_demo(page, "32-binary-search-advanced.html", "binary-search-advanced")
    click(demo, "搜索旋转数组")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("找到了！返回 7")
    expect(demo.locator(".box.found")).to_have_text("1")
    # 倒数第三帧：右半边 [6, 8] 有序，1 在 (0, 2] 里，往右走
    click(demo, "← 上一步")
    click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("右半边 [6, 8] 有序")
    expect(demo.locator(".box.sorted")).to_have_text(["0", "1", "2"])


def test_search_rotated_missing(page: Page):
    demo = open_demo(page, "32-binary-search-advanced.html", "binary-search-advanced")
    demo.get_by_label("target").fill("3")
    click(demo, "搜索旋转数组")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("没有 3，返回 -1")


def test_koko(page: Page):
    demo = open_demo(page, "32-binary-search-advanced.html", "binary-search-advanced")
    click(demo, "珂珂吃香蕉")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("最小速度是 4")
    expect(demo.locator(".box.found")).to_have_text("4")
    expect(demo.locator(".box.slow")).to_have_text(["3"])
    expect(demo.locator(".box.fast")).to_have_text(["5", "6"])
