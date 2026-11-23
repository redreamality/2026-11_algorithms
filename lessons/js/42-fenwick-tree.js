// 动画：树状数组。tree[位置] 画成一条横跨它管辖范围的格子，按 lowbit 分层。
// ① prefix_sum(7)：从位置 7 往下跳（减 lowbit）；② add(4, 3)：从位置 5 往上跳（加 lowbit），再查一次 prefix_sum(7)；
// ③ 逆序对计数：值先离散化成排名，每一步先查“前面 <= 它的个数”，再在它的排名上加 1。
(() => {
  const root = document.getElementById("fenwick");
  const lowbit = position => position & -position;
  const binary = (position, width) => position.toString(2).padStart(width, "0");

  // rows：画在树上面、和位置对齐的几行；tree 长度 size + 1，tree[0] 不用
  function snap(say, size, tree, { rows = [], treeStyles = {}, sequence = null, stat = "", best = null } = {}) {
    return {
      say, size, tree: [...tree], treeStyles: { ...treeStyles },
      rows: rows.map(row => ({ ...row, values: [...row.values], styles: { ...(row.styles || {}) } })),
      sequence: sequence && { ...sequence, styles: { ...sequence.styles } }, stat, best,
    };
  }

  function render(frame) {
    const { size } = frame;
    const width = binary(size, 0).length;
    const cells = [];
    const at = (row, column, node) => { node.style.gridRow = String(row); node.style.gridColumn = column; cells.push(node); };
    let row = 1;
    at(row, "1", el("span", { class: "label" }, "位置"));
    for (let position = 1; position <= size; position++) at(row, String(position + 1), el("span", { class: "index" }, position));
    row++;
    at(row, "1", el("span", { class: "label" }, "二进制"));
    for (let position = 1; position <= size; position++) at(row, String(position + 1), el("span", { class: "bits" }, binary(position, width)));
    for (const extra of frame.rows) {
      row++;
      at(row, "1", el("span", { class: "label" }, extra.label));
      extra.values.forEach((value, offset) => at(row, String(offset + 2), box(value, extra.cls + " " + (extra.styles[offset] || ""))));
    }
    const levels = [];
    for (let span = 1; span <= size; span *= 2) levels.unshift(span);
    const levelRow = {};
    for (const span of levels) {
      row++;
      levelRow[span] = row;
      at(row, "1", el("span", { class: "label" }, `lowbit = ${span}`));
    }
    for (let position = 1; position <= size; position++) {
      const span = lowbit(position);
      const node = el("span", { class: "box tree " + (frame.treeStyles[position] || "") },
        span > 1 ? `tree[${position}] = ` : null, el("b", { class: "value" }, frame.tree[position]));
      at(levelRow[span], `${position - span + 2} / ${position + 2}`, node);
    }
    const parts = [];
    if (frame.sequence) {
      const { values, ranks, styles } = frame.sequence;
      parts.push(el("div", { class: "fenwick", style: `grid-template-columns: 110px repeat(${values.length}, 52px)` },
        el("span", { class: "label" }, "numbers"), values.map((value, index) => box(value, "number " + (styles[index] || ""))),
        el("span", { class: "label" }, "排名"), ranks.map(rank => el("span", { class: "index" }, rank))));
    }
    parts.push(el("div", { class: "fenwick", style: `grid-template-columns: 110px repeat(${size}, 52px)` }, cells));
    parts.push(el("p", { class: "stat" }, frame.stat, frame.best === null ? null : el("b", { class: "best" }, frame.best)));
    return parts;
  }

  const player = new Player(root, render);
  const NUMBERS = [3, 1, 4, 1, 5, 9, 2, 6];

  function build(numbers) {
    const tree = Array(numbers.length + 1).fill(0);
    numbers.forEach((number, index) => {
      for (let position = index + 1; position <= numbers.length; position += lowbit(position)) tree[position] += number;
    });
    return tree;
  }

  const coverStyles = (from, to, cls = "range") => {
    const styles = {};
    for (let position = from; position <= to; position++) styles[position - 1] = cls;
    return styles;
  };

  // 往下跳求前缀和，每一跳一帧。numbersRow(样式) 返回要画在树上面的行
  function prefixSumFrames(frames, size, tree, count, numbersRow, { stat = "prefix_sum = ", note = "" } = {}) {
    const width = binary(size, 0).length;
    const taken = {};
    let total = 0;
    let covered = {};
    for (let position = count; position > 0; position -= lowbit(position)) {
      const span = lowbit(position);
      total += tree[position];
      covered = { ...covered, ...coverStyles(position - span + 1, position) };
      frames.push(snap(`位置 ${position}（二进制 ${binary(position, width)}），lowbit = ${span}，tree[${position}] 管位置 ${position - span + 1}～${position}，` +
        `加上 ${tree[position]}，total = ${total}。下一步跳到 ${position} - ${span} = ${position - span}。`,
        size, tree, { rows: numbersRow(covered), treeStyles: { ...taken, [position]: "hot" }, stat, best: total }));
      taken[position] = "done";
    }
    frames.push(snap(`跳到 0，停。prefix_sum(${count}) = ${total}，只加了 ${Object.keys(taken).length} 格。${note}`,
      size, tree, { rows: numbersRow(covered), treeStyles: taken, stat, best: total }));
    return total;
  }

  function queryFrames() {
    const tree = build(NUMBERS);
    const numbersRow = styles => [{ label: "numbers", cls: "number", values: NUMBERS, styles }];
    const frames = [snap(`numbers = [${NUMBERS.join(", ")}]。每条横格是一个 tree[位置]，管以它结尾、长度为 lowbit 的一段。求 prefix_sum(7)：前 7 个数的和。`,
      8, tree, { rows: numbersRow({}) })];
    prefixSumFrames(frames, 8, tree, 7, numbersRow, { note: "验算：3 + 1 + 4 + 1 + 5 + 9 + 2 = 25。" });
    return frames;
  }

  function addFrames() {
    const numbers = [...NUMBERS];
    const tree = build(numbers);
    const index = 4, delta = 3, size = numbers.length;
    const numbersRow = styles => [{ label: "numbers", cls: "number", values: numbers, styles }];
    const frames = [snap(`add(${index}, ${delta})：numbers[${index}] 加 ${delta}。下标 ${index} 在位置 ${index + 1}。要改的是所有管辖范围包含位置 ${index + 1} 的格子。`,
      size, tree, { rows: numbersRow({ [index]: "hot" }), treeStyles: {} })];
    numbers[index] += delta;
    const changed = {};
    for (let position = index + 1; position <= size; position += lowbit(position)) {
      const span = lowbit(position);
      tree[position] += delta;
      frames.push(snap(`位置 ${position}（二进制 ${binary(position, 4)}），tree[${position}] 管位置 ${position - span + 1}～${position}，包含位置 ${index + 1}，加 ${delta} 变成 ${tree[position]}。` +
        `下一步跳到 ${position} + ${span} = ${position + span}` + (position + span > size ? `，超过 n = ${size}，停。` : "。"),
        size, tree, { rows: numbersRow({ [index]: "hot" }), treeStyles: { ...changed, [position]: "hot" } }));
      changed[position] = "done";
    }
    frames.push(snap(`改完了，只动了 ${Object.keys(changed).length} 格：${Object.keys(changed).map(position => `tree[${position}]`).join("、")}。再查一次 prefix_sum(7)。`,
      size, tree, { rows: numbersRow({ [index]: "done" }), treeStyles: changed }));
    prefixSumFrames(frames, size, tree, 7, numbersRow, { note: "比修改前的 25 多了 3。" });
    return frames;
  }

  function inversionFrames() {
    const numbers = NUMBERS;
    const values = [...new Set(numbers)].sort((a, b) => a - b);
    const rankOf = new Map(values.map((value, rank) => [value, rank]));
    const ranks = numbers.map(number => rankOf.get(number));
    const size = values.length;
    const width = binary(size, 0).length;
    const tree = Array(size + 1).fill(0);
    const counts = Array(size).fill(0);
    const rows = (countStyles = {}) => [
      { label: "值", cls: "value-of-rank", values, styles: {} },
      { label: "出现次数", cls: "count", values: counts, styles: countStyles },
    ];
    const sequence = current => ({
      values: numbers, ranks,
      styles: Object.fromEntries(numbers.map((_, index) => [index, index < current ? "done" : index === current ? "hot" : ""])),
    });
    let inversionCount = 0;
    const frames = [snap(`离散化：去重排序后是 [${values.join(", ")}]，每个值换成它的排名（从 0 开始），排名 r 放在位置 r + 1。` +
      `树里记“每个排名出现过几次”，一开始全是 0。`,
      size, tree, { rows: rows(), sequence: sequence(-1), stat: "逆序对：", best: 0 })];
    numbers.forEach((number, seenCount) => {
      const rank = ranks[seenCount];
      const path = [];
      let notGreater = 0;
      for (let position = rank + 1; position > 0; position -= lowbit(position)) { path.push(position); notGreater += tree[position]; }
      const greater = seenCount - notGreater;
      inversionCount += greater;
      const countStyles = {};
      for (let other = rank + 1; other < size; other++) if (counts[other]) countStyles[other] = "range";
      frames.push(snap(`numbers[${seenCount}] = ${number}，排名 ${rank}，位置 ${rank + 1}。先查：prefix_sum(${rank + 1}) 往下跳 ${path.join(" → ")}` +
        ` → 0，前面 <= ${number} 的有 ${notGreater} 个。前面一共 ${seenCount} 个，所以比它大的有 ${seenCount} - ${notGreater} = ${greater} 个。`,
        size, tree, { rows: rows(countStyles), treeStyles: Object.fromEntries(path.map(position => [position, "hot"])),
          sequence: sequence(seenCount), stat: "逆序对：", best: inversionCount }));
      const updated = [];
      for (let position = rank + 1; position <= size; position += lowbit(position)) { tree[position] += 1; updated.push(position); }
      counts[rank] += 1;
      frames.push(snap(`再记：add(${rank}, 1)，从位置 ${rank + 1} 往上跳 ${updated.join(" → ")}，这几格都加 1。`,
        size, tree, { rows: rows({ [rank]: "done" }), treeStyles: Object.fromEntries(updated.map(position => [position, "done"])),
          sequence: sequence(seenCount), stat: "逆序对：", best: inversionCount }));
    });
    frames.push(snap(`走完了，逆序对一共 ${inversionCount} 个。每个数只做了一次查询、一次加，都是 O(log n)，位置的二进制最多 ${width} 位，所以每次最多跳 ${width} 下。`,
      size, tree, { rows: rows(), sequence: sequence(numbers.length), stat: "逆序对：", best: inversionCount }));
    return frames;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(queryFrames()) }, "前缀和查询"),
    el("button", { onclick: () => player.load(addFrames()) }, "单点加"),
    el("button", { onclick: () => player.load(inversionFrames()) }, "逆序对计数")));
  player.load([snap("点上面的按钮，选一个演示开始。", 8, build(NUMBERS),
    { rows: [{ label: "numbers", cls: "number", values: NUMBERS, styles: {} }] })]);
})();
