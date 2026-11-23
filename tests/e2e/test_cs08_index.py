"""计算机基础第 8 课两个动画的端到端测试。页面带 ?fast，每帧只停 10ms。

期望值由仓库外的参考实现（cs-verify-08/ref.py）独立算出：
- B+ 树（id 1～27，叶子每页 3 行，三层）：点查任何 id 都读 3 页；全表扫描读 9 页；
  范围 8～20 读 7 页、13 行；范围 1～27 读 11 页、27 行；范围 13～15 读 3 页。
- 联合索引 (user_id, status, created_at) 上 12 个条目：见下面参数表。
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons" / "cs"


def open_demo(page: Page, demo_id: str):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "08-index.html").as_uri() + "?fast")
    demo = page.locator("#" + demo_id)
    expect(demo.locator(".caption")).not_to_be_empty()
    assert not errors, errors
    return demo


def wait_done(demo):
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


@pytest.mark.parametrize("target", ["14", "1", "27", "30"])
def test_index_lookup_reads_three_pages(page: Page, target):
    demo = open_demo(page, "btree")
    demo.get_by_label("要找的 id").fill(target)
    demo.get_by_role("button", name="用索引查找").click()
    wait_done(demo)
    expect(demo.locator(".page-reads")).to_have_text("3")
    expect(demo.locator(".found-count")).to_have_text("0" if target == "30" else "1")


def test_full_scan_reads_every_page(page: Page):
    demo = open_demo(page, "btree")
    demo.get_by_label("要找的 id").fill("14")
    demo.get_by_role("button", name="全表扫描").click()
    wait_done(demo)
    expect(demo.locator(".page-reads")).to_have_text("9")
    expect(demo.locator(".found-rows")).to_have_text("14")


@pytest.mark.parametrize(
    "a, b, reads, count, rows",
    [
        ("8", "20", "7", "13", "8, 9, …, 20"),
        ("1", "27", "11", "27", "1, 2, …, 27"),
        ("13", "15", "3", "3", "13, 14, 15"),
        ("25", "40", "3", "3", "25, 26, 27"),
    ],
)
def test_range_query_follows_leaf_links(page: Page, a, b, reads, count, rows):
    demo = open_demo(page, "btree")
    demo.get_by_label("起点").fill(a)
    demo.get_by_label("终点").fill(b)
    demo.get_by_role("button", name="范围查询 id 在 a 到 b 之间").click()
    wait_done(demo)
    expect(demo.locator(".page-reads")).to_have_text(reads)
    expect(demo.locator(".found-count")).to_have_text(count)
    expect(demo.locator(".found-rows")).to_have_text(rows)


def test_lookup_step_back_shows_second_level(page: Page):
    """id = 14：倒退两步回到第 3 帧，正在读第 2 层（键 13、16），读页数 2，只有一个节点是橙色。"""
    demo = open_demo(page, "btree")
    demo.get_by_label("要找的 id").fill("14")
    demo.get_by_role("button", name="用索引查找").click()
    wait_done(demo)
    for _ in range(2):
        demo.get_by_role("button", name="← 上一步").click()
    expect(demo.locator(".caption")).to_contain_text("读第 2 页")
    expect(demo.locator(".caption")).to_contain_text("13、16")
    expect(demo.locator(".page-reads")).to_have_text("2")
    expect(demo.locator("svg.bptree rect.hot")).to_have_count(1)


@pytest.mark.parametrize(
    "where, used, scanned, matched",
    [
        ("user_id = 7", "用上 1 列：user_id", "5", "5"),
        ("user_id = 7 AND status = 'paid'", "用上 2 列：user_id → status", "3", "3"),
        ("status = 'paid' AND user_id = 7", "用上 2 列：user_id → status", "3", "3"),
        ("user_id = 7 AND status = 'paid' AND created_at > '2026-11-01'",
         "用上 3 列：user_id → status → created_at", "2", "2"),
        ("status = 'paid'", "用上 0 列：这个索引用不上", "12", "7"),
        ("user_id = 7 AND created_at > '2026-11-01'", "用上 1 列：user_id", "5", "4"),
        ("user_id > 5 AND status = 'paid'", "用上 1 列：user_id", "10", "6"),
        ("user_id + 1 = 8", "用上 0 列：这个索引用不上", "12", "5"),
        ("user_id = 7 AND status = 'paid' AND MONTH(created_at) = 11", "用上 2 列：user_id → status", "3", "2"),
    ],
)
def test_leftmost_prefix_conclusion(page: Page, where, used, scanned, matched):
    demo = open_demo(page, "leftmost")
    demo.get_by_role("button", name=where, exact=True).click()
    wait_done(demo)
    expect(demo.locator(".used-columns")).to_have_text(used)
    expect(demo.locator(".scan-count")).to_have_text(scanned)
    expect(demo.locator(".match-count")).to_have_text(matched)


def test_leftmost_step_back_shows_where_it_stops(page: Page):
    """跳过 status：倒退两步到检查 status 的那一帧，status 标红，created_at 还没检查。"""
    demo = open_demo(page, "leftmost")
    demo.get_by_role("button", name="user_id = 7 AND created_at > '2026-11-01'", exact=True).click()
    wait_done(demo)
    for _ in range(2):
        demo.get_by_role("button", name="← 上一步").click()
    expect(demo.locator(".caption")).to_contain_text("条件里没有 status")
    expect(demo.locator(".col-chip.used")).to_have_attribute("data-col", "user_id")
    expect(demo.locator(".col-chip.stop")).to_have_attribute("data-col", "status")
    expect(demo.locator(".col-chip.pending")).to_have_attribute("data-col", "created_at")
    expect(demo.locator(".idx-entries tr.scan")).to_have_count(5)
