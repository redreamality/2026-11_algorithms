// 动画：区间 DP 两道题。石子合并枚举分割点，最长回文子序列看两端；都按区间长度从短到长填表。
// 表格：行是左端点 i，列是右端点 j。橙色 cur = 正在填的格，蓝色 dep = 它用到的格，红色 best = 最终答案，灰色 off = i > j 没有意义。
(() => {
  const root = document.getElementById("interval-dp");

  function renderTable(f) {
    const n = f.items.length;
    const head = el("tr", {}, el("th", {}, "i \\ j"), f.items.map((_, j) => el("th", {}, String(j))));
    const rows = f.items.map((_, i) => el("tr", {},
      el("th", {}, String(i)),
      f.items.map((_, j) => {
        const key = i + "," + j, value = f.grid[i][j];
        const cls = i > j ? "off" : f.cls[key] || "";
        return el("td", { class: cls, "data-cell": key }, value == null ? "" : String(value));
      })));
    return el("table", { class: "dp" }, head, rows);
  }

  function render(f) {
    // 上面一排是原始数据，正在处理的区间 i..j 标成橙色
    const items = el("div", { class: "row items" }, el("span", { class: "label" }, f.itemsLabel),
      f.items.map((item, k) => box(item, f.range && k >= f.range[0] && k <= f.range[1] ? "hot" : "")));
    return [items, el("p", { class: "label" }, f.tableTitle), renderTable(f), f.extra && el("p", { class: "stat" }, f.extra)];
  }

  const player = new Player(root, render);
  const copy = grid => grid.map(row => [...row]);

  // ---------- 石子合并 ----------
  function mergeStones() {
    const piles = [3, 4, 2, 4];
    const n = piles.length;
    const prefixTotal = [0];
    piles.forEach(pile => prefixTotal.push(prefixTotal[prefixTotal.length - 1] + pile));
    const cost = piles.map(() => piles.map(() => null));
    const base = { items: piles, itemsLabel: "piles：", tableTitle: "merge_cost[i][j]（把第 i 堆到第 j 堆合成一堆的最少代价）" };
    const snap = (say, cls = {}, range = null, extra = "") => ({ ...base, grid: copy(cost), cls, range, say, extra });

    const fr = [snap("一排 4 堆石子，每次合并相邻两堆，代价是新堆的石子数。merge_cost[i][j] = 区间 i..j 合成一堆的最少代价。灰色格子 i > j 没有意义。")];
    const diagonal = {};
    for (let i = 0; i < n; i++) { cost[i][i] = 0; diagonal[`${i},${i}`] = "cur"; }
    fr.push(snap("长度 1：只有一堆，不用合，对角线全填 0。这是初始值。", diagonal, null, "区间长度 = 1"));

    for (let length = 2; length <= n; length++) {
      for (let i = 0; i + length - 1 < n; i++) {
        const j = i + length - 1;
        const rangeTotal = prefixTotal[j + 1] - prefixTotal[i];
        let bestSplit = i, bestValue = Infinity;
        const tries = [];
        for (let k = i; k < j; k++) {
          const value = cost[i][k] + cost[k + 1][j];
          tries.push(`k = ${k}：${cost[i][k]} + ${cost[k + 1][j]} = ${value}`);
          if (value < bestValue) { bestValue = value; bestSplit = k; }
        }
        cost[i][j] = bestValue + rangeTotal;
        const left = piles.slice(i, bestSplit + 1).join(" "), right = piles.slice(bestSplit + 1, j + 1).join(" ");
        fr.push(snap(
          `区间 ${i}..${j}，石子总数 ${rangeTotal}。枚举分割点：${tries.join("；")}。` +
          `最小的是 k = ${bestSplit}（[${left}] 和 [${right}]），填 ${bestValue} + ${rangeTotal} = ${cost[i][j]}。`,
          { [`${i},${j}`]: "cur", [`${i},${bestSplit}`]: "dep", [`${bestSplit + 1},${j}`]: "dep" },
          [i, j], `区间长度 = ${length}`));
      }
    }
    fr.push(snap(`填完了。右上角就是整排石子的答案：最少总代价 ${cost[0][n - 1]}。最后一步是 [3 4] 和 [2 4] 两块合并。`,
      { [`0,${n - 1}`]: "best" }, [0, n - 1], `答案 = ${cost[0][n - 1]}`));
    return fr;
  }

  // ---------- 最长回文子序列 ----------
  function palindromeSubsequence() {
    const text = "bbbab";
    const n = text.length;
    const longest = [...text].map(() => [...text].map(() => null));
    const base = { items: [...text], itemsLabel: "text：", tableTitle: "longest[i][j]（text[i..j] 里最长回文子序列的长度）" };
    const snap = (say, cls = {}, range = null, extra = "") => ({ ...base, grid: copy(longest), cls, range, say, extra });

    const fr = [snap(`text = "${text}"。longest[i][j] = text[i..j] 里最长回文子序列的长度。只看两端：相同就配成一对，不同就扔掉一端。`)];
    const diagonal = {};
    for (let i = 0; i < n; i++) { longest[i][i] = 1; diagonal[`${i},${i}`] = "cur"; }
    fr.push(snap("长度 1：单个字符就是回文，对角线全填 1。", diagonal, null, "区间长度 = 1"));

    for (let length = 2; length <= n; length++) {
      for (let i = 0; i + length - 1 < n; i++) {
        const j = i + length - 1;
        const piece = text.slice(i, j + 1);
        let say, cls = { [`${i},${j}`]: "cur" };
        if (text[i] === text[j]) {
          const inner = length === 2 ? 0 : longest[i + 1][j - 1];
          longest[i][j] = inner + 2;
          if (length > 2) cls[`${i + 1},${j - 1}`] = "dep";
          say = `区间 ${i}..${j} = "${piece}"：两端都是 ${text[i]}，配成一对放最外层。` +
            (length === 2 ? "中间是空串，算 0，" : `中间 ${i + 1}..${j - 1} 是 ${inner}，`) + `填 ${inner} + 2 = ${longest[i][j]}。`;
        } else {
          const dropLeft = longest[i + 1][j], dropRight = longest[i][j - 1];
          longest[i][j] = Math.max(dropLeft, dropRight);
          cls[`${i + 1},${j}`] = "dep";
          cls[`${i},${j - 1}`] = "dep";
          say = `区间 ${i}..${j} = "${piece}"：两端 ${text[i]} ≠ ${text[j]}，至少扔掉一端。扔左端看 ${i + 1}..${j} 是 ${dropLeft}，` +
            `扔右端看 ${i}..${j - 1} 是 ${dropRight}，填 ${longest[i][j]}。`;
        }
        fr.push(snap(say, cls, [i, j], `区间长度 = ${length}`));
      }
    }
    fr.push(snap(`填完了。右上角 longest[0][${n - 1}] = ${longest[0][n - 1]}：最长回文子序列是 "bbbb"（跳过了 a）。`,
      { [`0,${n - 1}`]: "best" }, [0, n - 1], `答案 = ${longest[0][n - 1]}`));
    return fr;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(mergeStones()) }, "石子合并"),
    el("button", { onclick: () => player.load(palindromeSubsequence()) }, "最长回文子序列")));
  player.load([mergeStones()[0]]);
})();
