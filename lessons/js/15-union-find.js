// 动画：并查集的森林。每个圆圈是一个元素，箭头指向它的 parent；根指向自己，不画箭头。
(() => {
  const root = document.getElementById("uf");
  const N = 8, R = 18, DX = 56, DY = 66;
  let st;

  function svg(tag, attrs, ...kids) {
    const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
    e.append(...kids);
    return e;
  }

  // 每棵树：叶子从左到右占一格，父节点放在孩子们的正中间上方
  function layout(parent) {
    const kids = parent.map(() => []);
    parent.forEach((p, i) => { if (p !== i) kids[p].push(i); });
    const pos = [];
    let slot = 0;
    const place = (i, d) => {
      if (!kids[i].length) pos[i] = { x: 30 + DX * slot++, y: 30 + DY * d };
      else {
        kids[i].forEach(k => place(k, d + 1));
        const xs = kids[i].map(k => pos[k].x);
        pos[i] = { x: (Math.min(...xs) + Math.max(...xs)) / 2, y: 30 + DY * d };
      }
    };
    parent.forEach((p, i) => { if (p === i) place(i, 0); });
    return pos;
  }

  const marker = (id, color) => svg("marker", { id, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto" },
    svg("path", { d: "M0,0 L10,5 L0,10 z", fill: color }));

  function render(f) {
    const pos = layout(f.parent);
    const h = Math.max(...pos.map(p => p.y)) + 30, w = 60 + DX * (N - 1);
    const g = svg("svg", { class: "forest", width: w, height: h, viewBox: `0 0 ${w} ${h}` },
      svg("defs", {}, marker("uf-ah", "#555"), marker("uf-ah-new", "#e65100")));
    f.parent.forEach((p, i) => {
      if (p === i) return;
      const a = pos[i], b = pos[p];
      const len = Math.hypot(b.x - a.x, b.y - a.y), ux = (b.x - a.x) / len, uy = (b.y - a.y) / len;
      const isNew = f.changed.includes(i);
      g.append(svg("line", { class: "edge" + (isNew ? " new" : ""), "data-from": i,
        x1: a.x + ux * R, y1: a.y + uy * R, x2: b.x - ux * (R + 2), y2: b.y - uy * (R + 2),
        "marker-end": `url(#uf-ah${isNew ? "-new" : ""})` }));
    });
    pos.forEach((p, i) => {
      const cls = ["unode", f.parent[i] === i && "root", f.path.includes(i) && "path", i === f.cur && "cur"].filter(Boolean).join(" ");
      g.append(svg("g", { class: cls, "data-node": i },
        svg("circle", { cx: p.x, cy: p.y, r: R }),
        svg("text", { x: p.x, y: p.y + 5 }, String(i))));
    });
    return [
      g,
      el("div", { class: "row parent" }, el("span", { class: "label" }, "parent ="),
        f.parent.map((p, i) => el("div", { class: "node" },
          el("div", { class: "tag" }, String(i)),
          box(p, f.changed.includes(i) ? "hot" : "")))),
      el("p", { class: "stat" }, "集合数 count = ", el("b", { class: "count" }, f.count)),
    ];
  }

  const player = new Player(root, render);

  const fresh = () => ({ parent: [...Array(N).keys()], size: Array(N).fill(1), count: N });
  const snap = (say, extra = {}) =>
    ({ say, parent: [...st.parent], count: st.count, path: [], cur: null, changed: [], ...extra });

  function find(fr, x) {
    const path = [x];
    let r = x;
    fr.push(snap(st.parent[x] === x ? `find(${x})：${x} 指向自己，它就是根。` : `find(${x})：从 ${x} 出发，沿着箭头往上走。`, { path: [x], cur: x }));
    while (st.parent[r] !== r) {
      r = st.parent[r];
      path.push(r);
      fr.push(snap(st.parent[r] === r ? `走到 ${r}，它指向自己，就是根。` : `走到 ${r}，还不是根，继续往上。`, { path: [...path], cur: r }));
    }
    const fix = path.filter(i => i !== r && st.parent[i] !== r);
    for (const i of fix) {
      st.parent[i] = r;
      fr.push(snap(`路径压缩：让 ${i} 直接指向根 ${r}。`, { path, cur: i, changed: [i] }));
    }
    if (fix.length) fr.push(snap(`压缩完成：路上的点都直接指向根 ${r}，下次 find 一步就到。`, { changed: fix }));
    return r;
  }

  function union(fr, a, b) {
    const ra = find(fr, a), rb = find(fr, b);
    if (ra === rb) return fr.push(snap(`${a} 和 ${b} 的根都是 ${ra}：本来就在一起，返回 False。`, { path: [ra], cur: ra }));
    let big = ra, small = rb;
    if (st.size[ra] < st.size[rb]) [big, small] = [rb, ra];
    const tie = st.size[ra] === st.size[rb] ? "（一样大，让 a 的根当新根）" : "";
    fr.push(snap(`根 ${ra} 的树有 ${st.size[ra]} 个，根 ${rb} 的树有 ${st.size[rb]} 个：小树挂到大树下面${tie}。`, { path: [ra, rb] }));
    st.parent[small] = big;
    st.size[big] += st.size[small];
    st.count--;
    fr.push(snap(`parent[${small}] = ${big}：只改一个指针，两棵树合成一棵，返回 True。`, { path: [big], changed: [small] }));
  }

  const num = (v, label) => el("input", { type: "number", min: "0", max: String(N - 1), value: v, "aria-label": label });
  const ia = num("0", "a"), ib = num("1", "b");
  const run = op => () => {
    const a = Number(ia.value), b = Number(ib.value);
    const ok = x => Number.isInteger(x) && x >= 0 && x < N;
    if (!ok(a) || (op === union && !ok(b))) return player.load([snap(`请输入 0～${N - 1} 之间的整数。`)]);
    const fr = [snap("操作前的样子。")];
    op(fr, a, b);
    player.load(fr);
  };
  const reset = () => {
    st = fresh();
    player.load([snap(`${N} 个元素，各自是一棵只有根的树（自己指向自己）。`)]);
  };
  const chain = () => {
    st = fresh();
    st.parent = [0, 0, 1, 2, 3, 5, 6, 7];  // 4 → 3 → 2 → 1 → 0
    st.size[0] = 5;
    st.count = 4;
    const fr = [snap("假设合并时没按大小，搭出了一条长链 4 → 3 → 2 → 1 → 0。")];
    find(fr, 4);
    player.load(fr);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "a ="), ia,
    el("span", { class: "label" }, "b ="), ib,
    el("button", { onclick: run(union) }, "union(a, b)"),
    el("button", { onclick: run(find) }, "find(a)"),
    el("button", { onclick: chain }, "长链 + find(4)"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
