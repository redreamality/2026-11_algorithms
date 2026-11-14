// 动画：选择排序 / 插入排序，一步步比较、交换。相等的数标上 a、b、c，用来看排序稳不稳定。
(() => {
  const root = document.getElementById("ssort");
  let arr, cmp, moves, algo;  // arr：[{v, t}]，t 是相等元素的标记

  function snap(say, { done = 0, ptrs = {}, hot = [], min = null } = {}) {
    return { say, done, ptrs, hot, min, cmp, moves, algo, arr: arr.map(x => ({ ...x })) };
  }

  function render(f) {
    const items = f.arr.map((x, k) => {
      const ptr = Object.keys(f.ptrs).filter(p => f.ptrs[p] === k);
      const cls = "box" + (k < f.done && !f.hot.includes(k) && f.min !== k ? " done" : "") + (f.hot.includes(k) ? " hot" : "") + (f.min === k ? " found" : "");
      return el("div", { class: "node" },
        el("span", { class: cls }, String(x.v), x.t && el("sub", {}, x.t)),
        el("div", { class: "tag ptr" }, ptr.join(" / ") || " "));
    });
    return [
      el("div", { class: "row list" }, items),
      el("p", { class: "stat" }, "比较次数 = ", el("b", { class: "cmp" }, f.cmp),
        f.algo === "insertion" ? "　挪动次数 = " : "　交换次数 = ", el("b", { class: "moves" }, f.moves)),
    ];
  }

  const player = new Player(root, render);
  const name = x => x.v + (x.t || "");
  const swap = (a, b) => ([arr[a], arr[b]] = [arr[b], arr[a]]);

  function selection(fr) {
    const n = arr.length;
    for (let i = 0; i < n - 1; i++) {
      let m = i;
      fr.push(snap(`第 ${i + 1} 轮：在右边没排好的部分里找最小的，先假设是 ${name(arr[i])}。`, { done: i, ptrs: { i, min: m }, min: m }));
      for (let j = i + 1; j < n; j++) {
        cmp++;
        const less = arr[j].v < arr[m].v;
        fr.push(snap(less ? `${name(arr[j])} < ${name(arr[m])}，最小值换成 ${name(arr[j])}。` : `${name(arr[j])} 不比 ${name(arr[m])} 小，最小值不变。`,
          { done: i, ptrs: { i, j, min: less ? j : m }, hot: [j], min: less ? j : m }));
        if (less) m = j;
      }
      if (m === i) {
        fr.push(snap(`${name(arr[i])} 本来就是最小的，不用交换。左边排好了 ${i + 1} 个。`, { done: i + 1, min: i }));
        continue;
      }
      const jumped = arr.slice(i + 1, m).some(x => x.v === arr[i].v);
      moves++;
      swap(i, m);
      fr.push(snap(`把最小的 ${name(arr[i])} 和位置 ${i} 的 ${name(arr[m])} 交换。` +
        (jumped ? `注意：${name(arr[m])} 被甩到了和它相等的数后面，这就是不稳定！` : ""), { done: i + 1, hot: [i, m] }));
    }
  }

  function insertion(fr) {
    const n = arr.length;
    for (let i = 1; i < n; i++) {
      fr.push(snap(`拿起 ${name(arr[i])}，把它插进左边已经排好的 ${i} 个里。`, { done: i, ptrs: { x: i }, min: i }));
      let k = i;
      while (k > 0) {
        cmp++;
        const a = arr[k - 1], x = arr[k];
        if (a.v > x.v) {
          swap(k - 1, k);
          moves++;
          k--;
          fr.push(snap(`${name(a)} > ${name(x)}，${name(a)} 往右挪一格。`, { done: i + 1, ptrs: { x: k }, hot: [k + 1], min: k }));
        } else {
          fr.push(snap(a.v === x.v ? `${name(a)} = ${name(x)}，相等就停，不越过它：所以插入排序是稳定的。` : `${name(a)} 不比 ${name(x)} 大，停下。`,
            { done: i + 1, ptrs: { x: k }, hot: [k - 1], min: k }));
          break;
        }
      }
      if (k === 0) fr.push(snap(`${name(arr[0])} 走到了最左边。`, { done: i + 1, ptrs: { x: 0 }, min: 0 }));
    }
  }

  const input = el("input", { type: "text", value: "3 5 3 1 4 2", "aria-label": "数组", size: "22" });
  const pick = el("select", { "aria-label": "算法" },
    el("option", { value: "selection" }, "选择排序"),
    el("option", { value: "insertion" }, "插入排序"));

  function run(onlyFirst) {
    const vals = input.value.trim().split(/[\s,，]+/).filter(Boolean).map(Number);
    [cmp, moves, algo] = [0, 0, pick.value];
    arr = [];
    if (!vals.length || vals.length > 10 || vals.some(v => !Number.isInteger(v))) {
      return player.load([snap("请输入 1～10 个整数，用空格隔开。")]);
    }
    // 出现不止一次的数，按出现顺序标上 a、b、c……
    const seen = {};
    arr = vals.map(v => ({ v, t: vals.filter(u => u === v).length > 1 ? "abcdefghij"[(seen[v] = (seen[v] ?? -1) + 1)] : "" }));
    const order = arr.map(name);
    const fr = [snap(`原数组。相等的数标了 a、b…，排完看看它们的先后变没变。`)];
    if (onlyFirst === true) return player.load(fr);
    (algo === "insertion" ? insertion : selection)(fr);
    const dups = arr.filter(x => x.t);
    const stable = dups.every((x, k) => dups.slice(k + 1).every(y => y.v !== x.v || order.indexOf(name(x)) < order.indexOf(name(y))));
    const n = arr.length;
    fr.push(snap(`排好了！比较 ${cmp} 次（n(n−1)/2 = ${n * (n - 1) / 2}）。` +
      (dups.length ? (stable ? "相等的数保持了原来的先后：稳定。" : "相等的数先后颠倒了：不稳定。") : ""), { done: n }));
    player.load(fr);
  }

  const preset = s => () => { input.value = s; run(); };
  const shuffle = () => preset(Array.from({ length: 8 }, () => 1 + Math.floor(Math.random() * 9)).join(" "))();

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "数组 ="), input, pick,
    el("button", { onclick: run }, "排序"),
    el("button", { onclick: preset("1 2 4 3 5 6 8 7") }, "近乎有序"),
    el("button", { onclick: shuffle }, "随机一组")));
  run(true);
})();
