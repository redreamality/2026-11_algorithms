"""第 16 课动画的端到端测试。页面地址带 ?fast，每帧只停 10ms。"""

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


def dist(demo, name: str):
    return demo.locator(f'[data-dist="{name}"]')


def test_final_distances(page: Page):
    demo = open_demo(page, "16-dijkstra.html", "dijkstra")
    click(demo, "从 A 出发")
    wait_done(demo)
    expect(demo.locator(".dist .box")).to_have_text(["A: 0", "B: 3", "C: 1", "D: 3", "E: 6"])
    expect(demo.locator(".gnode.done")).to_have_count(5)
    expect(demo.locator(".heap .box")).to_have_count(0)
    expect(demo.locator(".caption")).to_contain_text("全部确定")


def test_b_relaxed_from_4_to_3(page: Page):
    demo = open_demo(page, "16-dijkstra.html", "dijkstra")
    click(demo, "从 A 出发")
    wait_done(demo)
    while not demo.locator(".step").inner_text().startswith("5 /"):  # 退回第 5 帧：C 刚被确定
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("取出堆顶 (1, C)")
    expect(dist(demo, "B")).to_have_text("B: 4")
    expect(dist(demo, "C")).to_have_class(re.compile("fixed"))
    click(demo, "下一步 →")  # 松弛 C–B：1 + 2 = 3 < 4
    expect(dist(demo, "B")).to_have_text("B: 3")
    expect(dist(demo, "B")).to_have_class(re.compile("hot"))
    expect(demo.locator('[data-edge="CB"]')).to_have_class(re.compile("relax"))
    expect(demo.locator(".heap .box")).to_contain_text(["(3, B)", "(4, B)"])


def test_stale_entry_skipped(page: Page):
    demo = open_demo(page, "16-dijkstra.html", "dijkstra")
    click(demo, "从 A 出发")
    wait_done(demo)
    texts = []
    while True:
        texts.append(demo.locator(".caption").inner_text())
        if demo.get_by_role("button", name="← 上一步").is_disabled():
            break
        click(demo, "← 上一步")
    assert any("过期的旧记录" in t and "(4, B)" in t for t in texts)
    assert any("松弛 B–D" in t and "不更新" in t for t in texts)
