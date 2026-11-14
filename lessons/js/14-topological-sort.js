// 动画：Kahn 算法给课程表排序。图用 SVG 画，节点下面的橙色数字是当前入度。
(() => {
  const root = document.getElementById("topo");
  const W = 96, H = 48;
  const NODES = [
    { name: "微积分", x: 10, y: 10 },
    { name: "编程入门", x: 10, y: 110 },
    { name: "数据结构", x: 160, y: 10 },
    { name: "数据库", x: 160, y: 110 },
    { name: "算法", x: 310, y: 10 },
    { name: "毕设", x: 460, y: 60 },
  ];
  const DAG = [[0, 2], [1, 2], [1, 3], [2, 4], [3, 5], [4, 5]];
  const CYCLE = [...DAG, [5, 1]];  // 编程入门要先修毕设：1 → 3 → 5 → 1 成环
  const name = i => NODES[i].name;

  function svg(tag, attrs, ...kids) {
    const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
    e.append(...kids);
    return e;
  }

  function edgePath([u, v]) {
    const a = NODES[u], b = NODES[v];
    if (b.x < a.x) {  // 往回指的边：从下面绕过去
      const sx = a.x + W / 2, sy = a.y + H, ex = b.x + W / 2, ey = b.y + H + 4;
      return `M${sx},${sy} Q${(sx + ex) / 2},270 ${ex},${ey}`;
    }
    const dy = Math.sign(a.y - b.y) * 12;  // 多条边指向同一个点时，落点上下错开
    return `M${a.x + W},${a.y + H / 2} L${b.x - 2},${b.y + H / 2 + dy}`;
  }

  function render(f) {
    const g = svg("svg", { class: "graph", width: 570, height: 215, viewBox: "0 0 570 215" },
      svg("defs", {},
        svg("marker", { id: "ah", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto" },
          svg("path", { d: "M0,0 L10,5 L0,10 z", fill: "#555" })),
        svg("marker", { id: "ah-gone", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto" },
          svg("path", { d: "M0,0 L10,5 L0,10 z", fill: "#ccc" }))));
    f.edges.forEach((e, k) => {
      const gone = f.gone.includes(k);
      g.append(svg("path", { class: "edge" + (gone ? " gone" : ""), d: edgePath(e), "marker-end": `url(#ah${gone ? "-gone" : ""})` }));
    });
    NODES.forEach((n, i) => {
      const cls = ["gnode", f.order.includes(i) && i !== f.cur && "done", f.queue.includes(i) && "queued",
        i === f.cur && "cur", i === f.drop && "drop"].filter(Boolean).join(" ");
      g.append(svg("g", { class: cls, "data-node": n.name },
        svg("rect", { x: n.x, y: n.y, width: W, height: H, rx: 4 }),
        svg("text", { x: n.x + W / 2, y: n.y + 20 }, n.name),
        svg("text", { class: "deg", x: n.x + W / 2, y: n.y + 40 }, `入度 ${f.indeg[i]}`)));
    });
    const line = (label, cls, ids, hot) => el("div", { class: "row " + cls },
      el("span", { class: "label" }, label),
      ids.length ? ids.map(i => box(name(i), hot ? "hot" : "")) : el("span", { class: "label" }, "（空）"));
    return [g, line("队列：", "queue", f.queue, true), line("结果：", "order", f.order, false)];
  }

  const player = new Player(root, render);

  function kahn(edges) {
    const n = NODES.length;
    const indeg = Array(n).fill(0), gone = [], order = [];
    let queue = [], cur = null, drop = null;
    const fr = [];
    const snap = say => fr.push({ say, edges, gone: [...gone], indeg: [...indeg], queue: [...queue], order: [...order], cur, drop });

    for (const [, v] of edges) indeg[v]++;
    snap("先数每门课的入度（有几条边指向它）= 还差几门先修课。");
    queue = indeg.map((d, i) => d === 0 ? i : null).filter(i => i !== null);
    snap(`入度为 0 的课现在就能学，全部入队：${queue.map(name).join("、") || "一门都没有"}。`);
    while (queue.length) {
      cur = queue.shift();
      drop = null;
      order.push(cur);
      snap(`${name(cur)} 出队，排进结果。`);
      edges.forEach(([u, v], k) => {
        if (u !== cur) return;
        indeg[v]--;
        gone.push(k);
        drop = v;
        if (indeg[v] === 0) {
          queue.push(v);
          snap(`划掉 ${name(cur)} → ${name(v)}：${name(v)} 的入度降到 0，先修课学完了，入队。`);
        } else {
          snap(`划掉 ${name(cur)} → ${name(v)}：${name(v)} 的入度减 1，还剩 ${indeg[v]}。`);
        }
      });
      drop = null;
    }
    cur = null;
    if (order.length === NODES.length) {
      snap(`队列空了，${order.length} 门课全排完：这就是一个合法的拓扑序。`);
    } else {
      snap(`队列空了，却只排了 ${order.length} 门，还剩 ${NODES.length - order.length} 门入度减不到 0：图里有环，抛 ValueError。`);
    }
    return fr;
  }

  const show = (edges, say) => player.load([{ say, edges, gone: [], indeg: Array(NODES.length).fill("?"), queue: [], order: [], cur: null, drop: null }]);

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(kahn(DAG)) }, "排序（无环）"),
    el("button", { onclick: () => player.load(kahn(CYCLE)) }, "排序（有环）"),
    el("button", { onclick: () => show(DAG, "一张课程依赖图。点上面的按钮开始排序。") }, "重置")));
  show(DAG, "一张课程依赖图。点上面的按钮开始排序。");
})();
