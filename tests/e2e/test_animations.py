"""讲解页动画的端到端测试：真的打开浏览器、点按钮，检查画面停在了对的状态。

页面地址带 ?fast，每帧只停 10ms。首次运行前要装浏览器：uv run playwright install chromium
"""

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


# ---------- 第 0 课 ----------

def test_growth_slider(page: Page):
    demo = open_demo(page, "00-complexity.html", "growth")
    demo.get_by_label("n").fill("100")
    expect(demo.locator(".n")).to_have_text("100")
    expect(demo.locator('[data-name="O(n²)"]')).to_have_text("10,000")
    expect(demo.locator('[data-name="O(log n)"]')).to_have_text("7")


def test_duplicate_slow_vs_fast(page: Page):
    demo = open_demo(page, "00-complexity.html", "dup")
    click(demo, "两两比较 O(n²)")
    wait_done(demo)
    expect(demo.locator(".ops")).to_have_text("22")
    expect(demo.locator(".box.found")).to_have_count(2)

    click(demo, "用 set O(n)")
    wait_done(demo)
    expect(demo.locator(".ops")).to_have_text("8")
    expect(demo.locator(".caption")).to_contain_text("找到重复")


# ---------- 第 1 课 ----------

def data_row(demo):
    return demo.locator(".row.data .box")


def test_append_doubles_capacity(page: Page):
    demo = open_demo(page, "01-dynamic-array.html", "darray")
    click(demo, "连续 append 8 次")
    wait_done(demo)
    expect(demo.locator(".cap")).to_have_text("8")
    click(demo, "append")
    wait_done(demo)
    expect(demo.locator(".size")).to_have_text("9")
    expect(demo.locator(".cap")).to_have_text("16")
    expect(data_row(demo)).to_have_count(16)
    expect(demo.locator(".stat")).to_contain_text("搬家共搬了 15 次")


def test_resize_shows_old_and_new_rows(page: Page):
    demo = open_demo(page, "01-dynamic-array.html", "darray")
    click(demo, "append")
    wait_done(demo)
    click(demo, "append")  # 容量 1 已满，这次要搬家
    wait_done(demo)
    click(demo, "← 上一步")
    click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("搬第 0 个")
    expect(demo.get_by_text("旧格子：")).to_be_visible()


def test_insert_and_remove_at(page: Page):
    demo = open_demo(page, "01-dynamic-array.html", "darray")
    click(demo, "连续 append 8 次")  # 1..8
    wait_done(demo)
    demo.get_by_label("下标 i").fill("0")
    click(demo, "insert(i)")  # 在最前面插入 9
    wait_done(demo)
    expect(data_row(demo).first).to_have_text("9")
    expect(demo.locator(".caption")).to_contain_text("挪了 8 次")

    demo.get_by_label("下标 i").fill("1")
    click(demo, "remove_at(i)")  # 删掉 1
    wait_done(demo)
    expect(data_row(demo).nth(1)).to_have_text("2")
    expect(demo.locator(".size")).to_have_text("8")


def test_errors_are_explained(page: Page):
    demo = open_demo(page, "01-dynamic-array.html", "darray")
    click(demo, "pop")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("IndexError")


def test_player_controls(page: Page):
    demo = open_demo(page, "01-dynamic-array.html", "darray")
    click(demo, "连续 append 8 次")
    wait_done(demo)
    total = int(demo.locator(".step").inner_text().split(" / ")[1])
    click(demo, "← 上一步")
    expect(demo.locator(".step")).to_have_text(f"{total - 1} / {total}")
    click(demo, "下一步 →")
    expect(demo.locator(".step")).to_have_text(f"{total} / {total}")
    expect(demo.get_by_role("button", name="下一步 →")).to_be_disabled()
    click(demo, "▶ 播放")  # 在最后一帧点播放 → 从头重放
    wait_done(demo)


# ---------- 第 2 课 ----------

def values(demo):
    return demo.locator(".row.list .node:not(.fade) .box")


def test_initial_list(page: Page):
    demo = open_demo(page, "02-linked-list.html", "llist")
    expect(values(demo)).to_have_text(["1", "2", "3", "4"])
    expect(demo.locator(".node").first.locator(".tag").first).to_have_text("head")
    expect(demo.locator(".node").last.locator(".tag").first).to_have_text("tail")


def test_reverse(page: Page):
    demo = open_demo(page, "02-linked-list.html", "llist")
    click(demo, "reverse")
    wait_done(demo)
    expect(values(demo)).to_have_text(["4", "3", "2", "1"])
    expect(demo.locator(".link")).to_have_text(["→", "→", "→"])
    expect(demo.locator(".node").first.locator(".tag").first).to_have_text("head")


def test_reverse_midway_arrows_turn(page: Page):
    demo = open_demo(page, "02-linked-list.html", "llist")
    click(demo, "reverse")
    wait_done(demo)
    for _ in range(3):  # 退回到最后一个节点刚掉完头的那一帧，此时还按原顺序摆放
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("掉头")
    expect(demo.locator(".link")).to_have_text(["←", "←", "←"])
    expect(demo.get_by_text("nxt = None")).to_be_visible()


def test_reverse_shows_gap_where_link_is_cut(page: Page):
    demo = open_demo(page, "02-linked-list.html", "llist")
    click(demo, "reverse")
    wait_done(demo)
    for _ in range(9):  # 退到第二个节点刚掉完头：1 ← 2　3 → 4，2 和 3 之间断开
        click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("掉头")
    expect(demo.locator(".link")).to_have_text(["←", "", "→"])


def test_remove_middle_shows_skip(page: Page):
    demo = open_demo(page, "02-linked-list.html", "llist")
    demo.get_by_label("要删的值").fill("2")
    click(demo, "remove(值)")
    wait_done(demo)
    click(demo, "← 上一步")  # 跳过它的那一帧
    expect(demo.locator(".caption")).to_contain_text("跳过它")
    expect(demo.locator(".link").first).to_have_text("⤼")


def test_remove_tail_moves_tail_back(page: Page):
    demo = open_demo(page, "02-linked-list.html", "llist")
    demo.get_by_label("要删的值").fill("4")
    click(demo, "remove(值)")
    wait_done(demo)
    expect(values(demo)).to_have_text(["1", "2", "3"])
    expect(demo.locator(".node").last.locator(".tag").first).to_have_text("tail")
    click(demo, "push_back")
    wait_done(demo)
    expect(values(demo)).to_have_text(["1", "2", "3", "5"])


def test_remove_missing(page: Page):
    demo = open_demo(page, "02-linked-list.html", "llist")
    demo.get_by_label("要删的值").fill("9")
    click(demo, "remove(值)")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("没找到")


def test_pop_until_empty_then_push_front(page: Page):
    demo = open_demo(page, "02-linked-list.html", "llist")
    for _ in range(4):
        click(demo, "pop_front")
        wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("链表空了")
    expect(demo.locator(".size")).to_have_text("0")
    click(demo, "push_front")
    wait_done(demo)
    expect(values(demo)).to_have_text(["5"])
    expect(demo.locator(".node .tag").first).to_have_text("head / tail")
