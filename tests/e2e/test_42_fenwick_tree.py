"""第 42 课动画的端到端测试：prefix_sum(7) 沿 7 → 6 → 4 往下跳、add(4, 3) 沿 5 → 6 → 8 往上跳、逆序对数对。
运行：uv run pytest tests/e2e/test_42_fenwick_tree.py"""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons"


def open_demo(page: Page, lesson: str, demo_id: str):
    errors = []
    page.on("pageerror", lambda error: errors.append(error))
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


def step_back_to(demo, caption_part: str):
    """从当前帧一步步往回退，直到说明文字里出现 caption_part。"""
    for _ in range(60):
        if caption_part in demo.locator(".caption").inner_text():
            return
        click(demo, "← 上一步")
    raise AssertionError(f"没有找到说明里含 {caption_part!r} 的帧")


def tree_values(demo):
    return demo.locator(".box.tree .value")


def test_initial_tree_layout(page: Page):
    demo = open_demo(page, "42-fenwick-tree.html", "fenwick")
    expect(tree_values(demo)).to_have_text(["3", "4", "4", "9", "5", "14", "2", "31"])


def test_prefix_sum_walks_down(page: Page):
    demo = open_demo(page, "42-fenwick-tree.html", "fenwick")
    click(demo, "前缀和查询")
    wait_done(demo)
    expect(demo.locator(".best")).to_have_text("25")
    # 拿过的正好是 tree[4]、tree[6]、tree[7]（按位置顺序排列）
    expect(demo.locator(".box.tree.done .value")).to_have_text(["9", "14", "2"])
    expect(demo.locator(".box.number.range")).to_have_count(7)
    step_back_to(demo, "位置 6（二进制 0110）")
    expect(demo.locator(".box.tree.hot .value")).to_have_text(["14"])
    expect(demo.locator(".best")).to_have_text("16")


def test_add_walks_up_then_query(page: Page):
    demo = open_demo(page, "42-fenwick-tree.html", "fenwick")
    click(demo, "单点加")
    wait_done(demo)
    expect(tree_values(demo)).to_have_text(["3", "4", "4", "9", "8", "17", "2", "34"])
    expect(demo.locator(".best")).to_have_text("28")
    expect(demo.locator(".caption")).to_contain_text("比修改前的 25 多了 3")
    step_back_to(demo, "只动了 3 格")
    expect(demo.locator(".box.tree.done .value")).to_have_text(["8", "17", "34"])
    expect(demo.locator(".box.number")).to_have_text(["3", "1", "4", "1", "8", "9", "2", "6"])


def test_count_inversions(page: Page):
    demo = open_demo(page, "42-fenwick-tree.html", "fenwick")
    click(demo, "逆序对计数")
    wait_done(demo)
    expect(demo.locator(".best")).to_have_text("8")
    expect(demo.locator(".caption")).to_contain_text("一共 8 个")
    expect(demo.locator(".box.count")).to_have_text(["2", "1", "1", "1", "1", "1", "1"])
    expect(tree_values(demo)).to_have_text(["2", "3", "1", "5", "1", "2", "1"])
    expect(demo.locator(".box.number.done")).to_have_count(8)
    # numbers[6] = 2：前面比它大的有 4 个（3、4、5、9）
    step_back_to(demo, "numbers[6] = 2")
    expect(demo.locator(".caption")).to_contain_text("比它大的有 6 - 2 = 4 个")
    expect(demo.locator(".box.count.range")).to_have_count(4)
