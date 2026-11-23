"""计算机基础第 6 课 HTTP 动画的端到端测试。页面带 ?fast，每帧只停 10ms。

期望值来自仓库外的独立参考实现（cs-verify-06/ref.py）：
按「浏览器 → nginx → shop-server → 数据库」逐层判断，得出每个场景的状态码和返回者。
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons" / "cs"


def open_page(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "06-http.html").as_uri() + "?fast")
    expect(page.locator("#url-to-page .caption")).to_contain_text("访问商品页")
    expect(page.locator("#status .caption")).to_contain_text("点上面任意一个场景")
    assert not errors, errors
    return page


def wait_done(demo):
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def back(demo, times):
    for _ in range(times):
        demo.get_by_role("button", name="← 上一步").click()


def test_url_to_page_ends_rendered(page: Page):
    demo = open_page(page).locator("#url-to-page")
    demo.get_by_role("button", name="访问商品页").click()
    wait_done(demo)
    expect(demo.locator(".phase")).to_have_text("⑦ 浏览器渲染")
    expect(demo.locator(".rendered h3")).to_have_text("帆布托特包")
    expect(demo.locator('[data-node="browser"]')).to_have_class(re.compile(r"\bis-ok\b"))


def test_url_to_page_request_frame_shows_raw_message(page: Page):
    """共 15 帧：准备 + 14 步。第 9 帧是「④ 发送 HTTP 请求」，从最后一帧退 6 步。"""
    demo = open_page(page).locator("#url-to-page")
    demo.get_by_role("button", name="访问商品页").click()
    wait_done(demo)
    expect(demo.locator(".step")).to_have_text("15 / 15")
    back(demo, 6)
    expect(demo.locator(".phase")).to_have_text("④ 发送 HTTP 请求")
    expect(demo.locator("pre.msg")).to_contain_text("GET /products/42 HTTP/1.1")
    expect(demo.locator("pre.msg")).to_contain_text("Host: shop.example.com")
    # 往前到第 4 帧（第 2、3 帧是 DNS 一问一答，第 4 帧是 TCP 第一次握手），检查序号与第 5 课一致
    back(demo, 5)
    expect(demo.locator(".step")).to_have_text("4 / 15")
    expect(demo.locator(".phase")).to_have_text("② TCP 三次握手")
    expect(demo.locator(".msg-line")).to_contain_text("seq=100")


@pytest.mark.parametrize(
    "button, code",
    [
        ("正常访问", "200"),
        ("下单成功", "201"),
        ("商品页已缓存且没改过", "304"),
        ("旧网址已永久迁移", "301"),
        ("没登录就看订单", "401"),
        ("看别人的订单", "403"),
        ("商品不存在", "404"),
        ("用 GET 去调只收 POST 的接口", "405"),
        ("应用代码抛异常", "500"),
        ("应用进程挂了，代理连不上", "502"),
        ("秒杀时过载限流", "503"),
        ("应用处理太慢，代理等超时", "504"),
    ],
)
def test_each_scenario_status_code(page: Page, button, code):
    demo = open_page(page).locator("#status")
    demo.get_by_role("button", name=button, exact=True).click()
    wait_done(demo)
    expect(demo.locator(".status-code")).to_have_text(code)


def test_403_marks_app_red_at_authorization_step(page: Page):
    """403 共 9 帧：第 7 帧 shop-server 发现订单属于 bob，标红。"""
    demo = open_page(page).locator("#status")
    demo.get_by_role("button", name="看别人的订单").click()
    wait_done(demo)
    back(demo, 2)
    expect(demo.locator(".step")).to_have_text("7 / 9")
    expect(demo.locator(".caption")).to_contain_text("授权失败")
    expect(demo.locator('[data-node="app"]')).to_have_class(re.compile(r"\bis-bad\b"))
    expect(demo.locator('[data-node="nginx"]')).not_to_have_class(re.compile(r"\bis-bad\b"))
    expect(demo.locator(".status-code")).to_have_count(0)


def test_502_vs_504_red_edge_between_nginx_and_app(page: Page):
    demo = open_page(page).locator("#status")
    demo.get_by_role("button", name="应用进程挂了，代理连不上").click()
    wait_done(demo)
    back(demo, 1)
    expect(demo.locator('[data-edge="nginx-app"]')).to_have_class(re.compile(r"\bis-bad\b"))
    expect(demo.locator('[data-node="app"]')).to_have_class(re.compile(r"\bis-down\b"))
    expect(demo.locator(".caption")).to_contain_text("RST")

    demo.get_by_role("button", name="应用处理太慢，代理等超时").click()
    wait_done(demo)
    back(demo, 1)
    expect(demo.locator('[data-edge="nginx-app"]')).to_have_class(re.compile(r"\bis-bad\b"))
    expect(demo.locator('[data-node="app"]')).not_to_have_class(re.compile(r"\bis-down\b"))
    expect(demo.locator(".caption")).to_contain_text("60 秒")


def test_301_and_503_never_reach_app(page: Page):
    demo = open_page(page).locator("#status")
    for button in ["旧网址已永久迁移", "秒杀时过载限流"]:
        demo.get_by_role("button", name=button).click()
        wait_done(demo)
        total = int(demo.locator(".step").inner_text().split("/")[1])
        for _ in range(total - 1):
            expect(demo.locator('[data-edge="nginx-app"] line')).to_have_class("dash")
            demo.get_by_role("button", name="← 上一步").click()
