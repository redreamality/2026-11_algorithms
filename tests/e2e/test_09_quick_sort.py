"""第 9 课快速排序动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

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


def test_partition_steps(page: Page):
    demo = open_demo(page, "09-quick-sort.html", "qsort")
    click(demo, "partition")
    wait_done(demo)
    # 帧：原数组、开始、7 次比较（3 次小于各多一帧交换）、基准交换、站定
    expect(demo.locator(".step")).to_have_text("14 / 14")
    expect(demo.locator(".box")).to_have_text(["2", "1", "3", "4", "9", "8", "6", "5"])
    expect(demo.locator(".box.done")).to_have_text(["4"])
    expect(demo.locator(".caption")).to_contain_text("最终位置 3")

    click(demo, "← 上一步")  # 基准还在最后，i 停在 3
    expect(demo.locator(".box.pivot")).to_have_text("4")
    expect(demo.locator(".tag.ptr", has_text="i")).to_have_count(1)
    expect(demo.locator(".box.less")).to_have_text(["2", "1", "3"])


def test_quick_sort_default(page: Page):
    demo = open_demo(page, "09-quick-sort.html", "qsort")
    click(demo, "quick_sort")
    wait_done(demo)
    expect(demo.locator(".box")).to_have_text(["1", "2", "3", "4", "5", "6", "8", "9"])
    expect(demo.locator(".box.done")).to_have_count(8)
    expect(demo.locator(".cmp")).to_have_text("16")
    expect(demo.locator(".caption")).to_contain_text("排好了")


def test_sorted_input_degrades_and_bad_input(page: Page):
    demo = open_demo(page, "09-quick-sort.html", "qsort")
    demo.get_by_label("数组").fill("1 2 3 4 5 6")
    click(demo, "quick_sort")
    wait_done(demo)
    expect(demo.locator(".cmp")).to_have_text("15")  # 5+4+3+2+1 = n(n-1)/2

    demo.get_by_label("数组").fill("a b")
    click(demo, "quick_sort")
    expect(demo.locator(".caption")).to_contain_text("请输入 1～10 个整数")
