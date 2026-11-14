"""第 19 课动画的端到端测试：朴素递归的重复调用、记忆化剪枝、填表。运行：uv run pytest tests/e2e/test_19_dp_memo.py"""

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


def test_naive_repeats(page: Page):
    demo = open_demo(page, "19-dp-memo.html", "dpmemo")
    demo.get_by_label("n").fill("5")
    click(demo, "朴素递归")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("fib(5) = 5")
    expect(demo.locator(".calls")).to_have_text("15")
    expect(demo.locator(".tree .box.found")).to_have_count(9)


def test_memo_prunes_subtrees(page: Page):
    demo = open_demo(page, "19-dp-memo.html", "dpmemo")
    demo.get_by_label("n").fill("5")
    click(demo, "记忆化")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("只调用了 9 次")
    expect(demo.locator(".calls")).to_have_text("9")
    expect(demo.locator(".tree .box.hit")).to_have_text(["2", "3"])
    expect(demo.locator(".tree .box.cut")).to_have_count(6)
    expect(demo.locator(".row.memo .box")).to_have_text(["1", "2", "3", "5"])


def test_table_fills_left_to_right(page: Page):
    demo = open_demo(page, "19-dp-memo.html", "dpmemo")
    demo.get_by_label("n").fill("5")
    click(demo, "填表")
    wait_done(demo)
    expect(demo.locator(".row.dp .box")).to_have_text(["0", "1", "1", "2", "3", "5"])
    for _ in range(2):  # 退回到填 dp[4] 的那一帧
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("dp[4] = dp[3] + dp[2]")
    expect(demo.locator(".row.dp .box.hot")).to_have_text(["1", "2"])
    expect(demo.locator(".row.dp .box.found")).to_have_text(["3"])
    expect(demo.locator(".row.dp .box.empty")).to_have_count(1)
