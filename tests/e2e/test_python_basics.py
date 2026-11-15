"""预备课动画的端到端测试。页面带 ?fast，每帧只停 10ms。"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"
PAGE = "python-basics.html"


def open_demo(page: Page, demo_id: str):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / PAGE).as_uri() + "?fast")
    demo = page.locator(f"#{demo_id}")
    expect(demo).not_to_be_empty()
    assert not errors, errors
    return demo


def wait_done(demo):
    """等动画放到最后一帧：计数器显示成 “N / N”。"""
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def click(demo, name: str):
    demo.get_by_role("button", name=name, exact=True).click()


def test_generator_pauses_at_yield_and_keeps_local(page: Page):
    demo = open_demo(page, "generator-demo")
    expect(demo.locator(".status")).to_have_text("未开始")
    expect(demo.locator(".got .box")).to_have_count(0)

    click(demo, "next(numbers)")
    wait_done(demo)
    expect(demo.locator(".status")).to_have_text("暂停")
    expect(demo.locator(".got .box")).to_have_text(["3"])
    expect(demo.locator(".listing .line.idle")).to_have_text("        yield n")
    expect(demo.locator(".local-n")).to_have_text("3")

    click(demo, "next(numbers)")
    wait_done(demo)
    expect(demo.locator(".local-n")).to_have_text("2")
    expect(demo.locator(".got .box")).to_have_text(["3", "2"])
    click(demo, "← 上一步")  # 退回去能看到从暂停处恢复执行
    click(demo, "← 上一步")
    click(demo, "← 上一步")
    expect(demo.locator(".listing .line.hot")).to_have_text("    while n > 0:")


def test_generator_ends_with_stop_iteration(page: Page):
    demo = open_demo(page, "generator-demo")
    for _ in range(4):
        click(demo, "next(numbers)")
        wait_done(demo)
    expect(demo.locator(".got .box")).to_have_text(["3", "2", "1"])
    expect(demo.locator(".status")).to_have_text("已结束")
    expect(demo.locator(".caption")).to_contain_text("StopIteration")

    click(demo, "重新开始")
    expect(demo.locator(".status")).to_have_text("未开始")
    expect(demo.locator(".got .box")).to_have_count(0)


def test_yield_from_passes_inner_values_through(page: Page):
    demo = open_demo(page, "yield-from-demo")
    click(demo, "next(gen)")
    wait_done(demo)
    expect(demo.locator(".inner-name")).to_have_text("count_down(2)")
    expect(demo.locator(".got .box")).to_have_text(["2"])

    click(demo, "next(gen)")
    wait_done(demo)
    click(demo, "next(gen)")  # 里层用完，换到下一个里层
    wait_done(demo)
    expect(demo.locator(".inner-name")).to_have_text('iter("ab")')
    expect(demo.locator(".got .box")).to_have_text(["2", "1", "a"])
    for _ in range(3):
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("yield from 接住它")


def test_yield_from_finishes_after_own_yield(page: Page):
    demo = open_demo(page, "yield-from-demo")
    for _ in range(5):
        click(demo, "next(gen)")
        wait_done(demo)
    expect(demo.locator(".got .box")).to_have_text(["2", "1", "a", "b", "done"])
    expect(demo.locator(".status")).to_have_text("暂停")
    click(demo, "next(gen)")
    wait_done(demo)
    expect(demo.locator(".status")).to_have_text("已结束")
    expect(demo.locator(".caption")).to_contain_text("StopIteration")
