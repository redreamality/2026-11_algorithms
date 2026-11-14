// 动画：fib(n) 的三种算法。朴素递归：红色 = 算过的又算一遍；记忆化：蓝色 = 查 memo 命中，下面的子树被剪掉；填表：一格格填 dp。
(() => {
  const root = document.getElementById("dpmemo");
  const DX = 44, DY = 52;
  let nodes, fr, status, memo, calls;

  // 把 fib(n) 的完整递归树先建出来：叶子从左到右排，父节点放在孩子中间
  function build(n) {
    nodes = [];
    let leaf = 0;
    const make = (k, depth) => {
      const nd = { id: nodes.length, n: k, depth, kids: [] };
      nodes.push(nd);
      if (k >= 2) nd.kids = [make(k - 1, depth + 1), make(k - 2, depth + 1)];
      nd.x = nd.kids.length ? (nd.kids[0].x + nd.kids[1].x) / 2 : (leaf++ + 0.5) * DX;
      return nd;
    };
    make(n, 0);
  }

  function snap(say, { cur = null, dp = null, src = [], memoNew = null } = {}) {
    fr.push({ say, cur, status: [...status], memo: memo && [...memo], memoNew, dp: dp && [...dp], src, calls });
  }

  function svgEl(tag, attrs) {
    const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
    return e;
  }

  function tree(f) {
    const W = Math.max(...nodes.map(nd => nd.x)) + DX / 2;
    const H = (Math.max(...nodes.map(nd => nd.depth)) + 1) * DY;
    const y = nd => nd.depth * DY + DY / 2;
    const svg = svgEl("svg", { width: W, height: H });
    for (const nd of nodes) for (const c of nd.kids) {
      const faint = !f.status[c.id] || f.status[c.id] === "cut";
      svg.append(svgEl("line", { x1: nd.x, y1: y(nd), x2: c.x, y2: y(c), stroke: faint ? "#ddd" : "#999", "stroke-width": 2 }));
    }
    const boxes = nodes.map(nd => {
      const s = f.status[nd.id];
      const cls = { dup: "found", done: "done", hit: "hit", cut: "empty cut" }[s] || (nd.id === f.cur ? "hot" : "empty");
      const b = box(nd.n, cls + (nd.id === f.cur ? " cur" : ""));
      b.style.left = nd.x + "px";
      b.style.top = y(nd) + "px";
      return b;
    });
    return el("div", { class: "tree", style: `width:${W}px;height:${H}px` }, svg, boxes);
  }

  // 一排带下标的格子：memo 或 dp 表
  function cells(name, arr, from, { hot = [], fresh = null } = {}) {
    const items = [];
    for (let i = from; i < arr.length; i++) {
      const cls = i === fresh ? "found" : hot.includes(i) ? "hot" : arr[i] == null ? "empty" : "";
      items.push(el("div", { class: "node" }, el("div", { class: "tag" }, String(i)), box(arr[i] ?? "?", cls)));
    }
    return el("div", { class: "row " + name }, el("span", { class: "label" }, name + " ="), items);
  }

  function render(f) {
    if (f.dp) return [
      cells("dp", f.dp, 0, { hot: f.src, fresh: f.memoNew }),
      el("p", { class: "stat" }, "已填 ", el("b", { class: "calls" }, f.calls), " 格"),
    ];
    return [
      tree(f),
      f.memo && cells("memo", f.memo, 2, { fresh: f.memoNew }),
      el("p", { class: "stat" }, "调用次数 = ", el("b", { class: "calls" }, f.calls)),
    ];
  }

  const player = new Player(root, render);

  function naive(nd, seen) {
    calls++;
    const dup = seen.has(nd.n);
    if (dup) status[nd.id] = "dup";
    let v;
    if (nd.n <= 1) {
      v = nd.n;
      if (!dup) status[nd.id] = "done";
      snap(`fib(${nd.n}) 是基线，直接返回 ${v}。` + (dup ? "（又调了一次）" : ""), { cur: nd.id });
    } else {
      snap(dup ? `调用 fib(${nd.n})：它之前已经算过了，现在又从头算一遍！` : `调用 fib(${nd.n})，先算 fib(${nd.n - 1})。`, { cur: nd.id });
      v = naive(nd.kids[0], seen) + naive(nd.kids[1], seen);
      if (!dup) status[nd.id] = "done";
      snap(`fib(${nd.n}) = fib(${nd.n - 1}) + fib(${nd.n - 2}) = ${v}，返回。`, { cur: nd.id });
    }
    seen.add(nd.n);
    return v;
  }

  function cutBelow(nd) {
    for (const c of nd.kids) { status[c.id] = "cut"; cutBelow(c); }
  }

  function memoized(nd) {
    calls++;
    if (nd.n <= 1) {
      status[nd.id] = "done";
      snap(`fib(${nd.n}) 是基线，直接返回 ${nd.n}。`, { cur: nd.id });
      return nd.n;
    }
    if (memo[nd.n] != null) {
      status[nd.id] = "hit";
      cutBelow(nd);
      snap(`fib(${nd.n}) 查 memo 命中，直接返回 ${memo[nd.n]}。它下面整棵子树都剪掉了。`, { cur: nd.id });
      return memo[nd.n];
    }
    snap(`调用 fib(${nd.n})：memo 里没有，往下算。`, { cur: nd.id });
    const v = memoized(nd.kids[0]) + memoized(nd.kids[1]);
    memo[nd.n] = v;
    status[nd.id] = "done";
    snap(`算出 fib(${nd.n}) = ${v}，存进 memo[${nd.n}]。`, { cur: nd.id, memoNew: nd.n });
    return v;
  }

  const val = el("input", { type: "number", value: "5", min: "1", max: "6", "aria-label": "n" });
  const getN = () => Math.min(6, Math.max(1, Number(val.value) || 1));

  function start(withMemo) {
    const n = getN();
    build(n);
    fr = [];
    calls = 0;
    status = nodes.map(() => "");
    memo = withMemo ? Array(n + 1).fill(null) : null;
    snap(withMemo ? `用记忆化算 fib(${n})。虚线方块是还没调用的。` : `用朴素递归算 fib(${n})。虚线方块是还没调用的。`);
    const v = withMemo ? memoized(nodes[0]) : naive(nodes[0], new Set());
    const dups = status.filter(s => s === "dup").length;
    snap(withMemo
      ? `完成：fib(${n}) = ${v}，只调用了 ${calls} 次（朴素递归要 ${nodes.length} 次）。`
      : `完成：fib(${n}) = ${v}，一共调用 ${calls} 次，其中 ${dups} 次（红色）是重复的。`);
    player.load(fr);
  }

  function table() {
    const n = getN();
    const dp = Array(n + 1).fill(null);
    fr = [];
    calls = 0;
    status = [];
    memo = null;
    snap(`开一张长 ${n + 1} 的表，dp[i] 表示 fib(i)。`, { dp });
    dp[0] = 0;
    calls++;
    if (n >= 1) { dp[1] = 1; calls++; }
    snap("先填初始值：dp[0] = 0，dp[1] = 1。", { dp });
    for (let i = 2; i <= n; i++) {
      dp[i] = dp[i - 1] + dp[i - 2];
      calls++;
      snap(`dp[${i}] = dp[${i - 1}] + dp[${i - 2}] = ${dp[i - 1]} + ${dp[i - 2]} = ${dp[i]}`, { dp, src: [i - 1, i - 2], memoNew: i });
    }
    snap(`填完：fib(${n}) = dp[${n}] = ${dp[n]}。每格只算一次，O(n)。`, { dp });
    player.load(fr);
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "n ="), val,
    el("button", { onclick: () => start(false) }, "朴素递归"),
    el("button", { onclick: () => start(true) }, "记忆化"),
    el("button", { onclick: table }, "填表")));
  build(getN());
  fr = [];
  calls = 0;
  status = nodes.map(() => "");
  memo = null;
  snap(`fib(${getN()}) 的完整递归树。点上面的按钮开始。`);
  player.load(fr);
})();
