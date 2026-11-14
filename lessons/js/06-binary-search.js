// 动画：在有序数组上二分。灰掉的格子已经被排除，答案只可能在 [lo, hi) 里。
(() => {
  const root = document.getElementById("bsearch");
  const A = [1, 3, 4, 7, 7, 7, 9, 12, 15, 18];
  const NB = " ";

  const snap = (say, lo, hi, { mid = null, found = null, cmp = 0 } = {}) => ({ say, lo, hi, mid, found, cmp });

  function render(f) {
    // 最后多画一个虚线格子“末尾”，因为 hi（和 lower_bound 的结果）可以等于 len(a)
    const cells = [...A, null].map((v, k) => {
      const ptrs = [k === f.lo && "lo", k === f.mid && "mid", k === f.hi && "hi"].filter(Boolean);
      const out = v != null && k !== f.found && (k < f.lo || k >= f.hi);
      const cls = k === f.found ? "found" : v == null ? "empty" : k === f.mid ? "hot" : "";
      return el("div", { class: "node" + (out ? " fade" : ""), "data-i": k },
        el("div", { class: "tag" }, v == null ? "末尾" : String(k)),
        box(v ?? "·", cls),
        el("div", { class: "tag ptr" }, ptrs.join(" / ") || NB));
    });
    return [
      el("div", { class: "row list" }, cells),
      el("p", { class: "stat" },
        "区间 [lo, hi) = ", el("b", { class: "range" }, `[${f.lo}, ${f.hi})`),
        "，还剩 ", el("b", { class: "left" }, f.hi - f.lo), " 个，已比较 ", el("b", { class: "cmp" }, f.cmp), " 次"),
    ];
  }

  const player = new Player(root, render);

  // 三种操作共用一个循环，区别只在“mid 算不算偏小”和“相等时停不停”
  function run(t, kind) {
    const fr = [];
    let lo = 0, hi = A.length, cmp = 0;
    const goal = { binary_search: `找 ${t}`, lower_bound: `找第一个 ≥ ${t} 的位置`, upper_bound: `找第一个 > ${t} 的位置` }[kind];
    fr.push(snap(`${kind}(${t})：${goal}。lo = 0，hi = ${hi}，答案在 [lo, hi) 里，hi 本身不算。`, lo, hi));
    while (lo < hi) {
      const mid = Math.floor((lo + hi) / 2), v = A[mid];
      cmp++;
      const head = `mid = (${lo} + ${hi}) // 2 = ${mid}，a[mid] = ${v}。`;
      if (kind === "binary_search" && v === t) {
        fr.push(snap(`${head}正好是 ${t}，找到了！返回 ${mid}。`, lo, hi, { mid, found: mid, cmp }));
        return player.load(fr);
      }
      const small = kind === "upper_bound" ? v <= t : v < t;
      if (small) {
        fr.push(snap(`${head}${v} ${v === t ? "≤" : "<"} ${t}：mid 和它左边都不是答案，lo = mid + 1。`, lo, hi, { mid, cmp }));
        lo = mid + 1;
      } else if (kind === "binary_search") {
        fr.push(snap(`${head}${v} > ${t}：mid 和它右边都不是答案，hi = mid。`, lo, hi, { mid, cmp }));
        hi = mid;
      } else {
        fr.push(snap(`${head}${v} ${v === t ? "≥" : ">"} ${t}：mid 可能就是答案，但左边也许还有更早的，hi = mid（mid 留在区间外当候选）。`, lo, hi, { mid, cmp }));
        hi = mid;
      }
      fr.push(snap(`区间缩成 [${lo}, ${hi})，还剩 ${hi - lo} 个。`, lo, hi, { cmp }));
    }
    if (kind === "binary_search") fr.push(snap(`lo == hi，区间空了：没有 ${t}，返回 -1。`, lo, hi, { cmp }));
    else fr.push(snap(`lo == hi，区间空了，结束：${kind}(${t}) = ${lo}。`, lo, hi, { found: lo, cmp }));
    player.load(fr);
  }

  const val = el("input", { type: "number", value: "12", "aria-label": "值" });
  const btn = kind => el("button", { onclick: () => run(Number(val.value), kind) }, `${kind}(值)`);
  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "值 ="), val,
    btn("binary_search"), btn("lower_bound"), btn("upper_bound")));
  player.load([snap("一个排好序的数组，上面是下标。选一个值，点按钮开始二分。", 0, A.length)]);
})();
