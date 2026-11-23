"""计算机基础第 7 课「SQL 执行顺序」动画的端到端测试。页面带 ?fast，每帧只停 10ms。

期望值不是手写的，也不取自 JS：测试现场用 Python 标准库 sqlite3，
在 examples/sql_in_practice.py 建好的同一组数据上真跑一遍同一条 SQL，拿它的结果和动画最终的 .result-table 比。
"""

import importlib.util
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

ROOT = Path(__file__).resolve().parents[2]
LESSONS = ROOT / "lessons" / "cs"

_spec = importlib.util.spec_from_file_location("sql_in_practice", ROOT / "examples" / "sql_in_practice.py")
sql_in_practice = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sql_in_practice)

MAIN = """SELECT u.city, SUM(o.quantity * p.price) AS total
FROM orders o
  JOIN users u    ON o.user_id = u.id
  JOIN products p ON o.product_id = p.id
WHERE o.created_at >= '2026-11-01'
GROUP BY u.city
HAVING SUM(o.quantity * p.price) > 200
ORDER BY total DESC
LIMIT 2"""
LEFT = "SELECT u.id, u.name FROM users u LEFT JOIN orders o ON o.user_id = u.id WHERE o.id IS NULL"
COUNT = "SELECT COUNT(*) AS all_rows, COUNT(city) AS has_city, COUNT(DISTINCT city) AS cities FROM users"
NOT_EQUAL = "SELECT name FROM users WHERE city <> '北京'"


def sqlite_cells(sql: str) -> list[str]:
    """在内存库里跑一遍，把结果按行展开成字符串列表，和 .result-table 的 td 一一对应。"""
    db = sql_in_practice.make_db()
    return [str(v) for row in db.execute(sql).fetchall() for v in row]


def open_demo(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "07-sql.html").as_uri() + "?fast")
    demo = page.locator("#query-order")
    expect(demo.locator(".caption")).to_contain_text("选一条查询")
    assert not errors, errors
    return demo


def wait_done(demo):
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def back(demo, times: int):
    for _ in range(times):
        demo.get_by_role("button", name="← 上一步").click()


@pytest.mark.parametrize(
    "button, sql",
    [
        ("主查询", MAIN),
        ("LEFT JOIN 找没下过单的用户", LEFT),
        ("COUNT(*) 与 COUNT(列)", COUNT),
        ("<> 遇到 NULL", NOT_EQUAL),
    ],
)
def test_final_result_matches_sqlite(page: Page, button, sql):
    expected = sqlite_cells(sql)
    assert expected, "参考查询不应为空"
    demo = open_demo(page)
    demo.get_by_role("button", name=button, exact=True).click()
    wait_done(demo)
    expect(demo.locator(".result-table td")).to_have_text(expected)


def test_main_query_sanity_values():
    """把 sqlite 的结果和正文里写的数字对一下，正文改了数据时这里会先报。"""
    assert sqlite_cells(MAIN) == ["上海", "1195", "北京", "496"]
    assert sqlite_cells(LEFT) == ["6", "周八"]
    assert sqlite_cells(COUNT) == ["6", "5", "4"]
    assert sqlite_cells(NOT_EQUAL) == ["李四", "赵六", "孙七"]


def test_where_frame_strikes_october_order(page: Page):
    """主查询共 10 帧（开头 1 帧 + 9 步）。从最后一帧退 5 步，回到 WHERE 那一帧。"""
    demo = open_demo(page)
    demo.get_by_role("button", name="主查询", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".step")).to_have_text("10 / 10")
    back(demo, 5)
    expect(demo.locator(".step")).to_have_text("5 / 10")
    expect(demo.locator(".caption")).to_contain_text("第 3 步 WHERE")
    expect(demo.locator(".sql-line.current")).to_have_count(1)
    expect(demo.locator(".sql-line.current")).to_contain_text("WHERE o.created_at")
    # FROM 和两行 JOIN 已经执行过；SELECT 写在第一行，但还没执行
    expect(demo.locator(".sql-line.done")).to_have_count(3)
    expect(demo.locator(".sql-line").first).not_to_have_class(re.compile(r"\bdone\b"))
    expect(demo.locator("tr.gone")).to_have_count(1)
    expect(demo.locator("tr.gone")).to_contain_text("2026-10-28")
    expect(demo.locator(".result-table")).to_have_count(0)


def test_group_by_frame_colors_four_groups(page: Page):
    """GROUP BY 那一帧：北京 3 行、上海 2 行、广州 1 行、深圳 1 行，各一种颜色。"""
    demo = open_demo(page)
    demo.get_by_role("button", name="主查询", exact=True).click()
    wait_done(demo)
    back(demo, 4)
    expect(demo.locator(".caption")).to_contain_text("第 4 步 GROUP BY")
    expect(demo.locator(".sql-line.current")).to_contain_text("GROUP BY u.city")
    for cls, count in [("g0", 3), ("g1", 2), ("g2", 1), ("g3", 1)]:
        expect(demo.locator(f"tr.{cls}")).to_have_count(count)
    expect(demo.locator("tr.g0").first).to_contain_text("北京")
    # 下一步 HAVING：广州那组变灰
    demo.get_by_role("button", name="下一步 →").click()
    expect(demo.locator("tr.gone")).to_have_count(1)
    expect(demo.locator("tr.gone")).to_contain_text("广州")


def test_left_join_pads_null_row(page: Page):
    """LEFT JOIN 那一帧有 9 行，周八那行右表列是 NULL。"""
    demo = open_demo(page)
    demo.get_by_role("button", name="LEFT JOIN 找没下过单的用户", exact=True).click()
    wait_done(demo)
    back(demo, 2)
    expect(demo.locator(".caption")).to_contain_text("LEFT JOIN")
    expect(demo.locator(".mid-table tr:has(td)")).to_have_count(9)
    expect(demo.locator("tr.new td.null")).to_have_count(2)
    expect(demo.locator("tr.new")).to_contain_text("周八")
