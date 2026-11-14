// 动画：AVL 插入。先像 BST 一样往下找位置，再沿路往回检查平衡因子，失衡就旋转。
// 橙色 = 正在看的节点，浅橙 = 走过的路，红色 = 失衡的节点，绿色 = 旋转后升上来的新根。
// 节点的横坐标按中序排名摆放，每个节点上方的小数字是它的 bf。
(() => {
  const root = document.getElementById("avl");
  const W = 480, DY = 60;
  let st, fr;

  const h = (nodes, id) => id === null ? 0 : 1 + Math.max(h(nodes, nodes[id].left), h(nodes, nodes[id].right));
  const bf = (nodes, id) => h(nodes, nodes[id].left) - h(nodes, nodes[id].right);
  const H = id => h(st.nodes, id), BF = id => bf(st.nodes, id), V = id => st.nodes[id].v;

  function snap(say, { cur = null, path = [], bad = null, done = null } = {}) {
    fr.push({ say, cur, path: [...path], bad, done, nodes: structuredClone(st.nodes), root: st.root });
  }

  function layout(f) {
    const pos = {}, parent = {};
    let k = 0, depth = 0;
    const go = (id, d, p) => {
      if (id === null) return;
      go(f.nodes[id].left, d + 1, id);
      pos[id] = [k++, d];
      parent[id] = p;
      depth = Math.max(depth, d);
      go(f.nodes[id].right, d + 1, id);
    };
    go(f.root, 0, null);
    return { pos, parent, n: k, depth };
  }

  function render(f) {
    const { pos, parent, n, depth } = layout(f);
    const stat = el("p", { class: "stat" }, "size = ", el("b", { class: "size" }, n),
      "，高度 = ", el("b", { class: "height" }, n ? depth + 1 : 0));
    if (!n) return [el("p", { class: "label" }, "空树（root = None）"), stat];
    const xy = id => [(pos[id][0] + 0.5) / n * W, pos[id][1] * DY + 44];
    const hh = depth * DY + 72;
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", W);
    svg.setAttribute("height", hh);
    const ids = Object.keys(pos).map(Number).sort((a, b) => pos[a][0] - pos[b][0]);  // 按中序从左到右
    for (const id of ids) {
      if (parent[id] === null) continue;
      const [x1, y1] = xy(parent[id]), [x2, y2] = xy(id);
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      Object.entries({ x1, y1, x2, y2, stroke: "#999", "stroke-width": 2 }).forEach(([k, v]) => line.setAttribute(k, v));
      svg.append(line);
    }
    const cls = id => id === f.bad ? "found" : id === f.done ? "done" : id === f.cur ? "hot" : f.path.includes(id) ? "path" : "";
    const items = ids.flatMap(id => {
      const [x, y] = xy(id);
      const b = box(f.nodes[id].v, cls(id));
      b.style.left = x + "px";
      b.style.top = y + "px";
      b.dataset.depth = pos[id][1];
      const v = bf(f.nodes, id);
      const t = el("span", { class: "bf" + (Math.abs(v) > 1 ? " bad" : "") }, (v > 0 ? "+" : "") + v);
      t.style.left = x + "px";
      t.style.top = (y - 34) + "px";
      return [b, t];
    });
    const sorted = ids.sort((a, b) => pos[a][0] - pos[b][0]).map(id => box(f.nodes[id].v, "small"));
    return [
      el("div", { class: "tree", style: `height:${hh}px` }, svg, items),
      el("div", { class: "row out" }, el("span", { class: "label" }, "中序："), sorted),
      stat,
    ];
  }

  const player = new Player(root, render);

  function relink(parent, old, child) {
    if (parent === null) st.root = child;
    else if (st.nodes[parent].left === old) st.nodes[parent].left = child;
    else st.nodes[parent].right = child;
  }

  // 旋转 y，返回升上来的新根；parent 是 y 原来的父亲
  function rotate(y, parent, dir) {
    const n = st.nodes[y];
    if (dir === "right") {
      const x = n.left;
      n.left = st.nodes[x].right;
      st.nodes[x].right = y;
      relink(parent, y, x);
      return x;
    }
    const x = n.right;
    n.right = st.nodes[x].left;
    st.nodes[x].left = y;
    relink(parent, y, x);
    return x;
  }

  function insert(v) {
    if (st.root === null) {
      st.root = st.nextId;
      st.nodes[st.nextId++] = { v, left: null, right: null };
      return snap(`树是空的，${v} 直接当根。`, { cur: st.root });
    }
    let cur = st.root;
    const path = [];
    while (true) {
      const n = st.nodes[cur];
      if (v === n.v) return snap(`${v} 已经在树里了：重复值忽略。`, { cur, path });
      const side = v < n.v ? "left" : "right";
      path.push(cur);
      if (n[side] === null) {
        n[side] = st.nextId;
        st.nodes[st.nextId++] = { v, left: null, right: null };
        snap(`和普通 BST 一样往下找，${v} 挂在 ${n.v} 的${side === "left" ? "左" : "右"}边。`, { cur: n[side], path });
        break;
      }
      cur = n[side];
    }
    // 沿路往回检查
    for (let i = path.length - 1; i >= 0; i--) {
      const id = path[i], parent = i > 0 ? path[i - 1] : null, b = BF(id);
      const up = path.slice(0, i);
      if (Math.abs(b) <= 1) {
        snap(`往回走到 ${V(id)}：bf = 左高 ${H(st.nodes[id].left)} − 右高 ${H(st.nodes[id].right)} = ${b}，没事。`, { cur: id, path: up });
        continue;
      }
      const heavy = b > 0 ? "left" : "right", c = st.nodes[id][heavy], cb = BF(c);
      snap(`往回走到 ${V(id)}：bf = ${b}，超出 ±1，失衡了！`, { bad: id, path: up });
      let top;
      if (b > 0 && cb >= 0) {
        snap(`LL：左孩子 ${V(c)} 的 bf = ${cb}，同号，一条直线。对 ${V(id)} 右旋一次。`, { bad: id, cur: c });
        top = rotate(id, parent, "right");
      } else if (b < 0 && cb <= 0) {
        snap(`RR：右孩子 ${V(c)} 的 bf = ${cb}，同号，一条直线。对 ${V(id)} 左旋一次。`, { bad: id, cur: c });
        top = rotate(id, parent, "left");
      } else {
        const lr = b > 0;
        snap(`${lr ? "LR" : "RL"}：${lr ? "左" : "右"}孩子 ${V(c)} 的 bf = ${cb}，异号，拐了个弯，要转两次。`, { bad: id, cur: c });
        const g = rotate(c, id, lr ? "left" : "right");
        snap(`① 先对 ${V(c)} ${lr ? "左" : "右"}旋，${V(g)} 升上来：变成了 ${lr ? "LL" : "RR"} 的一条直线。`, { bad: id, done: g });
        top = rotate(id, parent, lr ? "right" : "left");
      }
      snap(`旋转完成：${V(top)} 升上来当这棵子树的根，中序没变，树又平衡了。`, { done: top });
      return;
    }
    snap("一路回到根，没有失衡，不用旋转。");
  }

  function series(vals) {
    return () => {
      st = { nodes: {}, root: null, nextId: 0 };
      fr = [];
      snap(`从空树开始，依次插入 ${vals.join(", ")}。`);
      for (const v of vals) insert(v);
      player.load(fr);
    };
  }

  const val = el("input", { type: "number", value: "8", "aria-label": "值" });
  const one = () => {
    fr = [];
    snap("操作前的样子。");
    insert(Number(val.value));
    player.load(fr);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: series([1, 2, 3]) }, "插入 1, 2, 3"),
    el("button", { onclick: series([3, 1, 2]) }, "插入 3, 1, 2"),
    el("button", { onclick: series([1, 2, 3, 4, 5, 6, 7]) }, "插入 1～7"),
    el("span", { class: "label" }, "值 ="), val,
    el("button", { onclick: one }, "insert(值)")));
  st = { nodes: {}, root: null, nextId: 0 };
  fr = [];
  snap("空树。点上面的按钮开始插入。");
  player.load(fr);
})();
