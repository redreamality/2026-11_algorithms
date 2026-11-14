"""第 15 课动画的端到端测试。页面地址带 ?fast，每帧只停 10ms。"""

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


def union(demo, a: int, b: int):
    demo.get_by_label("a", exact=True).fill(str(a))
    demo.get_by_label("b", exact=True).fill(str(b))
    click(demo, "union(a, b)")
    wait_done(demo)


def parents(demo):
    return demo.locator(".parent .box")


def test_small_tree_goes_under_big_tree(page: Page):
    demo = open_demo(page, "15-union-find.html", "uf")
    expect(demo.locator(".count")).to_have_text("8")
    union(demo, 0, 1)
    union(demo, 2, 0)  # {2} 比 {0, 1} 小，挂到 0 下面
    expect(parents(demo)).to_have_text(["0", "0", "0", "3", "4", "5", "6", "7"])
    expect(demo.locator(".count")).to_have_text("6")
    expect(demo.locator(".caption")).to_contain_text("返回 True")


def test_union_same_set_returns_false(page: Page):
    demo = open_demo(page, "15-union-find.html", "uf")
    union(demo, 0, 1)
    union(demo, 1, 0)
    expect(demo.locator(".caption")).to_contain_text("返回 False")
    expect(demo.locator(".count")).to_have_text("7")


def test_path_compression_flattens_chain(page: Page):
    demo = open_demo(page, "15-union-find.html", "uf")
    click(demo, "长链 + find(4)")
    wait_done(demo)
    expect(parents(demo)).to_have_text(["0", "0", "0", "0", "0", "5", "6", "7"])
    expect(demo.locator(".caption")).to_contain_text("压缩完成")
    for _ in range(4):  # 退回到刚走到根、还没压缩的那一帧
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("就是根")
    expect(demo.locator(".unode.path")).to_have_count(5)
    expect(parents(demo)).to_have_text(["0", "0", "1", "2", "3", "5", "6", "7"])
    click(demo, "下一步 →")
    expect(demo.locator(".caption")).to_contain_text("让 4 直接指向根 0")
    expect(demo.locator(".edge.new")).to_have_count(1)
