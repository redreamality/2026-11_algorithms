"""计算机基础第 2 课两个动画的端到端测试。页面带 ?fast，每帧只停 10ms。

期望值由仓库外的独立 Python 参考实现算出（讲解页的表里也写着）：
序列 7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1：3 页框 FIFO 15、LRU 12、OPT 9；4 页框 FIFO 10、LRU 8、OPT 8。
Belady 序列 1 2 3 4 1 2 5 1 2 3 4 5，FIFO：3 页框 9 次，4 页框 10 次。
地址翻译（页 0→5、1→2、2→7、页 3 在磁盘，缺页调入页框 4）：0x1004→0x2004，0x1ABC→0x2ABC（TLB 命中），0x3010→0x4010。
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons" / "cs"


def open_page(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "02-virtual-memory.html").as_uri() + "?fast")
    expect(page.locator("#paging .caption")).to_contain_text("选一种置换算法")
    expect(page.locator("#mmu .caption")).to_contain_text("翻译")
    assert not errors, errors
    return page


def wait_done(demo):
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


@pytest.mark.parametrize(
    "frames, button, faults, rate",
    [
        ("3", "FIFO", "15", "75%"),
        ("3", "LRU", "12", "60%"),
        ("3", "OPT", "9", "45%"),
        ("4", "FIFO", "10", "50%"),
        ("4", "LRU", "8", "40%"),
        ("4", "OPT", "8", "40%"),
    ],
)
def test_replacement_fault_counts(page: Page, frames, button, faults, rate):
    demo = open_page(page).locator("#paging")
    demo.get_by_label("页框数").fill(frames)
    demo.get_by_role("button", name=button, exact=True).click()
    wait_done(demo)
    expect(demo.locator(".fault-count")).to_have_text(faults)
    expect(demo.locator(".fault-rate")).to_have_text(rate)
    expect(demo.locator("td.miss")).to_have_count(int(faults))


def test_belady_anomaly(page: Page):
    demo = open_page(page).locator("#paging")
    demo.get_by_role("button", name="Belady 异常").click()
    wait_done(demo)
    expect(demo.get_by_label("访问序列")).to_have_value("1 2 3 4 1 2 5 1 2 3 4 5")
    expect(demo.locator(".fault-count")).to_have_text("9")
    demo.get_by_label("页框数").fill("4")
    demo.get_by_role("button", name="Belady 异常").click()
    wait_done(demo)
    expect(demo.locator(".fault-count")).to_have_text("10")


def test_fifo_step_back_to_sixth_access(page: Page):
    """第 6 次访问页 3：页框里 2 0 1，FIFO 换出最早调入的 0；此前缺页 5 次。"""
    demo = open_page(page).locator("#paging")
    demo.get_by_role("button", name="FIFO", exact=True).click()
    wait_done(demo)
    for _ in range(14):  # 共 21 帧（开头 1 帧 + 20 次访问），从第 21 帧退到第 7 帧
        demo.get_by_role("button", name="← 上一步").click()
    caption = demo.locator(".caption")
    expect(caption).to_contain_text("第 6 次访问页 3")
    expect(caption).to_contain_text("换出 0")
    expect(demo.locator("th.cur")).to_have_text("3")
    expect(demo.locator("td.new.cur")).to_have_text("3")
    expect(demo.locator(".fault-count")).to_have_text("5")


def test_opt_step_back_explains_future_use(page: Page):
    demo = open_page(page).locator("#paging")
    demo.get_by_role("button", name="OPT", exact=True).click()
    wait_done(demo)
    for _ in range(14):
        demo.get_by_role("button", name="← 上一步").click()
    expect(demo.locator(".caption")).to_contain_text("未来最晚才用的是 1")
    expect(demo.locator(".caption")).to_contain_text("换出 1")


def test_address_translation_tlb_and_fault(page: Page):
    demo = open_page(page).locator("#mmu")
    addr = demo.get_by_label("虚拟地址")
    translate = demo.get_by_role("button", name="翻译")

    addr.fill("0x1004")
    translate.click()
    wait_done(demo)
    expect(demo.locator(".page-no")).to_have_text("1")
    expect(demo.locator(".offset")).to_have_text("0x0004")
    expect(demo.locator(".tlb-result")).to_have_text("未命中")
    expect(demo.locator(".phys-addr")).to_have_text("0x2004")

    addr.fill("0x1ABC")
    translate.click()
    wait_done(demo)
    expect(demo.locator(".tlb-result")).to_have_text("命中")
    expect(demo.locator(".phys-addr")).to_have_text("0x2ABC")

    addr.fill("0x3010")
    translate.click()
    wait_done(demo)
    expect(demo.locator(".fault-flag")).to_have_text("缺页")
    expect(demo.locator(".phys-addr")).to_have_text("0x4010")
    expect(demo.locator(".tlb tr")).to_have_count(3)  # 表头 + 页 1 + 页 3


def test_address_translation_decimal_and_out_of_range(page: Page):
    demo = open_page(page).locator("#mmu")
    demo.get_by_label("虚拟地址").fill("8500")  # = 0x2134，正文第 7 节的例子
    demo.get_by_role("button", name="翻译").click()
    wait_done(demo)
    expect(demo.locator(".phys-addr")).to_have_text("0x7134")
    demo.get_by_label("虚拟地址").fill("0x5000")
    demo.get_by_role("button", name="翻译").click()
    wait_done(demo)
    expect(demo.locator(".caption")).to_contain_text("越界")
