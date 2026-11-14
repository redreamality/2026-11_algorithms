// 动画：自己操作一个动态数组。每个按钮生成一串帧，看清楚每一步挪了谁。
(() => {
  const root = document.getElementById("darray");
  const st = { data: [null], size: 0, adds: 0, copies: 0, next: 1 };

  function snap(say, { hot = [], old = null, oldHot = [] } = {}) {
    return { say, hot, old: old && [...old], oldHot, data: [...st.data], size: st.size, adds: st.adds, copies: st.copies };
  }

  const cells = (data, hot) => data.map((v, k) => box(v ?? "·", v == null ? "empty" : hot.includes(k) ? "hot" : ""));

  const player = new Player(root, f => [
    f.old && el("div", { class: "row" }, el("span", { class: "label" }, "旧格子："), cells(f.old, f.oldHot)),
    el("div", { class: "row data" }, el("span", { class: "label" }, f.old ? "新格子：" : "格子："), cells(f.data, f.hot)),
    el("p", { class: "stat" },
      "size = ", el("b", { class: "size" }, f.size),
      "，capacity = ", el("b", { class: "cap" }, f.data.length),
      `　｜　一共加了 ${f.adds} 个元素，搬家共搬了 ${f.copies} 次，平均每加一个搬 `,
      el("b", {}, f.adds ? (f.copies / f.adds).toFixed(2) : "0"), " 次"),
  ]);

  function resize(fr) {
    const old = st.data;
    st.data = new Array(old.length * 2).fill(null);
    fr.push(snap(`满了！新开一排 ${st.data.length} 个格子（翻倍）。`, { old }));
    for (let k = 0; k < st.size; k++) {
      st.data[k] = old[k];
      st.copies++;
      fr.push(snap(`搬第 ${k} 个：${old[k]}`, { old, oldHot: [k], hot: [k] }));
    }
    fr.push(snap("搬完了，旧的那排扔掉。"));
  }

  function append(fr) {
    const v = st.next++;
    st.adds++;
    if (st.size === st.data.length) resize(fr);
    st.data[st.size++] = v;
    fr.push(snap(`append(${v})：放进第 ${st.size - 1} 格。O(1)`, { hot: [st.size - 1] }));
  }

  function insert(fr, i) {
    if (i < 0 || i > st.size) return fr.push(snap(`insert(${i})：下标越界，抛 IndexError。`));
    const v = st.next++;
    st.adds++;
    if (st.size === st.data.length) resize(fr);
    for (let k = st.size; k > i; k--) {
      st.data[k] = st.data[k - 1];
      fr.push(snap(`从最后一个开始往右挪：第 ${k - 1} 格 → 第 ${k} 格`, { hot: [k] }));
    }
    st.data[i] = v;
    st.size++;
    fr.push(snap(`腾出第 ${i} 格，放进 ${v}。挪了 ${st.size - 1 - i} 次，所以是 O(n)。`, { hot: [i] }));
  }

  function pop(fr) {
    if (st.size === 0) return fr.push(snap("数组是空的，pop 抛 IndexError。"));
    const v = st.data[--st.size];
    st.data[st.size] = null;
    fr.push(snap(`pop() 返回 ${v}，只动了最后一格。O(1)`));
  }

  function removeAt(fr, i) {
    if (i < 0 || i >= st.size) return fr.push(snap(`remove_at(${i})：下标越界，抛 IndexError。`));
    const v = st.data[i];
    fr.push(snap(`要删第 ${i} 格的 ${v}，右边的要逐个往左挪。`, { hot: [i] }));
    for (let k = i; k < st.size - 1; k++) {
      st.data[k] = st.data[k + 1];
      fr.push(snap(`第 ${k + 1} 格 → 第 ${k} 格`, { hot: [k] }));
    }
    st.data[--st.size] = null;
    fr.push(snap(`删完了，返回 ${v}。`));
  }

  const idx = el("input", { type: "number", value: "0", min: "0", "aria-label": "下标 i" });
  const run = (...ops) => () => {
    const fr = [snap("操作前的样子。")];
    for (const op of ops) op(fr, Number(idx.value));
    player.load(fr);
  };
  const reset = () => {
    Object.assign(st, { data: [null], size: 0, adds: 0, copies: 0, next: 1 });
    player.load([snap("空数组：capacity = 1。点 append 试试。")]);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: run(append) }, "append"),
    el("button", { onclick: run(...Array(8).fill(append)) }, "连续 append 8 次"),
    el("button", { onclick: run(pop) }, "pop"),
    el("span", { class: "label" }, "下标 i ="), idx,
    el("button", { onclick: run(insert) }, "insert(i)"),
    el("button", { onclick: run(removeAt) }, "remove_at(i)"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
