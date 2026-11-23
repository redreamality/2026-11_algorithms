"""附录·选择题速查：出栈序列判定器的端到端测试。

运行：uv run pytest tests/e2e/test_choice_cheatsheet.py
"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    page.goto((LESSONS / "choice-cheatsheet.html").as_uri() + "?fast")
    demo = page.locator("#pop-check")
    expect(demo).not_to_be_empty()
    assert not errors, errors
    return demo


def wait_done(demo):
    """等动画放到最后一帧：计数器显示成 “N / N”。"""
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def click(demo, name: str):
    demo.get_by_role("button", name=name, exact=True).click()


def simulate(demo, sequence: str):
    demo.get_by_label("出栈序列").fill(sequence)
    click(demo, "模拟")
    wait_done(demo)


def test_valid_sequence(page: Page):
    demo = open_demo(page)
    simulate(demo, "4 5 3 2 1")
    expect(demo.locator(".verdict")).to_have_text("合法")
    expect(demo.locator(".box.done")).to_have_text(["4", "5", "3", "2", "1"])
    expect(demo.locator(".stack-col .box")).to_have_count(0)
    # 5 进栈 + 5 出栈 + 开头和结尾各一帧
    expect(demo.locator(".step")).to_have_text("12 / 12")


def test_invalid_sequence_stops_where_blocked(page: Page):
    demo = open_demo(page)
    simulate(demo, "4 3 5 1 2")
    expect(demo.locator(".verdict")).to_have_text("不合法")
    expect(demo.locator(".caption")).to_contain_text("要弹 1")
    expect(demo.locator(".caption")).to_contain_text("栈顶是 2")
    expect(demo.locator(".box.done")).to_have_text(["4", "3", "5"])
    expect(demo.locator(".stack-col .box")).to_have_text(["1", "2"])  # 底 → 顶
    expect(demo.locator(".stack-col .box.blocked")).to_have_text("2")


def test_example_buttons(page: Page):
    demo = open_demo(page)
    click(demo, "不合法的例子")
    wait_done(demo)
    expect(demo.get_by_label("出栈序列")).to_have_value("4 3 5 1 2")
    expect(demo.locator(".verdict")).to_have_text("不合法")
    click(demo, "合法的例子")
    wait_done(demo)
    expect(demo.locator(".verdict")).to_have_text("合法")


def test_every_permutation_of_three(page: Page):
    """1 2 3 的 6 个排列里，只有 3 1 2 不合法（卡特兰数 C(3) = 5）。"""
    demo = open_demo(page)
    verdicts = {}
    for sequence in ["1 2 3", "1 3 2", "2 1 3", "2 3 1", "3 1 2", "3 2 1"]:
        simulate(demo, sequence)
        verdicts[sequence] = demo.locator(".verdict").inner_text()
    assert [sequence for sequence, verdict in verdicts.items() if verdict == "不合法"] == ["3 1 2"]


def test_bad_input_message(page: Page):
    demo = open_demo(page)
    demo.get_by_label("出栈序列").fill("1 2 2")
    click(demo, "模拟")
    expect(demo.locator(".verdict")).to_have_text("输入有误")
    expect(demo.locator(".caption")).to_contain_text("不是 1～n 的一个排列")
