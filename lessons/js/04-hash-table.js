// 动画：自己操作一个拉链法哈希表。key 只用整数，这样 hash(key) 就是它自己，下标 = key % 桶数。
(() => {
  const root = document.getElementById("hmap");
  const LOAD = 0.75;
  let st;

  const copy = bs => bs.map(b => b.map(p => ({ ...p })));
  const size = bs => bs.reduce((n, b) => n + b.length, 0);

  // mark：{ bucket, pair: [桶, 第几个], cls }；old：扩容时的旧桶
  function snap(say, mark = {}, old = null) {
    return { say, mark, buckets: copy(st.buckets), old: old && copy(old) };
  }

  function drawBuckets(bs, mark, title) {
    return el("div", { class: "table" },
      title && el("p", { class: "label" }, title),
      bs.map((b, i) => el("div", { class: "row bucket" },
        box(`[${i}]`, "small idx" + (mark.bucket === i ? " hot" : "")),
        el("span", null, "→"),
        b.length ? b.flatMap((p, j) => {
          const on = mark.pair && mark.pair[0] === i && mark.pair[1] === j;
          const moved = mark.moved && mark.moved.includes(p.k);  // 旧桶里已经搬走的
          const pair = box(`${p.k}: ${p.v}`, "pair" + (on ? " " + mark.cls : "") + (moved ? " moved" : ""));
          return j ? [el("span", null, "→"), pair] : [pair];
        }) : el("span", { class: "label" }, "空"))));
  }

  function render(f) {
    const n = size(f.old || f.buckets), cap = f.buckets.length;  // 搬家途中，元素总数按旧桶算
    return [
      f.old
        ? el("div", { class: "cols" },
            drawBuckets(f.old, f.mark.old || {}, `旧桶（${f.old.length} 个）`),
            drawBuckets(f.buckets, f.mark, `新桶（${cap} 个）`))
        : drawBuckets(f.buckets, f.mark),
      el("p", { class: "stat" },
        "size = ", el("b", { class: "size" }, n),
        "，capacity = ", el("b", { class: "cap" }, cap),
        "，负载因子 = ", el("b", { class: "load" }, (n / cap).toFixed(2))),
    ];
  }

  const player = new Player(root, render);
  const nextVal = () => "abcdefghijklmnopqrstuvwxyz"[st.t++ % 26];  // value 用字母自动编号

  // 算下标，然后沿着链一个个比较。返回 [桶号, 在链上的位置（没找到为 -1）]
  function find(fr, k) {
    const i = k % st.buckets.length;
    fr.push(snap(`hash(${k}) = ${k}，${k} % ${st.buckets.length} = ${i} → 去 ${i} 号桶。`, { bucket: i }));
    const b = st.buckets[i];
    for (let j = 0; j < b.length; j++) {
      if (b[j].k === k) return [i, j];
      fr.push(snap(`链上这个 key 是 ${b[j].k}，不是 ${k}，往后看。`, { bucket: i, pair: [i, j], cls: "hot" }));
    }
    return [i, -1];
  }

  function put(fr, k) {
    const [i, j] = find(fr, k);
    if (j >= 0) {
      st.buckets[i][j].v = nextVal();
      return fr.push(snap(`已经有 key ${k}：只覆盖 value，size 不变。`, { bucket: i, pair: [i, j], cls: "found" }));
    }
    const b = st.buckets[i];
    b.push({ k, v: nextVal() });
    fr.push(snap(b.length > 1
      ? `冲突！${i} 号桶里已经有别的 key，新的一对挂在链的末尾。`
      : `${i} 号桶是空的，直接放进去。`, { bucket: i, pair: [i, b.length - 1], cls: "found" }));
    const n = size(st.buckets), cap = st.buckets.length;
    if (n / cap <= LOAD) return fr.push(snap(`负载因子 ${n}/${cap} = ${(n / cap).toFixed(2)}，没超过 ${LOAD}，不用扩容。`));
    resize(fr, n, cap);
  }

  function resize(fr, n, cap) {
    const old = st.buckets;
    st.buckets = Array.from({ length: cap * 2 }, () => []);
    fr.push(snap(`负载因子 ${n}/${cap} = ${(n / cap).toFixed(2)} > ${LOAD}，链会越来越长。扩容：新开 ${cap * 2} 个桶。`, {}, old));
    const moved = [];
    old.forEach((b, oi) => b.forEach((p, oj) => {
      const i = p.k % st.buckets.length;
      st.buckets[i].push({ ...p });
      fr.push(snap(`rehash：${p.k} % ${st.buckets.length} = ${i}，搬进新的 ${i} 号桶。`,
        { bucket: i, pair: [i, st.buckets[i].length - 1], cls: "found", old: { bucket: oi, pair: [oi, oj], cls: "hot", moved: [...moved] } }, old));
      moved.push(p.k);
    }));
    fr.push(snap(`rehash 完成：桶多了，同一个 key 的下标可能变了，链也变短了。这次搬家 O(n)，均摊下来 put 仍是 O(1)。`));
  }

  function get(fr, k) {
    const [i, j] = find(fr, k);
    if (j < 0) return fr.push(snap(`${i} 号桶里找遍了也没有 ${k}，get 抛 KeyError。`, { bucket: i }));
    fr.push(snap(`找到了：get(${k}) = ${st.buckets[i][j].v}。`, { bucket: i, pair: [i, j], cls: "found" }));
  }

  function remove(fr, k) {
    const [i, j] = find(fr, k);
    if (j < 0) return fr.push(snap(`没有 key ${k}，remove 抛 KeyError。`, { bucket: i }));
    fr.push(snap(`找到 ${k}，把它从 ${i} 号桶的链上摘掉。`, { bucket: i, pair: [i, j], cls: "found" }));
    st.buckets[i].splice(j, 1);
    fr.push(snap("删完了，size 减一。", { bucket: i }));
  }

  const key = el("input", { type: "number", value: "9", min: "0", "aria-label": "key" });
  const run = op => () => {
    const k = Math.max(0, Math.trunc(Number(key.value)) || 0);  // 空输入当 0，负数当 0
    const fr = [snap("操作前的样子。")];
    op(fr, k);
    player.load(fr);
  };
  const reset = () => {
    st = { buckets: [[], [{ k: 5, v: "a" }], [{ k: 2, v: "b" }], []], t: 2 };
    player.load([snap("4 个桶，已经放了 5 和 2。试试 put(9)：9 % 4 = 1，会和 5 撞在同一个桶。")]);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "key ="), key,
    el("button", { onclick: run(put) }, "put(key)"),
    el("button", { onclick: run(get) }, "get(key)"),
    el("button", { onclick: run(remove) }, "remove(key)"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
