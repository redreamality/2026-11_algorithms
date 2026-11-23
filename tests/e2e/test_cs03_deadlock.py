"""计算机基础第 3 课两个动画的端到端测试。页面带 ?fast，每帧只停 10ms。

期望值由仓库外的独立参考实现算出（扫描规则：每轮从 P0 开始，选第一个 Need <= Work 的）：
- 初始状态安全，序列 P1 P3 P0 P2 P4
- P1 请求 (1,0,2)：批准，序列同上
- P1 获批后 P4 请求 (3,3,0)：A 类 3 > 2，资源不足，等待
- P1 获批后 P0 请求 (0,2,0)：试分配后 Available = (2,1,0)，不安全，拒绝
- 竞态：不加锁交替执行卖出 2 件；加锁卖出 1 件，stock 都是 0
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons" / "cs"
SEQ = "P1 → P3 → P0 → P2 → P4"


def open_page(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "03-deadlock.html").as_uri() + "?fast")
    expect(page.locator("#banker .caption")).to_contain_text("点上面的按钮开始")
    expect(page.locator("#race .caption")).to_contain_text("库存只剩 1 件")
    assert not errors, errors
    return page


def wait_done(demo):
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def test_safety_check_finds_sequence(page: Page):
    demo = open_page(page).locator("#banker")
    demo.get_by_role("button", name="安全性检查").click()
    wait_done(demo)
    expect(demo.locator(".safe-sequence")).to_have_text(SEQ)
    expect(demo.locator(".verdict")).to_have_text("安全")
    expect(demo.locator(".work")).to_have_text("(10,5,7)")
    expect(demo.locator(".need")).to_have_text(["(7,4,3)", "(1,2,2)", "(6,0,0)", "(0,1,1)", "(4,3,1)"])


def test_safety_check_middle_frame(page: Page):
    """第 2 轮扫描到 P2：Need (6,0,0) 不满足 Work (5,3,2)，P1 已完成。"""
    demo = open_page(page).locator("#banker")
    demo.get_by_role("button", name="安全性检查").click()
    wait_done(demo)
    expect(demo.locator(".step")).to_have_text("17 / 17")
    for _ in range(9):
        demo.get_by_role("button", name="← 上一步").click()
    expect(demo.locator(".caption")).to_contain_text("第 2 轮：P2")
    expect(demo.locator(".caption")).to_contain_text("A 类 6 > 5")
    expect(demo.locator("tr.checking")).to_have_class(re.compile(r"row-P2"))
    expect(demo.locator("tr.done")).to_have_count(1)
    expect(demo.locator("tr.done")).to_have_class(re.compile(r"row-P1"))
    expect(demo.locator(".work")).to_have_text("(5,3,2)")


@pytest.mark.parametrize(
    "button, verdict, sequence, available",
    [
        ("P1 请求 (1,0,2)", "批准", SEQ, "(2,3,0)"),
        ("P4 请求 (3,3,0)", "资源不足，等待", None, "(2,3,0)"),
        ("P0 请求 (0,2,0)", "不安全，拒绝", "找不到", "(2,3,0)"),
    ],
)
def test_requests(page: Page, button, verdict, sequence, available):
    demo = open_page(page).locator("#banker")
    demo.get_by_role("button", name=button).click()
    wait_done(demo)
    expect(demo.locator(".verdict")).to_have_text(verdict)
    if sequence is None:
        expect(demo.locator(".safe-sequence")).to_have_count(0)
    else:
        expect(demo.locator(".safe-sequence")).to_have_text(sequence)
    # 批准后 Available 是试分配后的值；拒绝 / 等待时保持 P1 获批后的值
    expect(demo.locator(".available")).to_have_text(available)


def test_p0_request_trial_state(page: Page):
    """P0 请求的试分配帧：Available 变成 (2,1,0)。"""
    demo = open_page(page).locator("#banker")
    demo.get_by_role("button", name="P0 请求 (0,2,0)").click()
    wait_done(demo)
    for _ in range(6):  # 最后一帧往前：P4、P3、P2、P1、P0 五次检查，再到「开始」帧
        demo.get_by_role("button", name="← 上一步").click()
    expect(demo.locator(".caption")).to_contain_text("安全性检查开始")
    expect(demo.locator(".available")).to_have_text("(2,1,0)")
    expect(demo.locator(".row-P0 .need")).to_have_text("(7,2,3)")


def test_reset(page: Page):
    demo = open_page(page).locator("#banker")
    demo.get_by_role("button", name="P0 请求 (0,2,0)").click()
    wait_done(demo)
    demo.get_by_role("button", name="重置", exact=True).click()
    expect(demo.locator(".available")).to_have_text("(3,3,2)")
    expect(demo.locator(".verdict")).to_have_count(0)


@pytest.mark.parametrize("button, sold, verdict", [("不加锁", "2", "超卖"), ("加锁", "1", "正确")])
def test_race(page: Page, button, sold, verdict):
    demo = open_page(page).locator("#race")
    demo.get_by_role("button", name=button, exact=True).click()
    wait_done(demo)
    expect(demo.locator(".stock-value")).to_have_text("0")
    expect(demo.locator(".order-count")).to_have_text(sold)
    expect(demo.locator(".race-verdict")).to_have_text(verdict)


def test_race_locked_blocks_t2(page: Page):
    """加锁时第 3 步 T2 去拿锁，锁在 T1 手里，T2 阻塞。"""
    demo = open_page(page).locator("#race")
    demo.get_by_role("button", name="加锁", exact=True).click()
    wait_done(demo)
    for _ in range(6):  # 共 10 帧，退到第 4 帧（T2 拿锁失败）
        demo.get_by_role("button", name="← 上一步").click()
    expect(demo.locator(".caption")).to_contain_text("T2 阻塞")
    expect(demo.locator(".stock-value")).to_have_text("1")
