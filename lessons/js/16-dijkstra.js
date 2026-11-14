// 动画：从 A 出发跑 Dijkstra。图用 SVG 画，边上的数字是权重；下面是 dist 表和最小堆。
(() => {
  const root = document.getElementById("dijkstra");
  const R = 22;
  const NODES = [
    { name: "A", x: 40, y: 100 },
    { name: "B", x: 200, y: 30 },
    { name: "C", x: 200, y: 170 },
    { name: "D", x: 360, y: 100 },
    { name: "E", x: 500, y: 100 },
  ];
  const EDGES = [[0, 1, 4], [0, 2, 1], [2, 1, 2], [1, 3, 1], [2, 3, 2], [3, 4, 3]];  // 无向边 (u, v, 权重)
  const name = i => NODES[i].name;
  const show = d => d === Infinity ? "∞" : String(d);

  function svg(tag, attrs, ...kids) {
    const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
    e.append(...kids);
    return e;
  }

  function render(f) {
    const g = svg("svg", { class: "graph", width: 540, height: 200, viewBox: "0 0 540 200" });
    EDGES.forEach(([u, v, w], k) => {
      const a = NODES[u], b = NODES[v];
      const cls = "edge" + (k === f.edge ? (f.better ? " relax" : " nope") : "");
      g.append(svg("line", { class: cls, "data-edge": name(u) + name(v), x1: a.x, y1: a.y, x2: b.x, y2: b.y }),
        svg("text", { class: "w", x: (a.x + b.x) / 2 + (a.x === b.x ? 12 : 0), y: (a.y + b.y) / 2 - 6 }, String(w)));
    });
    NODES.forEach((n, i) => {
      const cls = ["gnode", f.done.includes(i) && "done", i === f.cur && "cur"].filter(Boolean).join(" ");
      g.append(svg("g", { class: cls, "data-node": n.name },
        svg("circle", { cx: n.x, cy: n.y, r: R }),
        svg("text", { x: n.x, y: n.y + 5 }, n.name)));
    });
    const table = el("div", { class: "row dist" }, el("span", { class: "label" }, "dist："),
      NODES.map((n, i) => el("span", { class: "box" + (i === f.changed ? " hot" : "") + (f.done.includes(i) ? " fixed" : ""), "data-dist": n.name },
        `${n.name}: ${show(f.dist[i])}`)));
    const heap = el("div", { class: "row heap" }, el("span", { class: "label" }, "最小堆（小 → 大）："),
      f.heap.length ? f.heap.map(([d, i]) => box(`(${d}, ${name(i)})`, "small")) : el("span", { class: "label" }, "（空）"));
    return [g, table, heap];
  }

  const player = new Player(root, render);

  function run() {
    const n = NODES.length;
    const dist = Array(n).fill(Infinity), done = [];
    let heap = [], cur = null, edge = null, better = false, changed = null;
    const fr = [];
    const snap = say => fr.push({ say, dist: [...dist], done: [...done], heap: [...heap].sort((p, q) => p[0] - q[0] || p[1] - q[1]), cur, edge, better, changed });
    const push = (d, i) => heap.push([d, i]);

    dist[0] = 0;
    push(0, 0);
    changed = 0;
    snap("起点 A 的 dist 设为 0，其余都是 ∞；把 (0, A) 放进堆。");
    while (heap.length) {
      heap.sort((p, q) => p[0] - q[0] || p[1] - q[1]);
      const [d, u] = heap.shift();
      edge = null; changed = null; cur = u;
      if (done.includes(u)) {
        snap(`取出 (${d}, ${name(u)})，可 ${name(u)} 早就确定了（${dist[u]}）：这是过期的旧记录，跳过。`);
        continue;
      }
      done.push(u);
      snap(`取出堆顶 (${d}, ${name(u)})：它是剩下的点里最近的，dist[${name(u)}] = ${d} 就此确定，变绿。`);
      EDGES.forEach(([a, b, w], k) => {
        if (a !== u && b !== u) return;
        const v = a === u ? b : a;
        if (done.includes(v)) return;
        edge = k;
        const nd = d + w;
        if (nd < dist[v]) {
          better = true; changed = v;
          const old = show(dist[v]);
          dist[v] = nd;
          push(nd, v);
          snap(`松弛 ${name(u)}–${name(v)}：${d} + ${w} = ${nd} < ${old}，更新 dist[${name(v)}] = ${nd}，(${nd}, ${name(v)}) 进堆。`);
        } else {
          better = false; changed = null;
          snap(`松弛 ${name(u)}–${name(v)}：${d} + ${w} = ${nd}，不比 ${dist[v]} 小，不更新。`);
        }
      });
      edge = null; changed = null;
    }
    cur = null;
    snap(`堆空了，全部确定：${NODES.map((nd, i) => `${nd.name}=${dist[i]}`).join("，")}。`);
    return fr;
  }

  const reset = () => player.load([{ say: "一张带权无向图。点“从 A 出发”开始。", dist: Array(NODES.length).fill(Infinity), done: [], heap: [], cur: null, edge: null, better: false, changed: null }]);

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(run()) }, "从 A 出发"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
