"""第 12 课堆动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

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


def arr(demo):
    return demo.locator(".row.arr .box")


def test_push_bubbles_up_to_root(page: Page):
    demo = open_demo(page, "12-heap.html", "heap")
    expect(arr(demo)).to_have_text(["1", "3", "2", "6", "4", "5"])
    demo.get_by_label("要插入的值").fill("0")
    click(demo, "push(值)")
    wait_done(demo)
    expect(arr(demo)).to_have_text(["0", "3", "1", "6", "4", "5", "2"])
    expect(demo.locator(".tree .box").first).to_have_text("0")
    expect(demo.locator(".tree line")).to_have_count(6)
    click(demo, "← 上一步")
    click(demo, "← 上一步")  # 最后一次交换：树和数组里都标红两个格子
    expect(demo.locator(".caption")).to_contain_text("交换")
    expect(demo.locator(".row.arr .box.found")).to_have_text(["0", "1"])
    expect(demo.locator(".tree .box.found")).to_have_count(2)


def test_pop_sifts_down(page: Page):
    demo = open_demo(page, "12-heap.html", "heap")
    click(demo, "pop")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("返回 1")
    expect(arr(demo)).to_have_text(["2", "3", "5", "6", "4"])
    expect(demo.locator(".size")).to_have_text("5")


def test_heapify_then_sort(page: Page):
    demo = open_demo(page, "12-heap.html", "heap")
    click(demo, "heapify 乱序数组")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("建堆完成")
    expect(arr(demo).first).to_have_text("1")
    click(demo, "堆排序")
    wait_done(demo)
    expect(demo.locator(".row.out .box")).to_have_text([str(i) for i in range(1, 10)])
    expect(demo.locator(".size")).to_have_text("0")
    click(demo, "pop")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("IndexError")
