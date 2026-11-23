// 动画：差分数组。① 求差分 → 两次区间加（各改两格）→ 前缀和还原；
// ② 拼车：每单乘客改两格，再从位置 0 累加车上人数，第一次超载就停。
(() => {
  const root = document.getElementById("difference");

  // rows: [{ label, cls, values, styles }]，values 里的 null 画成 “?”，undefined 画成空位
  function snap(say, width, rows, { stat = "", best = null } = {}) {
    return { say, width, rows: rows.map(row => ({ ...row, values: [...row.values], styles: { ...(row.styles || {}) } })), stat, best };
  }

  function render(frame) {
    const cells = [el("span", { class: "label" }, frame.indexLabel || "下标")];
    for (let index = 0; index < frame.width; index++) cells.push(el("span", { class: "index" }, index));
    for (const row of frame.rows) {
      cells.push(el("span", { class: "label" }, row.label));
      for (let index = 0; index < frame.width; index++) {
        const value = row.values[index];
        if (value === undefined) cells.push(el("span"));
        else if (value === null) cells.push(box("?", "empty " + row.cls));
        else cells.push(box(value, row.cls + " " + (row.styles[index] || "")));
      }
    }
    return [
      el("div", { class: "grid-rows", style: `grid-template-columns: 110px repeat(${frame.width}, 40px)` }, cells),
      el("p", { class: "stat" }, frame.stat, frame.best === null ? null : el("b", { class: "best" }, frame.best)),
    ];
  }

  const player = new Player(root, render);
  const list = values => `[${values.join(", ")}]`;

  function rangeAddFrames() {
    const numbers = [3, 1, 4, 1, 5, 9, 2, 6];
    const n = numbers.length;
    const difference = Array(n + 1).fill(null);
    const restored = Array(n).fill(null);
    const frames = [];
    const push = (say, { numberStyles = {}, differenceStyles = {}, restoredStyles = {}, stat = "", best = null } = {}) =>
      frames.push(snap(say, n + 1, [
        { label: "numbers", cls: "number", values: numbers, styles: numberStyles },
        { label: "difference", cls: "diff", values: difference, styles: differenceStyles },
        { label: "还原", cls: "restored", values: restored, styles: restoredStyles },
      ], { stat, best }));

    push(`numbers = ${list(numbers)}。差分数组 difference 比它多一格，第 i 格记“numbers[i] 比前一个多了多少”。`);
    numbers.forEach((number, index) => {
      const previous = index === 0 ? 0 : numbers[index - 1];
      difference[index] = number - previous;
      push(index === 0
        ? `difference[0] = numbers[0] = ${number}（可以想成前面有一个看不见的 0）。`
        : `difference[${index}] = numbers[${index}] - numbers[${index - 1}] = ${number} - ${previous} = ${difference[index]}。`,
        { numberStyles: index === 0 ? { 0: "hot" } : { [index - 1]: "hot", [index]: "hot" }, differenceStyles: { [index]: "done" } });
    });
    difference[n] = 0;
    push(`多出来的 difference[${n}] = 0，专门接住 right + 1 == n 时的“减回去”。差分数组建好了，下面开始做区间加。`,
      { differenceStyles: { [n]: "hot" } });

    const operations = [[2, 5, 2], [4, 7, 3]];
    const expected = [...numbers];
    for (const [left, right, delta] of operations) {
      const numberStyles = {};
      for (let index = left; index <= right; index++) { numberStyles[index] = "range"; expected[index] += delta; }
      difference[left] += delta;
      difference[right + 1] -= delta;
      push(`下标 ${left}～${right} 整体加 ${delta}：只改两格。difference[${left}] += ${delta} 变成 ${difference[left]}（从这里开始都多 ${delta}），` +
        `difference[${right + 1}] -= ${delta} 变成 ${difference[right + 1]}（过了 ${right} 再减回去）` +
        (right + 1 === n ? "，正好落在多出来的那一格上。" : "。") + "中间几格一个都没动。",
        { numberStyles, differenceStyles: { [left]: "plus", [right + 1]: "minus" } });
    }

    let runningTotal = 0;
    for (let index = 0; index < n; index++) {
      runningTotal += difference[index];
      restored[index] = runningTotal;
      push(`还原第 ${index} 个：前面的累计值加上 difference[${index}] = ${difference[index]}，得到 ${runningTotal}。`,
        { differenceStyles: { [index]: "hot" }, restoredStyles: { [index]: "done" } });
    }
    const same = restored.every((value, index) => value === expected[index]);
    push(`还原完成：${list(restored)}。直接在原数组上逐个加，结果也是 ${list(expected)}，两者${same ? "一样" : "不一样"}。` +
      `最后一格 difference[${n}] 没被读到。`,
      { restoredStyles: Object.fromEntries(restored.map((_, index) => [index, "done"])), stat: "还原结果 = ", best: list(restored) });
    return frames;
  }

  function carPoolingFrames() {
    const trips = [[2, 1, 5], [3, 3, 7]], capacity = 4, positionCount = 8;
    const difference = Array(positionCount + 1).fill(0);
    const onBoard = Array(positionCount).fill(null);
    const frames = [];
    const push = (say, { differenceStyles = {}, onBoardStyles = {}, stat = "", best = null } = {}) => {
      const counted = {};  // 已经累加过的位置一直保持绿色
      onBoard.forEach((value, position) => { if (value !== null) counted[position] = "done"; });
      const frame = snap(say, positionCount + 1, [
        { label: "difference", cls: "diff", values: difference, styles: differenceStyles },
        { label: "车上人数", cls: "onboard", values: onBoard, styles: { ...counted, ...onBoardStyles } },
      ], { stat, best });
      frame.indexLabel = "位置";
      frames.push(frame);
    };
    push(`trips = ${trips.map(list).join("、")}，capacity = ${capacity}。每单 [人数, 上车位置, 下车位置]，下车位置已经不占座。`);
    for (const [passengers, start, end] of trips) {
      difference[start] += passengers;
      difference[end] -= passengers;
      push(`${passengers} 人在位置 ${start} 上车、位置 ${end} 下车，占的是位置 ${start}～${end - 1}。` +
        `difference[${start}] += ${passengers}，difference[${end}] -= ${passengers}。`,
        { differenceStyles: { [start]: "plus", [end]: "minus" } });
    }
    let total = 0;
    for (let position = 0; position < positionCount; position++) {
      total += difference[position];
      onBoard[position] = total;
      if (total > capacity) {
        push(`位置 ${position}：累加 difference[${position}] = ${difference[position]}，车上 ${total} 人，超过 capacity = ${capacity}，直接返回 False。`,
          { differenceStyles: { [position]: "hot" }, onBoardStyles: { [position]: "over" }, stat: "car_pooling 返回 ", best: "False" });
        return frames;
      }
      push(`位置 ${position}：累加 difference[${position}] = ${difference[position]}，车上 ${total} 人，没超过 ${capacity}。`,
        { differenceStyles: { [position]: "hot" }, onBoardStyles: { [position]: "done" } });
    }
    push("每个位置都没超载，返回 True。", { stat: "car_pooling 返回 ", best: "True" });
    return frames;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(rangeAddFrames()) }, "区间加与还原"),
    el("button", { onclick: () => player.load(carPoolingFrames()) }, "拼车")));
  player.load([snap("点上面的按钮，选一个演示开始。", 9, [
    { label: "numbers", cls: "number", values: [3, 1, 4, 1, 5, 9, 2, 6] },
    { label: "difference", cls: "diff", values: Array(9).fill(null) },
  ])]);
})();
