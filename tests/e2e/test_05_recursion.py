"""第 5 课动画的端到端测试：调用栈的压入和弹出。运行：uv run pytest tests/e2e/test_05_recursion.py"""

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


def frames(demo):
    return demo.locator(".stack .frame .box")


def test_factorial_stack_empties(page: Page):
    demo = open_demo(page, "05-recursion.html", "callstack")
    demo.get_by_label("n").fill("4")
    click(demo, "factorial(n)")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("factorial(4) = 24")
    expect(frames(demo)).to_have_count(0)
    expect(demo.locator(".calls")).to_have_text("4")
    expect(demo.locator(".depth")).to_have_text("4")


def test_factorial_deepest_frame(page: Page):
    demo = open_demo(page, "05-recursion.html", "callstack")
    demo.get_by_label("n").fill("4")
    click(demo, "factorial(n)")
    wait_done(demo)
    for _ in range(8):  # 退回到 factorial(1) 碰到基线的那一帧：栈上 4 层，栈顶在最上面
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("基线条件")
    expect(frames(demo)).to_have_text(["factorial(1)", "factorial(2)", "factorial(3)", "factorial(4)"])
    expect(frames(demo).first).to_have_class(re.compile("found"))
    expect(demo.get_by_text("等 factorial(1) 的结果…")).to_be_visible()


def test_fib_repeats_work(page: Page):
    demo = open_demo(page, "05-recursion.html", "callstack")
    demo.get_by_label("n").fill("4")
    click(demo, "fib(n)")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("fib(4) = 3")
    expect(demo.locator(".calls")).to_have_text("9")
    expect(demo.locator(".depth")).to_have_text("4")
