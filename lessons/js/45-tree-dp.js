// 动画：主线那棵 6 个节点的树。打家劫舍 III 后序返回 (偷, 不偷)；树的直径先建邻接表、BFS 定顺序，再倒着处理。
// 橙色 = 正在处理的节点；绿色 = 处理完，下面的蓝字是交给父亲的值；红色 = 最终答案。
(() => {
  const root = document.getElementById("tree-dp");
  const VALUES = [3, 4, 5, 1, 3, 1];
  const EDGES = [[0, 1], [0, 2], [1, 3], [1, 4], [2, 5]];
  const POSITION = { 0: [220, 24], 1: [110, 96], 2: [330, 96], 3: [50, 168], 4: [170, 168], 5: [390, 168] };
  const BINARY_CHILDREN = { 0: [1, 2], 1: [3, 4], 2: [null, 5], 3: [null, null], 4: [null, null], 5: [null, null] };  // 二叉树的左、右孩子
  const WIDTH = 440, HEIGHT = 216;
  let frames, state;

  function reset(mode) {
    frames = [];
    state = { mode, returned: {}, finished: [], answer: [], stat: "", adjacency: null, order: null, edgeOn: -1, listHot: [] };
  }

  function snap(say, current = null) {
    frames.push({
      say, current, mode: state.mode, returned: { ...state.returned }, finished: [...state.finished], answer: [...state.answer],
      stat: state.stat, adjacency: state.adjacency && state.adjacency.map(list => [...list]), order: state.order && [...state.order],
      edgeOn: state.edgeOn, listHot: [...state.listHot],
    });
  }

  function svgLine(attributes) {
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    Object.entries(attributes).forEach(([key, value]) => line.setAttribute(key, value));
    return line;
  }

  function tree(frame) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", WIDTH);
    svg.setAttribute("height", HEIGHT);
    EDGES.forEach(([first, second], index) => {
      const [x1, y1] = POSITION[first], [x2, y2] = POSITION[second];
      const onAnswer = frame.answer.includes(first) && frame.answer.includes(second);
      const color = onAnswer ? "#c62828" : index === frame.edgeOn ? "#e65100" : "#999";
      svg.append(svgLine({ x1, y1, x2, y2, stroke: color, "stroke-width": onAnswer || index === frame.edgeOn ? 4 : 2 }));
    });
    const parts = [svg];
    for (let node = 0; node < VALUES.length; node++) {
      const [x, y] = POSITION[node];
      const cls = frame.answer.includes(node) ? "found" : node === frame.current ? "hot" : frame.finished.includes(node) ? "done" : "";
      const nodeBox = box(frame.mode === "rob" ? VALUES[node] : node, "small " + cls);
      nodeBox.dataset.node = node;
      nodeBox.style.left = x + "px";
      nodeBox.style.top = y + "px";
      parts.push(nodeBox);
      if (node in frame.returned) {
        const label = el("span", { class: "ret", "data-node": node }, frame.returned[node]);
        label.style.left = x + "px";
        label.style.top = y + 18 + "px";
        parts.push(label);
      }
    }
    return el("div", { class: "tree", style: `height:${HEIGHT}px` }, parts);
  }

  function render(frame) {
    const out = [tree(frame)];
    if (frame.adjacency) {
      out.push(el("p", { class: "label" }, "adjacency（邻接表）："));
      frame.adjacency.forEach((list, node) => out.push(el("div", { class: "adjacency" + (frame.listHot.includes(node) ? " hot" : ""), "data-list": node },
        `adjacency[${node}] = [${list.join(", ")}]`)));
    }
    if (frame.order) out.push(el("p", { class: "adjacency order" }, `order = [${frame.order.join(", ")}]`));
    if (frame.stat) out.push(el("p", { class: "stat" }, frame.stat));
    return out;
  }

  const player = new Player(root, render);

  // ---------- 打家劫舍 III ----------
  function robTree() {
    reset("rob");
    snap("打家劫舍 III：方框里是每间房子的钱，父子不能都偷。每个节点后序返回两个数：(偷它时子树最多多少, 不偷它时最多多少)。从根 3 开始。");
    const pair = {};

    function bestPair(node) {
      if (node === null) return [0, 0];
      const [left, right] = BINARY_CHILDREN[node];
      const isLeaf = left === null && right === null;
      if (!isLeaf) snap(`进入 ${VALUES[node]}：先算两个孩子各自的 (偷, 不偷)。`, node);
      const [leftTake, leftSkip] = bestPair(left);
      const [rightTake, rightSkip] = bestPair(right);
      const take = VALUES[node] + leftSkip + rightSkip;
      const skip = Math.max(leftTake, leftSkip) + Math.max(rightTake, rightSkip);
      pair[node] = [take, skip];
      state.returned[node] = `偷 ${take} / 不偷 ${skip}`;
      state.finished.push(node);
      const say = isLeaf
        ? `${VALUES[node]} 是叶子：偷它得 ${VALUES[node]}，不偷得 0。`
        : `回到 ${VALUES[node]}（后序位置）：左孩子 (${leftTake}, ${leftSkip})，右孩子 (${rightTake}, ${rightSkip})。` +
          `偷它 = ${VALUES[node]} + ${leftSkip} + ${rightSkip} = ${take}（孩子都不能偷）；` +
          `不偷它 = max(${leftTake}, ${leftSkip}) + max(${rightTake}, ${rightSkip}) = ${skip}（孩子随意）。`;
      snap(say, node);
      return [take, skip];
    }

    const [take, skip] = bestPair(0);
    // 倒推：从根往下，父亲偷了孩子就不偷；父亲没偷，孩子按两个数哪个大决定
    const robbed = [];
    const decide = (node, parentRobbed) => {
      if (node === null) return;
      const robThis = !parentRobbed && pair[node][0] >= pair[node][1];
      if (robThis) robbed.push(node);
      BINARY_CHILDREN[node].forEach(child => decide(child, robThis));
    };
    decide(0, false);
    state.answer = robbed;
    state.stat = `答案 = max(${take}, ${skip}) = ${Math.max(take, skip)}`;
    snap(`根的两个数是 (${take}, ${skip})，答案取大的 ${Math.max(take, skip)}：不偷根，偷 ${robbed.map(node => VALUES[node]).join(" 和 ")}（红色）。`);
    player.load(frames);
  }

  // ---------- 树的直径 ----------
  function diameter() {
    reset("diameter");
    const count = VALUES.length;
    snap(`树的直径：同一棵树，输入换成边列表 edges = [${EDGES.map(edge => `(${edge.join(", ")})`).join(", ")}]，方框里是节点编号。第一步建邻接表。`);
    state.adjacency = Array.from({ length: count }, () => []);
    EDGES.forEach(([first, second], index) => {
      state.adjacency[first].push(second);
      state.adjacency[second].push(first);
      state.edgeOn = index;
      state.listHot = [first, second];
      snap(`边 (${first}, ${second}) 没有方向：${second} 记进 adjacency[${first}]，${first} 也记进 adjacency[${second}]。`);
    });
    state.edgeOn = -1;
    state.listHot = [];

    const parent = Array(count).fill(-1);
    parent[0] = 0;
    const order = [0];
    for (const node of order) {
      for (const neighbor of state.adjacency[node]) {
        if (parent[neighbor] === -1) { parent[neighbor] = node; order.push(neighbor); }
      }
    }
    state.order = order;
    snap(`第二步：选 0 当根，BFS 得到顺序 order，父亲总在孩子前面。记下每个节点的 parent：${order.slice(1).map(node => `${node} 的父亲是 ${parent[node]}`).join("，")}。倒着处理 order，孩子就总比父亲先算好。`);

    const deepest = Array(count).fill(0);
    let longest = 0, highest = -1;
    const topChildren = {};
    state.stat = "longest = 0";
    for (const node of [...order].reverse()) {
      // 邻居里去掉父亲，剩下的就是孩子（根的 parent 记成自己，不会出现在邻居里）
      const realChildren = state.adjacency[node].filter(neighbor => neighbor !== parent[node]);
      let first = 0, second = 0, firstChild = -1, secondChild = -1;
      for (const child of realChildren) {
        const depth = deepest[child] + 1;
        if (depth > first) { second = first; secondChild = firstChild; first = depth; firstChild = child; }
        else if (depth > second) { second = depth; secondChild = child; }
      }
      deepest[node] = first;
      topChildren[node] = [firstChild, secondChild];
      const better = first + second > longest;
      if (better) { longest = first + second; highest = node; }
      state.returned[node] = `深 ${first}`;
      state.finished.push(node);
      state.stat = `longest = ${longest}` + (highest >= 0 ? `（最高点是节点 ${highest}）` : "");
      const skipped = node === 0 ? "" : `跳过父亲 ${parent[node]}，`;
      const say = realChildren.length === 0
        ? `节点 ${node}：${skipped}没有孩子，是叶子，往下能走 0 条边。`
        : `节点 ${node}：${skipped}孩子是 ${realChildren.join("、")}，每个方向能走 ${realChildren.map(child => `${deepest[child]} + 1`).join("、")} 条边。` +
          `最深两个之和 ${first} + ${second} = ${first + second}，${better ? `比之前长，更新 longest = ${longest}` : `不比 longest = ${longest} 长`}。交给父亲 deepest = ${first}。`;
      snap(say, node);
    }

    // 从最高点往最深的两个孩子方向各走到底，拼出直径
    const chain = start => {
      const path = [];
      for (let node = start; node !== -1; node = topChildren[node][0]) path.push(node);
      return path;
    };
    const [firstChild, secondChild] = topChildren[highest];
    const path = [...(secondChild === -1 ? [] : chain(secondChild)).reverse(), highest, ...chain(firstChild)].reverse();
    state.answer = path;
    snap(`处理完了：直径 = ${longest}，路径 ${path.join(" → ")}。答案是 longest，不是根的 deepest[0] = ${deepest[0]}。`);
    player.load(frames);
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: robTree }, "打家劫舍 III"),
    el("button", { onclick: diameter }, "树的直径")));
  reset("rob");
  snap("主线那棵 6 个节点的树。点上面的按钮选一道题。");
  player.load(frames);
})();
