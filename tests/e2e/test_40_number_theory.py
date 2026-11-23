"""第 40 课动画的端到端测试：辗转相除、埃氏筛、快速幂。
运行：uv run pytest tests/e2e/test_40_number_theory.py"""

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


def test_gcd_steps(page: Page):
    demo = open_demo(page, "40-number-theory.html", "number-theory")
    click(demo, "辗转相除")
    wait_done(demo)
    expect(demo.locator(".stat")).to_have_text("gcd(190, 28) = 2")
    # 5 次取模 + 最后一行“停”
    expect(demo.locator(".nt-table tr:not(:first-child)")).to_have_count(6)
    expect(demo.locator(".nt-table tr.done td").first).to_have_text("2")
    click(demo, "← 上一步")
    expect(demo.locator(".nt-table tr.hot td")).to_have_text(["4", "2", "0"])


def test_sieve_finds_lucky_cards(page: Page):
    demo = open_demo(page, "40-number-theory.html", "number-theory")
    click(demo, "埃氏筛")
    wait_done(demo)
    expect(demo.locator(".card.prime")).to_have_text(["2", "3", "5", "7", "11", "13", "17", "19"])
    expect(demo.locator(".card.crossed")).to_have_count(12)
    expect(demo.locator(".stat")).to_have_text("幸运卡 8 张")
    # 倒回去找“从 9 开始划 3 的倍数”那一帧：9 是红色，当前质数是 3
    while "划掉 9 = 3 × 3" not in demo.locator(".caption").inner_text():
        click(demo, "← 上一步")
    expect(demo.locator(".card.gone")).to_have_text(["9"])
    expect(demo.locator(".card.current")).to_have_text(["3"])
    # 12 此时已经被 2 划掉（灰色），不是本步划掉的
    expect(demo.locator(".card.crossed", has_text=re.compile(r"^12$"))).to_have_count(1)


def test_fast_power_mod(page: Page):
    demo = open_demo(page, "40-number-theory.html", "number-theory")
    click(demo, "快速幂")
    wait_done(demo)
    expect(demo.locator(".stat")).to_have_text("7^9 mod 11 = 8")
    expect(demo.locator(".caption")).to_contain_text("7 × 8 = 56 ≡ 1")
    # 指数 1001 → 100 → 10 → 1 四行，再加结论行
    rows = demo.locator(".nt-table tr:not(:first-child)")
    expect(rows).to_have_count(5)
    expect(rows.locator("td:first-child")).to_have_text(["1001", "100", "10", "1", "0"])
    expect(rows.locator("td:nth-child(4)")).to_have_text(["7", "7", "7", "8", "8"])
