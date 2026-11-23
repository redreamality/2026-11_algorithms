// 第 4 课的两个动画。
// journey：一次请求从顾客电脑到网店服务器，逐层封装、逐跳转发、逐层解封装。
// subnet：子网计算器，逐步把 IP 和掩码转成二进制、按位与，算出网络地址、广播地址和可用主机数。

// ---------- 动画一：一次请求的旅程 ----------
(() => {
  const root = document.getElementById("journey");
  const MAC = {
    pc: "00:1A:2B:00:00:23", homeLan: "00:1A:2B:00:00:01", homeWan: "00:1A:2B:00:00:02",
    ispHome: "00:3C:9D:00:00:11", ispShop: "00:3C:9D:00:00:12", server: "00:3C:9D:00:00:80",
  };
  const DEVICES = [
    { name: "顾客电脑", addr: "192.168.1.23", top: 0 },
    { name: "家用路由器", addr: "192.168.1.1 | 203.0.113.7", top: 2 },
    { name: "运营商路由器", addr: "203.0.113.1 | 198.51.100.1", top: 2 },
    { name: "网店服务器", addr: "198.51.100.80", top: 0 },
  ];
  const LAYERS = ["应用层", "传输层", "网络层", "链路层", "物理层"];
  const UNITS = ["报文", "报文段", "分组", "帧", "比特"];
  const LINKS = ["电脑 → 家用路由器", "家用路由器 → 运营商路由器", "运营商路由器 → 服务器"];

  function simulate() {
    const frames = [];
    const p = { tp: null, ip: null, mac: null };
    const log = [];
    const push = (dev, layer, unit, changed, say, extra = {}) => frames.push({
      dev, layer, unit, changed, say,
      tp: p.tp && { ...p.tp }, ip: p.ip && { ...p.ip }, mac: p.mac && { ...p.mac },
      bits: layer === 4, log: log.map(r => ({ ...r })), ...extra,
    });
    const send = link => log.push({ link, ...p.mac, srcIp: p.ip.src, dstIp: p.ip.dst, ttl: p.ip.ttl });

    // 顾客电脑：从上往下封装
    push(0, 0, 0, [], "顾客电脑 · 应用层：浏览器生成一个 HTTP 请求「把首页发给我」（网店用 HTTPS，内容会被加密，第 6 课讲）。这份数据叫报文。");
    p.tp = { src: 50000, dst: 443 };
    push(0, 1, 1, ["tp"], "顾客电脑 · 传输层：在前面加上传输层首部，源端口 50000（内核临时分给浏览器），目的端口 443（shop-server 监听的端口）。现在叫报文段。");
    p.ip = { src: "192.168.1.23", dst: "198.51.100.80", ttl: 64 };
    push(0, 2, 2, ["ip"], "顾客电脑 · 网络层：加上 IP 首部，源 IP 192.168.1.23，目的 IP 198.51.100.80，TTL = 64。用自己的掩码一算：198.51.100.80 AND 255.255.255.0 = 198.51.100.0，不是本网络 192.168.1.0，所以下一跳是默认网关 192.168.1.1。现在叫分组。");
    p.mac = { src: MAC.pc, dst: MAC.homeLan };
    push(0, 3, 3, ["mac"], "顾客电脑 · 链路层：ARP 查到网关 192.168.1.1 的 MAC 是 :01。加上 MAC 首部：源 :23，目的 :01（是网关的 MAC，不是服务器的），末尾加尾部。现在叫帧。");
    send(LINKS[0]);
    push(0, 4, 4, [], "顾客电脑 · 物理层：整帧变成比特，以电信号发上网线，送到家用路由器。");

    // 家用路由器：拆到网络层，查路由表，做 NAT，重新封装
    const keep = p.mac;
    p.mac = null;
    push(1, 3, 2, [], `家用路由器 · 链路层：把比特还原成帧。目的 MAC :01 正是自己的内网口，收下，拆掉 MAC 首部和尾部（源 ${keep.src}，目的 ${keep.dst}）。`);
    p.ip = { ...p.ip, src: "203.0.113.7", ttl: 63 };
    p.tp = { ...p.tp, src: 60001 };
    push(1, 2, 2, ["ip", "tp", "ttl"], "家用路由器 · 网络层：目的 IP 198.51.100.80 不在 192.168.1.0/24 里，走默认路由，下一跳 203.0.113.1，从外网口发出；TTL 64 → 63。它还做了 NAT：把源地址 192.168.1.23:50000 改写成自己外网口的 203.0.113.7:60001，记进 NAT 表。");
    p.mac = { src: MAC.homeWan, dst: MAC.ispHome };
    push(1, 3, 3, ["mac"], "家用路由器 · 链路层：ARP 查到下一跳 203.0.113.1 的 MAC 是 :11。封装一个新帧：源 MAC :02（自己的外网口），目的 MAC :11。旧的 MAC 首部已经不在了。");
    send(LINKS[1]);
    push(1, 4, 4, [], "家用路由器 · 物理层：新帧变成比特，发往运营商路由器。");

    // 运营商路由器：普通转发，不改 IP 地址
    p.mac = null;
    push(2, 3, 2, [], "运营商路由器 · 链路层：目的 MAC :11 是自己，收下，拆掉 MAC 首部和尾部。");
    p.ip = { ...p.ip, ttl: 62 };
    push(2, 2, 2, ["ttl"], "运营商路由器 · 网络层：目的 IP 198.51.100.80 同时匹配 198.51.100.0/24 和默认路由 0.0.0.0/0，按最长前缀匹配选 /24：直连，从接机房一侧发出。TTL 63 → 62。源 IP、目的 IP 都原样保留。");
    p.mac = { src: MAC.ispShop, dst: MAC.server };
    push(2, 3, 3, ["mac"], "运营商路由器 · 链路层：服务器就在直连的网络里，ARP 查到 198.51.100.80 的 MAC 是 :80。新帧：源 MAC :12，目的 MAC :80。和上一段比，MAC 全换了，IP 一点没变。");
    send(LINKS[2]);
    push(2, 4, 4, [], "运营商路由器 · 物理层：新帧变成比特，发往网店服务器。");

    // 网店服务器：从下往上解封装
    p.mac = null;
    push(3, 3, 2, [], "网店服务器 · 链路层：目的 MAC :80 是自己，拆掉 MAC 首部和尾部，把分组交给网络层。");
    p.ip = null;
    push(3, 2, 1, [], "网店服务器 · 网络层：目的 IP 198.51.100.80 是自己，拆掉 IP 首部，把报文段交给传输层。");
    p.tp = null;
    const delivered = { port: 443, process: "shop-server（PID 1024）" };
    push(3, 1, 0, [], "网店服务器 · 传输层：目的端口 443，内核查到 shop-server（PID 1024）正在监听 443，拆掉传输层首部，把数据交给这个进程。", { delivered });
    push(3, 0, 0, [], "网店服务器 · 应用层：shop-server 读到 HTTP 请求，开始准备首页。全程结束。看下面的表：三段链路的 MAC 各不相同；运营商路由器前后，源 IP 和目的 IP 完全一样。", { delivered });
    return frames;
  }

  const span = (cls, text, red) => el("span", { class: cls, style: red ? "color:#c62828;font-weight:bold" : "" }, String(text));

  function packet(frame) {
    const has = key => frame.changed.includes(key) ? " changed" : "";
    const cells = [];
    if (frame.mac) cells.push(el("div", { class: "cell L2 hdr-mac" + has("mac") },
      el("b", {}, "MAC 首部"), "源 ", span("src-mac", frame.mac.src), el("br"), "目的 ", span("dst-mac", frame.mac.dst)));
    if (frame.ip) cells.push(el("div", { class: "cell L3 hdr-ip" + has("ip") },
      el("b", {}, "IP 首部"), "源 ", span("src-ip", frame.ip.src), el("br"), "目的 ", span("dst-ip", frame.ip.dst),
      el("br"), "TTL ", span("ttl", frame.ip.ttl, frame.changed.includes("ttl"))));
    if (frame.tp) cells.push(el("div", { class: "cell L4 hdr-tp" + has("tp") },
      el("b", {}, "传输层首部"), "源端口 ", span("src-port", frame.tp.src), el("br"), "目的端口 ", span("dst-port", frame.tp.dst)));
    cells.push(el("div", { class: "cell L5 hdr-app" }, el("b", {}, "HTTP 请求"), "把首页发给我"));
    if (frame.mac) cells.push(el("div", { class: "cell L2 hdr-trailer" + has("mac") }, el("b", {}, "尾部"), "校验"));
    return cells;
  }

  function render(frame) {
    const devices = el("div", { class: "net-devices" }, DEVICES.map((d, i) => el("div", { class: "net-device" + (i === frame.dev ? " hot" : "") },
      el("div", { class: "dev-name" }, d.name),
      d.addr.split(" | ").map(a => el("div", { class: "dev-addr" }, a)),
      LAYERS.map((name, k) => k < d.top
        ? el("div", { class: "net-layer", style: "visibility:hidden" }, name)
        : el("div", { class: "net-layer has" + (i === frame.dev && k === frame.layer ? " now" : "") }, name)))));
    const out = [
      devices,
      el("p", { class: "packet-unit" }, "此刻的数据单位：", el("b", { class: "unit" }, UNITS[frame.unit]),
        frame.bits ? "（下面这一整帧正以比特的形式在线路上传输）" : ""),
    ];
    if (frame.bits) out.push(el("div", { class: "packet" }, el("div", { class: "cell L1" }, "0110100101110010011010010110110001100101…")));
    out.push(el("div", { class: "packet" }, packet(frame)));
    if (frame.delivered) out.push(el("p", { class: "stat" }, "交给端口 ", el("b", { class: "delivered-port" }, String(frame.delivered.port)),
      " 上的进程 ", el("b", { class: "delivered-process" }, frame.delivered.process)));
    if (frame.log.length) out.push(el("table", { class: "hop-log" },
      el("tr", {}, ["已走过的链路", "源 MAC", "目的 MAC", "源 IP", "目的 IP", "TTL"].map(h => el("th", {}, h))),
      frame.log.map(r => el("tr", {}, el("td", {}, r.link), el("td", {}, r.src), el("td", {}, r.dst),
        el("td", {}, r.srcIp), el("td", {}, r.dstIp), el("td", {}, String(r.ttl))))));
    return out;
  }

  const player = new Player(root, render);
  const reset = () => player.load([{
    dev: null, layer: null, unit: 0, changed: [], tp: null, ip: null, mac: null, bits: false, log: [],
    say: "浏览器已经通过 DNS 知道 shop.example.com 是 198.51.100.80。点「发送请求」，看这条请求怎么走到 shop-server。",
  }]);
  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(simulate()) }, "发送请求"),
    el("button", { onclick: reset }, "重置旅程")));
  reset();
})();

// ---------- 动画二：子网计算器 ----------
(() => {
  const root = document.getElementById("subnet");
  const toDotted = n => [24, 16, 8, 0].map(s => (n >>> s) & 255).join(".");
  const toBits = n => (n >>> 0).toString(2).padStart(32, "0");

  function parse(text) {
    const m = /^\s*(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\s*$/.exec(text);
    if (!m) return null;
    const parts = m.slice(1).map(Number);
    if (parts.some(x => x > 255)) return null;
    return parts.reduce((acc, x) => acc * 256 + x, 0) >>> 0;
  }

  function simulate(text, prefixText) {
    const ip = parse(text);
    const prefix = Number(prefixText);
    if (ip === null) return [{ rows: [], error: true, say: `「${text}」不是合法的 IPv4 地址：要写成 4 段，每段 0～255，用点隔开。` }];
    if (!Number.isInteger(prefix) || prefix < 1 || prefix > 30) return [{ rows: [], error: true, say: "前缀长度请填 1～30 的整数（/31、/32 是点对点链路和单台主机的特例，这里不讨论）。" }];
    const n = 32 - prefix;
    const mask = (0xFFFFFFFF << n) >>> 0;
    const network = (ip & mask) >>> 0;
    const broadcast = (network | (~mask >>> 0)) >>> 0;
    const count = 2 ** n - 2;
    const dotted = toDotted(ip);
    const rows = [], frames = [];
    const result = { network: "?", broadcast: "?", count: "?", range: "" };
    const snap = (say, color) => frames.push({ rows: rows.map(r => ({ ...r })), color, prefix, result: { ...result }, say });

    rows.push({ label: "IP 地址", value: ip, dec: dotted });
    snap(`第 1 步：把 ${dotted} 的每一段写成 8 位二进制，一共 32 位。`, false);
    rows.push({ label: `掩码 /${prefix}`, value: mask, dec: toDotted(mask) });
    snap(`第 2 步：前缀 /${prefix} 就是掩码前 ${prefix} 位为 1、后 ${n} 位为 0，写成点分十进制是 ${toDotted(mask)}。蓝色是网络位，橙色是主机位。`, true);
    rows.push({ label: "按位与", value: network, dec: toDotted(network) });
    result.network = toDotted(network);
    snap(`第 3 步：IP 和掩码逐位做与运算：网络位原样保留，主机位全部变 0。得到网络地址 ${toDotted(network)}。`, true);
    rows.push({ label: "主机位全 1", value: broadcast, dec: toDotted(broadcast) });
    result.broadcast = toDotted(broadcast);
    snap(`第 4 步：把网络地址的 ${n} 个主机位全部改成 1，得到广播地址 ${toDotted(broadcast)}。`, true);
    result.count = String(count);
    result.range = `${toDotted(network + 1)} ～ ${toDotted(broadcast - 1)}`;
    snap(`第 5 步：主机位 n = 32 − ${prefix} = ${n}，一共 2^${n} = ${2 ** n} 个地址，去掉网络地址和广播地址，可用 2^${n} − 2 = ${count} 个。`, true);
    return frames;
  }

  function bits(value, prefix, color) {
    const s = toBits(value);
    return el("span", { class: "bits" }, [0, 1, 2, 3].map(o => el("span", { class: "octet" },
      [...s.slice(o * 8, o * 8 + 8)].map((b, k) => {
        const pos = o * 8 + k;
        return el("span", { class: "bit" + (color ? (pos < prefix ? " net" : " host") : "") }, b);
      }))));
  }

  function render(frame) {
    if (frame.error) return [el("p", { class: "subnet-error stat" }, "输入有误，请修改后重新计算。")];
    if (!frame.rows.length) return [el("p", { class: "label" }, "（还没开始计算）")];
    const r = frame.result;
    return [
      ...frame.rows.map(row => el("div", { class: "bits-row" },
        el("span", { class: "bits-label" }, row.label), bits(row.value, frame.prefix, frame.color),
        el("span", { class: "bits-dec" }, row.dec))),
      el("p", { class: "subnet-result stat" },
        "网络地址 ", el("b", { class: "network-address" }, r.network),
        "　广播地址 ", el("b", { class: "broadcast-address" }, r.broadcast),
        "　可用主机数 ", el("b", { class: "host-count" }, r.count),
        r.range ? el("span", {}, "（可用范围 ", el("b", { class: "host-range" }, r.range), "）") : ""),
    ];
  }

  const player = new Player(root, render);
  const address = el("input", { type: "text", value: "192.168.1.23", "aria-label": "IP 地址" });
  const prefix = el("input", { type: "number", value: "24", min: "1", max: "30", "aria-label": "前缀长度" });
  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "IP 地址"), address,
    el("span", { class: "label" }, "/"), prefix,
    el("button", { onclick: () => player.load(simulate(address.value, prefix.value)) }, "计算")));
  player.load([{ rows: [], say: "填好 IP 地址和前缀长度，点「计算」。" }]);
})();
