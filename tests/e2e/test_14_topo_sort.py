"""第 14 课动画的端到端测试。页面地址带 ?fast，每帧只停 10ms。"""

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


def deg(demo, name: str):
    return demo.locator(f'[data-node="{name}"] .deg')


def test_dag_sorts_everything(page: Page):
    demo = open_demo(page, "14-topological-sort.html", "topo")
    click(demo, "排序（无环）")
    wait_done(demo)
    expect(demo.locator(".order .box")).to_have_text(["微积分", "编程入门", "数据结构", "数据库", "算法", "毕设"])
    expect(demo.locator(".queue .box")).to_have_count(0)
    expect(demo.locator(".edge.gone")).to_have_count(6)
    expect(demo.locator(".caption")).to_contain_text("6 门课全排完")


def test_indegree_drops_step_by_step(page: Page):
    demo = open_demo(page, "14-topological-sort.html", "topo")
    click(demo, "排序（无环）")
    wait_done(demo)
    for _ in range(13):  # 退回第 2 帧：入度为 0 的两门课刚入队
        click(demo, "← 上一步")
    expect(demo.locator(".step")).to_have_text("2 / 15")
    expect(demo.locator(".queue .box")).to_have_text(["微积分", "编程入门"])
    expect(deg(demo, "数据结构")).to_have_text("入度 2")
    click(demo, "下一步 →")  # 微积分出队
    click(demo, "下一步 →")  # 划掉 微积分 → 数据结构
    expect(deg(demo, "数据结构")).to_have_text("入度 1")
    expect(demo.locator('[data-node="数据结构"]')).to_have_class(re.compile("drop"))
    expect(demo.locator(".caption")).to_contain_text("还剩 1")


def test_cycle_gets_stuck(page: Page):
    demo = open_demo(page, "14-topological-sort.html", "topo")
    click(demo, "排序（有环）")
    wait_done(demo)
    expect(demo.locator(".order .box")).to_have_text(["微积分"])
    expect(deg(demo, "编程入门")).to_have_text("入度 1")
    expect(demo.locator(".caption")).to_contain_text("有环")
