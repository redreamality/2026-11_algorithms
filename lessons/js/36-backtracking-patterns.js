// 动画：子集 II（含重复元素的子集）。
// 决策树按 DFS 的顺序一行一行长出来，缩进表示递归深度。
// “去重”模式下，同一层里和前一个数相同的分支直接剪掉（红色）；“不去重”模式下，会收集到重复的子集（红色）。
(() => {
  const root = document.getElementById("subsets");
  const INPUTS = { "1, 2, 2": [1, 2, 2], "2, 1, 2": [2, 1, 2], "1, 2, 2, 2": [1, 2, 2, 2] };
  const format = path => "[" + path.join(", ") + "]";

  function render(frame) {
    const arrayRow = el("div", { class: "row nums" }, el("span", { class: "label" }, "排好序的 sorted_nums："),
      frame.sortedNums.map((value, index) => el("span", { class: "node " + (index === frame.pickIndex ? "hot" : "") },
        el("span", { class: "tag" }, index === frame.startIndex ? "start" : ""),
        box(value, index === frame.skipIndex ? "found" : ""),
        el("span", { class: "label" }, `下标 ${index}`))));
    const tree = el("div", { class: "tree" }, frame.nodes.map((node, id) =>
      el("div", { class: `tree-node ${node.state} ${id === frame.currentNode ? "current" : ""}`, style: `padding-left:${node.depth * 30}px` },
        el("span", { class: "label" }, node.depth === 0 ? "根" : `选下标 ${node.index}`),
        box(format(node.path), "small"),
        node.state === "pruned" ? el("span", { class: "note" }, "× 同层重复，剪掉") : null,
        node.state === "duplicate" ? el("span", { class: "note" }, "重复的子集！") : null)));
    return [
      arrayRow,
      tree,
      el("div", { class: "row answers" }, el("span", { class: "label" }, "收集到的子集："),
        frame.answers.map(({ path, duplicate }) => box(format(path), "small " + (duplicate ? "found" : "")))),
      el("p", { class: "stat" }, "收集了 ", el("b", { class: "answer-count" }, frame.answers.length),
        " 个子集，其中重复 ", el("b", { class: "duplicate-count" }, frame.answers.filter(answer => answer.duplicate).length),
        " 个；剪掉 ", el("b", { class: "pruned-count" }, frame.nodes.filter(node => node.state === "pruned").length), " 枝"),
    ];
  }

  const player = new Player(root, render);

  function buildFrames(originalNums, removeDuplicates) {
    const sortedNums = [...originalNums].sort((first, second) => first - second);
    const nodes = [{ path: [], depth: 0, index: null, state: "" }];
    const answers = [], seen = new Set(), path = [];
    const snap = (say, { currentNode = null, pickIndex = null, skipIndex = null, startIndex = null } = {}) => ({
      say, sortedNums, currentNode, pickIndex, skipIndex, startIndex,
      nodes: nodes.map(node => ({ ...node })), answers: answers.map(answer => ({ ...answer })),
    });
    const frames = [snap(`输入 [${originalNums.join(", ")}]，先排序成 ${format(sortedNums)}，让相同的数挨在一起。`
      + (removeDuplicates ? "规则：同一层的 for 循环里，和前一个数相同的就跳过。" : "这次不加去重规则，看看会发生什么。"),
      { currentNode: 0 })];

    function backtrack(start, nodeId) {
      const key = format(path);
      const duplicate = seen.has(key);
      seen.add(key);
      answers.push({ path: [...path], duplicate });
      if (duplicate) nodes[nodeId].state = "duplicate";
      frames.push(snap(duplicate
        ? `收集 ${key}：它前面已经收集过了，这是一个重复的子集。`
        : `收集 ${key}。子集问题里每个节点都是一个答案。接下来这一层的 for 循环从下标 ${start} 开始挑。`,
        { currentNode: nodeId, startIndex: start }));
      for (let i = start; i < sortedNums.length; i++) {
        if (removeDuplicates && i > start && sortedNums[i] === sortedNums[i - 1]) {
          nodes.push({ path: [...path, sortedNums[i]], depth: path.length + 1, index: i, state: "pruned" });
          frames.push(snap(`同一层里，下标 ${i} 的 ${sortedNums[i]} 和前一个下标 ${i - 1} 的 ${sortedNums[i - 1]} 相同。`
            + `以 ${format([...path, sortedNums[i]])} 开头的子集，刚才走下标 ${i - 1} 那一枝时已经全部列过了，跳过（continue）。`,
            { currentNode: nodes.length - 1, skipIndex: i, startIndex: start }));
          continue;
        }
        path.push(sortedNums[i]);
        nodes.push({ path: [...path], depth: path.length, index: i, state: "" });
        const childId = nodes.length - 1;
        frames.push(snap(`① 选择下标 ${i}（${sortedNums[i]}），path 变成 ${format(path)}；② 递归，下一层从下标 ${i + 1} 开始。`,
          { currentNode: childId, pickIndex: i, startIndex: start }));
        backtrack(i + 1, childId);
        path.pop();
        frames.push(snap(`③ 撤销：拿掉 ${sortedNums[i]}，回到 ${format(path)} 这一层，试下一个下标。`,
          { currentNode: nodeId, startIndex: start }));
      }
    }

    backtrack(0, 0);
    const duplicateCount = answers.filter(answer => answer.duplicate).length;
    frames.push(snap(removeDuplicates
      ? `结束：一共 ${answers.length} 个不重复的子集，剪掉了 ${nodes.filter(node => node.state === "pruned").length} 枝。`
      : `结束：收集了 ${answers.length} 个，其中 ${duplicateCount} 个是重复的。去重规则就是为了在生成时直接剪掉它们。`));
    return frames;
  }

  const inputSelect = el("select", { "aria-label": "输入" }, Object.keys(INPUTS).map(name => el("option", { value: name }, name)));
  const run = removeDuplicates => () => player.load(buildFrames(INPUTS[inputSelect.value], removeDuplicates));

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "nums ="), inputSelect,
    el("button", { onclick: run(true) }, "去重（同层跳过）"),
    el("button", { onclick: run(false) }, "不去重（对照）")));
  player.load([{ say: "选一个输入，点上面的按钮开始。", sortedNums: [1, 2, 2], currentNode: null, pickIndex: null,
    skipIndex: null, startIndex: null, nodes: [], answers: [] }]);
})();
