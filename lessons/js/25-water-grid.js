// 动画：把盛最多水的所有组合 (i, j) 摆成上三角表格，看对撞指针每一步算了哪一格、砍掉了哪些格。
// 行 i 是左竖线，列 j 是右竖线，只有 i < j 的格子有意义。
// 每帧记录：每格的状态（todo 未处理 / calc 算过 / cut 被砍掉）、当前格、这一步新砍掉的格、统计行。
(() => {
  const root = document.getElementById("water-grid");
  const heights = [1, 8, 6, 2, 5, 4, 8, 3, 7];
  const n = heights.length;
  const area = (i, j) => Math.min(heights[i], heights[j]) * (j - i);
  const key = (i, j) => `${i},${j}`;

  function snap(say, status, { now = null, fresh = [], best = null } = {}) {
    let calc = 0, cut = 0;
    for (const s of Object.values(status)) { if (s === "calc") calc++; else if (s === "cut") cut++; }
    const total = n * (n - 1) / 2;
    return { say, status: { ...status }, now, fresh: new Set(fresh), best, calc, cut, todo: total - calc - cut };
  }

  function render(frame) {
    const cells = [el("div", { class: "wg-head" }, "左 \\ 右")];
    for (let j = 1; j < n; j++) cells.push(el("div", { class: "wg-head" }, `j=${j}`, el("br"), `高 ${heights[j]}`));
    for (let i = 0; i < n - 1; i++) {
      cells.push(el("div", { class: "wg-head" }, `i=${i}　高 ${heights[i]}`));
      for (let j = 1; j < n; j++) {
        if (j <= i) { cells.push(el("div", { class: "wg-cell na" })); continue; }
        const k = key(i, j);
        const state = frame.status[k] || "todo";
        let cls = "wg-cell " + state;
        if (frame.fresh.has(k)) cls += " fresh";
        if (frame.now && frame.now[0] === i && frame.now[1] === j) cls += " now";
        if (frame.best && frame.best[0] === i && frame.best[1] === j) cls += " top";
        // 算过的格子显示面积；被砍的格子用灰色小字显示它的真实面积，证明确实不可能更大
        const text = state === "todo" ? "" : String(area(i, j));
        cells.push(el("div", { class: cls, "data-cell": k, title: `(${i}, ${j}) 面积 ${area(i, j)}` }, text));
      }
    }
    return [el("div", { class: "wg-grid", style: `grid-template-columns: 92px repeat(${n - 1}, 40px)` }, cells),
      el("p", { class: "stat wg-stat" },
        `已计算 ${frame.calc} 格　被砍掉 ${frame.cut} 格　还没处理 ${frame.todo} 格（共 ${n * (n - 1) / 2} 格）`)];
  }

  function frames() {
    const status = {};
    const out = [snap(`heights = [${heights.join(", ")}]。每一格是一对竖线 (i, j)，一共 ${n * (n - 1) / 2} 格。` +
      "暴力做法要把每一格都算一遍。看看对撞指针算了几格、砍掉了几格。", status)];
    let left = 0, right = n - 1, bestArea = 0, bestPair = null;
    while (left < right) {
      const current = area(left, right);
      status[key(left, right)] = "calc";
      if (current > bestArea) { bestArea = current; bestPair = [left, right]; }
      const moveLeft = heights[left] < heights[right];
      // 移动 left：第 left 行剩下的格子 (left, left+1 .. right-1) 全部砍掉；移动 right：第 right 列剩下的格子砍掉
      const fresh = [];
      for (let m = left + 1; m < right; m++) fresh.push(moveLeft ? key(left, m) : key(m, right));
      for (const k of fresh) status[k] = "cut";
      const freshMax = Math.max(0, ...fresh.map(k => area(...k.split(",").map(Number))));
      const head = `算 (${left}, ${right})：min(${heights[left]}, ${heights[right]}) × ${right - left} = ${current}。`;
      let say;
      if (fresh.length === 0) {
        say = head + `这是剩下的最后一格，${moveLeft ? "left" : "right"} 一移动两个指针就相遇了。`;
      } else if (moveLeft) {
        say = head + `左边更矮，砍掉第 ${left} 行剩下的 ${fresh.length} 格：它们宽度更小，高度又不会超过 ${heights[left]}。` +
          `灰色小字是它们的真实面积，最大 ${freshMax}，确实不超过 ${current}。`;
      } else {
        const why = heights[left] === heights[right] ? "两边一样高，这里砍右边" : "右边更矮";
        say = head + `${why}，砍掉第 ${right} 列剩下的 ${fresh.length} 格：它们宽度更小，高度又不会超过 ${heights[right]}。` +
          `灰色小字是它们的真实面积，最大 ${freshMax}，确实不超过 ${current}。`;
      }
      out.push(snap(say, status, { now: [left, right], fresh, best: bestPair }));
      if (moveLeft) left++; else right--;
    }
    out.push(snap(`结束。只算了 ${n - 1} 格，砍掉 ${(n - 1) * (n - 2) / 2} 格，一格都没漏。最大面积 ${bestArea}，` +
      `在 (${bestPair[0]}, ${bestPair[1]}) 那一格（绿色）。一般地，n 根竖线只算 n - 1 格，所以是 O(n)。`,
      status, { best: bestPair }));
    return out;
  }

  const player = new Player(root, render);
  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(frames()) }, "演示搜索空间")));
  player.load([snap("点上面的按钮开始。行是左竖线 i，列是右竖线 j，每一格是一对竖线。", {})]);
})();
