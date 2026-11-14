// 动画两段：① 搜索旋转排序数组：每一步先判断哪一半有序（绿色），再决定去哪一半；
// ② 二分答案（珂珂吃香蕉）：在候选速度上二分，试过的速度来得及变绿、来不及变灰。
(() => {
  const root = document.getElementById("binary-search-advanced");
  const ROTATED = [4, 5, 6, 7, 9, 12, 0, 1, 2];
  const PILES = [3, 6, 7, 11], HOURS = 8;
  const SPEEDS = Array.from({ length: Math.max(...PILES) }, (_, k) => k + 1);
  const NO_BREAK_SPACE = " ";

  // values：这一排格子的值；left / right / middle：指针所在的下标；
  // sorted：[起, 止] 这一轮判断出的有序半边；tested：{下标: 来得及吗}；found：答案下标
  const snap = (say, data) => ({ say, sorted: null, tested: {}, found: null, middle: null, ...data });

  function render(frame) {
    const cells = frame.values.map((value, index) => {
      const pointers = [index === frame.left && "left", index === frame.middle && "middle", index === frame.right && "right"].filter(Boolean);
      const inSorted = frame.sorted && frame.sorted[0] <= index && index <= frame.sorted[1];
      // 试过的速度保留颜色，不灰掉，方便看出“来不及的都在左边、来得及的都在右边”
      const outside = index !== frame.found && !(index in frame.tested) && (index < frame.left || index > frame.right);
      let cls = "";
      if (index === frame.found) cls = "found";
      else if (index in frame.tested) cls = frame.tested[index] ? "fast" : "slow";
      else if (inSorted) cls = "sorted";
      else if (index === frame.middle) cls = "hot";
      return el("div", { class: "node" + (outside ? " fade" : ""), "data-index": index },
        el("div", { class: "tag" }, frame.mode === "koko" ? NO_BREAK_SPACE : String(index)),
        box(value, frame.mode === "koko" ? "small " + cls : cls),
        el("div", { class: "tag ptr" }, pointers.join(" / ") || NO_BREAK_SPACE));
    });
    return [
      el("div", { class: "row list" }, frame.mode === "koko" && el("span", { class: "label" }, "候选速度："), cells),
      el("p", { class: "stat" }, frame.stat),
    ];
  }

  const player = new Player(root, render);

  // ---------- 搜索旋转排序数组（闭区间 [left, right]） ----------
  function searchRotated(target) {
    const frames = [];
    let left = 0, right = ROTATED.length - 1, comparisons = 0;
    const stat = () => left <= right
      ? `区间 [left, right] = [${left}, ${right}]，还剩 ${right - left + 1} 个，已比较 ${comparisons} 次`
      : `区间空了，已比较 ${comparisons} 次`;
    const push = (say, data = {}) => frames.push(snap(say, { mode: "rotated", values: ROTATED, left, right, stat: stat(), ...data }));
    push(`在旋转数组里找 ${target}。用闭区间：left = 0，right = ${right}，两端都算在区间里。`);
    while (left <= right) {
      const middle = Math.floor((left + right) / 2), middleValue = ROTATED[middle];
      comparisons++;
      const head = `middle = (${left} + ${right}) // 2 = ${middle}，nums[middle] = ${middleValue}。`;
      if (middleValue === target) {
        push(`${head}正好等于 ${target}，找到了！返回 ${middle}。`, { middle, found: middle });
        return player.load(frames);
      }
      push(`${head}不等于 ${target}。接下来先判断哪一半是有序的。`, { middle });
      const leftValue = ROTATED[left], rightValue = ROTATED[right];
      if (leftValue <= middleValue) {
        const inside = leftValue <= target && target < middleValue;
        push(`nums[left] = ${leftValue} ≤ nums[middle] = ${middleValue}，所以左半边 [${left}, ${middle}] 有序（绿色），它的值在 ${leftValue} 到 ${middleValue} 之间。` +
          (inside ? `${leftValue} ≤ ${target} < ${middleValue}，${target} 只可能在左半边：right = middle - 1 = ${middle - 1}。`
                  : `${target} 不在 [${leftValue}, ${middleValue}) 里，不可能在左半边，去右半边：left = middle + 1 = ${middle + 1}。`),
          { middle, sorted: [left, middle] });
        if (inside) right = middle - 1; else left = middle + 1;
      } else {
        const inside = middleValue < target && target <= rightValue;
        push(`nums[left] = ${leftValue} > nums[middle] = ${middleValue}，断点在左半边，所以右半边 [${middle}, ${right}] 有序（绿色），它的值在 ${middleValue} 到 ${rightValue} 之间。` +
          (inside ? `${middleValue} < ${target} ≤ ${rightValue}，${target} 只可能在右半边：left = middle + 1 = ${middle + 1}。`
                  : `${target} 不在 (${middleValue}, ${rightValue}] 里，不可能在右半边，去左半边：right = middle - 1 = ${middle - 1}。`),
          { middle, sorted: [middle, right] });
        if (inside) left = middle + 1; else right = middle - 1;
      }
      if (left <= right) push(`区间缩成 [${left}, ${right}]。`);
    }
    push(`left = ${left} > right = ${right}，区间空了：数组里没有 ${target}，返回 -1。`);
    player.load(frames);
  }

  // ---------- 二分答案：珂珂吃香蕉 ----------
  function koko() {
    const frames = [];
    const tested = {};
    // 速度 speed 存在下标 speed - 1 的格子里
    let left = 0, right = SPEEDS.length - 1;
    const stat = () => `piles = [${PILES.join(", ")}]，hours = ${HOURS}；候选速度 [${SPEEDS[left]}, ${SPEEDS[right]}]`;
    const push = (say, data = {}) => frames.push(snap(say, { mode: "koko", values: SPEEDS, left, right, tested: { ...tested }, stat: stat(), ...data }));
    push(`速度最小是 1，最大取最大的那堆 ${SPEEDS[right]}（每堆 1 小时，一定来得及）。速度越快用时越少，所以要找第一个“来得及”的速度。`);
    while (left < right) {
      const middle = Math.floor((left + right) / 2), speed = SPEEDS[middle];
      const perPile = PILES.map(pile => Math.ceil(pile / speed));
      const total = perPile.reduce((sum, hours) => sum + hours, 0);
      const detail = PILES.map((pile, k) => `${pile} 根要 ${perPile[k]} 小时`).join("，");
      tested[middle] = total <= HOURS;
      const head = `试中间的速度 ${speed}：${detail}，共 ${total} 小时。`;
      if (total <= HOURS) {
        push(`${head}${total} ≤ ${HOURS}，来得及（绿色）。答案是 ${speed} 或者更慢的速度，right 移到 ${speed}。`, { middle });
        right = middle;
      } else {
        push(`${head}${total} > ${HOURS}，来不及（灰色）。比 ${speed} 更慢只会更来不及，left 移到 ${speed + 1}。`, { middle });
        left = middle + 1;
      }
      if (left < right) push(`候选速度缩成 [${SPEEDS[left]}, ${SPEEDS[right]}]。`);
    }
    push(`left == right，只剩速度 ${SPEEDS[left]}：最小速度是 ${SPEEDS[left]}。一共只试了 ${Object.keys(tested).length} 个速度，而不是从 1 开始一个个试。`, { found: left });
    player.load(frames);
  }

  const targetInput = el("input", { type: "number", value: "1", "aria-label": "target" });
  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "target ="), targetInput,
    el("button", { onclick: () => searchRotated(Number(targetInput.value)) }, "搜索旋转数组"),
    el("button", { onclick: koko }, "珂珂吃香蕉")));
  player.load([snap("一个旋转过的升序数组：原本是 [0, 1, 2, 4, 5, 6, 7, 9, 12]，开头的 0, 1, 2 被挪到了末尾。上面是下标。选一个按钮开始。",
    { mode: "rotated", values: ROTATED, left: 0, right: ROTATED.length - 1, stat: `区间 [left, right] = [0, ${ROTATED.length - 1}]` })]);
})();
