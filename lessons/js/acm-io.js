// 动画：ACM 模式读入。stdin 原文 → split() 切成 token → 同一个迭代器被 next() 一路往后取。
// 三种输入组织方式（单组 / 先读 T 组 / 读到 EOF）用的是同一道主线题：输出每个点的度数和平均度数。
(() => {
  const root = document.getElementById("acm-io");
  const FIRST_CASE = "4 3\n1 2\n2 3\n2 4";
  const SECOND_CASE = "3 1\n1 3";

  function render(frame) {
    const parts = [el("div", { class: "label" }, "stdin 原文（\\n 是换行）：")];
    parts.push(el("div", { class: "stdin-text" },
      frame.text.split("\n").flatMap(line => [line, el("span", { class: "newline" }, "\\n"), "\n"])));
    if (frame.split) {
      const hot = new Set(frame.hot);
      parts.push(el("div", { class: "row" }, el("span", { class: "label" }, "tokens："),
        frame.tokens.map((token, index) => box(token,
          "token " + (hot.has(index) ? "hot" : index < frame.position ? "used" : "")))));
    }
    if (frame.vars.length) {
      parts.push(el("div", { class: "vars" }, el("span", { class: "label" }, "变量："),
        frame.vars.map(([name, value]) => box(`${name} = ${value}`, "var " + (frame.hotVars.includes(name) ? "hot" : "")))));
    }
    if (frame.adjacency) {
      parts.push(el("div", { class: "adjacency" }, el("span", { class: "label" }, "adjacency："),
        frame.adjacency.slice(1).map((neighbors, index) =>
          box(`${index + 1}: [${neighbors.join(", ")}]`, "adj " + (frame.hotNodes.includes(index + 1) ? "hot" : "")))));
    }
    parts.push(el("div", { class: "output" }, el("span", { class: "label" }, "output_lines："),
      frame.output.map(line => box(line, "out"))));
    parts.push(el("p", { class: "stat" }, frame.split ? `已经取走 ${frame.position} / ${frame.tokens.length} 个 token` : ""));
    return parts;
  }

  const player = new Player(root, render);

  // mode: "single" | "cases" | "eof"
  function readingFrames(mode) {
    const text = mode === "single" ? FIRST_CASE
      : mode === "cases" ? `2\n${FIRST_CASE}\n${SECOND_CASE}` : `${FIRST_CASE}\n${SECOND_CASE}`;
    const tokens = text.split(/\s+/);
    const frames = [];
    let position = 0, split = false, adjacency = null;
    let vars = [];
    const output = [];

    function push(say, { hot = [], hotVars = [], hotNodes = [] } = {}) {
      frames.push({ say, text, tokens, split, position, hot, vars: vars.map(pair => [...pair]), hotVars,
        adjacency: adjacency && adjacency.map(neighbors => [...neighbors]), hotNodes, output: [...output] });
    }
    function setVar(name, value) {
      const found = vars.find(([existing]) => existing === name);
      if (found) found[1] = value; else vars.push([name, value]);
    }
    function next() { return Number(tokens[position++]); }

    function readOneCase(caseNumber, nodeCount, nodeSay) {
      vars = vars.filter(([name]) => name === "T");
      adjacency = null;
      setVar("n", nodeCount);
      push(nodeSay, { hot: [position - 1], hotVars: ["n"] });
      const edgeCount = next();
      setVar("m", edgeCount);
      adjacency = Array.from({ length: nodeCount + 1 }, () => []);
      push(`第 ${caseNumber} 组：read_graph 里 next(tokens) 取到 "${edgeCount}"，m = ${edgeCount}。` +
        `邻接表开 n + 1 = ${nodeCount + 1} 格，下标 0 不用，所以只显示 1～${nodeCount}。`, { hot: [position - 1], hotVars: ["m"] });
      for (let edge = 0; edge < edgeCount; edge++) {
        const u = next(), v = next();
        setVar("u", u); setVar("v", v);
        adjacency[u].push(v);
        adjacency[v].push(u);
        push(`第 ${edge + 1} 条边：连着两次 next，u = ${u}、v = ${v}。无向图，adjacency[${u}] 记上 ${v}，adjacency[${v}] 记上 ${u}。`,
          { hot: [position - 2, position - 1], hotVars: ["u", "v"], hotNodes: [u, v] });
      }
      const degrees = adjacency.slice(1).map(neighbors => neighbors.length);
      const average = (degrees.reduce((total, degree) => total + degree, 0) / nodeCount).toFixed(2);
      output.push(degrees.join(" "), average);
      push(`第 ${caseNumber} 组读完。度数是每个邻居列表的长度：${degrees.join(" ")}；平均 ${degrees.join(" + ")} 除以 ${nodeCount} = ${average}。` +
        `两行放进 output_lines，此时迭代器正好停在 ${position < tokens.length ? `下一组的开头（"${tokens[position]}"）` : "末尾"}。`);
    }

    push(`stdin 里的原文。${mode === "single" ? "单组：只有一张图。" : mode === "cases" ? "第一行 2 是 T，后面跟两张图。" : "两张图首尾相接，没告诉有几张，要读到 EOF。"}`);
    split = true;
    push(`text.split() 把所有空白（空格、换行）都当分隔符，切成 ${tokens.length} 个 token，换行信息没了。iter() 把它做成迭代器，还一个都没取。`);

    if (mode === "single") {
      readOneCase(1, next(), `next(tokens) 取第 1 个 token "4"，int 之后就是 n = 4。`);
      frames[frames.length - 1].say += " 全部 token 都取完了，一次写出 output_lines。";
    } else if (mode === "cases") {
      const caseCount = next();
      setVar("T", caseCount);
      push(`next(tokens) 取到 "${caseCount}"，T = ${caseCount}。for _ in range(T) 只在开头读这一次 T，之后循环 ${caseCount} 轮。`,
        { hot: [0], hotVars: ["T"] });
      for (let caseNumber = 1; caseNumber <= caseCount; caseNumber++) {
        const nodeCount = next();
        readOneCase(caseNumber, nodeCount, `range 的第 ${caseNumber} 轮：next(tokens) 取到 "${nodeCount}"，这一组 n = ${nodeCount}。`);
      }
      vars = vars.filter(([name]) => name === "T");
      adjacency = null;
      push(`range(T) 的 ${caseCount} 轮跑完，循环结束。output_lines 里有 ${output.length} 行，用 "\\n".join 一次写出。`);
    } else {
      let caseNumber = 0;
      while (position < tokens.length) {
        caseNumber++;
        const nodeCount = next();
        readOneCase(caseNumber, nodeCount, caseNumber === 1
          ? `for node_count_token in tokens：for 自己调用一次 next，取到 "${nodeCount}"，这就是第 1 组的 n = ${nodeCount}。`
          : `回到 for 的开头，它再调用一次 next，取到 "${nodeCount}"——上一组的 token 已经被 read_graph 取光，所以这正好是下一组的 n = ${nodeCount}。`);
      }
      vars = [];
      adjacency = null;
      push(`回到 for 的开头，它再调用 next：没有 token 了（EOF），迭代器抛 StopIteration，for 接住它、循环正常结束。` +
        `一共 ${caseNumber} 组，output_lines 里有 ${output.length} 行，一次写出。`);
    }
    return frames;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(readingFrames("single")) }, "单组"),
    el("button", { onclick: () => player.load(readingFrames("cases")) }, "先读 T 组"),
    el("button", { onclick: () => player.load(readingFrames("eof")) }, "读到 EOF")));
  player.load([{ say: "点上面的按钮，选一种输入方式开始。", text: FIRST_CASE, tokens: [], split: false, position: 0, hot: [],
    vars: [], hotVars: [], adjacency: null, hotNodes: [], output: [] }]);
})();
