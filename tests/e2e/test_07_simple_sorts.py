"""第 7 课简单排序动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

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


def boxes(demo):
    return demo.locator(".stage .box")


def test_selection_sort_is_unstable(page: Page):
    demo = open_demo(page, "07-simple-sorts.html", "ssort")
    expect(boxes(demo)).to_have_text(["3a", "5", "3b", "1", "4", "2"])
    demo.get_by_label("算法").select_option("selection")
    click(demo, "排序")
    wait_done(demo)
    expect(boxes(demo)).to_have_text(["1", "2", "3b", "3a", "4", "5"])
    expect(demo.locator(".cmp")).to_have_text("15")
    expect(demo.locator(".caption")).to_contain_text("不稳定")


def test_insertion_sort_is_stable_and_steps(page: Page):
    demo = open_demo(page, "07-simple-sorts.html", "ssort")
    demo.get_by_label("算法").select_option("insertion")
    click(demo, "排序")
    wait_done(demo)
    expect(boxes(demo)).to_have_text(["1", "2", "3a", "3b", "4", "5"])
    expect(demo.locator(".caption")).to_contain_text("稳定")
    expect(demo.locator(".caption")).not_to_contain_text("不稳定")
    # 帧：原数组、拿起5、5停、拿起3b、5挪、3a=3b停 ……
    for _ in range(int(demo.locator(".step").inner_text().split(" / ")[0]) - 6):
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("相等就停")
    expect(boxes(demo)).to_have_text(["3a", "3b", "5", "1", "4", "2"])
    expect(demo.locator(".tag.ptr", has_text="x")).to_have_count(1)


def test_nearly_sorted_is_fast_for_insertion(page: Page):
    demo = open_demo(page, "07-simple-sorts.html", "ssort")
    demo.get_by_label("算法").select_option("insertion")
    click(demo, "近乎有序")
    wait_done(demo)
    expect(boxes(demo)).to_have_text(["1", "2", "3", "4", "5", "6", "7", "8"])
    expect(demo.locator(".cmp")).to_have_text("9")  # 7 次基本比较 + 2 个逆序各多比一次
    expect(demo.locator(".moves")).to_have_text("2")

    demo.get_by_label("数组").fill("a b")
    click(demo, "排序")
    expect(demo.locator(".caption")).to_contain_text("请输入 1～10 个整数")
