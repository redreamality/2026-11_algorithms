"""第 4 课哈希表动画的端到端测试。页面地址带 ?fast，每帧只停 10ms。"""

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


def put(demo, key: int):
    demo.get_by_label("key").fill(str(key))
    click(demo, "put(key)")
    wait_done(demo)


def bucket(demo, i: int):
    return demo.locator(".bucket").nth(i).locator(".pair")


def test_collision_chains_in_same_bucket(page: Page):
    demo = open_demo(page, "04-hash-table.html", "hmap")
    expect(demo.locator(".bucket")).to_have_count(4)
    put(demo, 9)  # 9 % 4 = 1，和 5 撞车
    expect(bucket(demo, 1)).to_have_text(["5: a", "9: c"])
    expect(demo.locator(".load")).to_have_text("0.75")
    click(demo, "← 上一步")
    expect(demo.locator(".caption")).to_contain_text("冲突")
    expect(bucket(demo, 1).last).to_have_class(re.compile("found"))


def test_resize_rehashes_every_key(page: Page):
    demo = open_demo(page, "04-hash-table.html", "hmap")
    put(demo, 9)
    put(demo, 6)  # 4 / 4 > 0.75，扩容到 8 个桶
    expect(demo.locator(".cap")).to_have_text("8")
    expect(demo.locator(".bucket")).to_have_count(8)
    expect(bucket(demo, 1)).to_have_text(["9: c"])
    expect(bucket(demo, 5)).to_have_text(["5: a"])
    expect(bucket(demo, 6)).to_have_text(["6: d"])
    click(demo, "← 上一步")  # 最后一次搬家：旧桶和新桶并排
    expect(demo.locator(".caption")).to_contain_text("rehash：")
    expect(demo.get_by_text("旧桶（4 个）")).to_be_visible()
    expect(demo.locator(".pair.moved")).to_have_count(3)  # 5、9、2 已搬走，正在搬 6
    expect(demo.locator(".size")).to_have_text("4")  # 搬家途中元素总数不变


def test_get_overwrite_and_missing(page: Page):
    demo = open_demo(page, "04-hash-table.html", "hmap")
    put(demo, 5)  # 已有 5：覆盖
    expect(demo.locator(".caption")).to_contain_text("覆盖")
    expect(demo.locator(".size")).to_have_text("2")
    click(demo, "get(key)")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("get(5) = c")
    demo.get_by_label("key").fill("13")
    click(demo, "remove(key)")
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("KeyError")


def test_empty_key_counts_as_zero(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    demo = open_demo(page, "04-hash-table.html", "hmap")
    demo.get_by_label("key").fill("")
    click(demo, "put(key)")
    wait_done(demo)
    expect(bucket(demo, 0)).to_have_text(["0: c"])
    assert not errors, errors
