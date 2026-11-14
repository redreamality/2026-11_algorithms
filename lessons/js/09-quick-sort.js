// 动画：快速排序（Lomuto 分区）。基准固定取 a[hi]，这样有序输入的退化也能看出来。
// 数组只有一行，原地交换；当前区间外的格子变淡，已经站到最终位置的变绿。
(() => {
  const root = document.getElementById("qsort");
  let a, done, cmp;

  function snap(say, { lo = 0, hi = a.length - 1, i = null, j = null, pv = null, hot = [] } = {}) {
    return { say, lo, hi, i, j, pv, hot, cmp, vals: [...a], done: [...done] };
  }

  function render(f) {
    const cells = f.vals.map((v, k) => {
      const ptrs = [f.i === k && "i", f.j === k && "j"].filter(Boolean);
      const cls = ["small",
        f.done.includes(k) && "done",
        f.i != null && k >= f.lo && k < f.i && "less",
        f.hot.includes(k) && "hot",
        f.pv === k && "pivot"].filter(Boolean).join(" ");
      return el("div", { class: "node" + (k < f.lo || k > f.hi ? " out" : "") },
        el("div", { class: "tag" }, f.pv === k ? "基准" : " "),
        box(v, cls),
        el("div", { class: "tag ptr" }, ptrs.join(" / ") || " "));
    });
    return [
      el("div", { class: "row list" }, cells),
      el("p", { class: "stat" }, "比较次数 = ", el("b", { class: "cmp" }, f.cmp)),
    ];
  }

  const player = new Player(root, render);

  function partition(lo, hi, fr) {
    const pivot = a[hi];
    let i = lo;
    const at = (j, hot = []) => ({ lo, hi, i, j, pv: hi, hot });
    fr.push(snap(`分区 a[${lo}..${hi}]：基准取最后一个 ${pivot}。i = ${lo}，i 左边是“小于区”（现在是空的）。`, at(lo)));
    for (let j = lo; j < hi; j++) {
      cmp++;
      if (a[j] < pivot) {
        fr.push(snap(`${a[j]} < ${pivot}：把它换到 i 的位置，进小于区。`, at(j, [i, j])));
        [a[i], a[j]] = [a[j], a[i]];
        i++;
        fr.push(snap(i - 1 === j ? "i 和 j 在同一格，自己和自己换。i 往右挪一格。" : "交换完成，i 往右挪一格。", at(j)));
      } else {
        fr.push(snap(`${a[j]} ≥ ${pivot}：不动，j 往后走。`, at(j, [j])));
      }
    }
    fr.push(snap(`j 扫完了。把基准 ${pivot} 和 a[i] 交换，放到小于区后面。`, { lo, hi, i, pv: hi, hot: [i, hi] }));
    [a[i], a[hi]] = [a[hi], a[i]];
    done.push(i);
    fr.push(snap(`基准 ${pivot} 站到了最终位置 ${i}：左边都比它小，右边都不比它小。`, { lo, hi, hot: [i] }));
    return i;
  }

  function sort(lo, hi, fr) {
    if (lo > hi) return;
    if (lo === hi) {
      done.push(lo);
      return fr.push(snap(`a[${lo}..${hi}] 只剩 ${a[lo]} 一个，它自己就在最终位置。`, { lo, hi, hot: [lo] }));
    }
    const p = partition(lo, hi, fr);
    sort(lo, p - 1, fr);
    sort(p + 1, hi, fr);
  }

  const input = el("input", { type: "text", value: "5 2 8 1 9 3 6 4", "aria-label": "数组", size: "22" });

  function run(op) {
    a = input.value.trim().split(/[\s,，]+/).filter(Boolean).map(Number);
    done = [];
    cmp = 0;
    if (!a.length || a.length > 10 || a.some(v => !Number.isInteger(v))) {
      a = [];
      return player.load([snap("请输入 1～10 个整数，用空格隔开。")]);
    }
    const fr = [snap("原数组。")];
    if (op === "show") return player.load(fr);
    if (op === "partition") {
      partition(0, a.length - 1, fr);
    } else {
      sort(0, a.length - 1, fr);
      const n = a.length;
      fr.push(snap(`排好了！共比较 ${cmp} 次（n log n ≈ ${Math.round(n * Math.log2(n))}，n²/2 = ${n * n / 2}）。` +
        "基准固定取最后一个，输入已经有序时就会退化到 n²/2 左右，所以实际要随机挑基准。"));
    }
    player.load(fr);
  }

  const shuffle = () => {
    input.value = Array.from({ length: 8 }, () => 1 + Math.floor(Math.random() * 9)).join(" ");
    run();
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "数组 ="), input,
    el("button", { onclick: () => run("partition") }, "partition"),
    el("button", { onclick: () => run() }, "quick_sort"),
    el("button", { onclick: shuffle }, "随机一组")));
  run("show");
})();
