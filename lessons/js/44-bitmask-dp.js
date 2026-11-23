// 动画：状压 DP 两道题。分配任务填 best[assigned_mask]，旅行商填 shortest[visited_mask][last]；行按 mask 从小到大填。
// 橙色 cur = 正在填的格，蓝色 dep = 它用到的格，红色 best = 最终答案（和倒推出的选择），灰色 off = 没有意义的格。
(() => {
  const root = document.getElementById("bitmask-dp");
  const bits = (mask, width) => mask.toString(2).padStart(width, "0");
  const members = mask => [...Array(8).keys()].filter(k => (mask >> k) & 1);
  const bitCount = mask => members(mask).length;
  const show = value => value === Infinity ? "∞" : value;

  // 一张表：t.rowKeys 是每行 data-cell 用的编号，prefix 区分同一画面里的两张表
  function renderTable(t) {
    const head = el("tr", {}, el("th", {}, t.corner), t.cols.map(c => el("th", {}, String(c))));
    const rows = t.rows.map((name, r) => el("tr", {},
      el("th", {}, String(name)),
      t.cols.map((_, c) => {
        const key = (t.prefix || "") + t.rowKeys[r] + "," + c, value = t.grid[r][c];
        return el("td", { class: t.cls[key] || "", "data-cell": key }, value == null ? "" : String(value));
      })));
    return el("table", { class: "dp" }, head, rows);
  }

  function render(f) {
    return [
      ...f.tables.map(t => [el("p", { class: "label" }, t.title), renderTable(t)]).flat(),
      f.extra && el("p", { class: "stat" }, f.extra),
    ];
  }

  const player = new Player(root, render);

  // ---------- 分配任务 ----------
  function assignment() {
    const cost = [[9, 2, 7], [6, 4, 3], [5, 8, 1]];
    const n = cost.length, size = 1 << n;
    const best = Array(size).fill(null);
    const masks = [...Array(size).keys()];
    const snap = (say, cls = {}, extra = "") => ({
      say, extra,
      tables: [
        { title: "cost[骑手][单]", prefix: "c", corner: "骑手 \\ 单", cols: [0, 1, 2], rows: [0, 1, 2], rowKeys: [0, 1, 2], grid: cost, cls },
        { title: "best[assigned_mask]（这些单已经分给前几个骑手时的最少花费）", corner: "assigned_mask", cols: ["已分的单", "best"],
          rows: masks.map(mask => bits(mask, n)), rowKeys: masks,
          grid: masks.map(mask => [`{${members(mask).join(", ")}}`, best[mask] == null ? null : show(best[mask])]), cls },
      ],
    });

    const fr = [snap("3 个骑手按编号顺序接单。assigned_mask 的第 k 位是 1 = 单 k 已经分出去了；分出去几单，就说明前几个骑手安排好了。")];
    best[0] = 0;
    fr.push(snap("初始值：best[000] = 0，一单都没分，不花钱。", { "0,1": "cur" }));
    const chosen = Array(size).fill(null);
    for (let mask = 1; mask < size; mask++) {
      const worker = bitCount(mask) - 1;
      let bestTask = -1, bestValue = Infinity;
      const tries = members(mask).map(task => {
        const value = best[mask ^ (1 << task)] + cost[worker][task];
        if (value < bestValue) { bestValue = value; bestTask = task; }
        return `单 ${task}：best[${bits(mask ^ (1 << task), n)}] + ${cost[worker][task]} = ${value}`;
      });
      best[mask] = bestValue;
      chosen[mask] = bestTask;
      fr.push(snap(
        `assigned_mask = ${bits(mask, n)}：分出去 ${bitCount(mask)} 单，最后安排的是骑手 ${worker}。他送哪单？${tries.join("；")}。取最小 ${bestValue}。`,
        { [`${mask},1`]: "cur", [`${mask ^ (1 << bestTask)},1`]: "dep", [`c${worker},${bestTask}`]: "dep" }));
    }
    // 倒推：从全集开始，每次去掉最后那个骑手送的单
    const cls = { [`${size - 1},1`]: "best" };
    const plan = [];
    for (let mask = size - 1; mask > 0; mask ^= 1 << chosen[mask]) {
      const worker = bitCount(mask) - 1;
      cls[`c${worker},${chosen[mask]}`] = "best";
      plan.unshift(`骑手 ${worker} → 单 ${chosen[mask]}`);
    }
    fr.push(snap(`填完了。best[111] = ${best[size - 1]} 就是答案。倒推回去：${plan.join("，")}（红色）。`, cls, `答案 = ${best[size - 1]}`));
    return fr;
  }

  // ---------- 旅行商 ----------
  function travelingSalesman() {
    const distance = [[0, 2, 9, 10], [2, 0, 6, 4], [9, 6, 0, 3], [10, 4, 3, 0]];
    const n = distance.length, full = (1 << n) - 1;
    const masks = [...Array(1 << n).keys()].filter(mask => mask & 1);  // 只画含配送站 0 的集合
    const shortest = {};
    masks.forEach(mask => { shortest[mask] = Array(n).fill(null); });
    const meaningful = (mask, last) => ((mask >> last) & 1) && (last !== 0 || mask === 1);
    const offCells = {};
    masks.forEach(mask => { for (let last = 0; last < n; last++) if (!meaningful(mask, last)) offCells[`${mask},${last}`] = "off"; });
    const snap = (say, cls = {}, extra = "") => ({
      say, extra,
      tables: [
        { title: "distance[a][b]", prefix: "d", corner: "a \\ b", cols: [0, 1, 2, 3], rows: [0, 1, 2, 3], rowKeys: [0, 1, 2, 3], grid: distance, cls },
        { title: "shortest[visited_mask][last]（从 0 出发、走过这些点、停在 last 的最短距离）", corner: "visited_mask \\ last",
          cols: [0, 1, 2, 3], rows: masks.map(mask => bits(mask, n)), rowKeys: masks,
          grid: masks.map(mask => shortest[mask].map(value => value == null ? null : show(value))), cls: { ...offCells, ...cls } },
      ],
    });

    const fr = [snap("4 个点，0 是配送站。表的每一行是一个“去过的点”的集合（只画含 0 的 8 个），每一列是现在停在哪。灰色格子没有意义：last 不在集合里，或者还没出发就说停在 0。")];
    shortest[1][0] = 0;
    fr.push(snap("初始值：shortest[0001][0] = 0。只去过配送站，停在配送站，走了 0。", { "1,0": "cur" }));
    for (const mask of masks) {
      for (let last = 1; last < n; last++) {
        if (!meaningful(mask, last)) continue;
        const previousMask = mask ^ (1 << last);
        let bestPrevious = -1, bestValue = Infinity;
        const tries = [];
        for (let previous = 0; previous < n; previous++) {
          if (!((previousMask >> previous) & 1) || shortest[previousMask][previous] == null || shortest[previousMask][previous] === Infinity) continue;
          const value = shortest[previousMask][previous] + distance[previous][last];
          tries.push(`从 ${previous} 来：${shortest[previousMask][previous]} + ${distance[previous][last]} = ${value}`);
          if (value < bestValue) { bestValue = value; bestPrevious = previous; }
        }
        shortest[mask][last] = bestValue;
        fr.push(snap(
          `visited_mask = ${bits(mask, n)}，停在 ${last}。去掉 ${last} 是 ${bits(previousMask, n)}，上一站可能是：${tries.join("；")}。取最小 ${bestValue}。`,
          { [`${mask},${last}`]: "cur", [`${previousMask},${bestPrevious}`]: "dep", [`d${bestPrevious},${last}`]: "dep" }));
      }
    }
    // 全都走过以后回站
    const totals = [...Array(n).keys()].slice(1).map(last => shortest[full][last] + distance[last][0]);
    const answer = Math.min(...totals);
    const cls = {};
    totals.forEach((total, index) => { if (total === answer) cls[`${full},${index + 1}`] = "best"; });
    const lines = totals.map((total, index) => `停在 ${index + 1}：${shortest[full][index + 1]} + ${distance[index + 1][0]} = ${total}`);
    fr.push(snap(`所有点都去过了（1111 这一行），还要回到配送站：${lines.join("；")}。最短 ${answer}，路线 0 → 1 → 3 → 2 → 0（反过来走也是 ${answer}，所以有两格并列）。`,
      cls, `答案 = ${answer}`));
    return fr;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(assignment()) }, "分配任务"),
    el("button", { onclick: () => player.load(travelingSalesman()) }, "旅行商")));
  player.load([assignment()[0]]);
})();
