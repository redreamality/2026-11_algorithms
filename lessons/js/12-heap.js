// 动画：最小堆。上面画成树，下面是它真正的存法——数组。两边的同一个下标同时高亮。
(() => {
  const root = document.getElementById("heap");
  const MAX = 15;          // 最多 4 层，画得下
  const W = 600, DY = 60;  // 树的宽度、层高
  let st;

  // hot：正在比较的下标；swap：刚交换的下标
  function snap(say, { hot = [], swap = [] } = {}) {
    return { say, hot, swap, a: [...st.a], out: [...st.out] };
  }

  const cls = (f, i) => f.swap.includes(i) ? "found" : f.hot.includes(i) ? "hot" : "";

  function pos(i) {
    const d = Math.floor(Math.log2(i + 1)), k = i - (2 ** d - 1);
    return [(k + 0.5) / 2 ** d * W, d * DY + 22];
  }

  function tree(f) {
    const n = f.a.length;
    const h = n ? (Math.floor(Math.log2(n)) + 1) * DY - 16 : 40;
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", W);
    svg.setAttribute("height", h);
    for (let i = 1; i < n; i++) {
      const [x1, y1] = pos((i - 1) >> 1), [x2, y2] = pos(i);
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      Object.entries({ x1, y1, x2, y2, stroke: "#999", "stroke-width": 2 }).forEach(([k, v]) => line.setAttribute(k, v));
      svg.append(line);
    }
    const nodes = f.a.map((v, i) => {
      const b = box(v, cls(f, i));
      const [x, y] = pos(i);
      b.style.left = x + "px";
      b.style.top = y + "px";
      return b;
    });
    return el("div", { class: "tree", style: `height:${h}px` }, svg, nodes,
      !n && el("span", { class: "label" }, "（空堆）"));
  }

  function render(f) {
    return [
      tree(f),
      el("div", { class: "row arr" }, el("span", { class: "label" }, "数组："),
        f.a.map((v, i) => el("div", { class: "node" }, box(v, cls(f, i)), el("div", { class: "tag" }, i)))),
      f.out.length && el("div", { class: "row out" }, el("span", { class: "label" }, "已排好："),
        f.out.map(v => box(v, "done"))),
      el("p", { class: "stat" }, "size = ", el("b", { class: "size" }, f.a.length)),
    ];
  }

  const player = new Player(root, render);

  function swap(i, j) {
    [st.a[i], st.a[j]] = [st.a[j], st.a[i]];
  }

  function siftUp(fr, i) {
    const a = st.a;
    while (i > 0) {
      const p = (i - 1) >> 1;
      fr.push(snap(`比较 a[${i}] = ${a[i]} 和父亲 a[${p}] = ${a[p]}。`, { hot: [i, p] }));
      if (a[i] >= a[p]) return fr.push(snap(`${a[i]} 不比父亲小，停下。`, { hot: [i] }));
      swap(i, p);
      fr.push(snap(`比父亲小，交换，继续往上看。`, { swap: [i, p] }));
      i = p;
    }
    fr.push(snap(`${a[0]} 浮到了堆顶，停下。`, { hot: [0] }));
  }

  // verbose = false 时只记交换，堆排序用，免得帧太多
  function siftDown(fr, i, verbose = true) {
    const a = st.a, n = a.length;
    for (;;) {
      const l = 2 * i + 1, r = l + 1;
      if (l >= n) return verbose && fr.push(snap(`a[${i}] = ${a[i]} 没有孩子了，停下。`, { hot: [i] }));
      const c = r < n && a[r] < a[l] ? r : l;
      if (verbose) {
        const kids = r < n ? `两个孩子 ${a[l]} 和 ${a[r]}，较小的是 ${a[c]}` : `只有左孩子 ${a[l]}`;
        fr.push(snap(`a[${i}] = ${a[i]}：${kids}。`, { hot: r < n ? [i, l, r] : [i, l] }));
      }
      if (a[i] <= a[c]) return verbose && fr.push(snap(`${a[i]} 不比 ${a[c]} 大，停下。`, { hot: [i] }));
      swap(i, c);
      fr.push(snap(`${a[c]} 比 ${a[i]} 大，交换，继续往下看。`, { swap: [i, c] }));
      i = c;
    }
  }

  function push(fr, v) {
    if (st.a.length >= MAX) return fr.push(snap(`演示最多放 ${MAX} 个，先 pop 几个吧。`));
    st.a.push(v);
    fr.push(snap(`① ${v} 先放到数组末尾，也就是树的最后一个位置。`, { hot: [st.a.length - 1] }));
    siftUp(fr, st.a.length - 1);
    fr.push(snap(`push 完成。只走了一条到根的路：O(log n)。`));
  }

  function pop(fr, verbose = true) {
    const a = st.a;
    if (!a.length) return fr.push(snap("堆是空的，pop 抛 IndexError。"));
    const top = a[0];
    verbose && fr.push(snap(`堆顶 ${top} 就是最小值，拿走它。`, { hot: [0] }));
    if (a.length === 1) {
      a.pop();
      if (!verbose) st.out.push(top);
      return fr.push(snap(`只剩这一个，直接删掉。返回 ${top}。`));
    }
    a[0] = a.pop();
    if (!verbose) st.out.push(top);
    fr.push(snap(`末尾的 ${a[0]} 挪到堆顶${verbose ? "，然后往下沉" : ""}。`, { swap: [0] }));
    siftDown(fr, 0, verbose);
    verbose && fr.push(snap(`pop 完成，返回 ${top}。O(log n)。`));
  }

  function heapify(fr) {
    st.a = [9, 4, 7, 1, 8, 2, 6, 3, 5];
    st.out = [];
    const n = st.a.length;
    fr.push(snap(`一个乱序数组。从最后一个有孩子的节点 a[${(n >> 1) - 1}] 开始，往前逐个下沉。`));
    for (let i = (n >> 1) - 1; i >= 0; i--) {
      fr.push(snap(`轮到 a[${i}] = ${st.a[i]} 下沉。`, { hot: [i] }));
      siftDown(fr, i);
    }
    fr.push(snap("建堆完成：每个父亲都比孩子小。O(n)。"));
  }

  function heapSort(fr) {
    st.out = [];
    if (!st.a.length) return fr.push(snap("堆是空的，没什么可排。"));
    fr.push(snap("堆排序：一直 pop，拿出来的就是从小到大。"));
    while (st.a.length) pop(fr, false);
    fr.push(snap(`排好了：${st.out.join(" ")}。n 次 pop，每次 O(log n)，共 O(n log n)。`));
  }

  const val = el("input", { type: "number", value: "0", "aria-label": "要插入的值" });
  const run = op => () => {
    if (op !== heapSort) st.out = [];
    const fr = [snap("操作前的样子。")];
    op(fr, Number(val.value));
    player.load(fr);
  };
  const reset = () => {
    st = { a: [1, 3, 2, 6, 4, 5], out: [] };
    player.load([snap("一个最小堆：每个父亲都比孩子小。上面是树，下面是它在数组里的样子。")]);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "值 ="), val,
    el("button", { onclick: run(push) }, "push(值)"),
    el("button", { onclick: run(f => pop(f)) }, "pop"),
    el("button", { onclick: run(heapify) }, "heapify 乱序数组"),
    el("button", { onclick: run(heapSort) }, "堆排序"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
