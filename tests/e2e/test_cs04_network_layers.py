"""计算机基础第 4 课两个动画的端到端测试。页面带 ?fast，每帧只停 10ms。

期望值来源：
- 子网计算器：仓库外的参考脚本用 Python 的 ipaddress 模块算出
  192.168.1.23/24 → 192.168.1.0、192.168.1.255、254；
  172.16.45.200/20 → 172.16.32.0、172.16.47.255、4094；
  198.51.100.80/26 → 198.51.100.64、198.51.100.127、62。
- 请求旅程：讲解页第 1 节的固定地址表（每个接口的 IP 和 MAC）。
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

LESSONS = Path(__file__).resolve().parents[2] / "lessons" / "cs"

PC, HOME_LAN, HOME_WAN = "00:1A:2B:00:00:23", "00:1A:2B:00:00:01", "00:1A:2B:00:00:02"
ISP_HOME, ISP_SHOP, SERVER = "00:3C:9D:00:00:11", "00:3C:9D:00:00:12", "00:3C:9D:00:00:80"


def open_page(page: Page):
    errors = []
    page.on("pageerror", lambda e: errors.append(e))
    page.goto((LESSONS / "04-network-layers.html").as_uri() + "?fast")
    expect(page.locator("#journey .caption")).to_contain_text("发送请求")
    expect(page.locator("#subnet .caption")).to_contain_text("计算")
    assert not errors, errors
    return page


def wait_done(demo):
    expect(demo.locator(".step")).to_have_text(re.compile(r"^(\d+) / \1$"))


def hop_row(demo, i):
    """已走过的链路表的第 i 段（从 1 开始），返回各列的 locator。"""
    return demo.locator(".hop-log tr").nth(i).locator("td")


def test_journey_delivers_to_port_443(page: Page):
    demo = open_page(page).locator("#journey")
    demo.get_by_role("button", name="发送请求").click()
    wait_done(demo)
    expect(demo.locator(".delivered-port")).to_have_text("443")
    expect(demo.locator(".delivered-process")).to_contain_text("shop-server")
    expect(demo.locator(".net-device.hot .dev-name")).to_have_text("网店服务器")
    expect(demo.locator(".net-layer.now")).to_have_text("应用层")
    # 拆到最后只剩应用层数据
    expect(demo.locator(".hdr-mac")).to_have_count(0)
    expect(demo.locator(".hdr-ip")).to_have_count(0)
    expect(demo.locator(".hdr-tp")).to_have_count(0)


def test_mac_changes_every_hop_ip_unchanged_through_isp_router(page: Page):
    demo = open_page(page).locator("#journey")
    demo.get_by_role("button", name="发送请求").click()
    wait_done(demo)
    expect(demo.locator(".hop-log tr")).to_have_count(4)  # 表头 + 三段链路
    # 列：链路、源 MAC、目的 MAC、源 IP、目的 IP、TTL
    expect(hop_row(demo, 1)).to_have_text([re.compile("电脑"), PC, HOME_LAN, "192.168.1.23", "198.51.100.80", "64"])
    expect(hop_row(demo, 2)).to_have_text([re.compile("家用路由器"), HOME_WAN, ISP_HOME, "203.0.113.7", "198.51.100.80", "63"])
    expect(hop_row(demo, 3)).to_have_text([re.compile("运营商路由器"), ISP_SHOP, SERVER, "203.0.113.7", "198.51.100.80", "62"])


def test_step_back_to_isp_router_network_layer(page: Page):
    """从最后一帧退 6 步，到运营商路由器在网络层查路由表的那一帧。"""
    demo = open_page(page).locator("#journey")
    demo.get_by_role("button", name="发送请求").click()
    wait_done(demo)
    for _ in range(6):
        demo.get_by_role("button", name="← 上一步").click()
    expect(demo.locator(".caption")).to_contain_text("最长前缀匹配")
    expect(demo.locator(".net-device.hot .dev-name")).to_have_text("运营商路由器")
    expect(demo.locator(".net-layer.now")).to_have_text("网络层")
    expect(demo.locator(".unit")).to_have_text("分组")
    # 拆到了网络层：没有 MAC 首部，IP 地址和进入前一样，TTL 已减到 62
    expect(demo.locator(".hdr-mac")).to_have_count(0)
    expect(demo.locator(".src-ip")).to_have_text("203.0.113.7")
    expect(demo.locator(".dst-ip")).to_have_text("198.51.100.80")
    expect(demo.locator(".ttl")).to_have_text("62")
    # 往前一步是刚收下帧的链路层，往后一步换上新的 MAC
    demo.get_by_role("button", name="下一步 →").click()
    expect(demo.locator(".src-mac")).to_have_text(ISP_SHOP)
    expect(demo.locator(".dst-mac")).to_have_text(SERVER)
    expect(demo.locator(".dst-ip")).to_have_text("198.51.100.80")


@pytest.mark.parametrize(
    "address, prefix, network, broadcast, count",
    [
        ("192.168.1.23", "24", "192.168.1.0", "192.168.1.255", "254"),
        ("172.16.45.200", "20", "172.16.32.0", "172.16.47.255", "4094"),
        ("198.51.100.80", "26", "198.51.100.64", "198.51.100.127", "62"),
    ],
)
def test_subnet_calculator(page: Page, address, prefix, network, broadcast, count):
    demo = open_page(page).locator("#subnet")
    demo.get_by_label("IP 地址").fill(address)
    demo.get_by_label("前缀长度").fill(prefix)
    demo.get_by_role("button", name="计算").click()
    wait_done(demo)
    expect(demo.locator(".network-address")).to_have_text(network)
    expect(demo.locator(".broadcast-address")).to_have_text(broadcast)
    expect(demo.locator(".host-count")).to_have_text(count)
    expect(demo.locator(".bits .bit.net")).to_have_count(4 * int(prefix))  # 4 行，每行 prefix 个网络位


def test_subnet_default_values_and_middle_step(page: Page):
    demo = open_page(page).locator("#subnet")
    expect(demo.get_by_label("IP 地址")).to_have_value("192.168.1.23")
    expect(demo.get_by_label("前缀长度")).to_have_value("24")
    demo.get_by_role("button", name="计算").click()
    wait_done(demo)
    for _ in range(2):  # 退到第 3 步：按位与
        demo.get_by_role("button", name="← 上一步").click()
    expect(demo.locator(".caption")).to_contain_text("第 3 步")
    expect(demo.locator(".network-address")).to_have_text("192.168.1.0")
    expect(demo.locator(".broadcast-address")).to_have_text("?")
    expect(demo.locator(".bits-row .bits-dec")).to_have_text(["192.168.1.23", "255.255.255.0", "192.168.1.0"])


def test_subnet_rejects_bad_address(page: Page):
    demo = open_page(page).locator("#subnet")
    demo.get_by_label("IP 地址").fill("192.168.1.300")
    demo.get_by_role("button", name="计算").click()
    expect(demo.locator(".caption")).to_contain_text("不是合法的 IPv4 地址")
    expect(demo.locator(".network-address")).to_have_count(0)
