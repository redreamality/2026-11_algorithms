// 动画：一维 DP 三道题。打家劫舍一格格填表；最长递增子序列看 smallest_tail 怎么变；最大子数组和看“接上还是重来”。
// 表格里：橙色 cur = 正在填的格，蓝色 dep = 它用到的格，绿色 pick = 最后选中的，红色 best = 最终答案。
(() => {
  const root = document.getElementById("dp1d");

  function renderTable(f) {
    const head = el("tr", {}, el("th", {}, f.corner), f.cols.map(c => el("th", {}, String(c))));
    const rows = f.rows.map((name, i) => el("tr", {},
      el("th", {}, name),
      f.cols.map((_, j) => {
        const key = i + "," + j, value = f.grid[i][j];
        return el("td", { class: f.cls[key] || "", "data-cell": key }, value == null ? "" : String(value));
      })));
    return el("table", { class: "dp" }, head, rows);
  }

  function renderTails(f) {
    return [
      el("div", { class: "row" }, el("span", { class: "label" }, "numbers："),
        f.numbers.map((n, k) => box(n, k === f.at ? "hot" : k < f.at ? "" : "empty"))),
      el("div", { class: "row tails" }, el("span", { class: "label" }, "smallest_tail："),
        f.tails.length ? f.tails.map((n, k) => box(n, k === f.changed ? "hot" : "")) : el("span", { class: "label" }, "（空）")),
    ];
  }

  function render(f) {
    return [...[].concat(f.kind === "tails" ? renderTails(f) : renderTable(f)), f.extra && el("p", { class: "stat" }, f.extra)];
  }

  const player = new Player(root, render);

  // ---------- 打家劫舍 ----------
  function rob() {
    const values = [2, 7, 9, 3, 1];
    const n = values.length;
    const best = Array(n).fill(null);
    const base = { corner: "下标 i", cols: [...values.keys()], rows: ["house_values[i]", "best_amount_up_to[i]"] };
    const snap = (say, cls = {}, extra = "") =>
      ({ ...base, grid: [values, [...best]], cls, say, extra });
    const fr = [snap("一排 5 间房子，相邻的不能都偷。下面一行 best_amount_up_to[i] = 只考虑下标 0..i 时最多能偷多少，从左往右填。")];

    best[0] = values[0];
    fr.push(snap(`i = 0：只有一间房子，偷它。best_amount_up_to[0] = ${values[0]}。`, { "1,0": "cur", "0,0": "dep" }));
    best[1] = Math.max(values[0], values[1]);
    fr.push(snap(`i = 1：两间相邻，只能偷一间，挑钱多的：max(${values[0]}, ${values[1]}) = ${best[1]}。`,
      { "1,1": "cur", "0,0": "dep", "0,1": "dep" }));
    for (let i = 2; i < n; i++) {
      const skip = best[i - 1], take = best[i - 2] + values[i];
      best[i] = Math.max(skip, take);
      const choice = take > skip ? "偷更划算" : "不偷更划算";
      fr.push(snap(`i = ${i}：不偷第 ${i} 间 → 抄左边 ${skip}；偷第 ${i} 间 → 隔一格的 ${best[i - 2]} + ${values[i]} = ${take}。${choice}，填 ${best[i]}。`,
        { [`1,${i}`]: "cur", [`1,${i - 1}`]: "dep", [`1,${i - 2}`]: "dep", [`0,${i}`]: "dep" }));
    }

    // 从右往左倒推偷了哪几间：这一格等于左边一格，说明没偷这一间
    const picked = [];
    for (let i = n - 1; i >= 0;) {
      if (i > 0 && best[i] === best[i - 1]) { i--; continue; }
      picked.unshift(i);
      i -= 2;
    }
    const cls = { [`1,${n - 1}`]: "best" };
    picked.forEach(i => { cls[`0,${i}`] = "pick"; });
    fr.push(snap(`填完了。最后一格就是答案：最多偷 ${best[n - 1]}。倒推回去，偷的是第 ${picked.join("、")} 间（绿色）。`,
      cls, `答案 = ${best[n - 1]}`));
    return fr;
  }

  // ---------- 最长递增子序列：smallest_tail + 二分 ----------
  function lis() {
    const numbers = [10, 9, 2, 5, 3, 7, 101, 18];
    const tails = [];
    const snap = (say, at, changed = -1, extra = "") =>
      ({ kind: "tails", numbers, tails: [...tails], at, changed, say, extra });
    const fr = [snap("smallest_tail[k] = 长度为 k + 1 的递增子序列里，最小的结尾。从左到右，一个数一个数地处理。", -1)];
    numbers.forEach((number, at) => {
      let low = 0, high = tails.length;  // 二分：第一个 ≥ number 的位置
      while (low < high) {
        const middle = (low + high) >> 1;
        if (tails[middle] < number) low = middle + 1; else high = middle;
      }
      if (low === tails.length) {
        tails.push(number);
        fr.push(snap(`${number} 比 smallest_tail 里所有数都大，能接在最长的后面：追加到末尾，长度变成 ${tails.length}。`, at, low));
      } else {
        const old = tails[low];
        tails[low] = number;
        fr.push(snap(`第一个 ≥ ${number} 的是位置 ${low} 上的 ${old}，换成 ${number}：长度 ${low + 1} 的子序列，结尾可以更小了。`, at, low));
      }
    });
    fr.push(snap(`处理完了。smallest_tail 的长度 ${tails.length} 就是答案（注意它的内容不一定是真实的子序列）。`,
      numbers.length, -1, `答案 = ${tails.length}`));
    return fr;
  }

  // ---------- 最大子数组和 ----------
  function kadane() {
    const numbers = [-2, 1, -3, 4, -1, 2, 1, -5, 4];
    const n = numbers.length;
    const endingHere = Array(n).fill(null), overall = Array(n).fill(null);
    const base = { corner: "下标 i", cols: [...numbers.keys()],
      rows: ["numbers[i]", "best_sum_ending_here", "best_sum_overall"] };
    const snap = (say, cls = {}, extra = "") =>
      ({ ...base, grid: [numbers, [...endingHere], [...overall]], cls, say, extra });
    const fr = [snap("best_sum_ending_here = 必须以 numbers[i] 结尾的子数组的最大和；best_sum_overall = 到目前为止见过的最大和。")];

    let start = 0, bestStart = 0, bestEnd = 0;
    endingHere[0] = overall[0] = numbers[0];
    fr.push(snap(`i = 0：只有 ${numbers[0]} 自己，两行都填 ${numbers[0]}。`, { "1,0": "cur", "2,0": "cur" }));
    for (let i = 1; i < n; i++) {
      const extend = endingHere[i - 1] + numbers[i];
      let say;
      if (extend >= numbers[i]) {
        endingHere[i] = extend;
        say = `i = ${i}：接上前面 ${endingHere[i - 1]} + ${numbers[i]} = ${extend}，比只要 ${numbers[i]} 自己大，接上。`;
      } else {
        endingHere[i] = numbers[i];
        start = i;
        say = `i = ${i}：前面那段是 ${endingHere[i - 1]}，接上只会拖后腿（${extend} < ${numbers[i]}），从 ${numbers[i]} 重新开始。`;
      }
      if (endingHere[i] > overall[i - 1]) { overall[i] = endingHere[i]; bestStart = start; bestEnd = i; say += ` 刷新最大和：${overall[i]}。`; }
      else { overall[i] = overall[i - 1]; say += ` 最大和保持 ${overall[i]}。`; }
      fr.push(snap(say, { [`1,${i}`]: "cur", [`1,${i - 1}`]: "dep", [`0,${i}`]: "dep", [`2,${i}`]: "cur" }));
    }
    const cls = { [`2,${n - 1}`]: "best" };
    for (let i = bestStart; i <= bestEnd; i++) cls[`0,${i}`] = "pick";
    const part = numbers.slice(bestStart, bestEnd + 1);
    fr.push(snap(`扫完了。最大和是 ${overall[n - 1]}，对应下标 ${bestStart} 到 ${bestEnd} 这一段 [${part.join(", ")}]（绿色）。`,
      cls, `答案 = ${overall[n - 1]}`));
    return fr;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(rob()) }, "打家劫舍"),
    el("button", { onclick: () => player.load(lis()) }, "最长递增子序列"),
    el("button", { onclick: () => player.load(kadane()) }, "最大子数组和")));
  player.load([rob()[0]]);
})();
