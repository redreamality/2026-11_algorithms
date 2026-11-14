// 动画：活动选择。活动画在时间轴上，按某个顺序逐个看：不和已选的重叠就选，否则跳过。
(() => {
  const root = document.getElementById("acts");
  const T = 16;  // 时间轴 0..16
  const ACTS = [
    ["A", 1, 4], ["B", 3, 5], ["C", 0, 6], ["D", 5, 7],
    ["E", 3, 9], ["F", 6, 10], ["G", 8, 11], ["H", 12, 16],
  ];
  const pct = t => (t / T * 100) + "%";

  function render(f) {
    const rows = f.order.map(([name, s, e]) => {
      const cls = name === f.cur ? "cur" : f.picked.includes(name) ? "picked" : f.skipped.includes(name) ? "skipped" : "";
      return el("div", { class: "act " + cls, "data-act": name },
        el("span", { class: "act-name" }, name),
        el("div", { class: "track" },
          el("span", { class: "seg", style: `left:${pct(s)};width:${pct(e - s)}` }, `${s}–${e}`),
          f.end !== null && el("span", { class: "endline", style: `left:${pct(f.end)}` })));
    });
    return [
      el("div", { class: "timeline" }, rows),
      el("p", { class: "stat" }, "已选 ", el("b", { class: "count" }, f.picked.length), " 个",
        f.end !== null ? `；上一个选中的在 ${f.end} 结束（红线）` : ""),
    ];
  }

  const player = new Player(root, render);

  function run(key, label) {
    const order = [...ACTS].sort((a, b) => a[key] - b[key] || a[2] - b[2]);
    const picked = [], skipped = [];
    let end = null;
    const snap = (say, cur = null) => ({ say, cur, order, end, picked: [...picked], skipped: [...skipped] });
    const fr = [snap(`按${label}从早到晚排好，从上往下逐个看。`)];
    for (const [name, s, e] of order) {
      if (end === null || s >= end) {
        fr.push(snap(`${name}（${s}–${e}）在 ${s} 开始，不早于 ${end ?? "-∞"}：不冲突，选它。`, name));
        picked.push(name);
        end = e;
      } else {
        fr.push(snap(`${name}（${s}–${e}）在 ${s} 开始，早于 ${end}：和已选的重叠，跳过。`, name));
        skipped.push(name);
      }
    }
    fr.push(snap(`看完了，选了 ${picked.length} 个：${picked.join("、")}。`
      + (key === 2 ? "按结束时间选，这就是最多的。" : "比按结束时间少：先选的 C 太长，占掉了后面好几个。")));
    player.load(fr);
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => run(2, "结束时间") }, "按结束时间选"),
    el("button", { onclick: () => run(1, "开始时间") }, "按开始时间选（反例）")));
  player.load([{ say: "8 个活动，同一时间只能参加一个。点上面的按钮开始。", cur: null, order: ACTS, end: null, picked: [], skipped: [] }]);
})();
