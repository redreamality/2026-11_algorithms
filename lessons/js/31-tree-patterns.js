// 动画：同一棵树上演示两道题的后序汇总。
// 橙色 = 正在处理的节点；绿色 = 已经处理完，下面的蓝字是它交给父亲的返回值；红色 = 最终答案。
(() => {
  const root = document.getElementById("tree-patterns");
  // 按下标存：下标 i 的左孩子是 2i+1，右孩子是 2i+2。没有出现的下标表示没有节点。
  const NODES = { 0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 7: 6, 10: 7, 15: 8, 22: 9 };
  const WIDTH = 520, LEVEL_HEIGHT = 66, LEVELS = 5;
  const exists = index => index in NODES;
  const leftOf = index => 2 * index + 1;
  const rightOf = index => 2 * index + 2;
  const isLeaf = index => !exists(leftOf(index)) && !exists(rightOf(index));
  let frames, returned, finished, extra;

  // current：正在处理的下标；answer：要标红的下标；extra：画面下方那行统计
  function snap(say, { current = null, answer = [] } = {}) {
    frames.push({ say, current, answer: [...answer], returned: { ...returned }, finished: [...finished], extra: { ...extra } });
  }

  function position(index) {
    const depth = Math.floor(Math.log2(index + 1)), offset = index - (2 ** depth - 1);
    return [(offset + 0.5) / 2 ** depth * WIDTH, depth * LEVEL_HEIGHT + 20];
  }

  function svgLine(attributes) {
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    Object.entries(attributes).forEach(([key, value]) => line.setAttribute(key, value));
    return line;
  }

  function tree(frame) {
    const height = (LEVELS - 1) * LEVEL_HEIGHT + 56;
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", WIDTH);
    svg.setAttribute("height", height);
    const parts = [svg];
    for (const key of Object.keys(NODES)) {
      const index = Number(key);
      if (index > 0) {
        const parent = (index - 1) >> 1;
        const [x1, y1] = position(parent), [x2, y2] = position(index);
        const onAnswer = frame.answer.includes(index) && frame.answer.includes(parent);
        svg.append(svgLine({ x1, y1, x2, y2, stroke: onAnswer ? "#c62828" : "#999", "stroke-width": onAnswer ? 4 : 2 }));
      }
      const cls = frame.answer.includes(index) ? "found" : index === frame.current ? "hot" : frame.finished.includes(index) ? "done" : "";
      const [x, y] = position(index);
      const node = box(NODES[index], "small " + cls);
      node.dataset.value = NODES[index];
      node.style.left = x + "px";
      node.style.top = y + "px";
      parts.push(node);
      if (index in frame.returned) {
        const label = el("span", { class: "ret", "data-value": NODES[index] }, frame.returned[index]);
        label.style.left = x + "px";
        label.style.top = y + 18 + "px";
        parts.push(label);
      }
    }
    return el("div", { class: "tree", style: `height:${height}px` }, parts);
  }

  function render(frame) {
    return [tree(frame), frame.extra.text && el("p", { class: "stat" }, frame.extra.text)];
  }

  const player = new Player(root, render);

  function reset() {
    frames = [];
    returned = {};
    finished = [];
    extra = {};
  }

  // ---------- 直径 ----------
  function diameter() {
    reset();
    let longestPath = 0, highestPoint = null;
    const depthOf = {};
    const showLongest = () => {
      extra.text = `longest_path = ${longestPath}` + (highestPoint === null ? "" : `（最高点是节点 ${NODES[highestPoint]}）`);
    };
    showLongest();
    snap("求直径：递归函数 depth(node) 返回子树有多深；每个节点在后序位置顺便算一次“以它为最高点的最长路径”。从根 1 开始。");

    function depth(index) {
      if (!exists(index)) return 0;
      const value = NODES[index];
      if (!isLeaf(index)) snap(`进入 ${value}：先递归算左子树的深度，再算右子树的深度。`, { current: index });
      const leftDepth = depth(leftOf(index));
      const rightDepth = depth(rightOf(index));
      const throughHere = leftDepth + rightDepth;
      const myDepth = 1 + Math.max(leftDepth, rightDepth);
      depthOf[index] = myDepth;
      const better = throughHere > longestPath;
      if (better) {
        longestPath = throughHere;
        highestPoint = index;
      }
      returned[index] = `深 ${myDepth}`;
      finished.push(index);
      showLongest();
      const head = isLeaf(index)
        ? `${value} 是叶子：左右都是空树，深度都是 0。`
        : `回到 ${value}（后序位置）：左子树深 ${leftDepth}，右子树深 ${rightDepth}。`;
      const compare = better
        ? `以 ${value} 为最高点的最长路径有 ${leftDepth} + ${rightDepth} = ${throughHere} 条边，比之前记录的都长，更新 longest_path = ${throughHere}。`
        : `以 ${value} 为最高点的最长路径有 ${leftDepth} + ${rightDepth} = ${throughHere} 条边，不比 longest_path = ${longestPath} 长，不更新。`;
      snap(`${head}${compare}交给父亲的是深度 1 + max(${leftDepth}, ${rightDepth}) = ${myDepth}。`, { current: index });
      return myDepth;
    }

    depth(0);
    // 从最高点往左、往右各走到最深处，拼出整条直径
    const deepestChain = index => {
      if (!exists(index)) return [];
      const next = (depthOf[leftOf(index)] || 0) >= (depthOf[rightOf(index)] || 0) ? leftOf(index) : rightOf(index);
      return [index, ...deepestChain(next)];
    };
    const path = [...deepestChain(leftOf(highestPoint)).reverse(), highestPoint, ...deepestChain(rightOf(highestPoint))];
    const rootLeft = depthOf[leftOf(0)] || 0, rootRight = depthOf[rightOf(0)] || 0;
    snap(`全部处理完：直径 = ${longestPath}，路径是 ${path.map(index => NODES[index]).join(" → ")}。最高点是节点 ${NODES[highestPoint]}，不经过根 1：以根为最高点只有 ${rootLeft} + ${rootRight} = ${rootLeft + rootRight} 条边。`, { answer: path });
    player.load(frames);
  }

  // ---------- 最近公共祖先 ----------
  function lowestCommonAncestor(firstValue, secondValue) {
    reset();
    extra.text = `要找的两个节点：${firstValue} 和 ${secondValue}`;
    snap(`找 ${firstValue} 和 ${secondValue} 的最近公共祖先。递归函数返回“在这棵子树里找到的东西”：找到目标就返回目标，左右都找到就返回自己，都没找到就返回空。`);
    const isTarget = index => NODES[index] === firstValue || NODES[index] === secondValue;
    const name = index => index === null ? "空" : String(NODES[index]);

    function find(index) {
      if (!exists(index)) return null;
      const value = NODES[index];
      if (isTarget(index)) {
        returned[index] = `返回 ${value}`;
        finished.push(index);
        snap(`${value} 就是要找的目标之一：直接把自己交给父亲，不用再往下找。`, { current: index });
        return index;
      }
      if (isLeaf(index)) {
        returned[index] = "返回 空";
        finished.push(index);
        snap(`${value} 是叶子，也不是目标，左右子树都是空的：返回 空。`, { current: index });
        return null;
      }
      snap(`进入 ${value}：它不是目标，去左右子树里找。`, { current: index });
      const foundInLeft = find(leftOf(index));
      const foundInRight = find(rightOf(index));
      let result, say;
      if (foundInLeft !== null && foundInRight !== null) {
        result = index;
        say = `回到 ${value}（后序位置）：左边找到了 ${name(foundInLeft)}，右边找到了 ${name(foundInRight)}。两个目标分居两侧，${value} 就是最近公共祖先，返回 ${value}。`;
      } else if (foundInLeft !== null || foundInRight !== null) {
        result = foundInLeft ?? foundInRight;
        say = `回到 ${value}（后序位置）：只有${foundInLeft !== null ? "左" : "右"}边找到了 ${name(result)}，另一边是空，把 ${name(result)} 原样往上交。`;
      } else {
        result = null;
        say = `回到 ${value}（后序位置）：左右都没找到，返回 空。`;
      }
      returned[index] = `返回 ${name(result)}`;
      finished.push(index);
      snap(say, { current: index });
      return result;
    }

    const answer = find(0);
    snap(`最近公共祖先是 ${name(answer)}。根节点 1 只从左边收到了 ${name(answer)}，于是把它原样交了出来。`, { answer: [answer] });
    player.load(frames);
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: diameter }, "求直径"),
    el("button", { onclick: () => lowestCommonAncestor(8, 7) }, "找最近公共祖先(8, 7)")));
  reset();
  snap("一棵 9 个节点的二叉树。点上面的按钮选一道题。");
  player.load(frames);
})();
