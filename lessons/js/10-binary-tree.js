// 动画：在一棵小树上演示四种遍历。橙色 = 正在访问，绿色 = 已输出；下面列出输出序列和调用栈 / 队列。
(() => {
  const root = document.getElementById("btree");
  // 按下标存：i 的孩子是 2i+1 和 2i+2，null 表示没有这个节点
  const T = [1, 2, 3, 4, 5, null, 6];
  const W = 480, DY = 60;
  const has = i => i < T.length && T[i] !== null;
  let out, fr;

  // cur：正在访问的下标；stack：递归调用栈；queue：层序用的队列
  function snap(say, { cur = null, stack = null, queue = null } = {}) {
    fr.push({ say, cur, stack: stack && [...stack], queue: queue && [...queue], out: [...out] });
  }

  function pos(i) {
    const d = Math.floor(Math.log2(i + 1)), k = i - (2 ** d - 1);
    return [(k + 0.5) / 2 ** d * W, d * DY + 22];
  }

  function tree(f) {
    const h = 3 * DY - 16;
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", W);
    svg.setAttribute("height", h);
    for (let i = 1; i < T.length; i++) {
      if (!has(i)) continue;
      const [x1, y1] = pos((i - 1) >> 1), [x2, y2] = pos(i);
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      Object.entries({ x1, y1, x2, y2, stroke: "#999", "stroke-width": 2 }).forEach(([k, v]) => line.setAttribute(k, v));
      svg.append(line);
    }
    const nodes = T.map((v, i) => {
      if (v === null) return null;
      const b = box(v, i === f.cur ? "hot" : f.out.includes(v) ? "done" : "");
      const [x, y] = pos(i);
      b.style.left = x + "px";
      b.style.top = y + "px";
      return b;
    });
    return el("div", { class: "tree", style: `height:${h}px` }, svg, nodes);
  }

  function render(f) {
    return [
      tree(f),
      el("div", { class: "row out" }, el("span", { class: "label" }, "输出："),
        f.out.length ? f.out.map(v => box(v, "done")) : el("span", { class: "label" }, "（还没有）")),
      f.stack && el("div", { class: "row stack" }, el("span", { class: "label" }, "调用栈（底 → 顶）："),
        f.stack.length ? f.stack.map(i => box(T[i], "small")) : el("span", { class: "label" }, "空")),
      f.queue && el("div", { class: "row queue" }, el("span", { class: "label" }, "队列（队头 → 队尾）："),
        f.queue.length ? f.queue.map(i => box(T[i], "small")) : el("span", { class: "label" }, "空")),
    ];
  }

  const player = new Player(root, render);

  // order：在第几步输出根。0 = 前序，1 = 中序，2 = 后序
  function walk(i, order, stack) {
    if (!has(i)) return;
    stack.push(i);
    const v = T[i];
    const emit = () => {
      out.push(v);
      snap(`输出 ${v}。`, { cur: i, stack });
    };
    snap(`进入 ${v}。`, { cur: i, stack });
    if (order === 0) emit();
    walk(2 * i + 1, order, stack);
    if (order === 1) {
      if (has(2 * i + 1)) snap(`左子树做完，回到 ${v}。`, { cur: i, stack });
      emit();
    }
    walk(2 * i + 2, order, stack);
    if (order === 2) {
      if (has(2 * i + 1) || has(2 * i + 2)) snap(`两棵子树都做完，回到 ${v}。`, { cur: i, stack });
      emit();
    }
    stack.pop();
  }

  const NAMES = ["前序（根 → 左 → 右）", "中序（左 → 根 → 右）", "后序（左 → 右 → 根）"];

  const recursive = order => () => {
    out = []; fr = [];
    const stack = [];
    snap(`${NAMES[order]}：从根开始递归。`, { stack });
    walk(0, order, stack);
    snap(`${NAMES[order].slice(0, 2)}结果：${out.join(" ")}。每个节点进出一次，O(n)。`, { stack });
    player.load(fr);
  };

  function level() {
    out = []; fr = [];
    const q = [0];
    snap("层序：先把根放进队列。", { queue: q });
    while (q.length) {
      const i = q.shift();
      out.push(T[i]);
      snap(`出队 ${T[i]}，输出它。`, { cur: i, queue: q });
      const kids = [2 * i + 1, 2 * i + 2].filter(has);
      if (kids.length) {
        q.push(...kids);
        snap(`把它的孩子 ${kids.map(k => T[k]).join("、")} 入队。`, { cur: i, queue: q });
      }
    }
    snap(`队列空了，结束。层序结果：${out.join(" ")}。`, { queue: q });
    player.load(fr);
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: recursive(0) }, "前序"),
    el("button", { onclick: recursive(1) }, "中序"),
    el("button", { onclick: recursive(2) }, "后序"),
    el("button", { onclick: level }, "层序")));
  out = []; fr = [];
  snap("一棵 6 个节点的二叉树。点上面的按钮选一种遍历。");
  player.load(fr);
})();
