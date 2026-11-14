"""第 23 课动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"
PAGE = "23-kmp.html"


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


def test_naive_vs_kmp_counts(page: Page):
    demo = open_demo(page, PAGE, "kmp")
    expect(demo.locator(".row.pi .box")).to_have_text(["0", "0", "1", "2", "0"])
    click(demo, "暴力匹配")
    wait_done(demo)
    expect(demo.locator(".hits")).to_have_text("2, 7")
    expect(demo.locator(".cmp")).to_have_text("22")

    click(demo, "KMP")
    wait_done(demo)
    expect(demo.locator(".hits")).to_have_text("2, 7")
    expect(demo.locator(".cmp")).to_have_text("13")


def test_kmp_jump_keeps_i(page: Page):
    demo = open_demo(page, PAGE, "kmp")
    click(demo, "KMP")
    wait_done(demo)
    for _ in range(18 - 7):  # 退回第 7 帧：第一次失配后查表跳过去
        click(demo, "← 上一步")
    expect(demo.locator(".step")).to_have_text("7 / 18")
    expect(demo.locator(".caption")).to_contain_text("j = 2。i 还是 4")
    expect(demo.locator(".row.pi .box.hot")).to_have_text("2")
    expect(demo.locator(".row.pat .box.ok")).to_have_text(["A", "B"])
    expect(demo.locator(".row.idx .box").nth(4)).to_have_text("i")


def test_empty_and_overlap(page: Page):
    demo = open_demo(page, PAGE, "kmp")
    demo.get_by_label("模式").fill("")
    click(demo, "KMP")
    expect(demo.locator(".caption")).to_contain_text("空模式")

    demo.get_by_label("文本").fill("aaaa")
    demo.get_by_label("模式").fill("aa")
    click(demo, "KMP")
    wait_done(demo)
    expect(demo.locator(".hits")).to_have_text("0, 1, 2")
