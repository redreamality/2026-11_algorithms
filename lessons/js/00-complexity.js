// 动画 1：拖动 n，看各档复杂度要做多少步。条形长度以 n² 为满格。
(() => {
  const root = document.getElementById("growth");
  const log = n => Math.max(1, Math.ceil(Math.log2(n)));
  const rows = [
    ["O(1)", () => 1],
    ["O(log n)", n => log(n)],
    ["O(n)", n => n],
    ["O(n log n)", n => n * log(n)],
    ["O(n²)", n => n * n],
  ];
  const slider = el("input", { type: "range", min: "1", max: "100", value: "10", "aria-label": "n" });
  const nLabel = el("b", { class: "n" });
  const bars = el("div");
  root.append(el("p", {}, "n = ", nLabel, "　", slider), bars);

  function draw() {
    const n = Number(slider.value);
    nLabel.textContent = n;
    bars.replaceChildren(...rows.map(([name, f]) => {
      const steps = f(n);
      return el("div", { class: "bar-row" },
        el("span", {}, name),
        el("span", { class: "bar-track" }, el("span", { class: "bar", style: `width:${Math.max(0.5, steps / (n * n) * 100)}%` })),
        el("span", { class: "bar-num", "data-name": name }, steps.toLocaleString("en-US")));
    }));
  }
  slider.addEventListener("input", draw);
  draw();
})();

// 动画 2：同一组数，两两比较 vs 用 set，数一数各做了多少次。
(() => {
  const root = document.getElementById("dup");
  let nums = [3, 8, 1, 6, 2, 9, 4, 6];

  const player = new Player(root, f => [
    el("div", { class: "row" }, el("span", { class: "label" }, "nums："),
      f.nums.map((v, k) => box(v, f.hot.includes(k) ? (f.found ? "found" : "hot") : ""))),
    f.set && el("div", { class: "row" }, el("span", { class: "label" }, "set 里："),
      f.set.length ? f.set.map(v => box(v, "small")) : el("span", { class: "label" }, "（空）")),
    el("p", { class: "stat" }, f.set ? "查 set 的次数：" : "比较次数：", el("b", { class: "ops" }, f.ops)),
  ]);

  function slow() {
    const fr = [{ nums, hot: [], ops: 0, say: "两层循环：拿每个数，和它后面的每个数比一次。" }];
    let ops = 0;
    for (let i = 0; i < nums.length; i++) {
      for (let j = i + 1; j < nums.length; j++) {
        ops++;
        const found = nums[i] === nums[j];
        fr.push({ nums, hot: [i, j], ops, found,
          say: found ? `nums[${i}] == nums[${j}]，找到重复！一共比较了 ${ops} 次。`
                     : `比较 nums[${i}] 和 nums[${j}]：${nums[i]} ≠ ${nums[j]}` });
        if (found) return fr;
      }
    }
    fr.push({ nums, hot: [], ops, say: `没有重复。比较了 ${ops} 次，大约是 n²/2。` });
    return fr;
  }

  function fast() {
    const fr = [{ nums, hot: [], ops: 0, set: [], say: "从左到右扫一遍，用 set 记住见过的数。" }];
    const seen = [];
    let ops = 0;
    for (let i = 0; i < nums.length; i++) {
      ops++;
      if (seen.includes(nums[i])) {
        fr.push({ nums, hot: [i], ops, set: [...seen], found: true,
          say: `${nums[i]} 已经在 set 里了，找到重复！只查了 ${ops} 次。` });
        return fr;
      }
      seen.push(nums[i]);
      fr.push({ nums, hot: [i], ops, set: [...seen], say: `${nums[i]} 不在 set 里，把它放进去。` });
    }
    fr.push({ nums, hot: [], ops, set: [...seen], say: `没有重复。只查了 ${ops} 次，正好是 n。` });
    return fr;
  }

  function shuffle() {
    nums = Array.from({ length: 8 }, () => 1 + Math.floor(Math.random() * 20));
    player.load([{ nums, hot: [], ops: 0, say: "换了一组数。选一种办法开始。" }]);
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(slow()) }, "两两比较 O(n²)"),
    el("button", { onclick: () => player.load(fast()) }, "用 set O(n)"),
    el("button", { onclick: shuffle }, "换一组数")));
  player.load([{ nums, hot: [], ops: 0, say: "选一种办法开始，比比哪个做的次数少。" }]);
})();
