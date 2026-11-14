// 动画：二维 DP 三道题。最小路径和、编辑距离、最长回文子串，都是一格一格地填表。
// 橙色 cur = 正在填的格，蓝色 dep = 它用到的格，红色 path = 倒推出来的路线，灰色 off = 不需要填的格。
(() => {
  const root = document.getElementById("dp2d");

  // 一张表：prefix 用来区分同一画面里的两张表（data-cell 前缀）
  function renderTable(t) {
    const head = el("tr", {}, el("th", {}, t.corner), t.cols.map(c => el("th", {}, String(c))));
    const rows = t.rows.map((name, i) => el("tr", {},
      el("th", {}, String(name)),
      t.cols.map((_, j) => {
        const key = (t.prefix || "") + i + "," + j, value = t.grid[i][j];
        return el("td", { class: t.cls[key] || "", "data-cell": key }, value == null ? "" : String(value));
      })));
    return el("table", { class: "dp" }, head, rows);
  }

  function render(f) {
    return [
      ...f.tables.map(t => [t.title && el("p", { class: "label" }, t.title), renderTable(t)]).flat(),
      f.extra && el("p", { class: "stat" }, f.extra),
    ];
  }

  const player = new Player(root, render);
  const copy = grid => grid.map(r => [...r]);

  // ---------- 最小路径和 ----------
  function minPath() {
    const grid = [[1, 3, 1], [1, 5, 1], [4, 2, 1]];
    const m = grid.length, n = grid[0].length;
    const cost = grid.map(r => r.map(() => null));
    const labels = { cols: [...Array(n).keys()], rows: [...Array(m).keys()], corner: "i \\ j" };
    const snap = (say, cls = {}, extra = "") => ({
      say, extra,
      tables: [
        { ...labels, title: "grid（每格的数字）", prefix: "g", grid, cls },
        { ...labels, title: "cheapest_cost_to[i][j]（走到这格的最小和）", grid: copy(cost), cls },
      ],
    });
    const fr = [snap("cheapest_cost_to[i][j] = 从左上角走到 (i, j) 路过数字的最小和。从上到下、从左到右填。")];
    for (let i = 0; i < m; i++) {
      for (let j = 0; j < n; j++) {
        const cls = { [`${i},${j}`]: "cur", [`g${i},${j}`]: "dep" };
        let say;
        if (i === 0 && j === 0) {
          cost[i][j] = grid[0][0];
          say = `起点：就是它自己的数字 ${grid[0][0]}。`;
        } else if (i === 0) {
          cost[i][j] = cost[i][j - 1] + grid[i][j];
          cls[`${i},${j - 1}`] = "dep";
          say = `第 0 行只能从左边来：${cost[i][j - 1]} + ${grid[i][j]} = ${cost[i][j]}。`;
        } else if (j === 0) {
          cost[i][j] = cost[i - 1][j] + grid[i][j];
          cls[`${i - 1},${j}`] = "dep";
          say = `第 0 列只能从上面来：${cost[i - 1][j]} + ${grid[i][j]} = ${cost[i][j]}。`;
        } else {
          const up = cost[i - 1][j], left = cost[i][j - 1];
          cost[i][j] = grid[i][j] + Math.min(up, left);
          cls[`${i - 1},${j}`] = "dep"; cls[`${i},${j - 1}`] = "dep";
          say = `上面 ${up}、左边 ${left}，取小的 ${Math.min(up, left)}，加上自己 ${grid[i][j]}，得 ${cost[i][j]}。`;
        }
        fr.push(snap(say, cls));
      }
    }
    // 从右下角倒推路线：每次走向更小的那一格（上或左）
    const cls = {}, route = [];
    let i = m - 1, j = n - 1;
    while (true) {
      cls[`${i},${j}`] = "path"; cls[`g${i},${j}`] = "path";
      route.unshift(grid[i][j]);
      if (i === 0 && j === 0) break;
      if (i === 0) j--;
      else if (j === 0) i--;
      else if (cost[i - 1][j] <= cost[i][j - 1]) i--;
      else j--;
    }
    fr.push(snap(`填完了。右下角 ${cost[m - 1][n - 1]} 就是答案。倒推回去，路线是 ${route.join(" → ")}（红色）。`,
      cls, `答案 = ${cost[m - 1][n - 1]}`));
    return fr;
  }

  // ---------- 编辑距离 ----------
  function editDistance() {
    const source = "horse", target = "ros";
    const m = source.length, n = target.length;
    const table = Array.from({ length: m + 1 }, () => Array(n + 1).fill(null));
    const labels = { corner: "source \\ target", cols: ['""', ...target], rows: ['""', ...source] };
    const snap = (say, cls = {}, extra = "") => ({ say, extra, tables: [{ ...labels, grid: copy(table), cls }] });
    for (let j = 0; j <= n; j++) table[0][j] = j;
    for (let i = 0; i <= m; i++) table[i][0] = i;
    const fr = [snap("table[i][j] = 把 source 的前 i 个字符变成 target 的前 j 个字符的最少操作数。" +
      "第 0 行是 j（空串只能插入），第 0 列是 i（只能删除）。")];
    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        const a = source[i - 1], b = target[j - 1];
        const diag = table[i - 1][j - 1], up = table[i - 1][j], left = table[i][j - 1];
        if (a === b) {
          table[i][j] = diag;
          fr.push(snap(`"${source.slice(0, i)}" → "${target.slice(0, j)}"：末尾都是 ${a}，直接对上，不花操作，抄左上 ${diag}。`,
            { [`${i},${j}`]: "cur", [`${i - 1},${j - 1}`]: "dep" }));
        } else {
          table[i][j] = 1 + Math.min(diag, up, left);
          fr.push(snap(`"${source.slice(0, i)}" → "${target.slice(0, j)}"：末尾 ${a} ≠ ${b}。` +
            `左上 ${diag} + 1（把 ${a} 换成 ${b}）、上 ${up} + 1（删掉 ${a}）、左 ${left} + 1（插入 ${b}），最小是 ${table[i][j]}。`,
            { [`${i},${j}`]: "cur", [`${i - 1},${j - 1}`]: "dep", [`${i - 1},${j}`]: "dep", [`${i},${j - 1}`]: "dep" }));
        }
      }
    }
    // 倒推操作：看当前格是从哪一格来的
    const ops = [], cls = {};
    let i = m, j = n;
    while (i > 0 || j > 0) {
      cls[`${i},${j}`] = "path";
      if (i > 0 && j > 0 && source[i - 1] === target[j - 1] && table[i][j] === table[i - 1][j - 1]) { i--; j--; }
      else if (i > 0 && j > 0 && table[i][j] === table[i - 1][j - 1] + 1) { ops.unshift(`把 ${source[i - 1]} 换成 ${target[j - 1]}`); i--; j--; }
      else if (i > 0 && table[i][j] === table[i - 1][j] + 1) { ops.unshift(`删掉 ${source[i - 1]}`); i--; }
      else { ops.unshift(`插入 ${target[j - 1]}`); j--; }
    }
    cls["0,0"] = "path";
    fr.push(snap(`填完了。右下角 ${table[m][n]} 就是答案。从右下角倒推（红色），用到的操作：${ops.join("，")}。`,
      cls, `答案 = ${table[m][n]}`));
    return fr;
  }

  // ---------- 最长回文子串 ----------
  function palindrome() {
    const text = "babad", n = text.length;
    const table = Array.from({ length: n }, () => Array(n).fill(null));
    const off = {};
    for (let i = 0; i < n; i++) for (let j = 0; j < i; j++) off[`${i},${j}`] = "off";
    const labels = { corner: "i \\ j", cols: [...text].map((c, k) => `${k} ${c}`), rows: [...text].map((c, k) => `${k} ${c}`) };
    const snap = (say, cls = {}, extra = "") =>
      ({ say, extra, tables: [{ ...labels, grid: copy(table), cls: { ...off, ...cls } }] });
    const fr = [snap("is_palindrome[i][j] = text[i..j] 是不是回文。只填 i ≤ j 的格子（灰色不用填），按子串长度从 1 到 5 一圈圈往右上填。")];
    let bestStart = 0, bestLength = 0;
    for (let length = 1; length <= n; length++) {
      for (let i = 0; i + length - 1 < n; i++) {
        const j = i + length - 1;
        const piece = text.slice(i, j + 1);
        const sameEnds = text[i] === text[j];
        const cls = { [`${i},${j}`]: "cur" };
        let say;
        if (length <= 2) {
          table[i][j] = sameEnds ? "✓" : "✗";
          say = length === 1 ? `长度 1："${piece}" 单个字符一定是回文。`
            : `长度 2："${piece}" 两端${sameEnds ? "相同，是回文" : "不同，不是回文"}。`;
        } else {
          const inner = table[i + 1][j - 1];
          cls[`${i + 1},${j - 1}`] = "dep";
          table[i][j] = sameEnds && inner === "✓" ? "✓" : "✗";
          say = `长度 ${length}："${piece}" 两端 ${text[i]} 和 ${text[j]} ${sameEnds ? "相同" : "不同"}；` +
            `中间 "${text.slice(i + 1, j)}" 看左下那格 is_palindrome[${i + 1}][${j - 1}] = ${inner}。所以${table[i][j] === "✓" ? "是" : "不是"}回文。`;
        }
        if (table[i][j] === "✓" && length > bestLength) { bestStart = i; bestLength = length; say += " 刷新最长。"; }
        fr.push(snap(say, cls));
      }
    }
    const answer = text.slice(bestStart, bestStart + bestLength);
    fr.push(snap(`填完了。最长的回文子串是 "${answer}"（从下标 ${bestStart} 开始，长度 ${bestLength}，红色那格）。`,
      { [`${bestStart},${bestStart + bestLength - 1}`]: "path" }, `答案 = ${answer}`));
    return fr;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(minPath()) }, "最小路径和"),
    el("button", { onclick: () => player.load(editDistance()) }, "编辑距离"),
    el("button", { onclick: () => player.load(palindrome()) }, "最长回文子串")));
  player.load([editDistance()[0]]);
})();
