// 动画：Kruskal 给 6 个村子修路。图用 SVG 画；下面是按权排好的边列表和当前的连通块（并查集）。
(() => {
  const root = document.getElementById("kruskal");
  const NODES = [
    { name: "A", x: 60, y: 40 }, { name: "B", x: 220, y: 40 }, { name: "C", x: 380, y: 40 },
    { name: "D", x: 60, y: 180 }, { name: "E", x: 220, y: 180 }, { name: "F", x: 380, y: 180 },
  ];
  // (w, u, v)，故意打乱顺序，动画第一步先排序
  const FULL = [[4, 0, 1], [6, 1, 2], [2, 0, 3], [5, 1, 3], [3, 1, 4], [1, 4, 2], [7, 3, 4], [8, 2, 5], [9, 4, 5]];
  const SPLIT = FULL.filter(([, u, v]) => u !== 5 && v !== 5);  // F 没有路
  const name = i => NODES[i].name;
  const label = ([w, u, v]) => `${name(u)}–${name(v)} ${w}`;

  function svg(tag, attrs, ...kids) {
    const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
    e.append(...kids);
    return e;
  }

  function render(f) {
    const g = svg("svg", { class: "graph", width: 440, height: 220, viewBox: "0 0 440 220" });
    f.edges.forEach((e, k) => {
      const [w, u, v] = e, a = NODES[u], b = NODES[v];
      const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      g.append(svg("g", { class: "edge " + (f.state[k] || ""), "data-edge": label(e) },
        svg("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y }),
        svg("rect", { x: mx - 9, y: my - 10, width: 18, height: 20 }),
        svg("text", { class: "w", x: mx, y: my }, w)));
    });
    NODES.forEach(n => g.append(svg("g", { class: "gnode" },
      svg("circle", { cx: n.x, cy: n.y, r: 18 }), svg("text", { x: n.x, y: n.y }, n.name))));
    const list = el("div", { class: "row elist" }, el("span", { class: "label" }, "边（按权排好）："),
      f.edges.map((e, k) => box(label(e), (f.state[k] === "cur" ? "hot" : f.state[k]) || "")));
    const groups = {};
    NODES.forEach((_, i) => (groups[f.root[i]] ||= []).push(name(i)));
    const blocks = el("div", { class: "row blocks" }, el("span", { class: "label" }, "连通块："),
      Object.values(groups).map(m => box(`{${m.join(", ")}}`)));
    const total = f.edges.reduce((s, [w], k) => s + (f.state[k] === "pick" ? w : 0), 0);
    const picked = f.state.filter(s => s === "pick").length;
    return [g, list, blocks, el("p", { class: "stat" }, `已选 ${picked} / ${NODES.length - 1} 条，总权 = `, el("b", { class: "total" }, total))];
  }

  const player = new Player(root, render);

  function kruskal(input) {
    const n = NODES.length, parent = [...Array(n).keys()];
    const find = x => parent[x] === x ? x : (parent[x] = find(parent[x]));
    const fr = [];
    let edges = input, state = [];
    const snap = say => fr.push({ say, edges, state: [...state], root: parent.map((_, i) => find(i)) });

    snap("一开始每个村子自成一块，边还没排序。");
    edges = [...input].sort((a, b) => a[0] - b[0]);
    snap("① 把边按权从小到大排好。接下来从最便宜的开始，一条条看。");
    let picked = 0;
    for (let k = 0; k < edges.length && picked < n - 1; k++) {
      const [w, u, v] = edges[k];
      state[k] = "cur";
      snap(`考察 ${label(edges[k])}：${name(u)} 和 ${name(v)} 在同一块吗？`);
      if (find(u) !== find(v)) {
        parent[find(u)] = find(v);
        state[k] = "pick";
        picked++;
        snap(`不在同一块，连上不会成环：选中，两块合成一块。`);
      } else {
        state[k] = "skip";
        snap(`${name(u)} 和 ${name(v)} 早就连通了，再加这条边会成环：跳过。`);
      }
    }
    const total = edges.reduce((s, [w], k) => s + (state[k] === "pick" ? w : 0), 0);
    if (picked === n - 1) {
      snap(`已经选够 n − 1 = ${n - 1} 条，提前收工。最小生成树总权 = ${total}。`);
    } else {
      snap(`边全看完了，只选到 ${picked} 条，不够 ${n - 1} 条：图不连通，抛 ValueError。`);
    }
    return fr;
  }

  const show = edges => player.load([{ say: "6 个村子和可以修的路，数字是造价。点上面的按钮开始。",
    edges, state: [], root: NODES.map((_, i) => i) }]);

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(kruskal(FULL)) }, "开始 Kruskal"),
    el("button", { onclick: () => player.load(kruskal(SPLIT)) }, "不连通的图"),
    el("button", { onclick: () => show(FULL) }, "重置")));
  show(FULL);
})();
