// 动画：把 DP 表一格一格填出来。当前格橙色，它依赖的格子蓝色，LCS 回溯的路线红色。
(() => {
  const root = document.getElementById("dp");

  function render(f) {
    const head = el("tr", {}, el("th", {}, f.corner), f.cols.map(c => el("th", {}, c)));
    const rows = f.rows.map((r, i) => el("tr", {},
      el("th", {}, r),
      f.cols.map((_, j) => {
        const k = i + "," + j, v = f.grid[i][j];
        const cls = f.cur === k ? "cur" : f.deps.includes(k) ? "dep" : f.path.includes(k) ? "path" : "";
        return el("td", { class: cls, "data-cell": k }, v == null ? "" : String(v));
      })));
    return [el("table", { class: "dp" }, head, rows), f.extra && el("p", { class: "stat" }, f.extra)];
  }

  const player = new Player(root, render);
  let base;  // 当前这张表的行名、列名
  const snap = (grid, say, { cur = null, deps = [], path = [], extra = "" } = {}) =>
    ({ ...base, grid: grid.map(r => [...r]), say, cur, deps, path, extra });

  function knapsack() {
    const items = [[1, 15], [3, 20], [4, 30]], cap = 5;
    base = { corner: "物品 \\ 容量 c", cols: [...Array(cap + 1).keys()],
      rows: ["不拿任何物品", ...items.map(([w, v], k) => `+物品${k + 1}（重${w} 值${v}）`)] };
    const g = items.map(() => Array(cap + 1).fill(null));
    g.unshift(Array(cap + 1).fill(0));
    const fr = [snap(g, "第 0 行：一件都不拿，价值都是 0。接下来一行行、从左到右填。")];
    items.forEach(([w, v], k) => {
      const i = k + 1;
      for (let c = 0; c <= cap; c++) {
        const up = g[i - 1][c];
        if (w > c) {
          g[i][c] = up;
          fr.push(snap(g, `容量 ${c} 装不下物品${i}（重 ${w}），只能不选：抄上面 ${up}。`,
            { cur: `${i},${c}`, deps: [`${i - 1},${c}`] }));
        } else {
          const take = g[i - 1][c - w] + v;
          g[i][c] = Math.max(up, take);
          fr.push(snap(g, `不选 = 上面 ${up}；选 = 上一行第 ${c - w} 格 ${g[i - 1][c - w]} + ${v} = ${take}。取大的：${g[i][c]}。`,
            { cur: `${i},${c}`, deps: [`${i - 1},${c}`, `${i - 1},${c - w}`] }));
        }
      }
    });
    fr.push(snap(g, `填完了。右下角就是答案：容量 ${cap} 最多拿到 ${g[items.length][cap]}。`,
      { cur: `${items.length},${cap}` }));
    return fr;
  }

  function lcs() {
    const a = "ABCB", b = "BDCAB";
    base = { corner: "a \\ b", cols: ["\"\"", ...b], rows: ["\"\"", ...a] };
    const g = [Array(b.length + 1).fill(0), ...[...a].map(() => [0, ...Array(b.length).fill(null)])];
    const fr = [snap(g, "第 0 行、第 0 列：和空串比，LCS 都是 0。")];
    for (let i = 1; i <= a.length; i++) {
      for (let j = 1; j <= b.length; j++) {
        const cur = `${i},${j}`;
        if (a[i - 1] === b[j - 1]) {
          g[i][j] = g[i - 1][j - 1] + 1;
          fr.push(snap(g, `${a[i - 1]} = ${b[j - 1]}，相同！左上 ${g[i - 1][j - 1]} + 1 = ${g[i][j]}。`,
            { cur, deps: [`${i - 1},${j - 1}`] }));
        } else {
          g[i][j] = Math.max(g[i - 1][j], g[i][j - 1]);
          fr.push(snap(g, `${a[i - 1]} ≠ ${b[j - 1]}，取上面 ${g[i - 1][j]} 和左边 ${g[i][j - 1]} 里大的：${g[i][j]}。`,
            { cur, deps: [`${i - 1},${j}`, `${i},${j - 1}`] }));
        }
      }
    }
    // 从右下角往回走，找出一个 LCS
    let i = a.length, j = b.length, out = "";
    const path = [];
    fr.push(snap(g, `表填完了，LCS 长度 = 右下角 ${g[i][j]}。下面从右下角往回走，把它找出来。`, { cur: `${i},${j}` }));
    while (i > 0 && j > 0) {
      path.push(`${i},${j}`);
      if (a[i - 1] === b[j - 1]) {
        out = a[i - 1] + out;
        fr.push(snap(g, `${a[i - 1]} 相同：收下它，走左上。`, { path: [...path], extra: `已收下：${out}` }));
        i--; j--;
      } else if (g[i - 1][j] >= g[i][j - 1]) {
        fr.push(snap(g, "字符不同：往上走（上面不比左边小）。", { path: [...path], extra: `已收下：${out}` }));
        i--;
      } else {
        fr.push(snap(g, "字符不同：往左走（左边更大）。", { path: [...path], extra: `已收下：${out}` }));
        j--;
      }
    }
    fr.push(snap(g, `走到边上，结束。一个最长公共子序列是 ${out}（长度 ${out.length}）。`,
      { path, extra: `LCS = ${out}` }));
    return fr;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(knapsack()) }, "0-1 背包"),
    el("button", { onclick: () => player.load(lcs()) }, "LCS")));
  player.load([knapsack()[0]]);
})();
