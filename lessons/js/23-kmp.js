// 动画：模式串在文本上滑动。暴力匹配失配就右移一格、从头比；KMP 失配时查前缀表 π 跳过去，文本指针 i 不回退。
(() => {
  const root = document.getElementById("kmp");

  function prefixFunction(p) {
    const pi = Array(p.length).fill(0);
    let j = 0;
    for (let i = 1; i < p.length; i++) {
      while (j && p[i] !== p[j]) j = pi[j - 1];
      if (p[i] === p[j]) j++;
      pi[i] = j;
    }
    return pi;
  }

  // 一帧：shift = 模式起点；matched = 已确认相等的前几个字符；ci/cj = 正在比较的位置；res = ok / bad
  let ctx;
  function snap(say, f = {}) {
    return { say, shift: 0, matched: 0, ci: -1, cj: -1, res: "", piHot: -1, ...f,
             text: ctx.text, pat: ctx.pat, showPi: ctx.showPi, pi: ctx.pi, cmp: ctx.cmp, hits: [...ctx.hits] };
  }

  function render(f) {
    const n = f.text.length;
    const blanks = k => Array.from({ length: k }, () => box("", "blank"));
    const textCls = k => {
      if (k === f.ci) return f.res;
      return k >= f.shift && k < f.shift + f.matched ? "ok" : "";
    };
    const patCls = k => (k === f.cj ? f.res : k < f.matched ? "ok" : "");
    const idx = el("div", { class: "row idx" }, el("span", { class: "lab" }, ""),
      Array.from({ length: n }, (_, k) => el("span", { class: "box blank-num" }, k === f.ci ? "i" : String(k))));
    const rows = [
      idx,
      el("div", { class: "row text" }, el("span", { class: "lab" }, "文本"),
        [...f.text].map((c, k) => box(c, textCls(k)))),
      el("div", { class: "row pat" }, el("span", { class: "lab" }, "模式"), blanks(f.shift),
        [...f.pat].map((c, k) => box(c, patCls(k)))),
    ];
    if (f.showPi) rows.push(el("div", { class: "row pi" }, el("span", { class: "lab" }, "π"), blanks(f.shift),
      f.pi.map((v, k) => box(v, "small" + (k === f.piHot ? " hot" : "")))));
    rows.push(el("p", { class: "stat" }, "比较次数 = ", el("b", { class: "cmp" }, f.cmp),
      "　找到的起点 = ", el("b", { class: "hits" }, f.hits.length ? f.hits.join(", ") : "（还没有）")));
    return rows;
  }

  const player = new Player(root, render);

  function cmpFrame(fr, i, j, extra) {
    ctx.cmp++;
    const ok = ctx.text[i] === ctx.pat[j];
    fr.push(snap(`比较 文本[${i}]='${ctx.text[i]}' 和 模式[${j}]='${ctx.pat[j]}'：${ok ? "相等" : "不等"}${ok ? "。" : extra}`,
      { shift: i - j, matched: j, ci: i, cj: j, res: ok ? "ok" : "bad" }));
    return ok;
  }

  function naive(fr) {
    const { text, pat } = ctx, n = text.length, m = pat.length;
    for (let s = 0; s + m <= n; s++) {
      let k = 0;
      while (k < m && cmpFrame(fr, s + k, k,
        k ? `。模式右移一格，从模式开头重新比（i 退回到 ${s + 1}）。` : "。模式右移一格。")) k++;
      if (k === m) {
        ctx.hits.push(s);
        fr.push(snap(`整个模式都对上了：找到起点 ${s}。再右移一格接着找。`, { shift: s, matched: m }));
      }
    }
  }

  function kmp(fr) {
    const { text, pat, pi } = ctx, m = pat.length;
    let j = 0;
    for (let i = 0; i < text.length; i++) {
      while (j > 0 && !cmpFrame(fr, i, j, `。查 π[${j - 1}] = ${pi[j - 1]}，i 不动，模式跳过去。`)) {
        const k = pi[j - 1];
        fr.push(snap(`前 ${j} 个已对上的字符里，开头 ${k} 个 = 结尾 ${k} 个，所以模式直接右移到让开头 ${k} 个对齐，j = ${k}。i 还是 ${i}。`,
          { shift: i - k, matched: k, ci: i, piHot: j - 1 }));
        j = k;
      }
      if (j === 0 && !cmpFrame(fr, i, 0, "。j 已经是 0，没得跳：模式右移一格，i 前进。")) continue;
      j++;
      if (j === m) {
        ctx.hits.push(i - m + 1);
        const k = pi[m - 1];
        fr.push(snap(`整个模式都对上了：找到起点 ${i - m + 1}。按 π[${m - 1}] = ${k} 滑动，接着找。`,
          { shift: i - m + 1, matched: m, piHot: m - 1 }));
        j = k;
      }
    }
  }

  const textIn = el("input", { type: "text", value: "ABABABCABABC", maxlength: "16", "aria-label": "文本" });
  const patIn = el("input", { type: "text", value: "ABABC", maxlength: "8", "aria-label": "模式" });

  const setup = showPi => {
    ctx = { text: textIn.value, pat: patIn.value, showPi, cmp: 0, hits: [] };
    ctx.pi = prefixFunction(ctx.pat);
  };
  const run = (algo, showPi) => () => {
    setup(showPi);
    const fr = [snap("模式放在文本最左边，准备开始。")];
    if (!ctx.pat || ctx.pat.length > ctx.text.length) {
      fr.push(snap(ctx.pat ? "模式比文本长，不可能匹配，返回 []。" : "空模式：按约定返回 []。"));
    } else {
      algo(fr);
      fr.push(snap(`结束：一共比较 ${ctx.cmp} 次，找到 [${ctx.hits.join(", ")}]。`,
        { shift: Math.max(0, ctx.text.length - ctx.pat.length) }));
    }
    player.load(fr);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "文本"), textIn,
    el("span", { class: "label" }, "模式"), patIn,
    el("button", { onclick: run(naive, false) }, "暴力匹配"),
    el("button", { onclick: run(kmp, true) }, "KMP")));
  setup(true);
  player.load([snap("先点“暴力匹配”，再点“KMP”，比一比比较次数。")]);
})();
