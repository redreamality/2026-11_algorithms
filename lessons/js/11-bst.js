// 动画：二叉搜索树的查找、插入、删除。橙色 = 正在比较，浅橙 = 走过的路，红色 = 要删的，绿色 = 后继。
// 节点的横坐标按中序排名摆放，所以从左到右读正好是从小到大。
(() => {
  const root = document.getElementById("bst");
  const W = 480, DY = 54;
  let st, fr;

  function snap(say, { cur = null, path = [], del = null, succ = null } = {}) {
    fr.push({ say, cur, path: [...path], del, succ, nodes: structuredClone(st.nodes), root: st.root });
  }

  // 中序排名 → x，深度 → y
  function layout(f) {
    const pos = {}, parent = {};
    let k = 0, depth = 0;
    const go = (id, d, p) => {
      if (id === null) return;
      const n = f.nodes[id];
      go(n.left, d + 1, id);
      pos[id] = [k++, d];
      parent[id] = p;
      depth = Math.max(depth, d);
      go(n.right, d + 1, id);
    };
    go(f.root, 0, null);
    return { pos, parent, n: k, depth };
  }

  function render(f) {
    const { pos, parent, n, depth } = layout(f);
    const stat = el("p", { class: "stat" }, "size = ", el("b", { class: "size" }, n),
      "，高度 = ", el("b", { class: "height" }, n ? depth + 1 : 0));
    if (!n) return [el("p", { class: "label" }, "空树（root = None）"), stat];
    const xy = id => [(pos[id][0] + 0.5) / n * W, pos[id][1] * DY + 22];
    const h = depth * DY + 44;
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", W);
    svg.setAttribute("height", h);
    const ids = Object.keys(pos).map(Number);
    for (const id of ids) {
      if (parent[id] === null) continue;
      const [x1, y1] = xy(parent[id]), [x2, y2] = xy(id);
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      Object.entries({ x1, y1, x2, y2, stroke: "#999", "stroke-width": 2 }).forEach(([k, v]) => line.setAttribute(k, v));
      svg.append(line);
    }
    const cls = id => id === f.del ? "found" : id === f.succ ? "done" : id === f.cur ? "hot" : f.path.includes(id) ? "path" : "";
    const boxes = ids.map(id => {
      const b = box(f.nodes[id].v, cls(id));
      const [x, y] = xy(id);
      b.style.left = x + "px";
      b.style.top = y + "px";
      b.dataset.depth = pos[id][1];
      return b;
    });
    const sorted = ids.sort((a, b) => pos[a][0] - pos[b][0]).map(id => box(f.nodes[id].v, "small"));
    return [
      el("div", { class: "tree", style: `height:${h}px` }, svg, boxes),
      el("div", { class: "row out" }, el("span", { class: "label" }, "中序："), sorted),
      stat,
    ];
  }

  const player = new Player(root, render);

  function add(v) {
    const id = st.nextId++;
    st.nodes[id] = { v, left: null, right: null };
    return id;
  }

  // 把 parent 指向 old 的那根线改成指向 child
  function relink(parent, old, child) {
    if (parent === null) st.root = child;
    else if (st.nodes[parent].left === old) st.nodes[parent].left = child;
    else st.nodes[parent].right = child;
  }

  const dir = (v, n) => v < n.v ? ["left", "左", "<"] : ["right", "右", ">"];

  function insert(v, quiet) {
    const say = quiet ? () => {} : snap;
    if (st.root === null) {
      st.root = add(v);
      return say(`树是空的，${v} 直接当根。`, { cur: st.root });
    }
    let cur = st.root;
    const path = [];
    while (true) {
      const n = st.nodes[cur];
      if (v === n.v) return say(`${v} 已经在树里了：重复值忽略，返回 False。`, { cur, path });
      const [side, zh, op] = dir(v, n);
      say(`${v} ${op} ${n.v}，往${zh}走。`, { cur, path });
      path.push(cur);
      if (n[side] === null) {
        n[side] = add(v);
        return say(`${zh}边是空的，${v} 就挂在这里。比较了 ${path.length} 次，不超过树高：O(h)。`, { cur: n[side], path });
      }
      cur = n[side];
    }
  }

  function contains(v) {
    let cur = st.root;
    const path = [];
    while (cur !== null) {
      const n = st.nodes[cur];
      if (v === n.v) return snap(`找到 ${v}，返回 True。比较了 ${path.length + 1} 次。`, { cur, path });
      const [side, zh, op] = dir(v, n);
      snap(`${v} ${op} ${n.v}，往${zh}走。另一半子树根本不用看。`, { cur, path });
      path.push(cur);
      cur = n[side];
    }
    snap(`走到 None 也没找到 ${v}，返回 False。`, { path });
  }

  function remove(v) {
    let parent = null, cur = st.root;
    const path = [];
    while (cur !== null && st.nodes[cur].v !== v) {
      const n = st.nodes[cur];
      const [side, zh, op] = dir(v, n);
      snap(`${v} ${op} ${n.v}，往${zh}走。`, { cur, path });
      path.push(cur);
      parent = cur;
      cur = n[side];
    }
    if (cur === null) return snap(`走到 None 也没找到 ${v}，返回 False。`, { path });
    const n = st.nodes[cur];
    const kids = [n.left, n.right].filter(k => k !== null);
    if (kids.length === 0) {
      snap(`找到 ${v}。情况一：它没有孩子，直接删掉。`, { path, del: cur });
      relink(parent, cur, null);
      delete st.nodes[cur];
      return snap("删完了，返回 True。", { path });
    }
    if (kids.length === 1) {
      const child = kids[0];
      snap(`找到 ${v}。情况二：它只有一个孩子 ${st.nodes[child].v}，让孩子顶上来。`, { path, del: cur, cur: child });
      relink(parent, cur, child);
      delete st.nodes[cur];
      return snap(`${st.nodes[child].v} 接替了 ${v} 的位置。中序依然从小到大，返回 True。`, { path, cur: child });
    }
    snap(`找到 ${v}。情况三：它有两个孩子，没法直接删。去找后继：右子树里最小的值。`, { path, del: cur });
    let sp = cur, s = n.right;
    snap(`先往右走一步：${st.nodes[s].v}。`, { del: cur, cur: s });
    while (st.nodes[s].left !== null) {
      sp = s;
      s = st.nodes[s].left;
      snap(`再一路往左走：${st.nodes[s].v}。`, { del: cur, cur: s });
    }
    const sv = st.nodes[s].v;
    snap(`${sv} 没有左孩子，它就是后继：比 ${v} 大的值里最小的那个。`, { del: cur, succ: s });
    n.v = sv;
    snap(`把 ${sv} 复制到 ${v} 的位置。左边都比 ${sv} 小、右边都比 ${sv} 大，规则没破坏。`, { succ: cur, del: s });
    relink(sp, s, st.nodes[s].right);
    delete st.nodes[s];
    snap(`再删掉原来的 ${sv}。它没有左孩子，属于情况一或二。返回 True。`, { succ: cur });
  }

  function sortedInsert() {
    st = { nodes: {}, root: null, nextId: 0 };
    fr = [];
    snap("从空树开始，按 1、2、3……7 的顺序插入。");
    for (let v = 1; v <= 7; v++) insert(v);
    snap("每个新值都比前面的大，只能一直往右挂：退化成链表。高度 = n = 7，查找变成 O(n)。");
    player.load(fr);
  }

  const val = el("input", { type: "number", value: "2", "aria-label": "值" });
  const run = op => () => {
    fr = [];
    snap("操作前的样子。");
    op(Number(val.value));
    player.load(fr);
  };
  const reset = () => {
    st = { nodes: {}, root: null, nextId: 0 };
    for (const v of [5, 3, 8, 1, 4, 7, 9, 6]) insert(v, true);
    fr = [];
    snap("一棵 8 个节点的二叉搜索树：每个节点左边都比它小，右边都比它大。");
    player.load(fr);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "值 ="), val,
    el("button", { onclick: run(contains) }, "contains(值)"),
    el("button", { onclick: run(insert) }, "insert(值)"),
    el("button", { onclick: run(remove) }, "remove(值)"),
    el("button", { onclick: sortedInsert }, "有序插入 1～7"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
