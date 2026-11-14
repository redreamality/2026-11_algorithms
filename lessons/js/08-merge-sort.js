// 动画：归并排序。先把数组一层层对半拆到只剩 1 个，再按递归的顺序两两合并。
// 每一段画在它在原数组里的位置正下方，所以拆分树和合并过程能上下对齐。
(() => {
  const root = document.getElementById("msort");
  let segs, cmp, n;  // segs：所有区段 {id, depth, lo, vals, out, taken, state}；state：raw 未排 / merge 合并中 / done 有序

  function snap(say, { show = 99, hot = {} } = {}) {
    return { say, show, hot, cmp, n, segs: segs.map(s => ({ ...s, vals: [...s.vals], out: s.out && [...s.out] })) };
  }

  function render(f) {
    const cells = f.segs.filter(s => s.depth < f.show).map(s => {
      const ptr = f.hot[s.id] || {};
      const shown = s.state === "raw" ? s.vals : s.vals.map((_, k) => k < s.out.length ? s.out[k] : " ");
      return el("span", { class: "seg " + s.state, "data-depth": s.depth, style: `grid-row:${s.depth + 1};grid-column:${s.lo + 1} / span ${s.vals.length};grid-template-columns:repeat(${s.vals.length}, 1fr)` },
        shown.map((v, k) => el("div", { class: "node" + (k < s.taken ? " fade" : "") },
          box(v, "small" + (s.state === "merge" && k >= s.out.length ? " empty" : "") + (k in ptr ? " hot" : "")),
          el("div", { class: "tag ptr" }, ptr[k] || " "))));
    });
    return [
      el("div", { class: "mtree", style: `grid-template-columns:repeat(${f.n}, 48px)` }, cells),
      el("p", { class: "stat" }, "比较次数 = ", el("b", { class: "cmp" }, f.cmp)),
    ];
  }

  const player = new Player(root, render);

  function build(vals, lo, depth) {
    const s = { id: segs.length, depth, lo, vals, out: null, taken: 0, state: "raw" };
    segs.push(s);
    if (vals.length === 1) [s.state, s.out] = ["done", [...vals]];
    else {
      const mid = vals.length >> 1;
      s.kids = [build(vals.slice(0, mid), lo, depth + 1), build(vals.slice(mid), lo + mid, depth + 1)];
    }
    return s;
  }

  function sort(s, fr) {
    if (!s.kids) return;
    const [L, R] = s.kids;
    sort(L, fr);
    sort(R, fr);
    const a = L.out, b = R.out;
    let i = 0, j = 0;
    s.state = "merge";
    s.out = [];
    const ptrs = extra => ({ [L.id]: { [i]: "i" }, [R.id]: { [j]: "j" }, [s.id]: extra });
    fr.push(snap(`合并 [${a.join(", ")}] 和 [${b.join(", ")}]：两边各自已经有序，i、j 都从头开始。`, { hot: ptrs({}) }));
    while (i < a.length && j < b.length) {
      cmp++;
      const k = s.out.length;
      let say;
      if (a[i] <= b[j]) {
        say = a[i] === b[j] ? `${a[i]} = ${b[j]}，相等时取左边的，这样排序是稳定的。` : `${a[i]} < ${b[j]}，取左边的 ${a[i]}，i 往后走。`;
        s.out.push(a[i++]);
      } else {
        say = `${b[j]} < ${a[i]}，取右边的 ${b[j]}，j 往后走。`;
        s.out.push(b[j++]);
      }
      L.taken = i;
      R.taken = j;
      fr.push(snap(say, { hot: ptrs({ [k]: "" }) }));
    }
    const side = i < a.length ? "右" : "左";
    const rest = i < a.length ? a.slice(i) : b.slice(j);
    const k0 = s.out.length;
    s.out.push(...rest);
    L.taken = a.length;
    R.taken = b.length;
    s.state = "done";
    const tail = Object.fromEntries(rest.map((_, k) => [k0 + k, ""]));
    fr.push(snap(`${side}边用完了，另一边剩下的 [${rest.join(", ")}] 不用再比，直接接到后面。得到 [${s.out.join(", ")}]。`, { hot: { [s.id]: tail } }));
  }

  const input = el("input", { type: "text", value: "5 2 4 7 1 3 2 6", "aria-label": "数组", size: "22" });

  function run(onlyFirst) {
    const vals = input.value.trim().split(/[\s,，]+/).filter(Boolean).map(Number);
    segs = [];
    cmp = 0;
    n = Math.max(vals.length, 1);
    if (!vals.length || vals.length > 10 || vals.some(v => !Number.isInteger(v))) {
      return player.load([snap("请输入 1～10 个整数，用空格隔开。", { show: 0 })]);
    }
    const top = build(vals, 0, 0);
    const depth = Math.max(...segs.map(s => s.depth));
    const fr = [snap("原数组。归并排序：拆成两半，各自排好，再合并。", { show: 1 })];
    if (onlyFirst === true) return player.load(fr);
    for (let d = 1; d <= depth; d++) {
      fr.push(snap(d < depth ? "从中间切开，每一段再继续对半切……" : "切到每段只剩 1 个：一个数自己就是有序的。接下来开始两两合并。", { show: d + 1 }));
    }
    sort(top, fr);
    const nlogn = Math.round(vals.length * Math.log2(vals.length));
    fr.push(snap(`排好了！共比较 ${cmp} 次（n log n ≈ ${nlogn}）。一共 ${depth} 层，每层合并加起来最多 n 次比较。`));
    player.load(fr);
  }

  const shuffle = () => {
    input.value = Array.from({ length: 8 }, () => 1 + Math.floor(Math.random() * 9)).join(" ");
    run();
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "数组 ="), input,
    el("button", { onclick: run }, "merge_sort"),
    el("button", { onclick: shuffle }, "随机一组")));
  run(true);
})();
