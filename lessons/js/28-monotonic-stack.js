// 动画：单调栈。三道题共用一个画面：上面是柱子（数组），中间是栈里的下标，下面是答案。
// 橙色 = 正在处理的元素，蓝色 = 还在栈里，红色 = 这一步被弹出，绿框 = 正在结算的那一段。
(() => {
  const root = document.getElementById("monotonic");
  const EXAMPLES = {
    temperature: "73, 74, 75, 71, 69, 72, 76, 73",
    rectangle: "2, 1, 5, 6, 2, 3",
    rain: "0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1",
  };
  let mode = "temperature", numbers, stackOfIndices, answer, water, result;

  function snap(say, { current = null, popped = [], span = null, walls = [], fresh = null } = {}) {
    return {
      say, mode, numbers: [...numbers], stack: [...stackOfIndices], answer: answer && [...answer],
      water: [...water], result, current, popped, span, walls, fresh,
    };
  }

  function render(f) {
    const base = f.mode === "temperature" ? Math.min(...f.numbers) - 1 : 0;
    const top = Math.max(1, ...f.numbers.map((value, k) => value + f.water[k])) - base;
    const unit = Math.min(24, 120 / top);
    const columns = f.numbers.map((value, k) => {
      const inSpan = f.span && k >= f.span[0] && k <= f.span[1];
      const cls = ["col",
        f.stack.includes(k) && "in-stack",
        f.popped.includes(k) && "popped",
        f.walls.includes(k) && "wall",
        k === f.current && "current",
        inSpan && "span"].filter(Boolean).join(" ");
      const isSentinel = f.mode === "rectangle" && k === f.numbers.length - 1;
      return el("div", { class: cls },
        el("span", { class: "num" }, String(value)),
        f.water[k] ? el("div", { class: "water", style: `height:${f.water[k] * unit}px` }) : null,
        el("div", { class: "bar", style: `height:${Math.max(2, (value - base) * unit)}px` }),
        el("span", { class: "index-label" }, isSentinel ? "补的 0" : `下标 ${k}`));
    });
    const stackBoxes = f.stack.map(index => box(`${index}（${f.numbers[index]}）`));
    const parts = [
      el("div", { class: "bars" }, columns),
      el("div", { class: "row stack-row" },
        el("span", { class: "label" }, "栈底"),
        stackBoxes.length ? stackBoxes : el("span", { class: "label" }, "（空栈）"),
        el("span", { class: "label" }, "← 栈顶　（格式：下标（值））")),
    ];
    if (f.mode === "temperature") {
      parts.push(el("div", { class: "row answer-row" },
        el("span", { class: "label" }, "answer："),
        f.answer.map((days, k) => box(days, k === f.fresh ? "fresh" : ""))));
      parts.push(el("p", { class: "stat" }, "答案：", el("b", { class: "result" }, `[${f.answer.join(", ")}]`)));
    } else {
      const name = f.mode === "rectangle" ? "目前最大面积" : "目前接到的水";
      parts.push(el("p", { class: "stat" }, `${name} = `, el("b", { class: "result" }, f.result)));
    }
    return parts;
  }

  const player = new Player(root, render);

  function dailyTemperatures(frames) {
    frames.push(snap("从左往右处理每一天。栈里放“还没等到更热天气”的那些天的下标。"));
    numbers.forEach((value, i) => {
      frames.push(snap(`看第 ${i} 天：${value} 度。拿它和栈顶比。`, { current: i }));
      while (stackOfIndices.length && numbers[stackOfIndices[stackOfIndices.length - 1]] < value) {
        const waitingIndex = stackOfIndices.pop();
        answer[waitingIndex] = i - waitingIndex;
        frames.push(snap(`${value} 度比栈顶第 ${waitingIndex} 天的 ${numbers[waitingIndex]} 度热：第 ${waitingIndex} 天等到了，`
          + `answer[${waitingIndex}] = ${i} - ${waitingIndex} = ${answer[waitingIndex]}。把它弹出。`,
          { current: i, popped: [waitingIndex], fresh: waitingIndex }));
      }
      const stopReason = stackOfIndices.length
        ? `栈顶第 ${stackOfIndices[stackOfIndices.length - 1]} 天不比它冷，停止弹出。`
        : "栈空了，停止弹出。";
      stackOfIndices.push(i);
      frames.push(snap(`${stopReason}把第 ${i} 天入栈，它也开始等。栈里的气温从底到顶仍然递减。`, { current: i }));
    });
    const left = stackOfIndices.join("、");
    frames.push(snap(`遍历结束。栈里剩下的第 ${left} 天之后没有更热的日子，答案保持 0。`
      + `最终答案 [${answer.join(", ")}]。`));
  }

  function largestRectangle(frames) {
    numbers.push(0);
    water = numbers.map(() => 0);
    frames.push(snap("末尾补一根高 0 的柱子，保证最后所有柱子都会被弹出结算。栈里的高度从底到顶保持递增。"));
    numbers.forEach((height, i) => {
      frames.push(snap(`看下标 ${i}：高 ${height}。比栈顶矮，就要弹出栈顶并结算。`, { current: i }));
      while (stackOfIndices.length && numbers[stackOfIndices[stackOfIndices.length - 1]] > height) {
        const topIndex = stackOfIndices.pop();
        const leftBoundary = stackOfIndices.length ? stackOfIndices[stackOfIndices.length - 1] : -1;
        const width = i - leftBoundary - 1;
        const area = numbers[topIndex] * width;
        const improved = area > result;
        result = Math.max(result, area);
        frames.push(snap(`高 ${height} 比栈顶下标 ${topIndex}（高 ${numbers[topIndex]}）矮，弹出并结算下标 ${topIndex}：`
          + `右边界 = ${i}，左边界 = ${stackOfIndices.length ? `新栈顶 ${leftBoundary}` : "−1（栈空了）"}，`
          + `宽 = ${i} − (${leftBoundary}) − 1 = ${width}，面积 = ${numbers[topIndex]} × ${width} = ${area}。`
          + (improved ? "刷新最大面积！" : "没有超过目前的最大值。"),
          { current: i, popped: [topIndex], span: [leftBoundary + 1, i - 1] }));
      }
      stackOfIndices.push(i);
      frames.push(snap(`下标 ${i} 入栈。栈里的高度从底到顶仍然递增。`, { current: i }));
    });
    frames.push(snap(`所有柱子都结算完了，最大矩形面积 = ${result}。`));
  }

  function trapRainWater(frames) {
    frames.push(snap("栈里的高度从底到顶保持递减（还在下坡）。遇到比栈顶高的柱子，说明出现了右墙。"));
    numbers.forEach((height, i) => {
      frames.push(snap(`看下标 ${i}：高 ${height}。`, { current: i }));
      while (stackOfIndices.length && numbers[stackOfIndices[stackOfIndices.length - 1]] < height) {
        const bottomIndex = stackOfIndices.pop();
        if (!stackOfIndices.length) {
          frames.push(snap(`弹出槽底下标 ${bottomIndex}，栈空了：左边没有墙，水会流走，停止。`,
            { current: i, popped: [bottomIndex] }));
          break;
        }
        const leftIndex = stackOfIndices[stackOfIndices.length - 1];
        const level = Math.min(numbers[leftIndex], height) - numbers[bottomIndex];
        const width = i - leftIndex - 1;
        for (let k = leftIndex + 1; k < i; k++) water[k] += level;
        result += level * width;
        frames.push(snap(`弹出槽底下标 ${bottomIndex}（高 ${numbers[bottomIndex]}）。左墙是新栈顶 ${leftIndex}（高 ${numbers[leftIndex]}），`
          + `右墙是 ${i}（高 ${height}）。这一层水高 min(${numbers[leftIndex]}, ${height}) − ${numbers[bottomIndex]} = ${level}，`
          + `宽 ${i} − ${leftIndex} − 1 = ${width}，加 ${level * width} 格水。`,
          { current: i, popped: [bottomIndex], walls: [leftIndex, i], span: [leftIndex + 1, i - 1] }));
      }
      stackOfIndices.push(i);
      frames.push(snap(`下标 ${i} 入栈。栈里的高度从底到顶仍然递减。`, { current: i }));
    });
    frames.push(snap(`扫完了，一共接到 ${result} 格水。`));
  }

  const RUNNERS = { temperature: dailyTemperatures, rectangle: largestRectangle, rain: trapRainWater };

  const picker = el("select", { "aria-label": "题目" },
    el("option", { value: "temperature" }, "每日温度"),
    el("option", { value: "rectangle" }, "最大矩形"),
    el("option", { value: "rain" }, "接雨水"));
  const input = el("input", { type: "text", value: EXAMPLES.temperature, size: "30", "aria-label": "数组" });
  picker.addEventListener("change", () => { input.value = EXAMPLES[picker.value]; });

  function reset() {
    mode = picker.value;
    numbers = input.value.split(/[^0-9]+/).filter(Boolean).map(Number).slice(0, 14);
    if (!numbers.length) numbers = EXAMPLES[mode].split(", ").map(Number);
    stackOfIndices = [];
    answer = mode === "temperature" ? numbers.map(() => 0) : null;
    water = numbers.map(() => 0);
    result = 0;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "题目"), picker,
    el("span", { class: "label" }, "数组"), input,
    el("button", { onclick: () => { reset(); const frames = []; RUNNERS[mode](frames); player.load(frames); } }, "开始")));
  reset();
  player.load([snap("选好题目，点“开始”。")]);
})();
