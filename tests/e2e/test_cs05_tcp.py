"""计算机基础第 5 课两个动画的端到端测试。页面带 ?fast，每帧只停 10ms。

期望值由仓库外的 Python 参考实现算出（cs-verify-05/ref.py）：
- 客户端 ISN 100、服务器 ISN 300，请求 100 字节、响应 200 字节：
  握手 SYN 100 / SYN+ACK 300,101 / ACK 101,301；挥手 FIN 201,501 / ACK 501,202 / FIN 501,202 / ACK 202,502。
- Reno，ssthresh 16，第 12 轮出事（cwnd 23 → ssthresh 11）：
  正常增长第 20 轮 31；超时：第 13 轮 1、第 17 轮 11、第 20 轮 14；3 个重复 ACK：第 13 轮 11、第 20 轮 18。
  ssthresh 8、第 6 轮超时：第 11 轮 6，第 20 轮 15，ssthresh 5。
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons" / "cs"


def open_page(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "05-tcp.html").as_uri() + "?fast")
    expect(page.locator("#handshake .caption")).to_contain_text("三次握手")
    expect(page.locator("#cwnd .caption")).to_contain_text("点上面的按钮")
    assert not errors, errors
    return page.locator("#handshake"), page.locator("#cwnd")


def wait_done(demo):
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def back(demo, n):
    for _ in range(n):
        demo.get_by_role("button", name="← 上一步").click()


def labels(demo):
    return demo.locator(".msg .msg-label")


def test_handshake_ends_established_with_correct_third_segment(page: Page):
    demo, _ = open_page(page)
    demo.get_by_role("button", name="三次握手", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".client-state")).to_have_text("ESTABLISHED")
    expect(demo.locator(".server-state")).to_have_text("ESTABLISHED")
    expect(labels(demo)).to_have_text(["SYN seq=100", "SYN+ACK seq=300 ack=101", "ACK seq=101 ack=301"])


def test_handshake_middle_frame_after_first_syn(page: Page):
    demo, _ = open_page(page)
    demo.get_by_role("button", name="三次握手", exact=True).click()
    wait_done(demo)
    back(demo, 2)  # 4 帧：初始、①、②、③ → 退到 ①
    expect(demo.locator(".step")).to_have_text("2 / 4")
    expect(demo.locator(".caption")).to_contain_text("客户端发 SYN")
    expect(demo.locator(".client-state")).to_have_text("SYN_SENT")
    expect(demo.locator(".server-state")).to_have_text("SYN_RCVD")
    expect(demo.locator(".msg.latest .msg-label")).to_have_text("SYN seq=100")


def test_teardown_ends_time_wait_and_closed(page: Page):
    demo, _ = open_page(page)
    demo.get_by_role("button", name="四次挥手", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".client-state")).to_have_text("TIME_WAIT")
    expect(demo.locator(".server-state")).to_have_text("CLOSED")
    expect(labels(demo)).to_have_text([
        "FIN+ACK seq=201 ack=501", "ACK seq=501 ack=202", "FIN+ACK seq=501 ack=202", "ACK seq=202 ack=502"])
    back(demo, 2)  # 退到 ② 之后：半关闭
    expect(demo.locator(".client-state")).to_have_text("FIN_WAIT_2")
    expect(demo.locator(".server-state")).to_have_text("CLOSE_WAIT")


def test_full_process(page: Page):
    demo, _ = open_page(page)
    demo.get_by_role("button", name="完整过程", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".msg")).to_have_count(10)
    expect(labels(demo).nth(2)).to_have_text("ACK seq=101 ack=301")
    expect(labels(demo).nth(3)).to_have_text("ACK seq=101 ack=301 [100 字节]")
    expect(labels(demo).nth(4)).to_have_text("ACK seq=301 ack=201 [200 字节]")
    expect(demo.locator(".client-state")).to_have_text("TIME_WAIT")
    expect(demo.locator(".server-state")).to_have_text("CLOSED")


def test_lost_synack_is_retransmitted(page: Page):
    demo, _ = open_page(page)
    demo.get_by_role("button", name="握手时第二个报文丢失", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".msg")).to_have_count(4)
    expect(demo.locator(".msg.lost")).to_have_count(1)
    expect(labels(demo).nth(2)).to_have_text("重发 SYN+ACK seq=300 ack=101")
    expect(demo.locator(".client-state")).to_have_text("ESTABLISHED")
    expect(demo.locator(".server-state")).to_have_text("ESTABLISHED")
    back(demo, 2)  # 退到丢失那一帧
    expect(demo.locator(".client-state")).to_have_text("SYN_SENT")
    expect(demo.locator(".server-state")).to_have_text("SYN_RCVD")


@pytest.mark.parametrize(
    "button, final_cwnd, final_ss",
    [("正常增长", "31", "16"), ("第 N 轮超时", "14", "11"), ("第 N 轮收到 3 个重复 ACK", "18", "11")],
)
def test_cwnd_final_round(page: Page, button, final_cwnd, final_ss):
    _, demo = open_page(page)
    demo.get_by_role("button", name=button, exact=True).click()
    wait_done(demo)
    expect(demo.locator(".round-value")).to_have_text("20")
    expect(demo.locator(".cwnd-value")).to_have_text(final_cwnd)
    expect(demo.locator(".ssthresh-value")).to_have_text(final_ss)


def test_cwnd_timeout_middle_rounds(page: Page):
    _, demo = open_page(page)
    demo.get_by_role("button", name="第 N 轮超时", exact=True).click()
    wait_done(demo)
    back(demo, 3)  # 第 20 轮 → 第 17 轮
    expect(demo.locator(".round-value")).to_have_text("17")
    expect(demo.locator(".cwnd-value")).to_have_text("11")
    expect(demo.locator(".phase")).to_have_text("拥塞避免")
    back(demo, 4)  # → 第 13 轮
    expect(demo.locator(".cwnd-value")).to_have_text("1")
    expect(demo.locator(".ssthresh-value")).to_have_text("11")
    expect(demo.locator(".phase")).to_have_text("慢启动")
    back(demo, 1)  # → 第 12 轮：出事的那一轮
    expect(demo.locator(".cwnd-value")).to_have_text("23")
    expect(demo.locator(".caption")).to_contain_text("超时")
    expect(demo.locator(".event-mark")).to_have_count(1)


def test_cwnd_dup_ack_round_13(page: Page):
    _, demo = open_page(page)
    demo.get_by_role("button", name="第 N 轮收到 3 个重复 ACK", exact=True).click()
    wait_done(demo)
    back(demo, 7)
    expect(demo.locator(".round-value")).to_have_text("13")
    expect(demo.locator(".cwnd-value")).to_have_text("11")
    expect(demo.locator(".phase")).to_have_text("拥塞避免")


def test_cwnd_custom_inputs_match_self_test(page: Page):
    _, demo = open_page(page)
    demo.get_by_label("初始 ssthresh").fill("8")
    demo.get_by_label("出事的轮次").fill("6")
    demo.get_by_role("button", name="第 N 轮超时", exact=True).click()
    wait_done(demo)
    expect(demo.locator(".cwnd-value")).to_have_text("15")
    expect(demo.locator(".ssthresh-value")).to_have_text("5")
    back(demo, 9)  # → 第 11 轮
    expect(demo.locator(".round-value")).to_have_text("11")
    expect(demo.locator(".cwnd-value")).to_have_text("6")
