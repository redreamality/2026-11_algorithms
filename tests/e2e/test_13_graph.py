"""第 13 课动画的端到端测试。运行：uv run pytest tests/e2e/test_13_graph.py"""

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


def order(demo):
    return demo.locator(".row.order .box")


def held(demo):
    return demo.locator(".row.queue .box")


def test_bfs_from_0(page: Page):
    demo = open_demo(page, "13-graph-traversal.html", "graph")
    expect(demo.locator("g.vertex")).to_have_count(6)
    click(demo, "BFS")
    wait_done(demo)
    expect(order(demo)).to_have_text(["0", "1", "2", "3", "4", "5"])
    expect(demo.locator("g.vertex.done")).to_have_count(6)
    expect(demo.locator("line.tree")).to_have_count(5)  # 6 个点的 BFS 树有 5 条边
    expect(demo.locator('g[data-id="5"] .dist')).to_have_text("d=3")
    expect(held(demo)).to_have_count(0)


def test_bfs_other_start(page: Page):
    demo = open_demo(page, "13-graph-traversal.html", "graph")
    demo.get_by_label("起点").select_option("3")
    click(demo, "BFS")
    wait_done(demo)
    expect(order(demo)).to_have_text(["3", "1", "2", "4", "5", "0"])
    expect(demo.locator('g[data-id="0"] .dist')).to_have_text("d=2")


def test_dfs_goes_deep_then_backtracks(page: Page):
    demo = open_demo(page, "13-graph-traversal.html", "graph")
    click(demo, "DFS")
    wait_done(demo)
    expect(order(demo)).to_have_text(["0", "1", "3", "2", "4", "5"])
    caption = demo.locator(".caption")
    for _ in range(40):  # 退回到 2 刚出栈的那一帧
        if "2 的邻居都看完了" in caption.inner_text():
            break
        click(demo, "← 上一步")
    expect(caption).to_contain_text("2 的邻居都看完了")
    expect(held(demo)).to_have_text(["0", "1", "3"])
    click(demo, "← 上一步")  # 出栈前，2 还在栈顶
    expect(held(demo)).to_have_text(["0", "1", "3", "2"])
    expect(demo.locator("g.vertex.cur")).to_have_attribute("data-id", "2")
