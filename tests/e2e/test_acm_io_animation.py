"""预备课「ACM 模式输入输出」动画的端到端测试：三种输入方式下，迭代器取 token 的位置、邻接表和输出都对。
运行：uv run pytest tests/e2e/test_acm_io_animation.py"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"
FIRST_OUTPUT = ["1 3 1 1", "1.50"]
BOTH_OUTPUTS = ["1 3 1 1", "1.50", "1 0 1", "0.67"]


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
    page.goto((LESSONS / "acm-io.html").as_uri() + "?fast")
    demo = page.locator("#acm-io")
    expect(demo).not_to_be_empty()
    assert not errors, errors
    return demo


def wait_done(demo):
    """等动画放到最后一帧：计数器显示成 “N / N”。"""
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def click(demo, name: str):
    demo.get_by_role("button", name=name, exact=True).click()


def test_single_case_consumes_every_token(page: Page):
    demo = open_demo(page)
    click(demo, "单组")
    wait_done(demo)
    expect(demo.locator(".box.token")).to_have_text(["4", "3", "1", "2", "2", "3", "2", "4"])
    expect(demo.locator(".box.token.used")).to_have_count(8)
    expect(demo.locator(".box.adj")).to_have_text(["1: [2]", "2: [1, 3, 4]", "3: [2]", "4: [2]"])
    expect(demo.locator(".box.out")).to_have_text(FIRST_OUTPUT)
    expect(demo.locator(".stat")).to_have_text("已经取走 8 / 8 个 token")


def test_single_case_step_back_shows_last_edge(page: Page):
    demo = open_demo(page)
    click(demo, "单组")
    wait_done(demo)
    click(demo, "← 上一步")
    expect(demo.locator(".box.token.hot")).to_have_text(["2", "4"])
    expect(demo.locator(".box.var.hot")).to_have_text(["u = 2", "v = 4"])
    expect(demo.locator(".box.adj.hot")).to_have_text(["2: [1, 3, 4]", "4: [2]"])
    expect(demo.locator(".box.out")).to_have_count(0)


def test_test_cases_reads_t_once(page: Page):
    demo = open_demo(page)
    click(demo, "先读 T 组")
    wait_done(demo)
    expect(demo.locator(".box.token")).to_have_count(13)  # T + 第一组 8 个 + 第二组 4 个
    expect(demo.locator(".box.token.used")).to_have_count(13)
    expect(demo.locator(".box.var")).to_have_text(["T = 2"])
    expect(demo.locator(".box.out")).to_have_text(BOTH_OUTPUTS)
    expect(demo.locator(".caption")).to_contain_text("range(T) 的 2 轮跑完")


def test_until_eof_stops_on_stop_iteration(page: Page):
    demo = open_demo(page)
    click(demo, "读到 EOF")
    wait_done(demo)
    expect(demo.locator(".box.token.used")).to_have_count(12)  # 第一组 8 个 + 第二组 4 个
    expect(demo.locator(".box.out")).to_have_text(BOTH_OUTPUTS)
    expect(demo.locator(".caption")).to_contain_text("StopIteration")


def test_until_eof_for_loop_picks_next_case_n(page: Page):
    demo = open_demo(page)
    click(demo, "读到 EOF")
    wait_done(demo)
    for _ in range(4):  # 退回到 for 取第二组 n 的那一帧
        click(demo, "← 上一步")
    expect(demo.locator(".box.token.hot")).to_have_text(["3"])
    expect(demo.locator(".box.token.used")).to_have_count(8)
    expect(demo.locator(".box.var")).to_have_text(["n = 3"])
    expect(demo.locator(".box.out")).to_have_text(FIRST_OUTPUT)
    expect(demo.locator(".caption")).to_contain_text("下一组的 n = 3")
