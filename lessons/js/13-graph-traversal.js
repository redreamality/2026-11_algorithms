// 动画：在一张 6 个点的小图上做 BFS / DFS。点按状态染色，旁边显示队列（或递归栈）和访问顺序。
(() => {
  const root = document.getElementById("graph");
  const POS = [[40, 100], [130, 35], [130, 165], [220, 100], [320, 35], [320, 165]];
  const EDGES = [[0, 1], [0, 2], [1, 3], [2, 3], [3, 4], [3, 5], [4, 5]];
  const G = POS.map(() => []);
  for (const [u, v] of EDGES) { G[u].push(v); G[v].push(u); }  // 邻居按加边顺序排

  let st;

  function snap(say) {
    return { say, state: [...st.state], dist: [...st.dist], tree: [...st.tree], box: [...st.box], order: [...st.order], kind: st.kind };
  }

  function sv(tag, attrs, ...children) {
    const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    e.append(...children);
    return e;
  }

  function render(f) {
    const isTree = (u, v) => f.tree.some(([a, b]) => (a === u && b === v) || (a === v && b === u));
    const svg = sv("svg", { class: "graph", width: 380, height: 200, viewBox: "0 0 380 200" },
      ...EDGES.map(([u, v]) => sv("line", { x1: POS[u][0], y1: POS[u][1], x2: POS[v][0], y2: POS[v][1], class: isTree(u, v) ? "tree" : "" })),
      ...POS.map(([x, y], i) => sv("g", { class: "vertex " + f.state[i], "data-id": i },
        sv("circle", { cx: x, cy: y, r: 18 }),
        sv("text", { x, y }, String(i)),
        f.dist[i] != null ? sv("text", { x: x + 23, y, class: "dist" }, "d=" + f.dist[i]) : "")));
    const name = f.kind === "bfs" ? "队列（左边出，右边进）：" : "递归栈（右边是栈顶）：";
    return [
      svg,
      el("div", { class: "row queue" }, el("span", { class: "label" }, name),
        f.box.length ? f.box.map(v => box(v, "small")) : el("span", { class: "label" }, "空")),
      el("div", { class: "row order" }, el("span", { class: "label" }, "访问顺序："), f.order.map(v => box(v, "small"))),
    ];
  }

  const player = new Player(root, render);

  function fresh(kind) {
    st = { kind, state: POS.map(() => ""), dist: POS.map(() => null), tree: [], box: [], order: [] };
  }

  function bfs(fr, s) {
    st.state[s] = "frontier";
    st.dist[s] = 0;
    st.box.push(s);
    fr.push(snap(`起点 ${s} 入队，马上标记为“见过”，距离 d=0。`));
    while (st.box.length) {
      const u = st.box.shift();
      st.state[u] = "cur";
      st.order.push(u);
      fr.push(snap(`出队 ${u}（d=${st.dist[u]}）。按顺序看它的邻居 ${G[u].join("、")}。`));
      for (const v of G[u]) {
        if (st.state[v]) { fr.push(snap(`${v} 已经见过，跳过。`)); continue; }
        st.state[v] = "frontier";
        st.dist[v] = st.dist[u] + 1;
        st.tree.push([u, v]);
        st.box.push(v);
        fr.push(snap(`${v} 没见过：标记、入队，距离 d=${st.dist[v]}。`));
      }
      st.state[u] = "done";
    }
    fr.push(snap(`队列空了，结束。每个点的 d 就是从 ${s} 出发的最少边数。`));
  }

  function dfs(fr, s) {
    function go(u, from) {
      st.state[u] = "cur";
      st.box.push(u);
      st.order.push(u);
      if (from != null) st.tree.push([from, u]);
      fr.push(snap(`访问 ${u}，压栈。按顺序看它的邻居 ${G[u].join("、")}。`));
      for (const v of G[u]) {
        if (st.state[v]) { fr.push(snap(`${u} 的邻居 ${v} 已经见过，跳过。`)); continue; }
        st.state[u] = "frontier";
        go(v, u);
        st.state[u] = "cur";
        fr.push(snap(`回到 ${u}，接着看下一个邻居。`));
      }
      st.box.pop();
      st.state[u] = "done";
      fr.push(snap(`${u} 的邻居都看完了，出栈。`));
    }
    go(s, null);
    fr.push(snap("栈空了，结束。"));
  }

  const start = el("select", { "aria-label": "起点" }, POS.map((_, i) => el("option", { value: i }, String(i))));
  const run = (kind, op) => () => {
    fresh(kind);
    const fr = [snap("开始前：所有点都没见过。")];
    op(fr, Number(start.value));
    player.load(fr);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "起点 ="), start,
    el("button", { onclick: run("bfs", bfs) }, "BFS"),
    el("button", { onclick: run("dfs", dfs) }, "DFS")));
  fresh("bfs");
  player.load([snap("一张 6 个点、7 条边的无向图。选个起点，点 BFS 或 DFS。")]);
})();
