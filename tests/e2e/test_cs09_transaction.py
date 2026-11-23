"""计算机基础第 9 课隔离级别动画的端到端测试。页面带 ?fast，每帧只停 10ms。

期望值由仓库外的参考实现（按 InnoDB 规则推演）独立算出：
脏读：读未提交 A 三次读到 10、9、10；其余级别都是 10。
不可重复读：读未提交 / 读已提交 99 → 109；可重复读 / 串行化 99 → 99。
幻读：读未提交 / 读已提交第二次查到 42、43；可重复读 / 串行化只有 42。
丢失修改：前三个级别最后 stock = 9（丢了一次）；串行化下死锁，回滚 B。
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons" / "cs"


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "09-transaction.html").as_uri() + "?fast")
    demo = page.locator("#isolation")
    expect(demo.locator(".caption")).to_contain_text("先选一个隔离级别")
    assert not errors, errors
    return demo


def wait_done(demo):
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def run(demo, level, scenario):
    demo.get_by_role("button", name=level, exact=True).click()
    demo.get_by_role("button", name=scenario, exact=True).click()
    wait_done(demo)
    expect(demo.locator(".level")).to_have_text(level)


def back(demo, steps):
    for _ in range(steps):
        demo.get_by_role("button", name="← 上一步", exact=True).click()


def test_read_uncommitted_has_dirty_read(page: Page):
    demo = open_demo(page)
    run(demo, "读未提交", "脏读")
    expect(demo.locator(".verdict")).to_contain_text("出现了脏读")
    expect(demo.locator(".read-value")).to_have_text("10")  # B 回滚后 A 又读回 10
    back(demo, 3)  # 退到 A 第二次 SELECT 那一帧
    expect(demo.locator(".caption")).to_contain_text("脏读！")
    expect(demo.locator(".read-value")).to_have_text("9")
    expect(demo.locator(".ver.uncommitted.seen")).to_have_count(1)


def test_read_committed_no_dirty_read_but_non_repeatable(page: Page):
    demo = open_demo(page)
    run(demo, "读已提交", "脏读")
    expect(demo.locator(".verdict")).to_contain_text("没有脏读")
    run(demo, "读已提交", "不可重复读")
    expect(demo.locator(".verdict")).to_contain_text("出现了不可重复读")
    expect(demo.locator(".read-value")).to_have_text("109")


def test_repeatable_read_has_no_non_repeatable_read(page: Page):
    demo = open_demo(page)
    run(demo, "可重复读", "不可重复读")
    expect(demo.locator(".verdict")).to_contain_text("没有不可重复读")
    expect(demo.locator(".read-value")).to_have_text("99")
    back(demo, 1)  # A 第二次读：跳过 B 在读视图之后提交的版本
    expect(demo.locator(".caption")).to_contain_text("读视图之后才提交")


@pytest.mark.parametrize("level, verdict, ids", [
    ("读已提交", "出现了幻读", "42、43"),
    ("可重复读", "没有幻读", "42"),
])
def test_phantom(page: Page, level, verdict, ids):
    demo = open_demo(page)
    run(demo, level, "幻读")
    expect(demo.locator(".verdict")).to_contain_text(verdict)
    expect(demo.locator(".read-value")).to_have_text(ids)


def test_serializable_blocks_b(page: Page):
    demo = open_demo(page)
    run(demo, "串行化", "脏读")
    expect(demo.locator(".verdict")).to_contain_text("没有脏读")
    expect(demo.locator(".col-b .slot.wait")).to_have_count(1)
    back(demo, 5)  # 退到 B 的 UPDATE 被 A 的 S 锁挡住那一帧
    expect(demo.locator(".caption")).to_contain_text("只能等待锁")
    expect(demo.locator(".col-b .slot.wait")).to_contain_text("等待锁")
    expect(demo.locator(".locks")).to_contain_text("A：S 锁（行 42）")


def test_lost_update(page: Page):
    demo = open_demo(page)
    run(demo, "可重复读", "丢失修改")
    expect(demo.locator(".verdict")).to_contain_text("出现了丢失修改")
    expect(demo.locator(".committed").first).to_have_text("stock 9 · price 99")
    run(demo, "串行化", "丢失修改")
    expect(demo.locator(".verdict")).to_contain_text("死锁")
    expect(demo.locator(".col-b .slot.bad").first).to_contain_text("死锁")
