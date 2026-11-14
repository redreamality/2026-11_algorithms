"""第 8 课归并排序动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

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


def top_row(demo):
    return demo.locator('.seg[data-depth="0"] .box')


def test_sorts_default_array(page: Page):
    demo = open_demo(page, "08-merge-sort.html", "msort")
    expect(top_row(demo)).to_have_text(["5", "2", "4", "7", "1", "3", "2", "6"])
    click(demo, "merge_sort")
    wait_done(demo)
    expect(top_row(demo)).to_have_text(["1", "2", "2", "3", "4", "5", "6", "7"])
    expect(demo.locator(".cmp")).to_have_text("17")
    expect(demo.locator(".caption")).to_contain_text("排好了")


def test_split_then_merge_with_pointers(page: Page):
    demo = open_demo(page, "08-merge-sort.html", "msort")
    demo.get_by_label("数组").fill("3 1 2")
    click(demo, "merge_sort")
    wait_done(demo)
    # 帧：原数组、切一层、切到底、合并[1]和[2]、取1、接2、合并[3]和[1,2]、取1、取2、接3、排好了
    expect(demo.locator(".step")).to_have_text("11 / 11")
    for _ in range(8):
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("切到每段只剩 1 个")
    expect(demo.locator(".seg")).to_have_count(5)  # 3 | 1 2 | 1 | 2 拆分树
    click(demo, "下一步 →")
    click(demo, "下一步 →")  # 取走 1
    expect(demo.locator(".caption")).to_contain_text("取左边的 1")
    expect(demo.locator(".tag.ptr", has_text="j")).to_have_count(1)
    expect(demo.locator(".node.fade")).to_have_count(1)


def test_tie_takes_left_and_bad_input(page: Page):
    demo = open_demo(page, "08-merge-sort.html", "msort")
    demo.get_by_label("数组").fill("1 1")
    click(demo, "merge_sort")
    wait_done(demo)
    click(demo, "← 上一步")
    click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("相等时取左边")

    demo.get_by_label("数组").fill("a b")
    click(demo, "merge_sort")
    expect(demo.locator(".caption")).to_contain_text("请输入 1～10 个整数")
