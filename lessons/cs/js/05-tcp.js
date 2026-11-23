// 第 5 课两个动画：TCP 连接的一生（时序图）、Reno 拥塞窗口变化。
const SVG_NS = "http://www.w3.org/2000/svg";
function svgEl(tag, attrs, text) {
  const e = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text != null) e.textContent = text;
  return e;
}

// ---------- 动画一：时序图 ----------
(() => {
  const root = document.getElementById("handshake");
  // 主线数据：客户端 ISN = 100，服务器 ISN = 300；请求 100 字节，响应 200 字节
  // 每个报文：dir 谁发，sender / receiver 发出后、收到后各自进入的状态（null = 不变）
  const HANDSHAKE = [
    { dir: "C", flags: "SYN", seq: 100, ack: null, sender: "SYN_SENT", receiver: "SYN_RCVD",
      say: "① 客户端发 SYN，seq = 100（它的初始序号）。发出后进入 SYN_SENT；服务器收到后进入 SYN_RCVD。SYN 占一个序号，所以 100 用掉了。" },
    { dir: "S", flags: "SYN+ACK", seq: 300, ack: 101, sender: null, receiver: "ESTABLISHED",
      say: "② 服务器回 SYN+ACK：seq = 300（服务器自己的初始序号），ack = 101（客户端的 100 号已收到，下一个要 101）。客户端收到后进入 ESTABLISHED。" },
    { dir: "C", flags: "ACK", seq: 101, ack: 301, sender: null, receiver: "ESTABLISHED",
      say: "③ 客户端回 ACK：seq = 101，ack = 301（服务器的 SYN 占了 300，下一个要 301）。服务器收到后也进入 ESTABLISHED，连接建立。" },
  ];
  const DATA = [
    { dir: "C", flags: "ACK", seq: 101, ack: 301, len: 100, sender: null, receiver: null,
      say: "④ 浏览器发 100 字节的请求，seq = 101，占用 101～200 号字节。纯 ACK 不占序号，所以第三次握手的 seq = 101 这里还能接着用。" },
    { dir: "S", flags: "ACK", seq: 301, ack: 201, len: 200, sender: null, receiver: null,
      say: "⑤ 服务器发 200 字节的响应，seq = 301（301～500），顺带确认 ack = 201：101～200 全收到了。确认搭在数据报文上一起发，叫捎带确认。" },
    { dir: "C", flags: "ACK", seq: 201, ack: 501, len: 0, sender: null, receiver: null,
      say: "⑥ 客户端确认 ack = 501：301～500 全收到了，下一个要 501。" },
  ];
  const TEARDOWN = [
    { dir: "C", flags: "FIN+ACK", seq: 201, ack: 501, sender: "FIN_WAIT_1", receiver: "CLOSE_WAIT",
      say: "⑦ 客户端没有要发的了，发 FIN，seq = 201，进入 FIN_WAIT_1。服务器收到后进入 CLOSE_WAIT。FIN 也占一个序号。" },
    { dir: "S", flags: "ACK", seq: 501, ack: 202, sender: null, receiver: "FIN_WAIT_2",
      say: "⑧ 服务器先回 ACK，ack = 202（FIN 占了 201）。客户端收到后进入 FIN_WAIT_2。此时只关了客户端→服务器这个方向（半关闭），服务器还能继续发数据。" },
    { dir: "S", flags: "FIN+ACK", seq: 501, ack: 202, sender: "LAST_ACK", receiver: "TIME_WAIT",
      say: "⑨ 服务器的程序也调用 close，发 FIN，seq = 501，进入 LAST_ACK。客户端收到后进入 TIME_WAIT。" },
    { dir: "C", flags: "ACK", seq: 202, ack: 502, sender: null, receiver: "CLOSED",
      say: "⑩ 客户端回最后一个 ACK，ack = 502。服务器收到后 CLOSED；客户端还要在 TIME_WAIT 里等 2MSL 才 CLOSED（见第 9 节）。" },
  ];
  const LOST = [
    HANDSHAKE[0],
    { ...HANDSHAKE[1], lost: true, receiver: null,
      say: "② 服务器回的 SYN+ACK（seq = 300，ack = 101）在路上丢了。客户端还在 SYN_SENT 干等，服务器停在 SYN_RCVD，它发出 SYN+ACK 时启动了重传计时器。" },
    { ...HANDSHAKE[1], retrans: true,
      say: "③ 服务器的重传计时器到期，一直没等到 ACK，于是重发同一个 SYN+ACK，seq 和 ack 都不变（还是 300 / 101）。这次到了，客户端进入 ESTABLISHED。" },
    { ...HANDSHAKE[2], say: "④ 客户端回 ACK：seq = 101，ack = 301。服务器进入 ESTABLISHED。丢一个报文只是慢了一个超时时间，连接照样建立。" },
  ];

  const START = {
    handshake: ["CLOSED", "LISTEN", "客户端 CLOSED；服务器的网店程序已经在 443 端口上监听（LISTEN）。"],
    data: ["ESTABLISHED", "ESTABLISHED", "连接已经建好（接着三次握手：客户端下一个序号 101，服务器下一个序号 301）。"],
    teardown: ["ESTABLISHED", "ESTABLISHED", "数据传完了（客户端下一个序号 201，服务器下一个序号 501），由客户端先关闭。"],
  };

  function build(start, messages) {
    let [c, s, say] = START[start];
    const shown = [];
    const frames = [{ msgs: [], c, s, c0: c, s0: s, say }];
    for (const m of messages) {
      const fromC = m.dir === "C";
      if (m.sender) fromC ? (c = m.sender) : (s = m.sender);
      if (!m.lost && m.receiver) fromC ? (s = m.receiver) : (c = m.receiver);
      shown.push({ ...m, cAfter: c, sAfter: s });
      frames.push({ msgs: [...shown], c, s, c0: frames[0].c0, s0: frames[0].s0, say: m.say });
    }
    return frames;
  }

  const CX = 170, SX = 470, TOP = 46, STEP = 46, DROP = 32;
  function label(m) {
    let t = `${m.flags} seq=${m.seq}`;
    if (m.ack != null) t += ` ack=${m.ack}`;
    if (m.len) t += ` [${m.len} 字节]`;
    return t;
  }
  function timeline(frame) {
    const n = Math.max(frame.msgs.length, 3);
    const height = TOP + n * STEP + 20;
    const svg = svgEl("svg", { class: "seq-chart", viewBox: `0 0 640 ${height}`, width: 640 });
    svg.append(svgEl("text", { x: CX, y: 18, "text-anchor": "middle", class: "title" }, "客户端 :52000"));
    svg.append(svgEl("text", { x: SX, y: 18, "text-anchor": "middle", class: "title" }, "服务器 :443"));
    svg.append(svgEl("line", { x1: CX, y1: 28, x2: CX, y2: height - 6, class: "line" }));
    svg.append(svgEl("line", { x1: SX, y1: 28, x2: SX, y2: height - 6, class: "line" }));
    svg.append(svgEl("text", { x: CX - 8, y: 32, "text-anchor": "end", class: "small mono" }, frame.c0));
    svg.append(svgEl("text", { x: SX + 8, y: 32, class: "small mono" }, frame.s0));
    frame.msgs.forEach((m, i) => {
      const latest = i === frame.msgs.length - 1;
      const y1 = TOP + i * STEP, y2 = y1 + DROP;
      const [xa, xb] = m.dir === "C" ? [CX, SX] : [SX, CX];
      const g = svgEl("g", { class: "msg" + (m.lost ? " lost" : "") + (latest ? " latest" : "") });
      const cls = m.lost ? "arrow-red" : latest ? "arrow-hot" : "arrow-blue";
      const marker = m.lost ? "" : latest ? "url(#arrow-hot)" : "url(#arrow-blue)";
      const xEnd = m.lost ? (xa + xb) / 2 : xb + (xb > xa ? -2 : 2);
      const yEnd = m.lost ? (y1 + y2) / 2 : y2;
      const line = svgEl("line", { x1: xa, y1, x2: xEnd, y2: yEnd, class: cls });
      if (marker) line.setAttribute("marker-end", marker);
      if (m.lost) line.setAttribute("stroke-dasharray", "6 4");
      g.append(line);
      if (m.lost) g.append(svgEl("text", { x: xEnd, y: yEnd + 22, "text-anchor": "middle", class: "lost-mark" }, "✗"));
      const angle = Math.atan2(y2 - y1, xb - xa) * 180 / Math.PI;
      const mx = (xa + xb) / 2, my = (y1 + y2) / 2;
      const rot = xb > xa ? angle : angle + 180;
      g.append(svgEl("text", { x: mx, y: my - 6, "text-anchor": "middle", class: "mono msg-label", transform: `rotate(${rot} ${mx} ${my})` },
        (m.retrans ? "重发 " : "") + label(m) + (m.lost ? "（丢失）" : "")));
      // 两侧标出这一步之后的状态（有变化才标）
      const before = i === 0 ? [frame.c0, frame.s0] : [frame.msgs[i - 1].cAfter, frame.msgs[i - 1].sAfter];
      if (m.cAfter !== before[0]) g.append(svgEl("text", { x: CX - 8, y: m.dir === "C" ? y1 + 4 : y2 + 4, "text-anchor": "end", class: "small mono" }, m.cAfter));
      if (m.sAfter !== before[1]) g.append(svgEl("text", { x: SX + 8, y: m.dir === "S" ? y1 + 4 : y2 + 4, class: "small mono" }, m.sAfter));
      svg.append(g);
    });
    return svg;
  }

  function render(frame) {
    return [
      el("div", { class: "row" },
        el("span", { class: "label" }, "客户端状态："), box(frame.c, "client-state state-" + frame.c),
        el("span", { class: "label" }, "　服务器状态："), box(frame.s, "server-state state-" + frame.s)),
      timeline(frame),
    ];
  }

  const player = new Player(root, render);
  const SCENES = {
    "三次握手": () => build("handshake", HANDSHAKE),
    "传一段数据": () => build("data", DATA),
    "四次挥手": () => build("teardown", TEARDOWN),
    "完整过程": () => build("handshake", [...HANDSHAKE, ...DATA, ...TEARDOWN]),
    "握手时第二个报文丢失": () => build("handshake", LOST),
  };
  root.prepend(el("div", { class: "ops-bar" },
    ...Object.entries(SCENES).map(([name, make]) => el("button", { onclick: () => player.load(make()) }, name))));
  player.load([{ msgs: [], c: "CLOSED", s: "LISTEN", c0: "CLOSED", s0: "LISTEN", say: "点上面的按钮，看报文一个个发出去。建议先点「三次握手」。" }]);
})();

// ---------- 动画二：拥塞窗口 ----------
(() => {
  const root = document.getElementById("cwnd");
  const ROUNDS = 20;

  // 按 TCP Reno 逐轮算 cwnd。event 发生在第 at 轮（用这一轮的 cwnd 算新 ssthresh）
  function simulate(ssthresh0, event, at) {
    const rows = [];
    let cwnd = 1, ssthresh = ssthresh0;
    for (let r = 1; r <= ROUNDS; r++) {
      const phase = cwnd < ssthresh ? "慢启动" : "拥塞避免";
      const row = { r, cwnd, ssthresh, phase, event: null };
      if (event && r === at) {
        const next = Math.max(Math.floor(cwnd / 2), 2);
        row.event = event;
        row.say = event === "timeout"
          ? `第 ${r} 轮：cwnd = ${cwnd} 时超时。ssthresh = ${cwnd} / 2 = ${next}，cwnd 回到 1，下一轮重新慢启动。`
          : `第 ${r} 轮：cwnd = ${cwnd} 时收到 3 个重复 ACK。ssthresh = ${cwnd} / 2 = ${next}，cwnd = ssthresh = ${next}，下一轮直接拥塞避免（快恢复）。`;
        ssthresh = next;
        cwnd = event === "timeout" ? 1 : next;
      } else {
        const grow = cwnd < ssthresh ? Math.min(cwnd * 2, ssthresh) : cwnd + 1;
        row.say = cwnd < ssthresh
          ? `第 ${r} 轮：cwnd = ${cwnd} < ssthresh = ${row.ssthresh}，慢启动，下一轮翻倍${grow < cwnd * 2 ? `，但不超过 ssthresh，所以是 ${grow}` : `为 ${grow}`}。`
          : `第 ${r} 轮：cwnd = ${cwnd} ≥ ssthresh = ${row.ssthresh}，拥塞避免，下一轮只加 1，为 ${grow}。`;
        cwnd = grow;
      }
      rows.push(row);
    }
    return rows;
  }

  function chart(rows, upto) {
    const W = 600, H = 270, L = 46, R = 586, T = 16, B = 230;
    const top = Math.max(...rows.map(x => Math.max(x.cwnd, x.ssthresh))) + 2;
    const X = r => L + (r - 1) * (R - L) / (ROUNDS - 1);
    const Y = v => B - v * (B - T) / top;
    const svg = svgEl("svg", { class: "cwnd-chart", viewBox: `0 0 ${W} ${H}`, width: W });
    svg.append(svgEl("line", { x1: L, y1: B, x2: R + 8, y2: B, class: "line" }));
    svg.append(svgEl("line", { x1: L, y1: B, x2: L, y2: T - 6, class: "line" }));
    const step = top > 40 ? 10 : 5;
    for (let v = 0; v <= top; v += step) {
      svg.append(svgEl("text", { x: L - 6, y: Y(v) + 4, "text-anchor": "end", class: "small" }, v));
      if (v) svg.append(svgEl("line", { x1: L, y1: Y(v), x2: R, y2: Y(v), stroke: "#eee" }));
    }
    for (let r = 1; r <= ROUNDS; r++) svg.append(svgEl("text", { x: X(r), y: B + 16, "text-anchor": "middle", class: "small" }, r));
    svg.append(svgEl("text", { x: (L + R) / 2, y: B + 34, "text-anchor": "middle", class: "small" }, "轮次（每轮 = 一个 RTT）"));
    svg.append(svgEl("text", { x: L + 4, y: T - 4, class: "small" }, "cwnd（报文段个数）"));
    const shown = rows.slice(0, upto);
    if (!shown.length) return svg;
    // ssthresh：阶梯虚线
    let d = "";
    shown.forEach((x, i) => { d += `${i ? "L" : "M"}${X(x.r) - (i ? 0 : 0)},${Y(x.ssthresh)} `; if (i < shown.length - 1 && shown[i + 1].ssthresh !== x.ssthresh) d += `L${X(x.r) + (X(2) - X(1)) / 2},${Y(x.ssthresh)} L${X(x.r) + (X(2) - X(1)) / 2},${Y(shown[i + 1].ssthresh)} `; });
    svg.append(svgEl("path", { d, class: "dash ssthresh-line" }));
    svg.append(svgEl("polyline", { points: shown.map(x => `${X(x.r)},${Y(x.cwnd)}`).join(" "), class: "arrow-blue" }));
    shown.forEach((x, i) => {
      const last = i === shown.length - 1;
      svg.append(svgEl("circle", { cx: X(x.r), cy: Y(x.cwnd), r: last ? 5 : 3, class: x.event ? "bad" : last ? "hot" : "obj" }));
      if (x.event) svg.append(svgEl("text", { x: X(x.r), y: Y(x.cwnd) - 10, "text-anchor": "middle", class: "small event-mark" }, x.event === "timeout" ? "超时" : "3 个重复 ACK"));
    });
    const cur = shown[shown.length - 1];
    svg.append(svgEl("text", { x: X(cur.r) - 8, y: Y(cur.cwnd) - 10, "text-anchor": "end", class: "small" }, cur.cwnd));
    return svg;
  }

  function render(frame) {
    const cur = frame.upto ? frame.rows[frame.upto - 1] : null;
    return [
      el("div", { class: "row" },
        el("span", { class: "label" }, "轮次："), box(cur ? cur.r : "—", "round-value"),
        el("span", { class: "label" }, "　cwnd ="), box(cur ? cur.cwnd : "—", "cwnd-value hot"),
        el("span", { class: "label" }, "　ssthresh ="), box(cur ? cur.ssthresh : frame.rows[0].ssthresh, "ssthresh-value"),
        el("span", { class: "label" }, "　阶段："), box(cur ? cur.phase : "—", "phase")),
      chart(frame.rows, frame.upto),
    ];
  }

  const player = new Player(root, render);
  const ssInput = el("input", { type: "number", value: "16", min: "2", max: "64", "aria-label": "初始 ssthresh" });
  const atInput = el("input", { type: "number", value: "12", min: "1", max: String(ROUNDS - 1), "aria-label": "出事的轮次" });
  const params = () => [Math.min(64, Math.max(2, Number(ssInput.value) || 16)), Math.min(ROUNDS - 1, Math.max(1, Number(atInput.value) || 12))];
  const run = event => () => {
    const [ss, at] = params();
    const rows = simulate(ss, event, at);
    const head = event === "timeout" ? `第 ${at} 轮超时` : event === "dup3" ? `第 ${at} 轮收到 3 个重复 ACK` : "一直不出事";
    const frames = [{ rows, upto: 0, say: `初始 cwnd = 1，ssthresh = ${ss}，${head}。一帧走一轮。` }];
    rows.forEach((x, i) => frames.push({ rows, upto: i + 1, say: x.say }));
    player.load(frames);
  };
  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: run(null) }, "正常增长"),
    el("button", { onclick: run("timeout") }, "第 N 轮超时"),
    el("button", { onclick: run("dup3") }, "第 N 轮收到 3 个重复 ACK"),
    el("span", { class: "label" }, "初始 ssthresh ="), ssInput,
    el("span", { class: "label" }, "N ="), atInput));
  player.load([{ rows: simulate(16, null, 0), upto: 0, say: "点上面的按钮。可以先改初始 ssthresh 和出事的轮次 N。" }]);
})();
