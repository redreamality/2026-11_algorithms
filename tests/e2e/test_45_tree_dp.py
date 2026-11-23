"""第 45 课动画的端到端测试：打家劫舍 III 后序返回 (偷, 不偷)、边列表上的树的直径。
运行：uv run pytest tests/e2e/test_45_tree_dp.py"""

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


def test_rob_tree_returns_two_numbers(page: Page):
    demo = open_demo(page, "45-tree-dp.html", "tree-dp")
    click(demo, "打家劫舍 III")
    wait_done(demo)
    expect(demo.locator('.ret[data-node="0"]')).to_have_text("偷 8 / 不偷 9")
    expect(demo.locator('.ret[data-node="1"]')).to_have_text("偷 4 / 不偷 4")
    expect(demo.locator('.ret[data-node="2"]')).to_have_text("偷 5 / 不偷 1")
    expect(demo.locator('.ret[data-node="3"]')).to_have_text("偷 1 / 不偷 0")
    # 被偷的是价值 4 和 5 的两间（节点 1、2）
    expect(demo.locator(".tree .box.found")).to_have_text(["4", "5"])
    expect(demo.locator(".stat")).to_have_text("答案 = max(8, 9) = 9")
    # 倒数第二帧：回到根，后序位置
    click(demo, "← 上一步")
    expect(demo.locator(".tree .box.hot")).to_have_attribute("data-node", "0")
    expect(demo.locator(".caption")).to_contain_text("回到 3（后序位置）")


def test_tree_diameter_from_edge_list(page: Page):
    demo = open_demo(page, "45-tree-dp.html", "tree-dp")
    click(demo, "树的直径")
    wait_done(demo)
    # 1 帧开场 + 5 条边 + 1 帧 BFS + 6 个节点 + 1 帧答案
    expect(demo.locator(".step")).to_have_text("14 / 14")
    expect(demo.locator('[data-list="0"]')).to_have_text("adjacency[0] = [1, 2]")
    expect(demo.locator('[data-list="1"]')).to_have_text("adjacency[1] = [0, 3, 4]")
    expect(demo.locator(".order")).to_have_text("order = [0, 1, 2, 3, 4, 5]")
    expect(demo.locator('.ret[data-node="0"]')).to_have_text("深 2")
    expect(demo.locator(".tree .box.found")).to_have_count(5)
    expect(demo.locator(".caption")).to_contain_text("直径 = 4，路径 3 → 1 → 0 → 2 → 5")
    expect(demo.locator(".stat")).to_have_text("longest = 4（最高点是节点 0）")


def test_tree_diameter_builds_adjacency_both_ways(page: Page):
    demo = open_demo(page, "45-tree-dp.html", "tree-dp")
    click(demo, "树的直径")
    wait_done(demo)
    for _ in range(12):
        click(demo, "← 上一步")
    # 第 2 帧：处理边 (0, 1)，两头的列表都高亮
    expect(demo.locator(".step")).to_have_text("2 / 14")
    expect(demo.locator(".adjacency.hot")).to_have_count(2)
    expect(demo.locator('[data-list="0"]')).to_have_text("adjacency[0] = [1]")
    expect(demo.locator('[data-list="1"]')).to_have_text("adjacency[1] = [0]")
    # 走到倒序处理的第一个节点：最后进 order 的 5，跳过父亲 2，是叶子
    for _ in range(6):
        click(demo, "下一步 →")
    expect(demo.locator(".tree .box.hot")).to_have_attribute("data-node", "5")
    expect(demo.locator(".caption")).to_contain_text("跳过父亲 2")
