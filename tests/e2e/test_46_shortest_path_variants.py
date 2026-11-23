"""第 46 课动画的端到端测试：0-1 BFS 和 Floyd 放到最后一帧，再检查中间的关键帧。

运行：uv run pytest tests/e2e/test_46_shortest_path_variants.py
"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    page.goto((LESSONS / "46-shortest-path-variants.html").as_uri() + "?fast")
    demo = page.locator("#variants")
    expect(demo).not_to_be_empty()
    assert not errors, errors
    return demo


def wait_done(demo):
    """等动画放到最后一帧：计数器显示成 “N / N”。"""
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def click(demo, name: str):
    demo.get_by_role("button", name=name, exact=True).click()


def test_zero_one_bfs_final_distances(page: Page):
    demo = open_demo(page)
    click(demo, "0-1 BFS 从 A 出发")
    wait_done(demo)
    expect(demo.locator(".dist .box")).to_have_text(["A: 0", "B: 0", "C: 0", "D: 1", "E: 1"])
    expect(demo.locator(".gnode.done")).to_have_count(5)
    expect(demo.locator(".deque .box")).to_have_count(0)
    expect(demo.locator(".caption")).to_contain_text("全部确定")


def test_zero_one_bfs_front_and_back(page: Page):
    """B 先经收费路排到队尾 (1, B)，再经免费路 C–B 插到队头 (0, B)；后来 (1, B) 作为过期记录被跳过。"""
    demo = open_demo(page)
    click(demo, "0-1 BFS 从 A 出发")
    wait_done(demo)
    while "C–B 是免费路" not in demo.locator(".caption").inner_text():
        click(demo, "← 上一步")
    expect(demo.locator('[data-dist="B"]')).to_have_text("B: 0")
    expect(demo.locator('[data-edge="CB"]')).to_have_class(re.compile("relax"))
    expect(demo.locator(".deque .box")).to_have_text(["(0, B)", "(1, B)"])
    expect(demo.locator(".deque .box").first).to_have_class(re.compile("front"))
    expect(demo.locator(".deque .box").last).to_have_class(re.compile("back"))
    later_captions = []  # 从这一帧往后翻到最后一帧
    while not demo.get_by_role("button", name="下一步 →").is_disabled():
        click(demo, "下一步 →")
        later_captions.append(demo.locator(".caption").inner_text())
    assert any("过期记录" in caption and "(1, B)" in caption for caption in later_captions)


def test_floyd_final_table(page: Page):
    demo = open_demo(page)
    click(demo, "Floyd：逐个放开中转站")
    wait_done(demo)
    expected = {"A": "00011", "B": "00011", "C": "00011", "D": "11100", "E": "11100"}
    for start, row in expected.items():
        for end, value in zip("ABCDE", row):
            expect(demo.locator(f'[data-cell="{start}{end}"]')).to_have_text(value)
    expect(demo.locator(".matrix td", has_text="∞")).to_have_count(0)


def test_floyd_a_to_d_improves_twice(page: Page):
    """dist[A][D]：初始 ∞，k = B 时变成 2，k = C 时变成 1。"""
    demo = open_demo(page)
    click(demo, "Floyd：逐个放开中转站")
    wait_done(demo)
    seen = []
    while True:
        value = demo.locator('[data-cell="AD"]').inner_text()
        if not seen or seen[-1] != value:
            seen.append(value)
        if demo.get_by_role("button", name="← 上一步").is_disabled():
            break
        click(demo, "← 上一步")
    assert seen == ["1", "2", "∞"]
    # 第一帧还没有中转站：只能直达
    expect(demo.locator('[data-cell="AE"]')).to_have_text("∞")
    expect(demo.locator(".gnode.middle")).to_have_count(0)
    click(demo, "下一步 →")
    expect(demo.locator('.gnode.middle[data-node="A"]')).to_have_count(1)
    expect(demo.locator(".caption")).to_contain_text("k = A")


def test_reset(page: Page):
    demo = open_demo(page)
    click(demo, "0-1 BFS 从 A 出发")
    wait_done(demo)
    click(demo, "重置")
    expect(demo.locator(".step")).to_have_text("1 / 1")
    expect(demo.locator(".dist .box")).to_have_text(["A: ∞", "B: ∞", "C: ∞", "D: ∞", "E: ∞"])
