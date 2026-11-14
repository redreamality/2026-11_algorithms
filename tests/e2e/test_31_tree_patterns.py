"""第 31 课动画的端到端测试：后序位置求直径、找最近公共祖先。运行：uv run pytest tests/e2e/test_31_tree_patterns.py"""

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


def test_diameter(page: Page):
    demo = open_demo(page, "31-tree-patterns.html", "tree-patterns")
    click(demo, "求直径")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("直径 = 6")
    expect(demo.locator(".caption")).to_contain_text("8 → 6 → 4 → 2 → 5 → 7 → 9")
    expect(demo.locator(".tree .box.found")).to_have_count(7)
    expect(demo.locator(".stat")).to_have_text("longest_path = 6（最高点是节点 2）")
    # 每个节点交给父亲的都是深度：根是 5，节点 2 是 4
    expect(demo.locator('.ret[data-value="1"]')).to_have_text("深 5")
    expect(demo.locator('.ret[data-value="2"]')).to_have_text("深 4")


def test_lowest_common_ancestor(page: Page):
    demo = open_demo(page, "31-tree-patterns.html", "tree-patterns")
    click(demo, "找最近公共祖先(8, 7)")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("最近公共祖先是 2")
    expect(demo.locator(".tree .box.found")).to_have_text("2")
    expect(demo.locator('.ret[data-value="3"]')).to_have_text("返回 空")
    expect(demo.locator('.ret[data-value="1"]')).to_have_text("返回 2")
