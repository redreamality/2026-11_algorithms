// 第 2 课的两个动画：
// 1. #mmu：shop-server 的一个虚拟地址怎么拆成页号 + 偏移、查 TLB、查页表（可能缺页），得到物理地址。
// 2. #paging：页面置换模拟器（FIFO / LRU / OPT），每访问一页一帧。

const hex = x => "0x" + x.toString(16).toUpperCase().padStart(4, "0");

// ---------------- 动画 1：地址翻译 ----------------
(() => {
  const root = document.getElementById("mmu");
  const PAGE = 4096, TLB_SIZE = 2;
  // 和正文第 6 节的页表一致：页 3 在磁盘上，缺页时调入空闲的页框 4
  const initialTable = () => [
    { frame: 5, valid: 1 }, { frame: 2, valid: 1 }, { frame: 7, valid: 1 }, { frame: null, valid: 0 },
  ];
  let table = initialTable(), tlb = [];

  function parse(text) {
    const s = text.trim();
    if (/^0x[0-9a-f]+$/i.test(s)) return parseInt(s, 16);
    if (/^\d+$/.test(s)) return Number(s);
    return null;
  }

  function translate(va) {
    const page = Math.floor(va / PAGE), offset = va % PAGE;
    const frames = [];
    const snap = (stage, say, extra = {}) => frames.push({
      va, page, offset, stage, say, table: table.map(r => ({ ...r })), tlb: tlb.map(r => ({ ...r })), ...extra,
    });
    snap("split", `${hex(va)} = ${va}。${va} ÷ ${PAGE} = ${page} 余 ${offset}：页号 ${page}，页内偏移 ${hex(offset)}（低 12 位）。`);
    if (page >= table.length) {
      snap("error", `shop-server 的页表只有 ${table.length} 页（页 0～${table.length - 1}），页 ${page} 越界：内核报错，进程被终止。`, { result: "越界" });
      return frames;
    }
    const hit = tlb.find(e => e.page === page);
    if (hit) {
      snap("tlb-hit", `查 TLB：有「页 ${page} → 页框 ${hit.frame}」，TLB 命中，不用查页表。`, { tlbResult: "命中", hitPage: page });
      const pa = hit.frame * PAGE + offset;
      snap("done", `物理地址 = ${hit.frame} × 0x1000 + ${hex(offset)} = ${hex(pa)}。只访问了 1 次内存（取数据）。`, { tlbResult: "命中", pa, hitPage: page });
      return frames;
    }
    snap("tlb-miss", `查 TLB：没有页 ${page}，TLB 未命中，去内存里查页表（多访问 1 次内存）。`, { tlbResult: "未命中" });
    let note = "";
    if (!table[page].valid) {
      snap("fault", `页表第 ${page} 行的有效位是 0：页 ${page} 不在内存里，触发缺页中断。内核从磁盘把它读进空闲的页框 4，进程阻塞等待。`, { tlbResult: "未命中", rowHot: page, fault: true });
      table[page] = { frame: 4, valid: 1 };
      snap("loaded", `读完：页表第 ${page} 行改成「页框 4，有效位 1」。进程再被调度时重新执行这条访存指令。`, { tlbResult: "未命中", rowHot: page, fault: true });
      note = "（这次还经历了一次缺页）";
    } else {
      snap("table", `页表第 ${page} 行：页框 ${table[page].frame}，有效位 1，页在内存里。`, { tlbResult: "未命中", rowHot: page });
    }
    const frame = table[page].frame;
    let evicted = "";
    if (tlb.length === TLB_SIZE) evicted = `TLB 满了，换掉最早存进去的「页 ${tlb.shift().page}」，`;
    tlb.push({ page, frame });
    const pa = frame * PAGE + offset;
    snap("done", `${evicted}把「页 ${page} → 页框 ${frame}」存进 TLB。物理地址 = ${frame} × 0x1000 + ${hex(offset)} = ${hex(pa)}${note}。`,
      { tlbResult: "未命中", pa, rowHot: page, fault: frames.some(f => f.fault) });
    return frames;
  }

  function render(f) {
    const known = f.va != null;
    return [
      known && el("div", { class: "row" },
        el("span", { class: "label" }, "虚拟地址"), box(hex(f.va), "hot"),
        el("span", { class: "label" }, "= 页号"), el("span", { class: "box page-no" }, String(f.page)),
        el("span", { class: "label" }, "+ 页内偏移"), el("span", { class: "box offset" }, hex(f.offset))),
      el("div", { class: "pair" },
        el("div", {}, el("span", { class: "label" }, `TLB（最多 ${TLB_SIZE} 项）`),
          el("table", { class: "pt tlb" },
            el("tr", {}, el("th", {}, "页号"), el("th", {}, "页框号")),
            ...(f.tlb.length ? f.tlb.map(e => el("tr", {},
              el("td", { class: e.page === f.hitPage ? "ok" : "" }, String(e.page)),
              el("td", { class: e.page === f.hitPage ? "ok" : "" }, String(e.frame))))
              : [el("tr", {}, el("td", { colspan: "2" }, "（空）"))]))),
        el("div", {}, el("span", { class: "label" }, "shop-server 的页表（在内存里）"),
          el("table", { class: "pt" },
            el("tr", {}, el("th", {}, "页"), el("th", {}, "页框号"), el("th", {}, "有效位")),
            ...f.table.map((r, i) => {
              const cls = i === f.rowHot ? (f.stage === "fault" ? "bad" : "hot") : "";
              return el("tr", {}, el("td", { class: cls }, String(i)), el("td", { class: cls }, r.frame == null ? "—（磁盘）" : String(r.frame)),
                el("td", { class: cls }, String(r.valid)));
            })))),
      known && f.tlbResult && el("p", { class: "stat" }, "TLB：", el("b", { class: "tlb-result" }, f.tlbResult),
        f.fault ? el("span", {}, "，", el("b", { class: "fault-flag" }, "缺页")) : null),
      known && f.pa != null && el("p", { class: "stat" }, "物理地址 = ", el("b", { class: "phys-addr" }, hex(f.pa))),
      known && f.result && el("p", { class: "stat" }, el("b", { class: "phys-addr" }, f.result)),
    ];
  }

  const player = new Player(root, render);
  const input = el("input", { type: "text", value: "0x1004", size: "8", "aria-label": "虚拟地址" });
  const idle = say => ({ stage: "idle", table: table.map(r => ({ ...r })), tlb: tlb.map(r => ({ ...r })), say });
  const go = () => {
    const va = parse(input.value);
    if (va == null) return player.load([idle("看不懂这个地址。请输入十六进制（如 0x1ABC）或十进制（如 6844）。")]);
    player.load(translate(va));
  };
  const reset = () => {
    table = initialTable(); tlb = [];
    player.load([idle("TLB 是空的，页 3 还在磁盘上。输入一个虚拟地址，点「翻译」。")]);
  };
  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "虚拟地址 ="), input,
    el("button", { onclick: go }, "翻译"),
    el("button", { onclick: reset }, "清空 TLB 和页表")));
  reset();
})();

// ---------------- 动画 2：页面置换 ----------------
(() => {
  const root = document.getElementById("paging");
  const MAIN = "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1";
  const BELADY = "1 2 3 4 1 2 5 1 2 3 4 5";
  const NAMES = { FIFO: "FIFO 先进先出", LRU: "LRU 最近最久未使用", OPT: "OPT 最佳置换" };
  const pct = x => Number((x * 100).toFixed(1)) + "%";

  function simulate(policy, seq, n, intro) {
    const slots = Array(n).fill(null);
    const loaded = {}, last = {};
    const cols = [], frames = [];
    let faults = 0;
    frames.push({ seq, n, t: -1, cols: [], faults: 0, say: intro || `用 ${NAMES[policy]}，${n} 个页框，一开始都是空的。共 ${seq.length} 次访问。` });
    seq.forEach((p, t) => {
      const k = `第 ${t + 1} 次访问页 ${p}`;
      let say, out = null, hit = false;
      if (slots.includes(p)) {
        hit = true;
        say = `${k}：已经在页框里，命中。`;
      } else {
        faults++;
        const free = slots.indexOf(null);
        if (free >= 0) {
          slots[free] = p;
          say = `${k}：不在内存，缺页。还有空页框，直接调入页框 ${free + 1}。`;
        } else {
          let victim, reason;
          const list = f => slots.map(q => `${q}${f(q)}`).join("、");
          if (policy === "FIFO") {
            victim = slots.reduce((a, b) => (loaded[b] < loaded[a] ? b : a));
            reason = `最早调入的是 ${victim}（调入时刻：${list(q => ` 第 ${loaded[q] + 1} 次`)}）`;
          } else if (policy === "LRU") {
            victim = slots.reduce((a, b) => (last[b] < last[a] ? b : a));
            reason = `最久没用的是 ${victim}（最近一次用：${list(q => ` 第 ${last[q] + 1} 次`)}）`;
          } else {
            const next = q => { const i = seq.indexOf(q, t + 1); return i < 0 ? Infinity : i; };
            victim = slots.reduce((a, b) => (next(b) > next(a) ? b : a));
            reason = `未来最晚才用的是 ${victim}（下次用：${list(q => next(q) === Infinity ? " 不再用" : ` 第 ${next(q) + 1} 次`)}）`;
          }
          slots[slots.indexOf(victim)] = p;
          out = victim;
          say = `${k}：不在内存，缺页。页框已满，${reason}，换出 ${victim}。`;
        }
        loaded[p] = t;
      }
      last[p] = t;
      cols.push({ page: p, hit, out, slots: [...slots] });
      if (t === seq.length - 1) say += `结束：缺页 ${faults} 次，缺页率 ${faults} ÷ ${seq.length} = ${pct(faults / seq.length)}。`;
      frames.push({ seq, n, t, cols: [...cols], faults, say });
    });
    return frames;
  }

  function render(f) {
    const cell = i => i <= f.t ? f.cols[i] : null;
    const head = el("tr", {}, el("th", {}, "访问"),
      ...f.seq.map((p, i) => el("th", { class: i === f.t ? "cur" : "" }, String(p))));
    const rows = Array.from({ length: f.n }, (_, s) => el("tr", {}, el("th", {}, `页框 ${s + 1}`),
      ...f.seq.map((_, i) => {
        const c = cell(i);
        if (!c) return el("td", {}, "");
        const v = c.slots[s];
        let cls = v === c.page ? (c.hit ? "hit" : "new") : "";
        if (i === f.t) cls += " cur";
        return el("td", { class: cls.trim() }, v == null ? "" : String(v));
      })));
    const result = el("tr", {}, el("th", {}, "结果"),
      ...f.seq.map((_, i) => { const c = cell(i); return c ? el("td", { class: c.hit ? "hit" : "miss" }, c.hit ? "中" : "缺") : el("td", {}, ""); }));
    const outRow = el("tr", {}, el("th", {}, "换出"),
      ...f.seq.map((_, i) => { const c = cell(i); return el("td", {}, c && c.out != null ? String(c.out) : ""); }));
    const done = f.t + 1;
    return [
      el("div", { class: "trace-wrap" }, el("table", { class: "trace" }, head, ...rows, result, outRow)),
      el("p", { class: "stat" },
        "已访问 ", el("b", {}, String(done)), ` / ${f.seq.length} 次，缺页 `, el("b", { class: "fault-count" }, String(f.faults)),
        " 次，缺页率 ", el("b", { class: "fault-rate" }, done ? pct(f.faults / done) : "—")),
    ];
  }

  const player = new Player(root, render);
  const framesInput = el("input", { type: "number", value: "3", min: "1", max: "7", "aria-label": "页框数" });
  const seqInput = el("input", { type: "text", value: MAIN, size: "40", "aria-label": "访问序列" });
  const read = () => {
    const n = Math.round(Number(framesInput.value));
    const seq = seqInput.value.trim().split(/[\s,，]+/).filter(Boolean).map(Number);
    if (!(n >= 1 && n <= 7)) return [null, "页框数请填 1～7。"];
    if (!seq.length || seq.length > 30 || seq.some(x => !Number.isInteger(x) || x < 0 || x > 99))
      return [null, "访问序列请填 1～30 个 0～99 的页号，用空格隔开。"];
    return [{ n, seq }, null];
  };
  const run = (policy, intro) => () => {
    const [ok, err] = read();
    if (!ok) return player.load([{ seq: [], n: 0, t: -1, cols: [], faults: 0, say: err }]);
    player.load(simulate(policy, ok.seq, ok.n, intro && intro(ok)));
  };
  const belady = () => {
    seqInput.value = BELADY;
    run("FIFO", ({ n }) => `Belady 异常：序列 ${BELADY}，FIFO，${n} 个页框。3 个页框会缺页 9 次，4 个页框反而 10 次。跑完把页框数改成 ${n === 3 ? 4 : 3} 再点一次对比。`)();
  };
  const reset = () => {
    framesInput.value = "3"; seqInput.value = MAIN;
    const [ok] = read();
    player.load([{ seq: ok.seq, n: ok.n, t: -1, cols: [], faults: 0, say: "3 个页框都是空的。点上面的按钮选一种置换算法。" }]);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: run("FIFO") }, "FIFO"),
    el("button", { onclick: run("LRU") }, "LRU"),
    el("button", { onclick: run("OPT") }, "OPT"),
    el("button", { onclick: belady }, "Belady 异常"),
    el("span", { class: "label" }, "页框数 ="), framesInput,
    el("button", { onclick: reset }, "恢复默认")),
    el("div", { class: "ops-bar" }, el("span", { class: "label" }, "访问序列 ="), seqInput));
  reset();
})();
