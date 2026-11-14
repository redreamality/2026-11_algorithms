"""第 22 课动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"
PAGE = "22-trie.html"


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


def run(demo, op: str, word: str):
    demo.get_by_label("单词").fill(word)
    click(demo, op)
    wait_done(demo)


def test_initial_tree(page: Page):
    demo = open_demo(page, PAGE, "trie")
    # 根 + c a r t + d o g = 8 个节点，3 个结束点
    expect(demo.locator(".tree .box")).to_have_count(8)
    expect(demo.locator(".tree .box.end")).to_have_text(["r", "t", "g"])


def test_insert_shares_prefix(page: Page):
    demo = open_demo(page, PAGE, "trie")
    run(demo, "insert", "cart")
    expect(demo.locator(".tree .box")).to_have_count(9)  # 只新建了一个 t
    expect(demo.locator(".tree .box.end")).to_have_count(4)
    expect(demo.locator(".tree .box.path, .tree .box.hot")).to_have_text(["根", "c", "a", "r", "t"])
    click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("没有 't'，新建")
    expect(demo.locator(".tree .box.new")).to_have_text("t")


def test_prefix_and_search(page: Page):
    demo = open_demo(page, PAGE, "trie")
    run(demo, "前缀列词", "ca")
    expect(demo.locator(".row.out .box")).to_have_text(["car", "cat"])
    expect(demo.locator(".tree .box.path")).to_have_text(["根", "c", "a"])

    run(demo, "search", "ca")
    expect(demo.locator(".caption")).to_contain_text("search → False")

    run(demo, "前缀列词", "x")
    expect(demo.locator(".row.out")).to_contain_text("还没有")
    expect(demo.locator(".caption")).to_contain_text("返回 []")
