"""第 17 课动画的端到端测试。页面地址带 ?fast，每帧只停 10ms。"""

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


def test_builds_mst(page: Page):
    demo = open_demo(page, "17-kruskal.html", "kruskal")
    click(demo, "开始 Kruskal")
    wait_done(demo)
    expect(demo.locator(".elist .box.pick")).to_have_text(["E–C 1", "A–D 2", "B–E 3", "A–B 4", "C–F 8"])
    expect(demo.locator(".elist .box.skip")).to_have_text(["B–D 5", "B–C 6", "D–E 7"])
    expect(demo.locator(".blocks .box")).to_have_count(1)
    expect(demo.locator(".total")).to_have_text("18")
    expect(demo.locator(".caption")).to_contain_text("提前收工")


def test_skip_when_cycle(page: Page):
    demo = open_demo(page, "17-kruskal.html", "kruskal")
    click(demo, "开始 Kruskal")
    wait_done(demo)
    # 帧：初始、排序、然后每条边 2 帧（考察 + 结论）。B–D 是第 5 条，考察帧是第 11 帧
    total = int(demo.locator(".step").inner_text().split(" / ")[1])
    for _ in range(total - 11):
        click(demo, "← 上一步")
    expect(demo.locator(".step")).to_have_text(f"11 / {total}")
    expect(demo.locator('[data-edge="B–D 5"]')).to_have_class(re.compile("cur"))
    expect(demo.locator(".total")).to_have_text("10")
    click(demo, "下一步 →")
    expect(demo.locator('[data-edge="B–D 5"]')).to_have_class(re.compile("skip"))
    expect(demo.locator(".caption")).to_contain_text("成环")


def test_disconnected(page: Page):
    demo = open_demo(page, "17-kruskal.html", "kruskal")
    click(demo, "不连通的图")
    wait_done(demo)
    expect(demo.locator(".blocks .box")).to_have_count(2)
    expect(demo.locator(".caption")).to_contain_text("不连通")
