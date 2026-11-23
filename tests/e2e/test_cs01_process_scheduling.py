"""计算机基础第 1 课调度动画的端到端测试。页面带 ?fast，每帧只停 10ms。

期望值都是手算的（讲解页的表里也写着）：
FCFS 平均等待 4.75、SJF 4、SRTF 3、HRRN 4、RR(q=2) 5。
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons" / "cs"


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "01-process-scheduling.html").as_uri() + "?fast")
    demo = page.locator("#scheduler")
    expect(demo.locator(".caption")).to_contain_text("选一种调度算法")
    assert not errors, errors
    return demo


def wait_done(demo):
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def segments(demo):
    return demo.locator(".gantt .seg text")


@pytest.mark.parametrize(
    "button, order, turnaround, wait",
    [
        ("FCFS 先来先服务", ["P1", "P2", "P3", "P4"], "8.75", "4.75"),
        ("SJF 短作业优先", ["P1", "P3", "P2", "P4"], "8", "4"),
        ("SRTF 最短剩余时间优先", ["P1", "P2", "P3", "P2", "P4", "P1"], "7", "3"),
        ("HRRN 高响应比优先", ["P1", "P3", "P2", "P4"], "8", "4"),
        ("RR 时间片轮转", ["P1", "P2", "P1", "P3", "P2", "P4", "P1", "P4", "P1"], "9", "5"),
    ],
)
def test_each_policy_matches_hand_calculation(page: Page, button, order, turnaround, wait):
    demo = open_demo(page)
    demo.get_by_role("button", name=button).click()
    wait_done(demo)
    expect(segments(demo)).to_have_text(order)
    expect(demo.locator(".avg-turnaround")).to_have_text(turnaround)
    expect(demo.locator(".avg-wait")).to_have_text(wait)


def test_rr_requeues_new_arrival_before_preempted(page: Page):
    """t = 2：P2 先到达入队，P1 再因时间片用完回到队尾，所以调度器选 P2。"""
    demo = open_demo(page)
    demo.get_by_role("button", name="RR 时间片轮转").click()
    wait_done(demo)
    for _ in range(14):  # 从最后一帧（t=16）退到 t=2 那一帧
        demo.get_by_role("button", name="← 上一步").click()
    expect(demo.locator(".caption")).to_contain_text("t = 2")
    expect(demo.locator(".caption")).to_contain_text("调度器选 P2")
    expect(demo.locator(".running")).to_have_text("P2")
    expect(demo.locator(".queued")).to_have_text(["P1"])


def test_huge_quantum_degrades_to_fcfs(page: Page):
    demo = open_demo(page)
    demo.get_by_label("时间片").fill("10")
    demo.get_by_role("button", name="RR 时间片轮转").click()
    wait_done(demo)
    expect(segments(demo)).to_have_text(["P1", "P2", "P3", "P4"])
    expect(demo.locator(".avg-wait")).to_have_text("4.75")
