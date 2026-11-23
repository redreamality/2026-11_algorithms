// 第 3 课的两个动画：#race（两个线程卖最后一件商品）和 #banker（银行家算法）。
const vec = v => `(${v.join(",")})`;

// ---------- 动画一：竞态 ----------
(() => {
  const root = document.getElementById("race");
  if (!root) return;
  // 每个程序是一串操作；text 是显示的代码
  const PROGRAMS = {
    plain: [
      { op: "check", text: "if (stock > 0)" },
      { op: "read", text: "r = stock      // 读" },
      { op: "sub", text: "r = r - 1      // 减" },
      { op: "write", text: "stock = r; 下单 // 写" },
    ],
    locked: [
      { op: "lock", text: "lock(库存锁)" },
      { op: "check", text: "if (stock > 0)" },
      { op: "read", text: "r = stock      // 读" },
      { op: "sub", text: "r = r - 1      // 减" },
      { op: "write", text: "stock = r; 下单 // 写" },
      { op: "unlock", text: "unlock(库存锁)" },
    ],
  };
  // 交错顺序：每一项是这一步由哪个线程执行（下标 0 = T1，1 = T2）
  const SCHEDULES = { plain: [0, 1, 0, 1, 0, 1, 0, 1], locked: [0, 0, 1, 0, 0, 0, 0, 1, 1] };
  const NAMES = ["T1", "T2"];

  function simulate(kind) {
    const prog = PROGRAMS[kind];
    const th = [0, 1].map(() => ({ pc: 0, r: null, status: "就绪" }));
    const s = { stock: 1, orders: 0, owner: null, waiting: [] };
    const frames = [];
    const snap = (say, active) => ({ kind, say, active, stock: s.stock, orders: s.orders, owner: s.owner, th: th.map(t => ({ ...t })), done: false });
    frames.push(snap(kind === "plain"
      ? "不加锁：stock = 1，两个线程按 T1、T2、T1、T2……交替各走一步。"
      : "加锁：先 lock(库存锁) 再进临界区。同样让两个线程交替着走。", null));
    const finishIfEnd = t => { if (th[t].pc >= prog.length) th[t].status = "完成"; };
    for (const t of SCHEDULES[kind]) {
      const me = th[t], line = prog[me.pc], who = NAMES[t];
      let say;
      if (me.status === "阻塞") { say = `${who} 还在阻塞，轮不到它。`; frames.push(snap(say, t)); continue; }
      me.status = "运行";
      if (line.op === "lock") {
        if (s.owner === null) { s.owner = t; me.pc++; say = `${who}：锁空闲，拿到库存锁，进入临界区。`; }
        else { me.status = "阻塞"; s.waiting.push(t); say = `${who}：库存锁在 ${NAMES[s.owner]} 手里，${who} 阻塞，排队等锁。`; }
      } else if (line.op === "check") {
        if (s.stock > 0) { me.pc++; say = `${who} 检查：stock = ${s.stock} > 0，有货，继续。`; }
        else {
          me.pc = prog.findIndex(l => l.op === "unlock");
          if (me.pc < 0) me.pc = prog.length;
          say = `${who} 检查：stock = ${s.stock}，已售罄，不下单。`;
        }
      } else if (line.op === "read") { me.r = s.stock; me.pc++; say = `${who} 读：把内存里的 stock（${s.stock}）读进自己的寄存器，r = ${me.r}。`; }
      else if (line.op === "sub") { me.r -= 1; me.pc++; say = `${who} 减：r = ${me.r}。只改了寄存器，内存里的 stock 还是 ${s.stock}。`; }
      else if (line.op === "write") { s.stock = me.r; s.orders++; me.pc++; say = `${who} 写：stock = ${me.r}，订单创建成功（已卖出 ${s.orders} 件）。`; }
      else if (line.op === "unlock") {
        me.pc++;
        s.owner = null;
        say = `${who} 放开库存锁。`;
        if (s.waiting.length) {
          const w = s.waiting.shift();
          s.owner = w; th[w].pc++; th[w].status = "就绪";
          say += `唤醒等锁的 ${NAMES[w]}，锁交给它。`;
        }
      }
      finishIfEnd(t);
      if (me.status === "运行") me.status = me.pc >= prog.length ? "完成" : "就绪";
      frames.push(snap(say, t));
    }
    const last = frames[frames.length - 1];
    last.done = true;
    last.say += s.orders > 1
      ? ` 结束：只有 1 件货却卖出了 ${s.orders} 件，超卖！`
      : ` 结束：卖出 ${s.orders} 件，stock = ${s.stock}，结果正确。`;
    return frames;
  }

  function render(f) {
    const prog = f.kind ? PROGRAMS[f.kind] : PROGRAMS.plain;
    const cols = [0, 1].map(t => {
      const st = f.th[t];
      return el("div", {},
        el("p", {}, box(NAMES[t], "t" + (t + 1) + (f.active === t ? " running" : "")), ` ${st.status}，r = `, el("b", { class: `reg-${NAMES[t]}` }, st.r ?? "—")),
        ...prog.map((l, i) => el("div", { class: "code-line" + (st.pc === i && st.status !== "完成" ? " now" : "") }, l.text)));
    });
    return [
      el("div", { class: "race-cols" },
        ...cols,
        el("div", {},
          el("p", {}, "内存：stock = ", el("b", { class: "stock-value" }, f.stock)),
          el("p", {}, "已卖出：", el("b", { class: "order-count" }, f.orders), " 件"),
          f.kind === "locked" && el("p", {}, "库存锁：", f.owner === null ? "空闲" : `归 ${NAMES[f.owner]}`),
          f.done && el("p", { class: "race-verdict verdict " + (f.orders > 1 ? "bad" : "ok") }, f.orders > 1 ? "超卖" : "正确"))),
    ];
  }

  const player = new Player(root, render);
  const reset = () => player.load([{
    kind: null, active: null, stock: 1, orders: 0, owner: null, done: false,
    th: [0, 1].map(() => ({ pc: 0, r: null, status: "就绪" })),
    say: "库存只剩 1 件，两个线程同时下单。点「不加锁」或「加锁」看它们的交错。",
  }]);
  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(simulate("plain")) }, "不加锁"),
    el("button", { onclick: () => player.load(simulate("locked")) }, "加锁"),
    el("button", { onclick: reset }, "重置竞态")));
  reset();
})();

// ---------- 动画二：银行家算法 ----------
(() => {
  const root = document.getElementById("banker");
  if (!root) return;
  const TOTAL = [10, 5, 7];
  const ALLOC = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]];
  const MAX = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]];
  const N = 5, RES = ["A", "B", "C"];
  const add = (a, b) => a.map((x, i) => x + b[i]);
  const sub = (a, b) => a.map((x, i) => x - b[i]);
  const le = (a, b) => a.every((x, i) => x <= b[i]);
  const firstOver = (a, b) => a.findIndex((x, i) => x > b[i]);
  const why = (a, b) => { const k = firstOver(a, b); return `${RES[k]} 类 ${a[k]} > ${b[k]}`; };
  const avail = alloc => alloc.reduce((s, a) => sub(s, a), TOTAL);
  const clone = st => ({ alloc: st.alloc.map(r => [...r]), need: st.need.map(r => [...r]) });

  const initial = () => ({ alloc: ALLOC.map(r => [...r]), need: MAX.map((m, i) => sub(m, ALLOC[i])) });
  const afterP1 = () => { const s = initial(); s.alloc[1] = add(s.alloc[1], [1, 0, 2]); s.need[1] = sub(s.need[1], [1, 0, 2]); return s; };

  // 画面数据：state（alloc/need）、showNeed、work、done[]、checking、seq、verdict、highlightRow
  function frame(st, extra) {
    return { alloc: st.alloc.map(r => [...r]), need: st.need.map(r => [...r]), available: avail(st.alloc), showNeed: true, work: null, done: Array(N).fill(false), checking: null, seq: null, verdict: null, ...extra };
  }

  // 安全性检查：每轮从 P0 开始，选第一个未完成且 Need ≤ Work 的
  function safetyFrames(st, frames, prefix) {
    let work = avail(st.alloc);
    const done = Array(N).fill(false), seq = [];
    let round = 0;
    frames.push(frame(st, { work: [...work], done: [...done], seq: [], say: `${prefix}安全性检查开始：Work = Available = ${vec(work)}，所有任务标为未完成。` }));
    while (true) {
      round++;
      let found = -1;
      for (let i = 0; i < N; i++) {
        if (done[i]) continue;
        const ok = le(st.need[i], work);
        frames.push(frame(st, { work: [...work], done: [...done], seq: [...seq], checking: i,
          say: `第 ${round} 轮：P${i} Need ${vec(st.need[i])} ≤ Work ${vec(work)}？${ok ? "满足" : "不满足（" + why(st.need[i], work) + "）"}` }));
        if (ok) { found = i; break; }
      }
      if (found < 0) {
        const all = done.every(Boolean);
        return { safe: all, seq, work, done, round };
      }
      const before = work;
      work = add(work, st.alloc[found]);
      done[found] = true;
      seq.push(found);
      frames.push(frame(st, { work: [...work], done: [...done], seq: [...seq], checking: found,
        say: `P${found} 可以跑完，放回 Allocation：Work = ${vec(before)} + ${vec(st.alloc[found])} = ${vec(work)}。安全序列目前是 ${seqText(seq)}。` }));
      if (done.every(Boolean)) return { safe: true, seq, work, done, round };
    }
  }
  const seqText = seq => seq.length ? seq.map(i => "P" + i).join(" → ") : "（空）";

  function safetyOnly() {
    const st = initial();
    const frames = [];
    frames.push(frame(st, { showNeed: false, say: "初始状态：已知 Max 和 Allocation，Available = (10,5,7) − (7,2,5) = (3,3,2)。" }));
    frames.push(frame(st, { say: "先算 Need = Max − Allocation，例如 P0：(7,5,3) − (0,1,0) = (7,4,3)。" }));
    const r = safetyFrames(st, frames, "");
    frames.push(frame(st, { work: r.work, done: r.done, seq: r.seq, verdict: "safe",
      say: `所有任务都能完成，系统处于安全状态。安全序列 ${seqText(r.seq)}；最后 Work = ${vec(r.work)} 等于总量。` }));
    return frames;
  }

  function requestFrames(p, req, fromP1) {
    const st = fromP1 ? afterP1() : initial();
    const frames = [];
    const where = fromP1 ? "P1 的请求 (1,0,2) 已获批，当前 Available = (2,3,0)。" : "从初始状态出发，Available = (3,3,2)。";
    frames.push(frame(st, { highlightRow: p, say: `${where}P${p} 请求 ${vec(req)}。` }));
    if (!le(req, st.need[p])) {
      frames.push(frame(st, { highlightRow: p, verdict: "error", say: `第 1 步：Request ${vec(req)} ≤ Need ${vec(st.need[p])}？不满足，超过声明的最大需求，出错。` }));
      return frames;
    }
    frames.push(frame(st, { highlightRow: p, say: `第 1 步：Request ${vec(req)} ≤ Need[${p}] ${vec(st.need[p])}？满足。` }));
    const av = avail(st.alloc);
    if (!le(req, av)) {
      frames.push(frame(st, { highlightRow: p, verdict: "wait",
        say: `第 2 步：Request ${vec(req)} ≤ Available ${vec(av)}？不满足（${why(req, av)}），资源不够，P${p} 等待。` }));
      return frames;
    }
    frames.push(frame(st, { highlightRow: p, say: `第 2 步：Request ${vec(req)} ≤ Available ${vec(av)}？满足。` }));
    const trial = clone(st);
    trial.alloc[p] = add(trial.alloc[p], req);
    trial.need[p] = sub(trial.need[p], req);
    frames.push(frame(trial, { highlightRow: p,
      say: `第 3 步：试分配。Available = ${vec(av)} − ${vec(req)} = ${vec(avail(trial.alloc))}，Allocation[${p}] = ${vec(trial.alloc[p])}，Need[${p}] = ${vec(trial.need[p])}。` }));
    const r = safetyFrames(trial, frames, "第 4 步：");
    if (r.safe) {
      frames.push(frame(trial, { work: r.work, done: r.done, seq: r.seq, verdict: "grant",
        say: `试分配后安全，安全序列 ${seqText(r.seq)}，批准 P${p} 的请求。` }));
    } else {
      frames.push(frame(st, { done: r.done, seq: r.seq, verdict: "reject", highlightRow: p,
        say: `第 ${r.round} 轮扫完一个也找不到，试分配后不安全。拒绝 P${p} 的请求，撤回试分配，P${p} 等待。` }));
    }
    return frames;
  }

  const VERDICTS = {
    safe: ["安全", "ok"], grant: ["批准", "ok"], wait: ["资源不足，等待", "bad"],
    reject: ["不安全，拒绝", "bad"], error: ["出错：超过最大需求", "bad"],
  };

  function render(f) {
    const rows = f.alloc.map((a, i) => {
      const cls = f.checking === i ? "hot" : f.done[i] ? "ok" : f.highlightRow === i ? "hot" : "";
      const td = (text, extra) => el("td", { class: [cls, extra].filter(Boolean).join(" ") }, text);
      return el("tr", { class: `row-P${i} ${f.checking === i ? "checking" : ""} ${f.done[i] ? "done" : ""}` },
        td("P" + i), td(vec(a), "vec"), td(vec(MAX[i]), "vec"),
        td(f.showNeed ? vec(f.need[i]) : "?", "vec need"), td(f.done[i] ? "✓" : ""));
    });
    const v = f.verdict && VERDICTS[f.verdict];
    return [
      el("table", {},
        el("tr", {}, ...["任务", "Allocation", "Max", "Need", "完成"].map(h => el("th", {}, h))),
        ...rows),
      el("p", { class: "stat" },
        "Available = ", el("b", { class: "available vec" }, vec(f.available)),
        f.work && "　Work = ", f.work && el("b", { class: "work vec" }, vec(f.work))),
      f.seq && el("p", {}, "安全序列：", el("span", { class: "safe-sequence" },
        f.verdict === "reject" ? "找不到" : seqText(f.seq))),
      v && el("p", {}, "结论：", el("span", { class: "verdict " + v[1] }, v[0])),
    ];
  }

  const player = new Player(root, render);
  const reset = () => player.load([frame(initial(), { showNeed: false, say: "5 个任务、3 类资源（A 数据库连接、B 工作线程、C 缓存槽）。点上面的按钮开始。" })]);
  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(safetyOnly()) }, "安全性检查"),
    el("button", { onclick: () => player.load(requestFrames(1, [1, 0, 2], false)) }, "P1 请求 (1,0,2)"),
    el("button", { onclick: () => player.load(requestFrames(4, [3, 3, 0], true)) }, "P4 请求 (3,3,0)"),
    el("button", { onclick: () => player.load(requestFrames(0, [0, 2, 0], true)) }, "P0 请求 (0,2,0)"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
