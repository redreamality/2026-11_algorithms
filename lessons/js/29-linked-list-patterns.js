// 动画：链表高频技巧。节点按 order 从左到右摆放，箭头按每个节点真实的 next 画；
// 节点下方的橙色字是指向它的指针变量。最后一个节点的 next 如果指回前面，就画“↩ 回到 X”。
(() => {
  const root = document.getElementById("patterns");
  let nodes, order, head;

  function snap(say, { pointers = {}, fade = [] } = {}) {
    return { say, pointers, fade, nodes: structuredClone(nodes), order: [...order], head };
  }

  function render(f) {
    const items = [];
    const first = f.order[0], last = f.order[f.order.length - 1];
    if (first != null && f.order.length > 1 && f.nodes[first].next === null) items.push(el("span", { class: "label" }, "None ←"));
    f.order.forEach((id, k) => {
      const node = f.nodes[id];
      const topTags = [f.head === id && "head", node.dummy && "dummy"].filter(Boolean);
      const names = Object.keys(f.pointers).filter(name => f.pointers[name] === id);
      items.push(el("div", { class: "node" + (names.length ? " hot" : "") + (f.fade.includes(id) ? " fade" : "") },
        el("div", { class: "tag" }, topTags.join(" / ") || " "),
        box(node.value, node.dummy ? "dummy" : ""),
        el("div", { class: "tag ptr" }, names.join(" / ") || " ")));
      if (k < f.order.length - 1) {
        const rightId = f.order[k + 1];
        const skips = node.next != null && f.order.indexOf(node.next) > k + 1;
        const arrow = node.next === rightId ? "→" : f.nodes[rightId].next === id ? "←" : skips ? "⤼" : " ";
        items.push(el("span", { class: "link" }, arrow));
      }
    });
    if (last != null) {
      const tailNext = f.nodes[last].next;
      // 指回左边紧挨着的邻居时，中间已经画了“←”；除非那个邻居也指着尾巴（两节点的环），不用再画
      const leftNeighbor = f.order[f.order.length - 2];
      const alreadyDrawn = tailNext === leftNeighbor && f.nodes[leftNeighbor].next !== last;
      if (tailNext === null) items.push(el("span", { class: "label" }, "→ None"));
      else if (!alreadyDrawn) items.push(el("span", { class: "cycle-back" }, `↩ 回到 ${f.nodes[tailNext].value}`));
    }
    const toNone = Object.keys(f.pointers).filter(name => f.pointers[name] === null);
    const values = [];
    for (let id = f.head, steps = 0; id != null && steps <= f.order.length; id = f.nodes[id].next, steps++) values.push(f.nodes[id].value);
    const hasLoop = f.head != null && values.length > f.order.length;
    return [
      el("div", { class: "row list" }, items),
      toNone.length && el("p", { class: "label" }, toNone.join("、") + " = None"),
      el("p", { class: "stat" }, "从 head 沿 next 读出：",
        el("b", { class: "walk" }, hasLoop ? "（有环，读不完）" : `[${values.join(", ")}]`)),
    ];
  }

  const player = new Player(root, render);

  function build(values, cycleEntryIndex = -1) {
    nodes = {};
    order = values.map((value, k) => { nodes[k] = { value, next: null }; return k; });
    order.forEach((id, k) => { nodes[id].next = k + 1 < order.length ? order[k + 1] : null; });
    if (cycleEntryIndex >= 0 && order.length) nodes[order[order.length - 1]].next = order[cycleEntryIndex];
    head = order.length ? order[0] : null;
  }

  const valueOf = id => (id === null ? "None" : nodes[id].value);

  function reverseList(frames) {
    let previousNode = null, currentNode = head;
    frames.push(snap("准备：previous_node = None（反转好的部分还是空的），current_node = head。",
      { pointers: { previous_node: previousNode, current_node: currentNode } }));
    while (currentNode !== null) {
      const nextNode = nodes[currentNode].next;
      frames.push(snap(`① next_node = current_node.next：先记住 ${valueOf(currentNode)} 后面的 ${valueOf(nextNode)}，不然下一步改完指针就找不到它了。`,
        { pointers: { previous_node: previousNode, current_node: currentNode, next_node: nextNode } }));
      nodes[currentNode].next = previousNode;
      frames.push(snap(`② current_node.next = previous_node：让 ${valueOf(currentNode)} 掉头，指向 ${valueOf(previousNode)}。`,
        { pointers: { previous_node: previousNode, current_node: currentNode, next_node: nextNode } }));
      previousNode = currentNode;
      currentNode = nextNode;
      frames.push(snap(`③ previous_node 挪到 ${valueOf(previousNode)}，current_node 挪到 ${valueOf(currentNode)}。`
        + "previous_node 开头的那一段已经反转好了。",
        { pointers: { previous_node: previousNode, current_node: currentNode } }));
    }
    head = previousNode;
    frames.push(snap("current_node 是 None，循环结束。previous_node 指着原来的尾巴，它就是新的头：return previous_node。",
      { pointers: { previous_node: previousNode } }));
    order.reverse();
    frames.push(snap("把节点重新从左往右摆好：反转完成。整个过程没有新建任何节点，只改了 next。"));
  }

  function middleNode(frames) {
    let slow = head, fast = head;
    frames.push(snap("slow 和 fast 都从 head 出发。slow 每次走 1 步，fast 每次走 2 步。", { pointers: { slow, fast } }));
    while (fast !== null && nodes[fast].next !== null) {
      slow = nodes[slow].next;
      fast = nodes[nodes[fast].next].next;
      frames.push(snap(`slow 走 1 步到 ${valueOf(slow)}，fast 走 2 步到 ${valueOf(fast)}。`, { pointers: { slow, fast } }));
    }
    const reason = fast === null ? "fast 已经走到 None（节点数是偶数）" : "fast.next 是 None（节点数是奇数，fast 停在最后一个节点）";
    frames.push(snap(`${reason}，停下。slow 正好走了一半：中点是 ${valueOf(slow)}。`, { pointers: { slow } }));
  }

  function removeNthFromEnd(frames, n) {
    const length = order.length;
    if (n < 1 || n > length) return frames.push(snap(`N 必须在 1 到 ${length} 之间。`));
    const dummyId = "dummy";
    nodes[dummyId] = { value: "哑", next: head, dummy: true };
    order.unshift(dummyId);
    let ahead = dummyId, behind = dummyId;
    frames.push(snap(`在 head 前面放一个哑节点：dummy_node.next = head。ahead 和 behind 都从哑节点出发。`,
      { pointers: { ahead, behind } }));
    for (let step = 1; step <= n; step++) {
      ahead = nodes[ahead].next;
      frames.push(snap(`ahead 先走第 ${step} 步（共 ${n} 步），到 ${valueOf(ahead)}。`, { pointers: { ahead, behind } }));
    }
    frames.push(snap(`现在 ahead 比 behind 领先 ${n} 步。接下来两个一起走，直到 ahead.next 是 None。`, { pointers: { ahead, behind } }));
    while (nodes[ahead].next !== null) {
      ahead = nodes[ahead].next;
      behind = nodes[behind].next;
      frames.push(snap(`一起走一步：ahead 到 ${valueOf(ahead)}，behind 到 ${valueOf(behind)}。`, { pointers: { ahead, behind } }));
    }
    const target = nodes[behind].next;
    frames.push(snap(`ahead 停在最后一个节点。behind 的下一个（${valueOf(target)}）就是倒数第 ${n} 个`
      + (behind === dummyId ? "，它正是头节点，而 behind 还停在哑节点上。" : "。"),
      { pointers: { ahead, behind, target } }));
    nodes[behind].next = nodes[target].next;
    frames.push(snap(`behind.next = behind.next.next：跳过 ${valueOf(target)}。`
      + (behind === dummyId ? "删头节点和删中间节点是同一句代码，这就是哑节点的作用。" : ""),
      { pointers: { behind }, fade: [target] }));
    order = order.filter(id => id !== target);
    head = nodes[dummyId].next;
    frames.push(snap("返回 dummy_node.next，它就是新的头（不能返回旧的 head，它可能刚被删掉）。", { pointers: { behind } }));
    order = order.filter(id => id !== dummyId);
    delete nodes[dummyId];
    const values = [];
    for (let id = head; id !== null; id = nodes[id].next) values.push(nodes[id].value);
    frames.push(snap(`删除完成，结果是 [${values.join(", ")}]。`));
  }

  function findCycleEntry(frames) {
    if (order.length < 2) return frames.push(snap("至少要 2 个节点才好演示环。"));
    let slow = head, fast = head, meeting = null;
    frames.push(snap(`尾巴 ${valueOf(order[order.length - 1])} 的 next 指回了前面，形成环。`
      + "第一阶段：slow 每次 1 步，fast 每次 2 步，看会不会相遇。", { pointers: { slow, fast } }));
    let steps = 0;
    while (fast !== null && nodes[fast].next !== null) {
      slow = nodes[slow].next;
      fast = nodes[nodes[fast].next].next;
      steps++;
      if (slow === fast) {
        meeting = slow;
        frames.push(snap(`slow 走到 ${valueOf(slow)}，fast 也走到 ${valueOf(fast)}：相遇了，说明有环！此时 slow 共走了 ${steps} 步。`,
          { pointers: { slow, fast } }));
        break;
      }
      frames.push(snap(`slow 走 1 步到 ${valueOf(slow)}，fast 走 2 步到 ${valueOf(fast)}。`, { pointers: { slow, fast } }));
    }
    let fromHead = head, fromMeeting = meeting;
    frames.push(snap("第二阶段：from_head 从 head 出发，from_meeting 从相遇点出发，都每次走 1 步。",
      { pointers: { from_head: fromHead, from_meeting: fromMeeting } }));
    while (fromHead !== fromMeeting) {
      fromHead = nodes[fromHead].next;
      fromMeeting = nodes[fromMeeting].next;
      frames.push(snap(`都走 1 步：from_head 到 ${valueOf(fromHead)}，from_meeting 到 ${valueOf(fromMeeting)}。`,
        { pointers: { from_head: fromHead, from_meeting: fromMeeting } }));
    }
    frames.push(snap(`两个指针在 ${valueOf(fromHead)} 碰头：入环点是 ${valueOf(fromHead)}。`,
      { pointers: { from_head: fromHead, from_meeting: fromMeeting } }));
  }

  const valuesInput = el("input", { type: "text", value: "1, 2, 3, 4, 5", size: "18", "aria-label": "链表的值" });
  const nInput = el("input", { type: "number", value: "2", min: "1", "aria-label": "N" });
  const entryInput = el("input", { type: "number", value: "2", min: "0", "aria-label": "入环下标" });
  const readValues = () => {
    const values = valuesInput.value.split(/[^0-9-]+/).filter(Boolean).map(Number).slice(0, 9);
    return values.length ? values : [1, 2, 3, 4, 5];
  };
  const run = (operation, withCycle = false) => () => {
    const values = readValues();
    const entryIndex = Math.min(values.length - 1, Math.max(0, Number(entryInput.value) || 0));
    build(values, withCycle ? entryIndex : -1);
    const frames = [snap("操作前的样子。")];
    operation(frames, Number(nInput.value));
    player.load(frames);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "链表"), valuesInput,
    el("button", { onclick: run(reverseList) }, "反转链表"),
    el("button", { onclick: run(middleNode) }, "找中点"),
    el("span", { class: "label" }, "N ="), nInput,
    el("button", { onclick: run(removeNthFromEnd) }, "删除倒数第 N 个"),
    el("span", { class: "label" }, "尾巴指回下标"), entryInput,
    el("button", { onclick: run(findCycleEntry, true) }, "判环并找入环点")));
  build(readValues());
  player.load([snap("一条单链表。点上面的按钮选一个技巧。")]);
})();
