// 动画：一棵小 Trie。插入时逐字建路，查找 / 前缀列词时高亮走过的路。
// 绿色 = 有单词在这里结束，橙色 = 当前节点，浅橙 = 走过的路，虚线框 = 刚新建的节点。
(() => {
  const root = document.getElementById("trie");
  const DX = 46, DY = 52;
  let st, fr;

  // nodes[id] = { ch, kids: {字符: id}, end }；0 号是根
  function snap(say, { cur = null, path = [], fresh = null, out = null } = {}) {
    fr.push({ say, cur, path: [...path], fresh, out: out && [...out], nodes: structuredClone(st.nodes) });
  }

  // 布局：叶子从左到右依次排开，父节点放在孩子正中间
  function layout(nodes) {
    const pos = {};
    let leaf = 0, depth = 0;
    (function place(id, d) {
      depth = Math.max(depth, d);
      const kids = Object.keys(nodes[id].kids).sort().map(c => nodes[id].kids[c]);
      if (!kids.length) pos[id] = [leaf++ * DX + 24, d * DY + 18];
      else {
        kids.forEach(k => place(k, d + 1));
        pos[id] = [(pos[kids[0]][0] + pos[kids[kids.length - 1]][0]) / 2, d * DY + 18];
      }
    })(0, 0);
    return { pos, w: Math.max(leaf, 1) * DX + 8, h: depth * DY + 40 };
  }

  function tree(f) {
    const { pos, w, h } = layout(f.nodes);
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", w);
    svg.setAttribute("height", h);
    const boxes = [];
    for (const [id, n] of Object.entries(f.nodes)) {
      for (const k of Object.values(n.kids)) {
        const [x1, y1] = pos[id], [x2, y2] = pos[k];
        const on = f.path.includes(Number(id)) && f.path.includes(k);
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        Object.entries({ x1, y1, x2, y2, stroke: on ? "#e65100" : "#999", "stroke-width": on ? 3 : 2 })
          .forEach(([a, v]) => line.setAttribute(a, v));
        svg.append(line);
      }
      const i = Number(id);
      const cls = [n.end && "end", i === f.cur ? "hot" : f.path.includes(i) && "path", i === f.fresh && "new"];
      const b = box(i === 0 ? "根" : n.ch, cls.filter(Boolean).join(" "));
      b.dataset.id = id;
      b.style.left = pos[id][0] + "px";
      b.style.top = pos[id][1] + "px";
      boxes.push(b);
    }
    return el("div", { class: "tree", style: `height:${h}px;width:${w}px` }, svg, boxes);
  }

  function render(f) {
    return [
      tree(f),
      f.out && el("div", { class: "row out" }, el("span", { class: "label" }, "找到的词："),
        f.out.length ? f.out.map(w => box(w, "small end")) : el("span", { class: "label" }, "（还没有）")),
    ];
  }

  const player = new Player(root, render);

  function insert(word, quiet) {
    let cur = 0;
    const path = [0];
    if (!quiet) snap(`insert("${word}")：从根出发。`, { cur, path });
    for (const ch of word) {
      let fresh = null;
      if (!(ch in st.nodes[cur].kids)) {
        fresh = st.nextId++;
        st.nodes[fresh] = { ch, kids: {}, end: false };
        st.nodes[cur].kids[ch] = fresh;
      }
      cur = st.nodes[cur].kids[ch];
      path.push(cur);
      if (!quiet) snap(fresh === null ? `'${ch}' 这条路已经有了，直接走下去。` : `没有 '${ch}'，新建一个节点，再走下去。`,
        { cur, path, fresh });
    }
    if (quiet) return void (st.nodes[cur].end = true);
    if (st.nodes[cur].end) return snap(`走完了，这里本来就是结束点：${word} 已经在树里，什么都不变。`, { cur, path });
    st.nodes[cur].end = true;
    snap(`走完 ${word.length} 个字母，在最后一个节点标上结束标记（变绿）。O(L)`, { cur, path });
  }

  // 沿着 s 往下走，返回停下的节点；断路返回 null。每一步一帧。
  function walk(s, path) {
    let cur = 0;
    snap(`从根出发，沿着 "${s}" 一个字母一个字母往下走。`, { cur, path });
    for (const ch of s) {
      const nx = st.nodes[cur].kids[ch];
      if (nx === undefined) {
        snap(`当前节点没有 '${ch}' 这个孩子，路断了。`, { cur, path });
        return null;
      }
      cur = nx;
      path.push(cur);
      snap(`走到 '${ch}'。`, { cur, path });
    }
    return cur;
  }

  function search(word) {
    const path = [0];
    const cur = walk(word, path);
    if (cur === null) return snap(`search("${word}") → False：路都走不通。`, { path });
    const end = st.nodes[cur].end;
    snap(end ? `走完了，这个节点是结束点：search("${word}") → True。`
      : `走完了，可这个节点不是结束点（不是绿色）："${word}" 只是前缀，search → False。`, { cur, path });
  }

  function prefix(p) {
    const path = [0];
    const start = walk(p, path);
    const out = [];
    if (start === null) return snap(`没有以 "${p}" 开头的词，返回 []。`, { path, out });
    snap(`到了前缀节点。接下来把它下面的子树走一遍，孩子按字母顺序访问。`, { cur: start, path, out });
    (function dfs(id, s) {
      const n = st.nodes[id];
      if (n.end) {
        out.push(s);
        snap(`这里是结束点，收下 "${s}"。`, { cur: id, path, out });
      }
      for (const c of Object.keys(n.kids).sort()) dfs(n.kids[c], s + c);
    })(start, p);
    snap(`按字母顺序访问，结果天然有序：[${out.join(", ")}]。`, { path, out });
  }

  const word = el("input", { type: "text", value: "cart", "aria-label": "单词" });
  const run = op => () => {
    fr = [];
    op(word.value.trim().toLowerCase());
    player.load(fr);
  };
  const reset = () => {
    st = { nodes: { 0: { ch: "", kids: {}, end: false } }, nextId: 1 };
    fr = [];
    for (const w of ["car", "cat", "dog"]) insert(w, true);
    snap("存了 car、cat、dog。car 和 cat 共用 c → a 这一段。");
    player.load(fr);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "单词 ="), word,
    el("button", { onclick: run(w => insert(w, false)) }, "insert"),
    el("button", { onclick: run(search) }, "search"),
    el("button", { onclick: run(prefix) }, "前缀列词"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
