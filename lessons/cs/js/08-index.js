// 第 8 课的两个动画。
// 1. #btree：orders 表按主键 id 建的一棵三层 B+ 树（缩小版：27 行），比较「用索引查找」「全表扫描」「范围查询」各读几页。
// 2. #leftmost：联合索引 (user_id, status, created_at) 的最左前缀检查器，逐列看哪些列能用来定位。
const SVG_NS = "http://www.w3.org/2000/svg";
function svgElement(tag, attrs, text) {
  const e = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text != null) e.textContent = text;
  return e;
}

// ---------- 动画 1：B+ 树查找 vs 全表扫描 ----------
(() => {
  const root = document.getElementById("btree");
  // 叶子：9 页，每页放 3 行（id 1～27）。第 2 层：3 个节点，每个管 3 个叶子。根：管 3 个第 2 层节点。
  const LEAVES = Array.from({ length: 9 }, (_, i) => [3 * i + 1, 3 * i + 2, 3 * i + 3]);
  const INNER = [[4, 7], [13, 16], [22, 25]];
  const ROOT_KEYS = [10, 19];
  const MAX_ID = 27;
  // 节点里有几个键 ≤ x，就走第几个指针（从 0 数）
  const childIndex = (keys, x) => keys.filter(k => k <= x).length;

  const LEAF_W = 62, LEAF_GAP = 8, LEFT = 3, LEAF_Y = 170, INNER_Y = 92, ROOT_Y = 20, NODE_H = 30;
  const leafX = i => LEFT + i * (LEAF_W + LEAF_GAP);
  const innerCenter = j => leafX(3 * j) + (3 * LEAF_W + 2 * LEAF_GAP) / 2;

  function nodeBox(g, x, y, w, keys, state, hitKeys) {
    g.append(svgElement("rect", { x, y, width: w, height: NODE_H, rx: 3, class: state, "data-node": "" }));
    const cell = w / keys.length;
    keys.forEach((k, i) => {
      const hit = hitKeys && hitKeys.includes(k);
      if (hit) g.append(svgElement("rect", { x: x + i * cell + 2, y: y + 4, width: cell - 4, height: NODE_H - 8, rx: 2, class: "ok key-hit" }));
      g.append(svgElement("text", { x: x + i * cell + cell / 2, y: y + 20, "text-anchor": "middle", class: "mono" }, k));
    });
  }

  function treeSvg(frame) {
    const svg = svgElement("svg", { viewBox: "0 0 640 250", width: 640, class: "bptree" });
    const st = id => frame.states[id] || (frame.mode === "scan" && id[0] !== "l" ? "muted" : "plain");
    // 连线：根 → 第 2 层 → 叶子
    INNER.forEach((_, j) => svg.append(svgElement("line", { x1: 320, y1: ROOT_Y + NODE_H, x2: innerCenter(j), y2: INNER_Y, class: frame.mode === "scan" ? "dash" : "line" })));
    LEAVES.forEach((_, i) => {
      const j = Math.floor(i / 3);
      svg.append(svgElement("line", { x1: innerCenter(j), y1: INNER_Y + NODE_H, x2: leafX(i) + LEAF_W / 2, y2: LEAF_Y, class: frame.mode === "scan" ? "dash" : "line" }));
    });
    // 叶子之间的链表
    for (let i = 0; i < 8; i++) {
      svg.append(svgElement("line", { x1: leafX(i) + LEAF_W, y1: LEAF_Y + NODE_H / 2, x2: leafX(i + 1) - 1, y2: LEAF_Y + NODE_H / 2, class: "arrow-blue", "marker-end": "url(#arrow-blue)" }));
    }
    const g = svgElement("g", {});
    nodeBox(g, 275, ROOT_Y, 90, ROOT_KEYS, st("r"));
    INNER.forEach((keys, j) => nodeBox(g, innerCenter(j) - 45, INNER_Y, 90, keys, st("i" + j)));
    LEAVES.forEach((keys, i) => nodeBox(g, leafX(i), LEAF_Y, LEAF_W, keys, st("l" + i), frame.hits));
    svg.append(g);
    svg.append(svgElement("text", { x: 265, y: ROOT_Y + 20, "text-anchor": "end", class: "small" }, "根（第 1 层）"));
    svg.append(svgElement("text", { x: 375, y: ROOT_Y + 20, class: "small" }, "只存键和指针"));
    svg.append(svgElement("text", { x: 320, y: LEAF_Y + 52, "text-anchor": "middle", class: "small" },
      "叶子（第 3 层）：每个格子是一整行订单，叶子之间用链表从左到右串起来"));
    svg.append(svgElement("text", { x: 320, y: LEAF_Y + 72, "text-anchor": "middle", class: "small" },
      "橙色 = 正在读的页，绿色 = 已经读过的页，灰色 = 没读"));
    return svg;
  }

  const listIds = ids => {
    if (!ids.length) return "（没找到）";
    if (ids.length <= 4) return ids.join(", ");
    return `${ids[0]}, ${ids[1]}, …, ${ids[ids.length - 1]}`;
  };

  function makeFrames(mode, steps) {
    // steps: [{node, say, hits}]，每一步读一页
    const frames = [];
    const states = {};
    let hits = [];
    frames.push({ mode, states: {}, hits: [], reads: 0, found: null, say: steps.intro });
    steps.list.forEach((s, n) => {
      for (const k of Object.keys(states)) if (states[k] === "hot") states[k] = "ok";
      states[s.node] = "hot";
      hits = hits.concat(s.hits || []);
      frames.push({ mode, states: { ...states }, hits: [...hits], reads: n + 1, found: null, say: s.say });
    });
    for (const k of Object.keys(states)) if (states[k] === "hot") states[k] = "ok";
    frames.push({ mode, states: { ...states }, hits: [...hits], reads: steps.list.length, found: hits, say: steps.outro(steps.list.length, hits) });
    return frames;
  }

  function lookup(x) {
    const list = [];
    const c1 = childIndex(ROOT_KEYS, x);
    list.push({ node: "r", say: `读第 1 页（根）：键是 10、19。${x} ${x < 10 ? "< 10，走第 1 个指针" : x < 19 ? "在 10 和 19 之间，走第 2 个指针" : "≥ 19，走第 3 个指针"}。` });
    const keys = INNER[c1];
    const c2 = childIndex(keys, x);
    list.push({ node: "i" + c1, say: `读第 2 页（第 2 层）：键是 ${keys.join("、")}。${x} ${c2 === 0 ? `< ${keys[0]}，走第 1 个指针` : c2 === 1 ? `在 ${keys[0]} 和 ${keys[1]} 之间，走第 2 个指针` : `≥ ${keys[1]}，走第 3 个指针`}。` });
    const li = 3 * c1 + c2;
    const hit = LEAVES[li].includes(x) ? [x] : [];
    list.push({ node: "l" + li, hits: hit, say: `读第 3 页（叶子）：里面是 id ${LEAVES[li].join("、")} 的整行。${hit.length ? `找到 id = ${x}，整行数据就在这一页里。` : `没有 id = ${x}：这棵树里不存在这一行。`}` });
    return makeFrames("lookup", {
      intro: `用主键索引找 id = ${x}：从根出发，每层比较一次键，往下走一层就读一页。`,
      list,
      outro: (reads, found) => `完成：一共读了 ${reads} 页，${found.length ? "找到 1 行" : "没找到"}。树有几层就读几页，和表有多少行几乎无关。`,
    });
  }

  function fullScan(x) {
    const list = LEAVES.map((keys, i) => {
      const hit = keys.includes(x) ? [x] : [];
      return { node: "l" + i, hits: hit, say: `读第 ${i + 1} 页：id ${keys.join("、")}。${hit.length ? `有 id = ${x}，记下来，但不能停：没有索引，就不知道后面还有没有。` : `没有 id = ${x}，接着读下一页。`}` };
    });
    return makeFrames("scan", {
      intro: `全表扫描找 id = ${x}：假装上面两层不存在（灰色虚线），只能把 9 个数据页从第 1 页读到最后一页。`,
      list,
      outro: (reads, found) => `完成：读了全部 ${reads} 页，${found.length ? "找到 1 行" : "没找到"}。表有多少页就要读多少页。`,
    });
  }

  function range(a, b) {
    if (a > b) {
      return [{ mode: "range", states: {}, hits: [], reads: 0, found: [], say: `起点 ${a} 比终点 ${b} 大，范围是空的，一页也不用读。` }];
    }
    const list = [];
    const c1 = childIndex(ROOT_KEYS, a);
    list.push({ node: "r", say: `先像查单个 id 一样找起点 ${a}。读第 1 页（根）：键 10、19，走第 ${c1 + 1} 个指针。` });
    const c2 = childIndex(INNER[c1], a);
    list.push({ node: "i" + c1, say: `读第 2 页（第 2 层）：键 ${INNER[c1].join("、")}，走第 ${c2 + 1} 个指针。` });
    let li = 3 * c1 + c2;
    for (;;) {
      const keys = LEAVES[li];
      const hit = keys.filter(k => k >= a && k <= b);
      const last = keys[keys.length - 1];
      const more = last < b && li < LEAVES.length - 1;
      const first = list.length === 2;
      list.push({
        node: "l" + li, hits: hit,
        say: `读第 ${list.length + 1} 页（叶子 ${keys.join("、")}）：${hit.length ? `${hit.join("、")} 在范围内` : "这一页里没有范围内的 id"}。` +
          (more ? `最大的 ${last} 还小于 ${b}，${first ? "不用回到上层，" : ""}沿链表读右边的下一页。` : last >= b ? `已经出现 ≥ ${b} 的 id，后面只会更大，停下。` : "已经是最后一页，停下。"),
      });
      if (!more) break;
      li++;
    }
    return makeFrames("range", {
      intro: `范围查询 id 在 ${a} 到 ${b} 之间：先从根往下找到 ${a} 所在的叶子，再沿叶子链表往右读。`,
      list,
      outro: (reads, found) => `完成：一共读了 ${reads} 页，找到 ${found.length} 行。往下走 3 页，再沿链表多读 ${reads - 3} 页；不用每个 id 都从根重新找一遍。`,
    });
  }

  function render(frame) {
    return [
      treeSvg(frame),
      el("p", { class: "stat" },
        "读页次数 = ", el("b", { class: "page-reads" }, String(frame.reads)),
        frame.found ? el("span", {}, "　找到 ", el("b", { class: "found-count" }, String(frame.found.length)), " 行：", el("span", { class: "found-rows" }, listIds(frame.found))) : null),
    ];
  }

  const player = new Player(root, render);
  const num = (input, fallback) => {
    const v = parseInt(input.value, 10);
    return Number.isFinite(v) ? v : fallback;
  };
  const target = el("input", { type: "number", value: "14", min: "0", max: "40", "aria-label": "要找的 id", class: "num" });
  const from = el("input", { type: "number", value: "8", min: "0", max: "40", "aria-label": "起点", class: "num" });
  const to = el("input", { type: "number", value: "20", min: "0", max: "40", "aria-label": "终点", class: "num" });
  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "要找的 id"), target,
    el("button", { onclick: () => player.load(lookup(num(target, 14))) }, "用索引查找"),
    el("button", { onclick: () => player.load(fullScan(num(target, 14))) }, "全表扫描"),
    el("span", { class: "label" }, "　起点"), from, el("span", { class: "label" }, "终点"), to,
    el("button", { onclick: () => player.load(range(num(from, 8), num(to, 20))) }, "范围查询 id 在 a 到 b 之间")));
  player.load([{ mode: "lookup", states: {}, hits: [], reads: 0, found: null,
    say: `orders 表的缩小版：${MAX_ID} 行，按主键 id 建成三层 B+ 树，每个方框是磁盘上的一页。输入一个 id，点上面的按钮。` }]);
})();

// ---------- 动画 2：最左前缀检查器 ----------
(() => {
  const root = document.getElementById("leftmost");
  const COLUMNS = ["user_id", "status", "created_at"];
  // 联合索引里的条目，已经按 (user_id, status, created_at) 排好序；最后一列是主键 id
  const ENTRIES = [
    [5, "paid", "2026-10-30", 3], [5, "shipped", "2026-11-02", 9],
    [6, "paid", "2026-11-04", 12],
    [7, "paid", "2026-10-28", 2], [7, "paid", "2026-11-03", 8], [7, "paid", "2026-11-05", 15],
    [7, "refund", "2026-11-02", 7], [7, "shipped", "2026-11-06", 18],
    [8, "paid", "2026-11-01", 5], [8, "unpaid", "2026-11-07", 20],
    [9, "paid", "2026-11-08", 22], [9, "shipped", "2026-10-31", 4],
  ];
  // 每个条件：三列各自是什么情况。kind：eq 等值、range 范围、func 对列做了运算、none 没有条件
  const eq = (text, test) => ({ kind: "eq", text, test });
  const rg = (text, test) => ({ kind: "range", text, test });
  const fn = (text, test) => ({ kind: "func", text, test });
  const none = { kind: "none" };
  const CASES = [
    { sql: "user_id = 7", cols: [eq("user_id = 7", e => e[0] === 7), none, none] },
    { sql: "user_id = 7 AND status = 'paid'", cols: [eq("user_id = 7", e => e[0] === 7), eq("status = 'paid'", e => e[1] === "paid"), none] },
    { sql: "status = 'paid' AND user_id = 7", cols: [eq("user_id = 7", e => e[0] === 7), eq("status = 'paid'", e => e[1] === "paid"), none] },
    { sql: "user_id = 7 AND status = 'paid' AND created_at > '2026-11-01'", cols: [eq("user_id = 7", e => e[0] === 7), eq("status = 'paid'", e => e[1] === "paid"), rg("created_at > '2026-11-01'", e => e[2] > "2026-11-01")] },
    { sql: "status = 'paid'", cols: [none, eq("status = 'paid'", e => e[1] === "paid"), none] },
    { sql: "user_id = 7 AND created_at > '2026-11-01'", cols: [eq("user_id = 7", e => e[0] === 7), none, rg("created_at > '2026-11-01'", e => e[2] > "2026-11-01")] },
    { sql: "user_id > 5 AND status = 'paid'", cols: [rg("user_id > 5", e => e[0] > 5), eq("status = 'paid'", e => e[1] === "paid"), none] },
    { sql: "user_id + 1 = 8", cols: [fn("user_id + 1 = 8", e => e[0] + 1 === 8), none, none] },
    { sql: "user_id = 7 AND status = 'paid' AND MONTH(created_at) = 11", cols: [eq("user_id = 7", e => e[0] === 7), eq("status = 'paid'", e => e[1] === "paid"), fn("MONTH(created_at) = 11", e => e[2].slice(5, 7) === "11")] },
  ];

  function simulate(c) {
    const frames = [];
    const chips = COLUMNS.map(() => ({ state: "pending", note: "" }));
    const used = [];           // 用上的列的下标
    let stopped = false;
    const inRange = e => used.every(i => c.cols[i].test(e));
    const snap = (say, final) => ({
      c, chips: chips.map(x => ({ ...x })), used: [...used], say, final,
      scanned: ENTRIES.map(inRange),
      matched: final ? ENTRIES.map(e => inRange(e) && c.cols.every(s => s.kind === "none" || s.test(e))) : null,
    });
    frames.push(snap(`WHERE ${c.sql}。按索引列的顺序 user_id → status → created_at，从最左边一列开始逐列检查。`, false));
    COLUMNS.forEach((col, i) => {
      const s = c.cols[i];
      let say;
      if (stopped) {
        chips[i] = { state: "skip", note: s.kind === "none" ? "没有条件" : "只能逐条过滤" };
        say = `${col}：前面已经停下了，这一列${s.kind === "none" ? "也没有条件" : `的条件 ${s.text} 不能再用来定位，只能在找到的那一段里逐条检查`}。`;
      } else if (s.kind === "none") {
        stopped = true;
        chips[i] = { state: "stop", note: "缺了这一列，停下" };
        say = i === 0
          ? "user_id：条件里没有 user_id。索引首先按 user_id 排序，不知道 user_id，就不知道从哪里开始找，整个索引都用不上。"
          : `${col}：条件里没有 ${col}。在同一个 ${COLUMNS[i - 1]} 里，后面的列只有在 ${col} 也相同时才有序；跳过 ${col}，后面的列就是乱的，停在这里。`;
      } else if (s.kind === "func") {
        stopped = true;
        chips[i] = { state: "stop", note: "对列做了运算，停下" };
        say = `${col}：条件是 ${s.text}，对列做了运算或套了函数。索引里存的是 ${col} 本身的值、按它排序，不是按运算结果排序，没法用来定位，停在这里。`;
      } else if (s.kind === "range") {
        used.push(i);
        stopped = true;
        chips[i] = { state: "used", note: "范围：用上，然后停下" };
        say = `${col}：${s.text} 是范围条件，能用来定位一段连续的条目，用上了。但这一段里有好几种 ${col}，${i < 2 ? "后面的列在这一段里不再有序，从这里停下" : "它已经是最后一列"}。`;
      } else {
        used.push(i);
        chips[i] = { state: "used", note: "等值：用上" };
        say = `${col}：${s.text} 是等值条件，用上了。${col} 相同的条目挨在一起，而且它们内部按下一列排好了序，可以继续往下看。`;
      }
      frames.push(snap(say, false));
    });
    const n = used.length;
    const last = frames[frames.length - 1];
    const scanned = last.scanned.filter(Boolean).length;
    const f = snap("", true);
    const matched = f.matched.filter(Boolean).length;
    f.say = n === 0
      ? `结论：这个索引一列也用不上，只能把 ${ENTRIES.length} 条全部检查一遍（实际是全表扫描），满足条件的有 ${matched} 条。`
      : `结论：用上了 ${n} 列（${used.map(i => COLUMNS[i]).join("、")}），索引直接定位到 ${scanned} 条（橙色和绿色），逐条检查后满足全部条件的是绿色的 ${matched} 条。`;
    frames.push(f);
    return frames;
  }

  const usedText = used => used.length ? `用上 ${used.length} 列：${used.map(i => COLUMNS[i]).join(" → ")}` : "用上 0 列：这个索引用不上";

  function render(f) {
    const chipRow = el("div", { class: "row col-chips" },
      el("span", { class: "label" }, "索引列："),
      ...COLUMNS.map((col, i) => el("span", { class: `col-chip ${f.chips[i].state}`, "data-col": col },
        el("b", {}, col), el("span", { class: "chip-note" }, f.chips[i].note || (f.c.cols[i].kind === "none" ? "（无条件）" : f.c.cols[i].text)))));
    const rows = ENTRIES.map((e, k) => {
      const cls = f.matched ? (f.matched[k] ? "match" : f.scanned[k] ? "scan" : "") : (f.scanned[k] && f.used.length ? "scan" : "");
      return el("tr", { class: cls }, ...e.map(v => el("td", {}, String(v))));
    });
    return [
      el("div", { class: "sql-where mono" }, `SELECT * FROM orders WHERE ${f.c.sql}`),
      chipRow,
      el("table", { class: "idx-entries" },
        el("tr", {}, ...["user_id", "status", "created_at", "id（主键）"].map(h => el("th", {}, h))),
        ...rows),
      f.final && el("p", { class: "stat" },
        "结论：", el("b", { class: "used-columns" }, usedText(f.used)),
        "　索引定位到 ", el("b", { class: "scan-count" }, String(f.used.length ? f.scanned.filter(Boolean).length : ENTRIES.length)), " 条，",
        "满足条件 ", el("b", { class: "match-count" }, String(f.matched.filter(Boolean).length)), " 条"),
    ];
  }

  const player = new Player(root, render);
  root.prepend(el("div", { class: "ops-bar" },
    ...CASES.map(c => el("button", { onclick: () => player.load(simulate(c)) }, c.sql))));
  player.load([{
    c: { sql: "（先点上面的一个条件）", cols: [none, none, none] },
    chips: COLUMNS.map(() => ({ state: "pending", note: "" })), used: [], scanned: ENTRIES.map(() => false), matched: null, final: false,
    say: "联合索引 (user_id, status, created_at) 里的 12 个条目，已经按这三列排好序。点一个 WHERE 条件，看能用上几列。",
  }]);
})();
