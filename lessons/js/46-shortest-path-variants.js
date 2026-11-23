// 动画：主线例子“收费站”。五座城，边权 1 = 收费路（实线），0 = 免费路（虚线）。
// 0-1 BFS：deque 从队头取；走 0 边变短的邻居插到队头，走 1 边的排到队尾；出队时才确定。
// Floyd：一个一个放开中转站 k，对每一对 (i, j) 试 dist[i][k] + dist[k][j]。
(() => {
  const root = document.getElementById("variants");
  const R = 22;
  const NODES = [
    { name: "A", x: 40, y: 100 },
    { name: "B", x: 200, y: 30 },
    { name: "C", x: 200, y: 170 },
    { name: "D", x: 380, y: 30 },
    { name: "E", x: 380, y: 170 },
  ];
  const EDGES = [[0, 1, 1], [0, 2, 0], [2, 1, 0], [1, 3, 1], [2, 4, 1], [3, 4, 0]];  // 无向边 (u, v, 过路费)
  const COUNT = NODES.length;
  const name = i => NODES[i].name;
  const show = d => (d === Infinity ? "∞" : String(d));
  // 邻接表，按边的顺序排，和讲解页 toll_roads 的顺序一致
  const ADJACENT = NODES.map((_, u) => EDGES.flatMap(([a, b, w], k) => (a === u ? [[b, w, k]] : b === u ? [[a, w, k]] : [])));

  function svg(tag, attrs, ...kids) {
    const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
    e.append(...kids);
    return e;
  }

  function drawGraph(f) {
    const g = svg("svg", { class: "graph", width: 420, height: 200, viewBox: "0 0 420 200" });
    EDGES.forEach(([u, v, w], k) => {
      const a = NODES[u], b = NODES[v];
      const cls = "edge" + (w === 0 ? " free" : "") + (k === f.edge ? (f.better ? " relax" : " nope") : "");
      g.append(svg("line", { class: cls, "data-edge": name(u) + name(v), x1: a.x, y1: a.y, x2: b.x, y2: b.y }),
        svg("text", { class: "w" + (w === 0 ? " free" : ""), x: (a.x + b.x) / 2 + (a.x === b.x ? 14 : 0), y: (a.y + b.y) / 2 - 6 }, String(w)));
    });
    NODES.forEach((n, i) => {
      const cls = ["gnode", f.done.includes(i) && "done", i === f.cur && "cur", i === f.middle && "middle"].filter(Boolean).join(" ");
      g.append(svg("g", { class: cls, "data-node": n.name },
        svg("circle", { cx: n.x, cy: n.y, r: R }),
        svg("text", { x: n.x, y: n.y + 5 }, n.name)));
    });
    return g;
  }

  function render(f) {
    const parts = [drawGraph(f)];
    if (f.mode === "bfs") {
      parts.push(el("div", { class: "row dist" }, el("span", { class: "label" }, "dist："),
        NODES.map((n, i) => el("span", { class: "box" + (i === f.changed ? " hot" : "") + (f.done.includes(i) ? " fixed" : ""), "data-dist": n.name },
          `${n.name}: ${show(f.dist[i])}`))));
      parts.push(el("div", { class: "row deque" }, el("span", { class: "label" }, "deque（队头 → 队尾）："),
        f.queue.length ? f.queue.map(([d, i, side]) => box(`(${d}, ${name(i)})`, `small ${side}`)) : el("span", { class: "label" }, "（空）")));
    }
    if (f.mode === "floyd") {
      const isChanged = (i, j) => f.changed.some(([a, b]) => a === i && b === j);
      parts.push(el("table", { class: "matrix" },
        el("tr", {}, el("th", {}, "dist"), NODES.map(n => el("th", {}, n.name))),
        NODES.map((n, i) => el("tr", {}, el("th", {}, n.name),
          NODES.map((m, j) => el("td", { class: isChanged(i, j) ? "changed" : (f.middle !== null && (i === f.middle || j === f.middle) ? "via" : ""),
            "data-cell": n.name + m.name }, show(f.table[i][j])))))));
    }
    return parts;
  }

  const player = new Player(root, render);

  function bfsFrames() {
    const dist = Array(COUNT).fill(Infinity), done = [];
    let queue = [], cur = null, edge = null, better = false, changed = null;
    const frames = [];
    const snap = say => frames.push({ mode: "bfs", say, dist: [...dist], done: [...done], queue: queue.map(item => [...item]),
      cur, edge, better, changed, middle: null });

    dist[0] = 0;
    queue.push([0, 0, "back"]);
    changed = 0;
    snap("起点 A 的 dist 设为 0，其余都是 ∞；把 (0, A) 放进 deque。");
    while (queue.length) {
      const [d, u] = queue.shift();
      edge = null; changed = null; cur = u;
      if (done.includes(u)) {
        snap(`从队头取出 (${d}, ${name(u)})，可 ${name(u)} 早就确定成 ${dist[u]} 了：这是过期记录，跳过。`);
        continue;
      }
      done.push(u);
      snap(`从队头取出 (${d}, ${name(u)})：队头永远是最近的，dist[${name(u)}] = ${d} 就此确定，变绿。`);
      for (const [v, w, k] of ADJACENT[u]) {
        if (done.includes(v)) continue;
        edge = k;
        const candidate = d + w;
        if (candidate < dist[v]) {
          better = true; changed = v;
          const old = show(dist[v]);
          dist[v] = candidate;
          if (w === 0) {
            queue.unshift([candidate, v, "front"]);
            snap(`${name(u)}–${name(v)} 是免费路（0）：${d} + 0 = ${candidate} < ${old}，更新 dist[${name(v)}]。和 ${name(u)} 一样近，插到队头（appendleft，绿框）。`);
          } else {
            queue.push([candidate, v, "back"]);
            snap(`${name(u)}–${name(v)} 是收费路（1）：${d} + 1 = ${candidate} < ${old}，更新 dist[${name(v)}]。远一层，排到队尾（append，蓝框）。`);
          }
        } else {
          better = false; changed = null;
          snap(`${name(u)}–${name(v)}：${d} + ${w} = ${candidate}，不比 ${dist[v]} 小，不更新。`);
        }
      }
      edge = null; changed = null;
    }
    cur = null;
    snap(`deque 空了，全部确定：${NODES.map((n, i) => `${n.name}=${dist[i]}`).join("，")}。每个点、每条边只处理常数次，O(V + E)。`);
    return frames;
  }

  function initialTable() {
    const table = NODES.map((_, i) => NODES.map((_, j) => (i === j ? 0 : Infinity)));
    for (const [u, v, w] of EDGES) { table[u][v] = w; table[v][u] = w; }
    return table;
  }

  function floydFrames() {
    const table = initialTable();
    const frames = [];
    const snap = (say, middle, changed = [], cur = null) => frames.push({ mode: "floyd", say, table: table.map(row => [...row]),
      middle, changed, cur, done: [], edge: null, better: false });
    snap("初始表：对角线 0，有路直达填过路费，没有直达填 ∞。现在还不准中途经过任何城。", null);
    for (let k = 0; k < COUNT; k++) {
      snap(`放开中转站 k = ${name(k)}：对每一对 (i, j)，试 dist[i][${name(k)}] + dist[${name(k)}][j] 能不能更小。浅橙色是这一轮要用到的第 ${name(k)} 行、第 ${name(k)} 列。`, k);
      const changedThisRound = [];
      for (let i = 0; i < COUNT; i++) {
        for (let j = 0; j < COUNT; j++) {
          const through = table[i][k] + table[k][j];
          if (through < table[i][j]) {
            const old = show(table[i][j]);
            table[i][j] = through;
            changedThisRound.push([i, j]);
            snap(`dist[${name(i)}][${name(k)}] + dist[${name(k)}][${name(j)}] = ${table[i][k]} + ${table[k][j]} = ${through} < ${old}：`
              + `${name(i)} → ${name(k)} → ${name(j)} 更近，dist[${name(i)}][${name(j)}] 改成 ${through}。`, k, [[i, j]]);
          }
        }
      }
      snap(changedThisRound.length
        ? `k = ${name(k)} 这一轮改了 ${changedThisRound.length} 格（深橙色）。`
        : `k = ${name(k)} 这一轮没有任何一格能经过 ${name(k)} 变近，表不变。`, k, changedThisRound);
    }
    snap("五个中转站都放开了，表里就是任意两城之间最少过几次收费站：A、B、C 互相 0，D、E 之间 0，两组之间 1。三重循环，O(n³)。", null);
    return frames;
  }

  const reset = () => player.load([{ mode: "bfs", say: "五座城，虚线是免费路（0），实线是收费路（1）。点上面的按钮开始。",
    dist: Array(COUNT).fill(Infinity), done: [], queue: [], cur: null, edge: null, better: false, changed: null, middle: null }]);

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(bfsFrames()) }, "0-1 BFS 从 A 出发"),
    el("button", { onclick: () => player.load(floydFrames()) }, "Floyd：逐个放开中转站"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
