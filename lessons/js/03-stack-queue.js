// 动画：一个栈（list 末尾是栈顶）和一个环形队列（定长数组 + head + size，下标取模回绕）。

// ---------- 栈 ----------
(() => {
  const root = document.getElementById("stack");
  let items, next;

  const snap = (say, hot = -1) => ({ say, hot, items: [...items] });

  const player = new Player(root, f => [
    el("div", { class: "row data" },
      el("span", { class: "label" }, "栈底"),
      f.items.map((v, k) => box(v, k === f.hot ? "hot" : "")),
      el("span", { class: "label" }, f.items.length ? "← 栈顶" : "（空栈）")),
    el("p", { class: "stat" }, "len = ", el("b", { class: "size" }, f.items.length)),
  ]);

  function push(fr) {
    const v = next++;
    items.push(v);
    fr.push(snap(`push(${v})：append 到 list 末尾，它就是新的栈顶。O(1)`, items.length - 1));
  }

  function pop(fr) {
    if (!items.length) return fr.push(snap("栈是空的，pop 抛 IndexError。"));
    const top = items.length - 1;
    fr.push(snap(`要弹出栈顶 ${items[top]}：最后进来的，最先出去。`, top));
    const v = items.pop();
    fr.push(snap(`pop() 返回 ${v}。O(1)`));
  }

  function peek(fr) {
    if (!items.length) return fr.push(snap("栈是空的，peek 抛 IndexError。"));
    fr.push(snap(`peek() 返回 ${items[items.length - 1]}，只看不拿。`, items.length - 1));
  }

  const run = op => () => {
    const fr = [snap("操作前的样子。")];
    op(fr);
    player.load(fr);
  };
  const reset = () => {
    items = [1, 2, 3];
    next = 4;
    player.load([snap("一个有 3 个元素的栈，3 在最上面。")]);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: run(push) }, "push"),
    el("button", { onclick: run(pop) }, "pop"),
    el("button", { onclick: run(peek) }, "peek"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();

// ---------- 环形队列 ----------
(() => {
  const root = document.getElementById("cqueue");
  let st;

  function snap(say, { hot = [], old = null, oldHot = [] } = {}) {
    return { say, hot, old, oldHot, data: [...st.data], head: st.head, size: st.size };
  }

  // 一排格子：上面标下标，下面标 head / tail（tail = 下一个元素要放的位置）
  function cells(data, hot, head, size) {
    const tail = (head + size) % data.length;
    return data.map((v, k) => {
      const ptrs = head == null ? [] : [k === head && "head", k === tail && "tail"].filter(Boolean);
      return el("div", { class: "node" + (hot.includes(k) ? " hot" : "") },
        el("div", { class: "tag" }, `[${k}]`),
        box(v ?? "·", v == null ? "empty" : ""),
        el("div", { class: "tag ptr" }, ptrs.join(" / ") || " "));
    });
  }

  const player = new Player(root, f => [
    f.old && el("div", { class: "row old" }, el("span", { class: "label" }, "旧数组："), cells(f.old, f.oldHot, null, 0)),
    el("div", { class: "row data" }, el("span", { class: "label" }, f.old ? "新数组：" : "数组："), cells(f.data, f.hot, f.head, f.size)),
    el("p", { class: "stat" },
      "head = ", el("b", { class: "head" }, f.head),
      "，size = ", el("b", { class: "size" }, f.size),
      "，capacity = ", el("b", { class: "cap" }, f.data.length),
      "，tail = (head + size) % capacity = ", el("b", { class: "tail" }, (f.head + f.size) % f.data.length)),
  ]);

  function resize(fr) {
    const old = st.data, cap = old.length;
    st.data = new Array(cap * 2).fill(null);
    const h = st.head;
    st.head = 0;
    const n = st.size;
    st.size = 0;
    fr.push(snap(`满了！size = capacity = ${cap}。新开 ${cap * 2} 个格子，按队列顺序搬。`, { old }));
    for (let k = 0; k < n; k++) {
      const j = (h + k) % cap;
      st.data[k] = old[j];
      st.size++;
      fr.push(snap(`队列第 ${k} 个：旧[(${h} + ${k}) % ${cap}] = 旧[${j}] → 新[${k}]`, { old, oldHot: [j], hot: [k] }));
    }
    fr.push(snap("搬完了，head 归 0，旧数组扔掉。"));
  }

  function enqueue(fr) {
    const v = st.next++;
    if (st.size === st.data.length) resize(fr);
    const cap = st.data.length, raw = st.head + st.size, t = raw % cap;
    st.data[t] = v;
    st.size++;
    const how = raw >= cap ? `下标 ${raw} 超出末尾，% ${cap} 回绕到 ${t}！` : `放进第 ${t} 格。`;
    fr.push(snap(`enqueue(${v})：tail = (${st.head} + ${st.size - 1}) % ${cap} = ${t}，${how}`, { hot: [t] }));
  }

  function dequeue(fr) {
    if (!st.size) return fr.push(snap("队列是空的，dequeue 抛 IndexError。"));
    const h = st.head, v = st.data[h];
    fr.push(snap(`队头在第 ${h} 格，是 ${v}：最先进来的，最先出去。`, { hot: [h] }));
    st.data[h] = null;
    st.head = (h + 1) % st.data.length;
    st.size--;
    const how = h + 1 >= st.data.length ? `，回绕到 ${st.head}` : "";
    fr.push(snap(`dequeue() 返回 ${v}。head = (${h} + 1) % ${st.data.length} = ${st.head}${how}。元素一个都没挪，O(1)。`));
  }

  function peek(fr) {
    if (!st.size) return fr.push(snap("队列是空的，peek 抛 IndexError。"));
    fr.push(snap(`peek() 返回第 ${st.head} 格的 ${st.data[st.head]}，只看不拿。`, { hot: [st.head] }));
  }

  const run = op => () => {
    const fr = [snap("操作前的样子。")];
    op(fr);
    player.load(fr);
  };
  const reset = () => {
    st = { data: [null, null, 3, 4], head: 2, size: 2, next: 5 };
    player.load([snap("capacity = 4。1、2 已经出队，前两格空着，head 在 2。")]);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: run(enqueue) }, "enqueue"),
    el("button", { onclick: run(dequeue) }, "dequeue"),
    el("button", { onclick: run(peek) }, "peek"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
