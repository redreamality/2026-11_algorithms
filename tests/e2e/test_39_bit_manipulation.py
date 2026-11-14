"""第 39 课动画的端到端测试：异或抵消、n & (n - 1)、位掩码枚举子集。
运行：uv run pytest tests/e2e/test_39_bit_manipulation.py"""

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


def test_xor_cancels_pairs(page: Page):
    demo = open_demo(page, "39-bit-manipulation.html", "bits")
    click(demo, "异或抵消")
    wait_done(demo)
    expect(demo.locator(".num.result")).to_have_text("异或结果 = 4")
    expect(demo.locator(".stat")).to_have_text("答案 = 4")
    # 1 和 2 各两行变淡，每行 3 位
    expect(demo.locator(".bits .box.fade")).to_have_count(12)
    # 第 2 帧：刚异或进 4，结果行第 2 位被翻成 1
    for _ in range(int(demo.locator(".step").inner_text().split(" / ")[1]) - 2):
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("000 ^ 100 = 100")


def test_drop_lowest_bit_counts_ones(page: Page):
    demo = open_demo(page, "39-bit-manipulation.html", "bits")
    click(demo, "去掉最低位的 1")
    wait_done(demo)
    expect(demo.locator(".stat")).to_have_text("答案 = 3")
    expect(demo.locator(".caption")).to_contain_text("44 的二进制里有 3 个 1")
    click(demo, "← 上一步")
    # 最后一次：32 = 100000，去掉第 5 位
    expect(demo.locator(".bits .box.gone")).to_have_count(1)
    expect(demo.locator(".num.result")).to_have_text("相与 = 0")


def test_mask_subsets(page: Page):
    demo = open_demo(page, "39-bit-manipulation.html", "bits")
    click(demo, "位掩码枚举子集")
    wait_done(demo)
    expect(demo.locator(".subset")).to_have_text(
        ["[]", "[1]", "[2]", "[1, 2]", "[3]", "[1, 3]", "[2, 3]", "[1, 2, 3]"])
    expect(demo.locator(".stat")).to_have_text("共 8 个子集")
