// 动画：前缀和。① 一格格算出前缀和数组，再用一次减法回答区间查询；
// ② 和为 K 的子数组：每一步先查 prefix_sum - k 出现过几次，再把当前前缀和记进 dict。
(() => {
  const root = document.getElementById("prefix");

  // prefixSums 的长度是 numbers.length + 1，还没算到的位置是 null
  function snap(say, numbers, prefixSums, { numberStyles = {}, prefixStyles = {}, counts = null, countStyles = {}, stat = "", best = null } = {}) {
    return { say, numbers, prefixSums: [...prefixSums], numberStyles, prefixStyles,
      counts: counts && [...counts.entries()], countStyles, stat, best };
  }

  function render(frame) {
    const width = frame.prefixSums.length;
    const cells = [el("span", { class: "label" }, "下标")];
    for (let index = 0; index < width; index++) cells.push(el("span", { class: "index" }, index));
    cells.push(el("span", { class: "label" }, "numbers"));
    frame.numbers.forEach((number, index) => cells.push(box(number, "number " + (frame.numberStyles[index] || ""))));
    cells.push(el("span"));
    cells.push(el("span", { class: "label" }, "prefix_sum"));
    frame.prefixSums.forEach((value, index) => cells.push(value === null
      ? box("?", "empty prefix")
      : box(value, "prefix " + (frame.prefixStyles[index] || ""))));
    const parts = [el("div", { class: "grid-rows", style: `grid-template-columns: 110px repeat(${width}, 40px)` }, cells)];
    if (frame.counts) {
      parts.push(el("div", { class: "counts" },
        el("span", { class: "label" }, "count_by_prefix_sum："),
        frame.counts.map(([value, count]) => box(`${value}: ${count}`, "count " + (frame.countStyles[value] || "")))));
    }
    parts.push(el("p", { class: "stat" }, frame.stat, frame.best === null ? null : el("b", { class: "best" }, frame.best)));
    return parts;
  }

  const player = new Player(root, render);

  function rangeSumFrames() {
    const numbers = [-2, 0, 3, -5, 2, -1];
    const prefixSums = [0, ...numbers.map(() => null)];
    const frames = [snap(`numbers = [${numbers.join(", ")}]。prefix_sum 比 numbers 多一格，prefix_sum[0] = 0，表示一个数都不取。`,
      numbers, prefixSums, { prefixStyles: { 0: "done" } })];
    numbers.forEach((number, index) => {
      prefixSums[index + 1] = prefixSums[index] + number;
      frames.push(snap(`prefix_sum[${index + 1}] = prefix_sum[${index}] + numbers[${index}] = ${prefixSums[index]} + (${number}) = ${prefixSums[index + 1]}，` +
        `也就是前 ${index + 1} 个数的和。`,
        numbers, prefixSums, { numberStyles: { [index]: "hot" }, prefixStyles: { [index]: "hot", [index + 1]: "done" } }));
    });
    const queries = [[0, 2], [2, 5]];
    for (const [left, right] of queries) {
      const answer = prefixSums[right + 1] - prefixSums[left];
      const numberStyles = {};
      for (let index = left; index <= right; index++) numberStyles[index] = "range";
      frames.push(snap(`查询 sum_range(${left}, ${right})：前 ${right + 1} 个数的和减去前 ${left} 个数的和，中间这一段剩下来。` +
        `prefix_sum[${right + 1}] - prefix_sum[${left}] = ${prefixSums[right + 1]} - (${prefixSums[left]}) = ${answer}。只做了一次减法。`,
        numbers, prefixSums, {
          numberStyles, prefixStyles: { [left]: "hot", [right + 1]: "hot" },
          stat: `sum_range(${left}, ${right}) = `, best: answer,
        }));
    }
    return frames;
  }

  function subarraySumFrames() {
    const numbers = [3, 4, 7, 2, -3, 1, 4, 2], k = 7;
    const prefixSums = [0, ...numbers.map(() => null)];
    const countByPrefixSum = new Map([[0, 1]]);
    let prefixSum = 0, subarrayCount = 0;
    const foundRanges = [];
    const foundStyles = () => {
      const styles = {};
      for (const [start, end] of foundRanges) for (let index = start; index <= end; index++) styles[index] = "done";
      return styles;
    };
    const describe = ([start, end]) => `下标 ${start}～${end} 的 [${numbers.slice(start, end + 1).join(", ")}]`;
    const frames = [snap(`numbers = [${numbers.join(", ")}]，k = ${k}。dict 先放入 {0: 1}，代表一个数都没取时的前缀和 0。`,
      numbers, prefixSums, { prefixStyles: { 0: "done" }, counts: countByPrefixSum, countStyles: { 0: "done" }, stat: "找到的子数组个数：", best: 0 })];
    numbers.forEach((number, index) => {
      prefixSum += number;
      prefixSums[index + 1] = prefixSum;
      const wanted = prefixSum - k;
      const matches = countByPrefixSum.get(wanted) || 0;
      // 前缀和等于 wanted 的每个位置 start，都对应一段和为 k 的子数组 numbers[start..index]
      const newRanges = [];
      for (let start = 0; start <= index; start++) if (prefixSums[start] === wanted) newRanges.push([start, index]);
      subarrayCount += matches;
      foundRanges.push(...newRanges);
      const prefixStyles = { [index + 1]: "hot" };
      for (const [start] of newRanges) prefixStyles[start] = "hot";
      frames.push(snap(`走到 numbers[${index}] = ${number}，prefix_sum = ${prefixSum}。先查：prefix_sum - k = ${prefixSum} - ${k} = ${wanted}，` +
        (matches ? `dict 里它出现过 ${matches} 次，所以找到 ${matches} 个以这里结尾的子数组：${newRanges.map(describe).join("、")}。`
          : `dict 里没有 ${wanted}，以这里结尾的子数组没有和为 ${k} 的。`),
        numbers, prefixSums, {
          numberStyles: { ...foundStyles(), [index]: newRanges.length ? "done" : "hot" }, prefixStyles,
          counts: countByPrefixSum, countStyles: matches ? { [wanted]: "hot" } : {},
          stat: "找到的子数组个数：", best: subarrayCount,
        }));
      countByPrefixSum.set(prefixSum, (countByPrefixSum.get(prefixSum) || 0) + 1);
      frames.push(snap(`再记：把前缀和 ${prefixSum} 记进 dict，它现在出现过 ${countByPrefixSum.get(prefixSum)} 次。`,
        numbers, prefixSums, {
          numberStyles: foundStyles(), prefixStyles: { [index + 1]: "done" },
          counts: countByPrefixSum, countStyles: { [prefixSum]: "done" },
          stat: "找到的子数组个数：", best: subarrayCount,
        }));
    });
    frames.push(snap(`走完了。和为 ${k} 的子数组一共 ${subarrayCount} 个：${foundRanges.map(describe).join("、")}。数组里有负数 -3，如果照第 26 课的滑动窗口去做，只能找到前两个，后两个会被漏掉。`,
      numbers, prefixSums, { numberStyles: foundStyles(), counts: countByPrefixSum, stat: "找到的子数组个数：", best: subarrayCount }));
    return frames;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(rangeSumFrames()) }, "区域和查询"),
    el("button", { onclick: () => player.load(subarraySumFrames()) }, "和为 K 的子数组")));
  player.load([snap("点上面的按钮，选一个演示开始。", [-2, 0, 3, -5, 2, -1], [0, null, null, null, null, null, null])]);
})();
