// 动画：两个事务的时间线。按 InnoDB 的规则一条条执行语句，每条一帧：
// 左右两列是事务 A、B 执行过的语句；中间是商品 42 的版本链、锁、A 读到的值。
(() => {
  const root = document.getElementById("isolation");
  const LEVELS = { RU: "读未提交", RC: "读已提交", RR: "可重复读", SER: "串行化" };
  const VIEW_NOTE = {
    RU: "不用读视图：直接读最新版本，哪怕没提交",
    RC: "每条 SELECT 都新建一个读视图",
    RR: "第一条 SELECT 建读视图，之后一直用它",
    SER: "普通 SELECT 自动加 S 锁，读最新版本",
  };
  // 每个场景是一串 [事务, 动作, 参数]，四个隔离级别用同一串语句
  const SCENARIOS = {
    dirty: {
      label: "脏读",
      ops: [["A", "begin"], ["A", "read", "stock"], ["B", "begin"], ["B", "update", "stock"],
        ["A", "read", "stock"], ["B", "rollback"], ["A", "read", "stock"], ["A", "commit"]],
    },
    nonrepeat: {
      label: "不可重复读",
      ops: [["A", "begin"], ["A", "read", "price"], ["B", "begin"], ["B", "update", "price"],
        ["B", "commit"], ["A", "read", "price"], ["A", "commit"]],
    },
    phantom: {
      label: "幻读",
      ops: [["A", "begin"], ["A", "range"], ["B", "begin"], ["B", "insert"],
        ["B", "commit"], ["A", "range"], ["A", "commit"]],
    },
    lost: {
      label: "丢失修改",
      ops: [["A", "begin"], ["A", "read", "stock"], ["B", "begin"], ["B", "read", "stock"],
        ["A", "write"], ["A", "commit"], ["B", "write"], ["B", "commit"]],
    },
  };
  const other = t => (t === "A" ? "B" : "A");

  function simulate(scenario, level) {
    let seq = 0; // 全局提交序号：每提交一次加 1，初始数据算第 0 次
    const rows = { 42: [{ stock: 10, price: 99, trx: null, seq: 0 }] }; // 版本链，新版本在前
    let locks = []; // { trx, mode: "S" | "X", target: 42 | 43 | "gap" }
    const view = { A: null, B: null }, lastRead = { A: null, B: null };
    const status = { A: "未开始", B: "未开始" };
    const pending = { A: [], B: [] };
    const readsA = [];
    let dirty = false, deadlock = false, seenA = null;
    const slots = [], frames = [];

    const visible = (t, v) => {
      if (level === "RU" || level === "SER" || v.trx === t) return true;
      if (v.seq === null) return false;
      return v.seq <= (level === "RR" ? view[t] : seq);
    };
    const readRow = (t, id) => (rows[id] || []).find(v => visible(t, v)) || null;
    const conflict = (t, mode, target) => {
      const l = locks.find(l => l.trx !== t && l.target === target && (mode === "X" || l.mode === "X"));
      return l ? l.trx : null;
    };
    const lockName = target => (target === "gap" ? "间隙" : `行 ${target}`);
    const addLock = (trx, mode, target) => {
      if (!locks.some(l => l.trx === trx && l.mode === mode && l.target === target)) locks.push({ trx, mode, target });
    };
    // 这条语句要的锁：[模式, 目标]
    function needs(op) {
      const [, kind] = op;
      if (kind === "update" || kind === "write") return [["X", 42]];
      if (kind === "insert") return [["X", "gap"]];
      if (level === "SER" && kind === "read") return [["S", 42]];
      if (level === "SER" && kind === "range") return [["S", 42], ["S", "gap"]];
      return [];
    }
    const blocker = (t, op) => {
      for (const [mode, target] of needs(op)) {
        const u = conflict(t, mode, target);
        if (u) return { u, mode, target };
      }
      return null;
    };

    const snap = (say, extra = {}) => frames.push({
      level, scenario, say, slots: slots.map(s => ({ ...s })),
      rows: Object.entries(rows).map(([id, versions]) => ({ id: Number(id), versions: versions.map(v => ({ ...v })) })),
      locks: locks.map(l => `${l.trx}：${l.mode} 锁（${lockName(l.target)}）`),
      readA: readsA.length ? readsA[readsA.length - 1] : null,
      seenA: seenA && rows[seenA.id] && rows[seenA.id].includes(seenA.ver) ? { id: seenA.id, idx: rows[seenA.id].indexOf(seenA.ver) } : null, status: { ...status }, viewA: view.A, ...extra,
    });
    const show = (v, kind) => (kind === "range" ? v.join("、") : String(v));

    // 执行一条语句（锁已经确认拿得到），返回 [时间线上的短文字, 解说]
    function execute(t, op) {
      const [, kind, col] = op;
      for (const [mode, target] of needs(op)) addLock(t, mode, target);
      if (kind === "begin") {
        status[t] = "进行中";
        return ["BEGIN", `${t} 开始一个事务。`];
      }
      if (kind === "read") {
        if (level === "RR" && view[t] === null) view[t] = seq;
        const idx = rows[42].findIndex(v => visible(t, v));
        const v = rows[42][idx];
        const value = v[col];
        lastRead[t] = value;
        const isDirty = v.seq === null && v.trx !== t;
        if (t === "A") { readsA.push(value); seenA = { id: 42, ver: v }; if (isDirty) dirty = true; }
        const why = level === "SER" ? "，并给这一行加了 S 锁" : level === "RU" ? "（读未提交：直接读最新版本）"
          : idx === 0 ? ""
          : rows[42][0].seq === null ? `（最新版本是 ${rows[42][0].trx} 没提交的，看不见，顺着版本链往回找到已提交的版本）`
          : `（最新版本是 ${rows[42][0].trx} 在 A 建立读视图之后才提交的，看不见，顺着版本链往回找）`;
        return [`SELECT ${col} → ${value}`,
          `${t} 执行 SELECT ${col} FROM products WHERE id = 42，读到 ${col} = ${value}${why}。${isDirty ? "这是 B 还没提交的值：脏读！" : ""}`];
      }
      if (kind === "range") {
        if (level === "RR" && view[t] === null) view[t] = seq;
        const ids = Object.keys(rows).map(Number).sort((a, b) => a - b)
          .filter(id => { const v = readRow(t, id); return v && v.price <= 100; });
        readsA.push(ids);
        seenA = null;
        const why = level === "SER" ? "；串行化下这条查询给行 42 和它两边的间隙都加了锁" : "";
        return [`SELECT id … → ${ids.join("、")}`,
          `A 执行 SELECT id FROM products WHERE price <= 100，查到 ${ids.length} 行：${ids.join("、")}${why}。`];
      }
      if (kind === "update" || kind === "write") {
        const cur = rows[42][0];
        const v = { ...cur, trx: t, seq: null };
        let short, say;
        if (kind === "update" && col === "stock") {
          v.stock = cur.stock - 1;
          short = "UPDATE stock = stock − 1";
          say = `B 执行 UPDATE products SET stock = stock - 1 WHERE id = 42，生成一个未提交的新版本 stock = ${v.stock}，并给这一行加 X 锁。`;
        } else if (kind === "update") {
          v.price = 109;
          short = "UPDATE price = 109";
          say = "B 执行 UPDATE products SET price = 109 WHERE id = 42（涨价），生成一个未提交的新版本，并给这一行加 X 锁。";
        } else {
          v.stock = lastRead[t] - 1;
          short = `UPDATE stock = ${v.stock}`;
          say = `${t} 拿自己读到的 ${lastRead[t]} 在程序里减 1，执行 UPDATE products SET stock = ${v.stock} WHERE id = 42，并给这一行加 X 锁。`;
        }
        rows[42].unshift(v);
        return [short, say];
      }
      if (kind === "insert") {
        rows[43] = [{ stock: 5, price: 89, trx: t, seq: null }];
        return ["INSERT 商品 43", "B 上架一件新商品：INSERT INTO products (id, price, stock) VALUES (43, 89, 5)。"];
      }
      if (kind === "commit") {
        seq += 1;
        for (const id in rows) for (const v of rows[id]) if (v.trx === t && v.seq === null) v.seq = seq;
        status[t] = "已提交";
        locks = locks.filter(l => l.trx !== t);
        return ["COMMIT", `${t} 提交：它的新版本变成已提交，它持有的锁全部释放。`];
      }
      // rollback
      undo(t);
      return ["ROLLBACK", `${t} 回滚：顺着 undo log 把它写的新版本撤掉，锁全部释放。`];
    }
    function undo(t) {
      for (const id of Object.keys(rows)) {
        rows[id] = rows[id].filter(v => !(v.trx === t && v.seq === null));
        if (!rows[id].length) delete rows[id];
      }
      if (seenA && !rows[seenA.id]) seenA = null;
      status[t] = "已回滚";
      locks = locks.filter(l => l.trx !== t);
    }

    const shortOf = op => ({ read: `SELECT ${op[2]}`, range: "SELECT id …", update: op[2] === "stock" ? "UPDATE stock = stock − 1" : "UPDATE price = 109",
      write: "UPDATE stock = …", insert: "INSERT 商品 43", commit: "COMMIT", rollback: "ROLLBACK", begin: "BEGIN" }[op[1]]);

    // 让事务 t 把排着的语句往下执行，直到被锁挡住或做完
    function drive(t) {
      while (pending[t].length) {
        const op = pending[t][0];
        if (status[t] === "已回滚") {
          pending[t].shift();
          slots.push({ t, text: `${shortOf(op)}（已失效）`, cls: "bad" });
          snap(`${t} 的程序接着发 ${shortOf(op)}，但 ${t} 已经被回滚了，这句不起作用；程序应当重新执行整个事务。`);
          continue;
        }
        const b = blocker(t, op);
        if (b) {
          const slot = { t, text: `等待锁：${shortOf(op)}`, cls: "wait" };
          slots.push(slot);
          const want = `${b.mode} 锁（${lockName(b.target)}）`;
          // 对方是不是也在等自己？是就成环了
          if (pending[b.u].length && blocker(b.u, pending[b.u][0])?.u === t) {
            deadlock = true;
            slot.text = `死锁，被回滚：${shortOf(op)}`;
            slot.cls = "bad";
            pending[t] = [];
            undo(t);
            snap(`${t} 要加 ${want}，但 ${b.u} 持有和它冲突的锁，而 ${b.u} 又在等 ${t} 的锁：互相等待，成环了（死锁）。InnoDB 检测到死锁，回滚 ${t}，释放它的锁。`);
            drive(b.u);
            return;
          }
          snap(`${t} 要执行 ${shortOf(op)}，需要 ${want}，但 ${b.u} 持有和它冲突的锁（${b.u} 还没提交）。${t} 只能等待锁，后面的语句也要排队。`);
          return;
        }
        const resumed = slots.some(s => s.t === t && s.cls === "wait" && !s.resumed);
        const [text, say] = execute(t, op);
        if (resumed) slots.filter(s => s.t === t && s.cls === "wait").forEach(s => { s.resumed = true; });
        pending[t].shift();
        slots.push({ t, text: resumed ? `拿到锁：${text}` : text, cls: resumed ? "ok" : "" });
        snap(resumed ? `${other(t)} 释放了锁，${t} 等到了，接着执行。${say}` : say);
        if (op[1] === "commit" || op[1] === "rollback") drive(other(t));
      }
    }

    snap(`隔离级别：${LEVELS[level]}。场景：${SCENARIOS[scenario].label}。商品 42 开始时 stock = 10、price = 99。`);
    for (const op of SCENARIOS[scenario].ops) {
      const t = op[0];
      pending[t].push(op);
      if (pending[t].length === 1) drive(t);
    }
    const last = frames[frames.length - 1];
    last.verdict = verdict(scenario, level, { readsA, dirty, deadlock, rows });
    return frames;
  }

  function verdict(scenario, level, r) {
    const [first, second] = r.readsA;
    if (scenario === "dirty") return r.dirty
      ? "出现了脏读：A 读到了 B 没提交的 stock = 9，而 B 后来回滚了，这个 9 从来没有真正存在过。"
      : "没有脏读：A 始终没读到 B 未提交的修改。";
    if (scenario === "nonrepeat") return first !== second
      ? `出现了不可重复读：A 在同一个事务里两次读 price，先 ${first} 后 ${second}。`
      : `没有不可重复读：A 两次读到的 price 都是 ${first}。`;
    if (scenario === "phantom") {
      if (first.length !== second.length) return "出现了幻读：A 用同一个条件查第二次，多出了一行商品 43。";
      return level === "SER"
        ? "没有幻读：A 的查询锁住了间隙，B 的 INSERT 只能等 A 提交以后才执行。"
        : "没有幻读：A 的 SELECT 是快照读，读视图里看不到商品 43（换成当前读就能看到，见正文）。";
    }
    const stock = r.rows[42][0].stock;
    return r.deadlock
      ? `没有丢失修改：两个事务互相等对方的 S 锁，形成死锁，InnoDB 回滚了 B。最后 stock = ${stock}，只卖出 1 件；B 重试时会读到 9、写成 8。`
      : `出现了丢失修改：A、B 各卖出 1 件，stock 却只从 10 变成 ${stock}，A 的修改被 B 覆盖了。`;
  }

  function versionBox(v, seen) {
    const state = v.seq === null ? `${v.trx} 未提交` : v.trx ? `${v.trx} 已提交` : "初始";
    return el("span", { class: `ver ${v.seq === null ? "uncommitted" : "committed"}${seen ? " seen" : ""}` },
      el("span", {}, `stock ${v.stock} · price ${v.price}`), el("span", { class: "ver-state" }, state));
  }

  function render(f) {
    const column = t => el("div", { class: `col col-${t.toLowerCase()}` },
      el("div", { class: "col-head" }, `事务 ${t}`, el("span", { class: "label" }, `　${f.status[t]}`)),
      ...f.slots.map((s, i) => el("div", { class: `slot ${s.t === t ? s.cls : "blank"}` }, s.t === t ? `${i + 1}. ${s.text}` : "")));
    const rowsView = f.rows.map(r => {
      const committed = r.versions.find(v => v.seq !== null);
      return el("div", { class: "db-row" },
        el("div", {}, el("b", {}, `商品 ${r.id}`), "　已提交：",
          el("span", { class: "committed" }, committed ? `stock ${committed.stock} · price ${committed.price}` : "（无）")),
        el("div", { class: "chain" }, r.versions.map((v, i) => [i > 0 && el("span", { class: "link" }, "→"),
          versionBox(v, f.seenA && f.seenA.id === r.id && f.seenA.idx === i)]).flat()));
    });
    const read = f.readA === null ? "—" : Array.isArray(f.readA) ? f.readA.join("、") : String(f.readA);
    return [
      el("p", { class: "stat" }, "隔离级别：", el("b", { class: "level" }, LEVELS[f.level]),
        f.scenario && `　场景：${SCENARIOS[f.scenario].label}`),
      el("div", { class: "tl" },
        column("A"),
        el("div", { class: "db" },
          el("div", { class: "col-head" }, "数据库"),
          ...rowsView,
          el("div", { class: "label" }, "版本链：左边最新，→ 指向更旧的版本"),
          el("div", { class: "locks" }, "锁：", f.locks.length ? f.locks.join("；") : "无"),
          el("div", { class: "label" }, VIEW_NOTE[f.level]),
          el("div", { class: "read" }, "A 最近一次 SELECT 读到：", el("b", { class: "read-value" }, read))),
        column("B")),
      f.verdict && el("p", { class: `verdict ${f.verdict.startsWith("出现") ? "bad" : "ok"}` }, f.verdict),
    ];
  }

  const player = new Player(root, render);
  let level = "RR", scenario = null;
  const levelButtons = {};
  const play = () => {
    Object.entries(levelButtons).forEach(([k, b]) => b.classList.toggle("on", k === level));
    if (scenario) player.load(simulate(scenario, level));
    else player.load([{
      level, scenario: null, slots: [], locks: [], readA: null, seenA: null, viewA: null,
      status: { A: "未开始", B: "未开始" },
      rows: [{ id: 42, versions: [{ stock: 10, price: 99, trx: null, seq: 0 }] }],
      say: "先选一个隔离级别（默认是 MySQL 的「可重复读」），再选一个场景。",
    }]);
  };
  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "隔离级别："),
    ...Object.entries(LEVELS).map(([k, label]) => (levelButtons[k] = el("button", { onclick: () => { level = k; play(); } }, label))),
    el("span", { class: "label" }, "　场景："),
    ...Object.entries(SCENARIOS).map(([k, s]) => el("button", { onclick: () => { scenario = k; play(); } }, s.label))));
  play();
})();
