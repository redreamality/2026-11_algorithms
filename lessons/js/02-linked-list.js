// 动画：自己操作一条单链表。节点按 order 从左到右摆放，箭头按每个节点真实的 next 画。
(() => {
  const root = document.getElementById("llist");
  let st;

  function snap(say, { ptrs = {}, fade = [] } = {}) {
    return { say, ptrs, fade, nodes: structuredClone(st.nodes), order: [...st.order], head: st.head, tail: st.tail };
  }

  function render(f) {
    const items = [];
    const first = f.order[0], last = f.order[f.order.length - 1];
    if (first != null && f.order.length > 1 && f.nodes[first].next === null) items.push(el("span", { class: "label" }, "None ←"));
    f.order.forEach((id, k) => {
      const n = f.nodes[id];
      const tags = [f.head === id && "head", f.tail === id && "tail"].filter(Boolean);
      const ptrs = Object.keys(f.ptrs).filter(p => f.ptrs[p] === id);
      items.push(el("div", { class: "node" + (ptrs.length ? " hot" : "") + (f.fade.includes(id) ? " fade" : "") },
        el("div", { class: "tag" }, tags.join(" / ") || " "),
        box(n.v),
        el("div", { class: "tag ptr" }, ptrs.join(" / ") || " ")));
      if (k < f.order.length - 1) {
        const nx = f.order[k + 1];
        const skips = n.next != null && f.order.indexOf(n.next) > k + 1;  // 跳过了右边的邻居
        const arrow = n.next === nx ? "→" : f.nodes[nx].next === id ? "←" : skips ? "⤼" : " ";
        items.push(el("span", { class: "link" }, arrow));
      }
    });
    if (last != null && f.nodes[last].next === null) items.push(el("span", { class: "label" }, "→ None"));
    if (!f.order.length) items.push(el("span", { class: "label" }, "head = tail = None（空链表）"));
    const toNone = Object.keys(f.ptrs).filter(p => f.ptrs[p] === null);
    return [
      el("div", { class: "row list" }, items),
      toNone.length && el("p", { class: "label" }, toNone.join("、") + " = None"),
      el("p", { class: "stat" }, "size = ", el("b", { class: "size" }, f.order.filter(id => !f.fade.includes(id)).length)),
    ];
  }

  const player = new Player(root, render);

  function add(v) {
    const id = st.nextId++;
    st.nodes[id] = { v, next: null };
    return id;
  }

  function pushFront(fr) {
    const id = add(st.nextVal++);
    st.nodes[id].next = st.head;
    st.order.unshift(id);
    fr.push(snap(`① 新建节点 ${st.nodes[id].v}，让它的 next 指向旧的 head。`));
    st.head = id;
    if (st.tail === null) st.tail = id;
    fr.push(snap("② 再把 head 挪到新节点。顺序反过来，旧的头就找不到了。"));
  }

  function pushBack(fr) {
    const id = add(st.nextVal++);
    st.order.push(id);
    if (st.tail === null) {
      st.head = st.tail = id;
      return fr.push(snap(`链表是空的：head 和 tail 都指向新节点 ${st.nodes[id].v}。`));
    }
    fr.push(snap(`① 新建节点 ${st.nodes[id].v}。`));
    st.nodes[st.tail].next = id;
    fr.push(snap("② 旧 tail 的 next 指向它。"));
    st.tail = id;
    fr.push(snap("③ tail 挪过去。不用从头走，所以是 O(1)。"));
  }

  function popFront(fr) {
    if (st.head === null) return fr.push(snap("链表是空的，pop_front 抛 IndexError。"));
    const old = st.head;
    st.head = st.nodes[old].next;
    if (st.head === null) st.tail = null;
    fr.push(snap(`head 挪到下一个，旧的头 ${st.nodes[old].v} 没人指着了。`, { fade: [old] }));
    st.order = st.order.filter(id => id !== old);
    fr.push(snap(st.head === null ? "链表空了：head 和 tail 都要变回 None。" : "删完了。O(1)"));
  }

  function remove(fr, v) {
    let prev = null, cur = st.head;
    while (cur !== null) {
      if (st.nodes[cur].v === v) break;
      fr.push(snap(`cur 上是 ${st.nodes[cur].v}，不是 ${v}，往后走。`, { ptrs: { prev, cur } }));
      prev = cur;
      cur = st.nodes[cur].next;
    }
    if (cur === null) return fr.push(snap(`走到 None 也没找到 ${v}，抛 ValueError（和 list.remove 一样）。`, { ptrs: { prev, cur } }));
    fr.push(snap(`找到 ${v}！要删它，得站在它前一个节点上。`, { ptrs: { prev, cur } }));
    if (prev === null) {
      st.head = st.nodes[cur].next;
      fr.push(snap("它就是头：head 挪到下一个。", { ptrs: { cur }, fade: [cur] }));
    } else {
      st.nodes[prev].next = st.nodes[cur].next;
      fr.push(snap("prev.next = cur.next：直接跳过它。", { ptrs: { prev, cur }, fade: [cur] }));
    }
    if (st.tail === cur) {
      st.tail = prev;
      fr.push(snap("删的正好是尾巴：tail 退回 prev。", { ptrs: { prev }, fade: [cur] }));
    }
    st.order = st.order.filter(id => id !== cur);
    fr.push(snap("删完了。"));
  }

  function reverse(fr) {
    let prev = null, cur = st.head;
    fr.push(snap("准备：prev = None，cur = head。", { ptrs: { prev, cur } }));
    while (cur !== null) {
      const nxt = st.nodes[cur].next;
      fr.push(snap("① nxt = cur.next：先记住后面，等下要用。", { ptrs: { prev, cur, nxt } }));
      st.nodes[cur].next = prev;
      fr.push(snap("② cur.next = prev：掉头。", { ptrs: { prev, cur, nxt } }));
      prev = cur;
      cur = nxt;
      fr.push(snap("③ prev 和 cur 一起往前走一步。", { ptrs: { prev, cur } }));
    }
    [st.head, st.tail] = [prev, st.head];
    fr.push(snap("cur 走到 None，结束。head 换成 prev，tail 换成原来的头。", { ptrs: { prev } }));
    st.order.reverse();
    fr.push(snap("重新从左往右摆好：反转完成。没有新建任何节点。"));
  }

  const val = el("input", { type: "number", value: "3", "aria-label": "要删的值" });
  const run = op => () => {
    const fr = [snap("操作前的样子。")];
    op(fr, Number(val.value));
    player.load(fr);
  };
  const reset = () => {
    st = { nodes: {}, order: [], head: null, tail: null, nextId: 0, nextVal: 1 };
    const fr = [];
    for (let k = 0; k < 4; k++) pushBack(fr);
    player.load([snap("一条有 4 个节点的链表。每个节点只知道下一个是谁。")]);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: run(pushFront) }, "push_front"),
    el("button", { onclick: run(pushBack) }, "push_back"),
    el("button", { onclick: run(popFront) }, "pop_front"),
    el("span", { class: "label" }, "值 ="), val,
    el("button", { onclick: run(remove) }, "remove(值)"),
    el("button", { onclick: run(reverse) }, "reverse"),
    el("button", { onclick: reset }, "重置")));
  reset();
})();
