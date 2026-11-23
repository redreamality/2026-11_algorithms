// 动画：一条 SELECT 的执行顺序。每帧 = 高亮当前执行的子句 + 这一步之后的中间结果表。
// 数据和讲解页第 2 节的三张表完全一致。
(() => {
  const root = document.getElementById("query-order");
  const USERS = [[1, "张三", "北京"], [2, "李四", "上海"], [3, "王五", "北京"],
                 [4, "赵六", "广州"], [5, "孙七", "深圳"], [6, "周八", null]];
  const PRODUCTS = [[1, "键盘", 199, 30], [2, "鼠标", 99, 50], [3, "显示器", 999, 5],
                    [4, "耳机", 299, 0], [5, "U盘", 49, 100]];
  const ORDERS = [[1, 1, 1, 1, "2026-11-01"], [2, 1, 2, 2, "2026-11-03"], [3, 2, 3, 1, "2026-11-05"],
                  [4, 3, 2, 1, "2026-11-08"], [5, 4, 5, 2, "2026-10-28"], [6, 4, 2, 1, "2026-11-12"],
                  [7, 5, 4, 1, "2026-11-15"], [8, 2, 5, 4, "2026-11-18"]];
  const user = id => USERS.find(u => u[0] === id);
  const product = id => PRODUCTS.find(p => p[0] === id);

  // 一张中间表：label 标题；cols 列名；rows 每行 {cells, cls}；newCols 这一步新出现的列；result 是否最终结果
  const table = (label, cols, rows, extra = {}) => ({ label, cols, rows, newCols: [], result: false, ...extra });
  const row = (cells, cls = "") => ({ cells, cls });
  const line = (step, text) => ({ step, text });
  const USER_COLS = ["id", "name", "city"];

  // ---------- 主查询：各城市 11 月销售额前两名 ----------
  function mainSteps() {
    const base = ORDERS.map(o => ({ o, u: user(o[1]), p: product(o[2]) }));
    const steps = [];
    steps.push({ line: 1, say: "第 1 步 FROM：先拿到订单表 orders，共 8 行。",
      tables: [table("FROM orders o", ["o.id", "o.user_id", "o.product_id", "o.quantity", "o.created_at"],
        base.map(r => row(r.o)))] });
    steps.push({ line: 2, say: "第 2 步 JOIN users：每笔订单按 o.user_id = u.id 找到下单人，拼上他的城市 u.city。还是 8 行，只是多了一列。",
      tables: [table("JOIN users u 之后", ["o.id", "o.user_id", "u.city", "o.product_id", "o.quantity", "o.created_at"],
        base.map(r => row([r.o[0], r.o[1], r.u[2], r.o[2], r.o[3], r.o[4]])), { newCols: [2] })] });
    const cols = ["o.id", "o.user_id", "u.city", "o.product_id", "p.price", "o.quantity", "o.created_at"];
    const wide = r => [r.o[0], r.o[1], r.u[2], r.o[2], r.p[2], r.o[3], r.o[4]];
    steps.push({ line: 3, say: "仍是第 2 步：再按 o.product_id = p.id 找到商品，拼上单价 p.price。",
      tables: [table("JOIN products p 之后", cols, base.map(r => row(wide(r))), { newCols: [4] })] });
    const keep = r => r.o[4] >= "2026-11-01";
    const dropped = base.filter(r => !keep(r));
    const kept = base.filter(keep);
    steps.push({ line: 4, say: `第 3 步 WHERE：逐行判断 o.created_at >= '2026-11-01'。订单 ${dropped.map(r => r.o[0]).join("、")} 是 ${dropped.map(r => r.o[4]).join("、")}，条件为假，划掉。剩 ${kept.length} 行。`,
      tables: [table("WHERE 之后", cols, base.map(r => row(wide(r), keep(r) ? "" : "gone")))] });
    const cities = [...new Set(kept.map(r => r.u[2]))];
    const groupOf = r => cities.indexOf(r.u[2]);
    const grouped = [...kept].sort((a, b) => groupOf(a) - groupOf(b) || a.o[0] - b.o[0]);
    const amount = r => r.o[3] * r.p[2];
    const groups = cities.map((city, g) => {
      const rs = grouped.filter(r => groupOf(r) === g);
      return { city, g, ids: rs.map(r => r.o[0]), total: rs.reduce((s, r) => s + amount(r), 0) };
    });
    steps.push({ line: 5, say: `第 4 步 GROUP BY：按 u.city 把 ${kept.length} 行分成 ${groups.length} 组（同色 = 同一组）：${groups.map(x => `${x.city}（订单 ${x.ids.join("、")}）`).join("、")}。最右一列先把每行的 quantity × price 算好，方便下一步求和。`,
      tables: [table("GROUP BY u.city 之后", [...cols, "quantity × price"],
        grouped.map(r => row([...wide(r), amount(r)], "g" + groupOf(r))), { newCols: [7] })] });
    const passes = x => x.total > 200;
    const failed = groups.filter(x => !passes(x));
    steps.push({ line: 6, say: `第 5 步 HAVING：每组只剩一行，算出组内 SUM：${groups.map(x => `${x.city} ${x.total}`).join("，")}。${failed.map(x => `${x.city} ${x.total}`).join("、")} 不超过 200，整组去掉。`,
      tables: [table("HAVING 之后（每组一行）", ["u.city", "组里的订单", "SUM(o.quantity * p.price)"],
        groups.map(x => row([x.city, x.ids.join("、"), x.total], passes(x) ? "g" + x.g : "gone")))] });
    const left = groups.filter(passes);
    steps.push({ line: 0, say: "第 6 步 SELECT：每组输出 city 和 total 两列。别名 total 到这一步才出现，所以前面的 WHERE 里不能用它。",
      tables: [table("SELECT 之后", ["city", "total"], left.map(x => row([x.city, x.total], "g" + x.g)), { newCols: [1] })] });
    const sorted = [...left].sort((a, b) => b.total - a.total);
    steps.push({ line: 7, say: "第 8 步 ORDER BY：按 total 从大到小排。ORDER BY 在 SELECT 之后，所以可以用别名 total。（第 7 步 DISTINCT 这条查询没写，跳过。）",
      tables: [table("ORDER BY total DESC 之后", ["city", "total"], sorted.map(x => row([x.city, x.total], "g" + x.g)))] });
    const top = sorted.slice(0, 2);
    steps.push({ line: 8, say: `第 9 步 LIMIT 2：只留排好序的前两行。最终结果：${top.map(x => `${x.city} ${x.total}`).join("、")}。`,
      tables: [table("LIMIT 2", ["city", "total"], sorted.map((x, i) => row([x.city, x.total], i < 2 ? "" : "gone"))),
               table("最终结果", ["city", "total"], top.map(x => row([x.city, x.total])), { result: true })] });
    return steps;
  }

  // ---------- LEFT JOIN 找没下过单的用户 ----------
  function leftJoinSteps() {
    const joined = [];
    for (const u of USERS) {
      const mine = ORDERS.filter(o => o[1] === u[0]);
      if (mine.length) mine.forEach(o => joined.push({ u, o, padded: false }));
      else joined.push({ u, o: null, padded: true });
    }
    const cols = ["u.id", "u.name", "o.id", "o.created_at"];
    const cells = r => [r.u[0], r.u[1], r.o ? r.o[0] : null, r.o ? r.o[4] : null];
    const kept = joined.filter(r => r.o === null);
    return [
      { line: 1, say: `第 1 步 FROM：左表 users，${USERS.length} 行。`,
        tables: [table("FROM users u", USER_COLS.map(c => "u." + c), USERS.map(u => row(u)))] },
      { line: 2, say: `第 2 步 LEFT JOIN：每个用户配上自己的订单，有几单就变成几行；周八一单都没有，LEFT JOIN 仍给他一行，右表的列全填 NULL（加粗的那行）。共 ${joined.length} 行。`,
        tables: [table("LEFT JOIN orders o 之后", cols, joined.map(r => row(cells(r), r.padded ? "new" : "")), { newCols: [2, 3] })] },
      { line: 3, say: `第 3 步 WHERE o.id IS NULL：配上了订单的行 o.id 都有值，划掉；只剩补出来的 NULL 行，${kept.length} 行。`,
        tables: [table("WHERE 之后", cols, joined.map(r => row(cells(r), r.o === null ? "" : "gone")))] },
      { line: 0, say: `第 6 步 SELECT：输出 u.id 和 u.name。从没下过单的用户：${kept.map(r => r.u[1]).join("、")}。`,
        tables: [table("最终结果", ["u.id", "u.name"], kept.map(r => row([r.u[0], r.u[1]])), { result: true })] },
    ];
  }

  // ---------- COUNT(*) 与 COUNT(列) ----------
  function countSteps() {
    const all = USERS.length;
    const hasCity = USERS.filter(u => u[2] !== null).length;
    const firstSeen = new Set();
    const distinctRow = USERS.map(u => {
      if (u[2] === null) return "gone";
      if (firstSeen.has(u[2])) return "gone";
      firstSeen.add(u[2]);
      return "";
    });
    const cities = firstSeen.size;
    return [
      { line: 2, say: `第 1 步 FROM：users 表，${all} 行。注意周八的 city 是 NULL。`,
        tables: [table("FROM users", USER_COLS, USERS.map(u => row(u)))] },
      { line: [0, 1], say: `第 6 步 SELECT，先算 COUNT(*)：数的是行数，不看列里是什么，周八也算。结果 ${all}。`,
        tables: [table("COUNT(*) 数这些行", USER_COLS, USERS.map(u => row(u)))] },
      { line: [0, 1], say: `再算 COUNT(city)：只数 city 不是 NULL 的行，周八被跳过。结果 ${hasCity}。`,
        tables: [table("COUNT(city) 数这些行", USER_COLS, USERS.map(u => row(u, u[2] === null ? "gone" : "")))] },
      { line: [0, 1], say: `最后 COUNT(DISTINCT city)：不同的、非 NULL 的城市有几种。王五的「北京」和张三重复，只算一次。结果 ${cities}。`,
        tables: [table("COUNT(DISTINCT city) 数这些行", USER_COLS, USERS.map((u, i) => row(u, distinctRow[i])))] },
      { line: [0, 1], say: `三个聚合函数把 ${all} 行压成一行：${all}、${hasCity}、${cities}。只有 COUNT(*) 会把 NULL 那行算进去。`,
        tables: [table("最终结果", ["all_rows", "has_city", "cities"], [row([all, hasCity, cities])], { result: true })] },
    ];
  }

  // ---------- <> 遇到 NULL ----------
  function nullSteps() {
    const judge = u => (u[2] === null ? "UNKNOWN" : u[2] !== "北京" ? "TRUE" : "FALSE");
    const kept = USERS.filter(u => judge(u) === "TRUE");
    return [
      { line: 1, say: `第 1 步 FROM：users 表，${USERS.length} 行。`,
        tables: [table("FROM users", USER_COLS, USERS.map(u => row(u)))] },
      { line: 2, say: "第 3 步 WHERE：逐行算 city <> '北京'。周八的 city 是 NULL，和任何值比较都得 UNKNOWN；WHERE 只留 TRUE，所以周八和两个北京用户一起被划掉。",
        tables: [table("WHERE 之后", [...USER_COLS, "city <> '北京'"],
          USERS.map(u => row([...u, { v: judge(u), cls: judge(u) === "UNKNOWN" ? "hot" : judge(u) === "TRUE" ? "ok" : "" }],
            judge(u) === "TRUE" ? "" : "gone")), { newCols: [3] })] },
      { line: 0, say: `第 6 步 SELECT：输出 name，共 ${kept.length} 行：${kept.map(u => u[1]).join("、")}。想把周八也算进「不在北京」，要写 WHERE city <> '北京' OR city IS NULL。`,
        tables: [table("最终结果", ["name"], kept.map(u => row([u[1]])), { result: true })] },
    ];
  }

  const QUERIES = [
    { button: "主查询", build: mainSteps,
      intro: "这条查询写的时候 SELECT 在最前面，左边的小数字是它真正的执行顺序。点「下一步」从 FROM 开始看。",
      lines: [line(6, "SELECT u.city, SUM(o.quantity * p.price) AS total"),
              line(1, "FROM orders o"),
              line(2, "  JOIN users u    ON o.user_id = u.id"),
              line(2, "  JOIN products p ON o.product_id = p.id"),
              line(3, "WHERE o.created_at >= '2026-11-01'"),
              line(4, "GROUP BY u.city"),
              line(5, "HAVING SUM(o.quantity * p.price) > 200"),
              line(8, "ORDER BY total DESC"),
              line(9, "LIMIT 2;")] },
    { button: "LEFT JOIN 找没下过单的用户", build: leftJoinSteps,
      intro: "找出一单都没下过的用户：LEFT JOIN 保留左表每一行，配不上的右边补 NULL，再用 IS NULL 把它们挑出来。",
      lines: [line(6, "SELECT u.id, u.name"),
              line(1, "FROM users u"),
              line(2, "  LEFT JOIN orders o ON o.user_id = u.id"),
              line(3, "WHERE o.id IS NULL;")] },
    { button: "COUNT(*) 与 COUNT(列)", build: countSteps,
      intro: "同一张 users 表，三种 COUNT 数出三个不同的数。",
      lines: [line(6, "SELECT COUNT(*) AS all_rows, COUNT(city) AS has_city,"),
              line(6, "       COUNT(DISTINCT city) AS cities"),
              line(1, "FROM users;")] },
    { button: "<> 遇到 NULL", build: nullSteps,
      intro: "「不在北京的用户」：看看 city 为 NULL 的周八会不会被查出来。",
      lines: [line(6, "SELECT name"),
              line(1, "FROM users"),
              line(3, "WHERE city <> '北京';")] },
  ];

  // 把每一步包装成帧：current = 这一步执行的行，done = 之前已经执行过的行
  function toFrames(q) {
    const seen = [];
    const frames = [{ lines: q.lines, current: [], done: [], tables: [], say: q.intro }];
    for (const s of q.build()) {
      const current = [].concat(s.line);
      frames.push({ lines: q.lines, current, done: seen.filter(i => !current.includes(i)), tables: s.tables, say: s.say });
      for (const i of current) if (!seen.includes(i)) seen.push(i);
    }
    return frames;
  }

  function renderTable(t) {
    const header = el("tr", {}, t.cols.map((c, i) => el("th", { class: t.newCols.includes(i) ? "new-col" : "" }, c)));
    const body = t.rows.map(r => el("tr", { class: r.cls }, r.cells.map((v, i) => {
      const boxed = v !== null && typeof v === "object";
      const value = boxed ? v.v : v;
      const cls = [boxed ? v.cls : "", value === null ? "null" : "", t.newCols.includes(i) ? "new-col" : ""].filter(Boolean).join(" ");
      return el("td", { class: cls }, value === null ? "NULL" : String(value));
    })));
    return el("div", { class: "mid" },
      el("div", { class: "table-label" }, t.label),
      el("table", { class: t.result ? "mid-table result-table" : "mid-table" }, header, body));
  }

  function render(frame) {
    const lineClass = i => "sql-line" + (frame.current.includes(i) ? " current" : frame.done.includes(i) ? " done" : "");
    return [
      frame.lines.length ? el("div", { class: "sql-lines" },
        frame.lines.map((l, i) => el("div", { class: lineClass(i) }, el("span", { class: "step-no" }, String(l.step)), l.text))) : null,
      ...frame.tables.map(renderTable),
    ];
  }

  const player = new Player(root, render);
  const reset = () => player.load([{ lines: [], current: [], done: [], tables: [],
    say: "点上面的按钮选一条查询，看它按什么顺序执行。" }]);
  root.prepend(el("div", { class: "ops-bar" },
    ...QUERIES.map(q => el("button", { onclick: () => player.load(toFrames(q)) }, q.button)),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
