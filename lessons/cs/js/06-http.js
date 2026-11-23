// 第 6 课的两个动画，共用同一张架构图：浏览器 →（DNS）→ nginx → shop-server → 数据库。
// 每帧 = 各节点的状态 + 当前这一跳（谁发给谁、发了什么）+ 一句解释。
(() => {
  const SVG = "http://www.w3.org/2000/svg";
  function svgElement(tag, attrs, text) {
    const e = document.createElementNS(SVG, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    if (text != null) e.textContent = text;
    return e;
  }

  const NODES = {
    dns: { x: 10, y: 8, w: 110, h: 46, name: "DNS 服务器", sub: "UDP 53" },
    browser: { x: 10, y: 100, w: 110, h: 50, name: "浏览器", sub: "192.168.1.23" },
    nginx: { x: 190, y: 100, w: 120, h: 50, name: "nginx", sub: "反向代理 :443", mono: true },
    app: { x: 380, y: 100, w: 130, h: 50, name: "shop-server", sub: "应用 :8080", mono: true },
    db: { x: 560, y: 100, w: 72, h: 50, name: "数据库", sub: ":3306" },
  };
  // 每条边的两个端点（按键名里的先后顺序）
  const EDGES = {
    "browser-dns": [65, 98, 65, 56],
    "browser-nginx": [122, 125, 188, 125],
    "nginx-app": [312, 125, 378, 125],
    "app-db": [512, 125, 558, 125],
  };
  const ORDER = ["browser", "dns", "nginx", "app", "db"];
  const RECT_CLASS = { idle: "obj", hot: "hot", ok: "ok", bad: "bad", down: "muted" };

  function findEdge(from, to) {
    if (EDGES[`${from}-${to}`]) return { key: `${from}-${to}`, reversed: false };
    return { key: `${to}-${from}`, reversed: true };
  }

  function diagram(f) {
    const top = f.nodeSet.includes("dns") ? 0 : 64;
    const svg = svgElement("svg", { viewBox: `0 ${top} 640 ${170 - top}`, width: 640, class: "arch", role: "img", "aria-label": "架构图" });
    svg.append(svgElement("rect", { x: 178, y: 72, width: 458, height: 92, rx: 8, fill: "#fafafa", stroke: "#999", "stroke-dasharray": "5 4" }));
    svg.append(svgElement("text", { x: 186, y: 88, class: "small" }, "网店服务器 198.51.100.80"));
    const hop = f.hop && findEdge(f.hop.from, f.hop.to);
    for (const key of f.edgeSet) {
      const [x1, y1, x2, y2] = EDGES[key];
      const active = hop && hop.key === key;
      const bad = f.badEdges.includes(key);
      const g = svgElement("g", { class: "edge" + (bad ? " is-bad" : active ? " is-active" : ""), "data-edge": key });
      if (bad) {
        g.append(svgElement("line", { x1, y1, x2, y2, class: "arrow-red", "marker-end": "url(#arrow-red)" }));
        g.append(svgElement("text", { x: (x1 + x2) / 2, y: (y1 + y2) / 2 - 8, "text-anchor": "middle", fill: "#c62828", style: "fill:#c62828;font-weight:bold" }, "✕"));
      } else if (active) {
        const [ax, ay, bx, by] = hop.reversed ? [x2, y2, x1, y1] : [x1, y1, x2, y2];
        const response = ORDER.indexOf(f.hop.to) < ORDER.indexOf(f.hop.from);
        const color = response ? "green" : "blue";
        g.append(svgElement("line", { x1: ax, y1: ay, x2: bx, y2: by, class: "arrow-" + color, "marker-end": `url(#arrow-${color})`, "stroke-width": 3 }));
      } else {
        g.append(svgElement("line", { x1, y1, x2, y2, class: "dash" }));
      }
      svg.append(g);
    }
    for (const id of f.nodeSet) {
      const n = NODES[id];
      let state = f.nodes[id];
      if (f.hop && (f.hop.from === id || f.hop.to === id) && state === "idle") state = "hot";
      const g = svgElement("g", { class: "node is-" + state, "data-node": id });
      g.append(svgElement("rect", { x: n.x, y: n.y, width: n.w, height: n.h, rx: 5, class: RECT_CLASS[state] }));
      const cx = n.x + n.w / 2;
      g.append(svgElement("text", { x: cx, y: n.y + 20, "text-anchor": "middle", class: n.mono ? "mono" : "" }, n.name));
      g.append(svgElement("text", { x: cx, y: n.y + 38, "text-anchor": "middle", class: "small" }, state === "down" ? "进程已挂" : n.sub));
      svg.append(g);
    }
    return svg;
  }

  function statusKind(code) {
    if (code < 300) return "ok";
    if (code < 400) return "redirect";
    return "bad";
  }

  function render(f) {
    return [
      el("div", { class: "row" },
        el("span", { class: "phase" }, f.phase),
        f.msg && el("span", { class: "msg-line" }, f.msg)),
      diagram(f),
      f.pre && el("pre", { class: "msg" + (f.preResp ? " resp" : "") }, f.pre),
      f.rendered && el("div", { class: "rendered" },
        el("div", { class: "addr" }, "https://shop.example.com/products/42"),
        el("h3", {}, "帆布托特包"),
        el("p", {}, "¥89　", el("button", { disabled: "" }, "加入购物车"))),
      f.status && el("p", { class: "stat" },
        "状态码 ",
        el("span", { class: "status-code " + statusKind(f.status.code) }, String(f.status.code)),
        el("span", { class: "status-text" }, " " + f.status.text),
        el("span", { class: "reason" }, f.status.reason)),
    ];
  }

  // 把一串步骤变成帧。步骤：
  //   ["hop", 从, 到, 消息, 解释]   一个报文从一个节点送到相邻节点
  //   ["mark", 节点, 状态, 消息, 解释]  节点状态从此改变（ok / bad / hot）
  //   ["cut", 边, 消息, 解释]       这条边出了问题，标红
  function build({ phaseOf, nodeSet, edgeSet, start, steps, intro, down }) {
    const nodes = Object.fromEntries(nodeSet.map(id => [id, down && down.includes(id) ? "down" : "idle"]));
    const badEdges = [];
    const frames = [];
    const push = (extra, phase) => frames.push({ phase, nodeSet, edgeSet, nodes: { ...nodes }, badEdges: [...badEdges], ...extra });
    push({ say: intro, msg: start }, phaseOf(null));
    steps.forEach((step, i) => {
      const [kind, ...a] = step;
      const phase = phaseOf(step, i);
      if (kind === "hop") push({ hop: { from: a[0], to: a[1] }, msg: a[2], say: a[3], ...(a[4] || {}) }, phase);
      else if (kind === "mark") { nodes[a[0]] = a[1]; push({ msg: a[2], say: a[3] }, phase); }
      else if (kind === "cut") { badEdges.push(a[0]); push({ msg: a[1], say: a[2] }, phase); }
    });
    return frames;
  }

  // ---------- 动画 1：从输入网址到看到页面 ----------
  const REQUEST = [
    "GET /products/42 HTTP/1.1",
    "Host: shop.example.com",
    "User-Agent: Mozilla/5.0",
    "Accept: text/html",
    "Accept-Language: zh-CN",
    "Connection: keep-alive",
    "",
    "",
  ].join("\n");
  const RESPONSE = [
    "HTTP/1.1 200 OK",
    "Content-Type: text/html; charset=utf-8",
    "Content-Length: 84",
    "Cache-Control: max-age=60",
    'ETag: "p42-v3"',
    "Last-Modified: Sat, 21 Nov 2026 08:00:00 GMT",
    "",
    "<!doctype html>",
    "<title>帆布托特包</title>",
    "<h1>帆布托特包</h1>",
    "<p>¥89</p>",
  ].join("\n");

  const PAGE_STEPS = [
    ["① DNS 查询", "hop", "browser", "dns", "shop.example.com 的 IP 是多少？", "浏览器只知道域名，先向 DNS 服务器查 IP（UDP 53 端口，第 4 课）。"],
    ["① DNS 查询", "hop", "dns", "browser", "shop.example.com → 198.51.100.80", "拿到 IP 198.51.100.80。浏览器会把结果缓存一段时间，下次访问不用再查。"],
    ["② TCP 三次握手", "hop", "browser", "nginx", "SYN，seq=100（52000 → 443）", "网址是 https，默认端口 443。浏览器从临时端口 52000 发出 SYN，初始序号 100（第 5 课）。"],
    ["② TCP 三次握手", "hop", "nginx", "browser", "SYN+ACK，seq=300，ack=101", "在 443 端口监听的是 nginx，它回 SYN+ACK：自己的初始序号 300，确认号 101。"],
    ["② TCP 三次握手", "hop", "browser", "nginx", "ACK，seq=101，ack=301", "浏览器回 ACK，连接建立（ESTABLISHED）。到这里花了 1 个 RTT 加上 DNS 的时间。"],
    ["③ TLS 握手", "hop", "browser", "nginx", "ClientHello：支持的加密算法 + 随机数", "TCP 连上了，但还是明文。先做 TLS 握手：浏览器说明自己支持哪些加密算法。"],
    ["③ TLS 握手", "hop", "nginx", "browser", "ServerHello + 证书 → 验证书、商量出会话密钥", "nginx 出示证书；浏览器验证它是可信 CA 签的、域名对得上，双方商量出会话密钥。之后的报文都加密。"],
    ["④ 发送 HTTP 请求", "hop", "browser", "nginx", "GET /products/42 HTTP/1.1", "浏览器写好请求报文（下面是原文，传输时被 TLS 加密）：请求行、首部、空行，GET 没有正文。", { pre: REQUEST }],
    ["⑤ 服务器处理", "hop", "nginx", "app", "转发：GET /products/42（已解密的普通 HTTP）", "nginx 解密后，把请求转给上游 shop-server 的 8080 端口。"],
    ["⑤ 服务器处理", "hop", "app", "db", "SELECT name, price FROM products WHERE id = 42", "shop-server 去数据库查 42 号商品（第 7 课讲 SQL）。"],
    ["⑤ 服务器处理", "hop", "db", "app", "帆布托特包，89", "数据库返回一行数据。"],
    ["⑤ 服务器处理", "hop", "app", "nginx", "HTTP/1.1 200 OK + HTML", "shop-server 把商品拼成 HTML，写成响应交回 nginx。"],
    ["⑥ 响应报文", "hop", "nginx", "browser", "HTTP/1.1 200 OK（84 字节正文）", "nginx 把响应加密后发回浏览器。状态行、首部、空行、正文：", { pre: RESPONSE, preResp: true }],
    ["⑦ 浏览器渲染", "mark", "browser", "ok", "解析 HTML，画出页面", "浏览器解析 HTML 画出页面。HTML 里引用的图片会在同一条 TCP 连接上继续请求（持久连接）。"],
  ];

  function pageFrames() {
    const frames = build({
      nodeSet: ["dns", "browser", "nginx", "app", "db"],
      edgeSet: Object.keys(EDGES),
      phaseOf: (step, i) => (step ? PAGE_STEPS[i][0] : "准备"),
      start: "地址栏：https://shop.example.com/products/42",
      intro: "顾客在地址栏输入 https://shop.example.com/products/42，按下回车。",
      steps: PAGE_STEPS.map(s => s.slice(1)),
    });
    frames[frames.length - 1].rendered = true;
    return frames;
  }

  const pageRoot = document.getElementById("url-to-page");
  const pagePlayer = new Player(pageRoot, render);
  const pageReset = () => pagePlayer.load([{
    phase: "准备", nodeSet: ["dns", "browser", "nginx", "app", "db"], edgeSet: Object.keys(EDGES),
    nodes: { dns: "idle", browser: "idle", nginx: "idle", app: "idle", db: "idle" }, badEdges: [],
    say: "点「访问商品页」，看浏览器从输入网址到画出页面的每一步。",
  }]);
  pageRoot.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => pagePlayer.load(pageFrames()) }, "访问商品页"),
    el("button", { onclick: pageReset }, "重置")));
  pageReset();

  // ---------- 动画 2：状态码场景 ----------
  const B = "browser", N = "nginx", A = "app", D = "db";
  const SCENARIOS = [
    {
      label: "正常访问", code: 200, text: "OK", reason: "shop-server 查到商品，正常返回页面。",
      start: "GET /products/42",
      steps: [
        ["hop", B, N, "GET /products/42", "浏览器请求 42 号商品页。"],
        ["hop", N, A, "转发 GET /products/42", "nginx 转给上游 shop-server。"],
        ["hop", A, D, "SELECT … WHERE id = 42", "shop-server 查数据库。"],
        ["hop", D, A, "帆布托特包，89", "查到了。"],
        ["hop", A, N, "200 OK + HTML", "shop-server 拼好页面，回 200。"],
      ],
    },
    {
      label: "下单成功", code: 201, text: "Created", reason: "新订单建好了，Location: /orders/1001 指向它。",
      start: "POST /orders",
      steps: [
        ["hop", B, N, "POST /orders　Cookie: sid=7f3a9c　正文 {\"product_id\":42,\"qty\":1}", "alice 已登录，带着 Cookie 下单。"],
        ["hop", N, A, "转发 POST /orders", "nginx 转给 shop-server。"],
        ["mark", A, "ok", "sid=7f3a9c → alice", "shop-server 查会话表：sid=7f3a9c 是 alice，认证通过。"],
        ["hop", A, D, "INSERT INTO orders …", "写入一条新订单。"],
        ["hop", D, A, "新订单编号 1001", "数据库返回新订单的编号。"],
        ["hop", A, N, "201 Created　Location: /orders/1001", "新建了资源，所以回 201，不是 200。"],
      ],
    },
    {
      label: "商品页已缓存且没改过", code: 304, text: "Not Modified", reason: "版本标签没变：没有正文，浏览器继续用本机缓存。",
      start: "GET /products/42　If-None-Match: \"p42-v3\"",
      steps: [
        ["hop", B, N, "GET /products/42　If-None-Match: \"p42-v3\"", "缓存的 60 秒新鲜期过了，浏览器带着版本标签来问：我这份还能用吗？"],
        ["hop", N, A, "转发（带 If-None-Match）", "nginx 转给 shop-server。"],
        ["hop", A, D, "查 42 号商品的当前版本", "shop-server 查商品现在的版本。"],
        ["hop", D, A, "版本 \"p42-v3\"", "还是 p42-v3，商品没改过。"],
        ["hop", A, N, "304 Not Modified（无正文）", "和浏览器手里的一样，回 304，不用再传 84 字节的正文。"],
      ],
    },
    {
      label: "旧网址已永久迁移", code: 301, text: "Moved Permanently", reason: "nginx 直接回跳转；浏览器自动去 /products/42，并记住以后都去那里。",
      start: "GET /item.php?id=42",
      steps: [
        ["hop", B, N, "GET /item.php?id=42", "顾客点了一个旧书签。"],
        ["mark", N, "hot", "匹配到旧网址的跳转规则", "nginx 上配了规则：旧网址一律永久跳到新网址。请求根本不转给 shop-server。"],
      ],
    },
    {
      label: "没登录就看订单", code: 401, text: "Unauthorized", reason: "没有有效的 sid，shop-server 不知道你是谁（没认证）：先登录。",
      start: "GET /orders/1001",
      steps: [
        ["hop", B, N, "GET /orders/1001（没带 Cookie）", "顾客还没登录，浏览器里没有 sid。"],
        ["hop", N, A, "转发 GET /orders/1001", "nginx 不管登录，照常转发。"],
        ["mark", A, "bad", "没有 sid：认证失败", "shop-server 找不到 Cookie，不知道请求的是谁：认证失败。"],
        ["hop", A, N, "401 Unauthorized", "回 401。"],
      ],
    },
    {
      label: "看别人的订单", code: 403, text: "Forbidden", reason: "认证过了（是 alice），但订单是 bob 的（没授权）。",
      start: "GET /orders/1002",
      steps: [
        ["hop", B, N, "GET /orders/1002　Cookie: sid=7f3a9c", "alice 把地址里的 1001 改成 1002。"],
        ["hop", N, A, "转发 GET /orders/1002", "nginx 转给 shop-server。"],
        ["mark", A, "ok", "sid=7f3a9c → alice", "第一关认证：sid 对应 alice，通过。"],
        ["hop", A, D, "查 1002 号订单属于谁", "第二关授权：查这条订单的主人。"],
        ["hop", D, A, "属于 bob", "1002 号订单是 bob 的。"],
        ["mark", A, "bad", "alice ≠ bob：授权失败", "知道你是 alice，但订单属于 bob：授权失败。"],
        ["hop", A, N, "403 Forbidden", "回 403。"],
      ],
    },
    {
      label: "商品不存在", code: 404, text: "Not Found", reason: "路径对应的资源不存在。",
      start: "GET /products/999",
      steps: [
        ["hop", B, N, "GET /products/999", "请求 999 号商品。"],
        ["hop", N, A, "转发 GET /products/999", "nginx 转给 shop-server。"],
        ["hop", A, D, "SELECT … WHERE id = 999", "查数据库。"],
        ["hop", D, A, "0 行", "没有这个商品。"],
        ["mark", A, "bad", "找不到 999 号商品", "资源不存在。"],
        ["hop", A, N, "404 Not Found", "回 404。"],
      ],
    },
    {
      label: "用 GET 去调只收 POST 的接口", code: 405, text: "Method Not Allowed", reason: "/orders 存在，但只支持 POST（响应带 Allow: POST）。",
      start: "GET /orders",
      steps: [
        ["hop", B, N, "GET /orders　Cookie: sid=7f3a9c", "有人用 GET 去调下单接口。"],
        ["hop", N, A, "转发 GET /orders", "nginx 转给 shop-server。"],
        ["mark", A, "bad", "/orders 只接受 POST", "资源存在，方法不对。"],
        ["hop", A, N, "405 Method Not Allowed　Allow: POST", "回 405，并说明支持哪些方法。"],
      ],
    },
    {
      label: "应用代码抛异常", code: 500, text: "Internal Server Error", reason: "请求没问题，是 shop-server 自己的代码出错，由它返回。",
      start: "GET /products/42",
      steps: [
        ["hop", B, N, "GET /products/42", "一个完全正常的请求。"],
        ["hop", N, A, "转发 GET /products/42", "nginx 转给 shop-server。"],
        ["mark", A, "bad", "代码抛出异常", "shop-server 处理时抛了异常（例如访问了空对象）。"],
        ["hop", A, N, "500 Internal Server Error", "应用自己回 500，nginx 原样转回。"],
      ],
    },
    {
      label: "应用进程挂了，代理连不上", code: 502, text: "Bad Gateway", reason: "nginx 连不上上游，立刻替它回 502。",
      start: "GET /products/42", down: [A],
      intro: "shop-server 进程已经崩溃退出了（灰色），8080 端口上没有进程在监听。",
      steps: [
        ["hop", B, N, "GET /products/42", "请求照常到达 nginx。"],
        ["cut", "nginx-app", "连 8080 → 收到 RST（连接被拒绝）", "nginx 去连 8080，对方回 RST：没有进程在监听这个端口。连不上上游。"],
      ],
    },
    {
      label: "秒杀时过载限流", code: 503, text: "Service Unavailable", reason: "暂时过载，nginx 限流挡掉请求，Retry-After: 30。",
      start: "POST /orders",
      steps: [
        ["hop", B, N, "POST /orders　Cookie: sid=7f3a9c", "秒杀开始，几千个人同时下单。"],
        ["mark", N, "bad", "超过每秒请求上限", "这一秒的请求超过了 nginx 配的限流上限，多出的直接拒绝，不转给 shop-server。"],
      ],
    },
    {
      label: "应用处理太慢，代理等超时", code: 504, text: "Gateway Timeout", reason: "上游 60 秒内没回响应，nginx 替它回 504。",
      start: "GET /products/42",
      steps: [
        ["hop", B, N, "GET /products/42", "请求到达 nginx。"],
        ["hop", N, A, "转发 GET /products/42", "nginx 转给 shop-server，连接是通的。"],
        ["hop", A, D, "SELECT …（一条很慢的查询）", "shop-server 发出一条很慢的查询。"],
        ["mark", D, "hot", "查询还在跑……", "数据库还在执行；shop-server 在等数据库，nginx 在等 shop-server。"],
        ["cut", "nginx-app", "等满 60 秒，没收到响应", "nginx 等满 60 秒还没收到响应，放弃等待。"],
      ],
    },
  ];

  function scenarioFrames(sc) {
    const frames = build({
      nodeSet: [B, N, A, D],
      edgeSet: ["browser-nginx", "nginx-app", "app-db"],
      phaseOf: () => sc.label,
      start: sc.start,
      down: sc.down,
      intro: sc.intro || `场景：${sc.label}。`,
      steps: [...sc.steps, ["hop", N, B, `${sc.code} ${sc.text}`, `浏览器收到 ${sc.code}。`]],
    });
    frames[frames.length - 1].status = { code: sc.code, text: sc.text, reason: sc.reason };
    return frames;
  }

  const statusRoot = document.getElementById("status");
  const statusPlayer = new Player(statusRoot, render);
  const statusReset = () => statusPlayer.load([{
    phase: "选一个场景", nodeSet: [B, N, A, D], edgeSet: ["browser-nginx", "nginx-app", "app-db"],
    nodes: { browser: "idle", nginx: "idle", app: "idle", db: "idle" }, badEdges: [],
    say: "点上面任意一个场景，看请求走到哪里、在哪里出了问题、由谁返回哪个状态码。",
  }]);
  statusRoot.prepend(el("div", { class: "ops-bar" },
    ...SCENARIOS.map(sc => el("button", { onclick: () => statusPlayer.load(scenarioFrames(sc)) }, sc.label)),
    el("button", { onclick: statusReset }, "重置")));
  statusReset();
})();
