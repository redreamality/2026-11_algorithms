// 动画：LRU 缓存。上面是哈希表 key_to_node，下面是双向链表（head 哨兵 ⇄ 节点 ⇄ … ⇄ tail 哨兵，越靠左越新）。
// 橙色 = 正在处理的节点，绿色 = 刚插到最前面的节点；被摘下或被淘汰的节点单独显示在链表下方。
(() => {
  const root = document.getElementById("lru");
  let capacity, order, keyToValue, outputs;

  function snap(say, { lookup = null, hot = null, fresh = null, detached = null } = {}) {
    return {
      say, capacity, order: [...order], keyToValue: new Map(keyToValue), outputs: [...outputs],
      lookup, hot, fresh, detached,
    };
  }

  const nodeText = (f, key) => `${key}:${f.keyToValue.get(key)}`;
  const shown = value => (value === null ? "None" : String(value));

  function render(f) {
    const tableBoxes = [...f.keyToValue.keys()].map(key =>
      box(`${key} ↦ 节点 ${nodeText(f, key)}`, key === f.lookup ? "hot" : ""));
    const listItems = [box("head 哨兵", "sentinel")];
    for (const key of f.order) {
      const cls = key === f.hot ? "hot" : key === f.fresh ? "fresh" : "";
      listItems.push(el("span", { class: "link" }, "⇄"), box(nodeText(f, key), cls));
    }
    listItems.push(el("span", { class: "link" }, "⇄"), box("tail 哨兵", "sentinel"));
    return [
      el("div", { class: "row table-row" }, el("span", { class: "label" }, "key_to_node："),
        tableBoxes.length ? tableBoxes : el("span", { class: "label" }, "（空）")),
      el("div", { class: "row dll" }, listItems, el("span", { class: "label" }, "（越靠左越新）")),
      f.detached && el("p", { class: "detached" }, f.detached),
      el("p", { class: "stat" }, `缓存项数 len(key_to_node) = ${f.keyToValue.size} / capacity = ${f.capacity}；各次操作的返回值：`,
        el("b", { class: "outputs" }, `[${f.outputs.map(shown).join(", ")}]`)),
    ];
  }

  const player = new Player(root, render);

  function moveToFront(frames, key, why) {
    const wasFirst = order[0] === key;
    order = order.filter(other => other !== key);
    frames.push(snap(`① _remove_node：让 ${key} 前后的两个节点直接相连，把它摘下来。`,
      { hot: key, detached: `摘下来的节点：${key}:${keyToValue.get(key)}` }));
    order.unshift(key);
    frames.push(snap(`② _add_to_front：插到 head 哨兵后面，${key} 现在是最近用过的。${why}`
      + (wasFirst ? "（它本来就在最前面，摘下再放回，位置不变。）" : ""), { fresh: key }));
  }

  function get(frames, key) {
    frames.push(snap(`get(${key})：先查 key_to_node。`, { lookup: key }));
    if (!keyToValue.has(key)) {
      outputs.push(-1);
      return frames.push(snap(`${key} 不在 key_to_node 里，返回 -1。`));
    }
    frames.push(snap(`key_to_node[${key}] 直接拿到节点 ${key}:${keyToValue.get(key)}，O(1)。get 也算用过，要把它挪到最前面。`,
      { lookup: key, hot: key }));
    outputs.push(keyToValue.get(key));
    moveToFront(frames, key, `返回 ${keyToValue.get(key)}。`);
  }

  function put(frames, key, value) {
    frames.push(snap(`put(${key}, ${value})：先查 key_to_node。`, { lookup: key }));
    outputs.push(null);
    if (keyToValue.has(key)) {
      keyToValue.set(key, value);
      frames.push(snap(`${key} 已经在缓存里：把节点的值改成 ${value}。更新也算用过，要挪到最前面。`, { lookup: key, hot: key }));
      return moveToFront(frames, key, "");
    }
    if (order.length === capacity) {
      const leastRecentKey = order[order.length - 1];
      frames.push(snap(`${key} 不在缓存里，而缓存满了（${order.length} = capacity）。最久没用的是 tail 哨兵前面的 ${leastRecentKey}，淘汰它。`,
        { hot: leastRecentKey }));
      const evictedText = `${leastRecentKey}:${keyToValue.get(leastRecentKey)}`;
      order.pop();
      keyToValue.delete(leastRecentKey);
      frames.push(snap(`_remove_node 把它摘下来，再用节点里存的 key（${leastRecentKey}）删掉 key_to_node[${leastRecentKey}]。`,
        { detached: `被淘汰的节点：${evictedText}（链表和哈希表里都删掉了）` }));
    }
    order.unshift(key);
    keyToValue.set(key, value);
    frames.push(snap(`新建节点 ${key}:${value}，_add_to_front 插到 head 哨兵后面，再登记 key_to_node[${key}] = 这个节点。`,
      { lookup: key, fresh: key }));
  }

  const capacityInput = el("input", { type: "number", value: "2", min: "1", max: "5", "aria-label": "capacity" });
  const keyInput = el("input", { type: "number", value: "1", "aria-label": "key" });
  const valueInput = el("input", { type: "number", value: "1", "aria-label": "value" });

  function reset() {
    capacity = Math.min(5, Math.max(1, Number(capacityInput.value) || 2));
    capacityInput.value = capacity;
    order = [];
    keyToValue = new Map();
    outputs = [];
  }

  const run = operation => () => {
    const frames = [snap("操作前的样子。")];
    operation(frames);
    player.load(frames);
  };

  function playExample() {
    capacityInput.value = 2;
    reset();
    const frames = [snap("LeetCode 146 的例子：capacity = 2，从空缓存开始。")];
    const operations = [["put", 1, 1], ["put", 2, 2], ["get", 1], ["put", 3, 3], ["get", 2],
      ["put", 4, 4], ["get", 1], ["get", 3], ["get", 4]];
    for (const [name, key, value] of operations) name === "put" ? put(frames, key, value) : get(frames, key);
    frames.push(snap(`示例结束。各次返回值是 [${outputs.map(shown).join(", ")}]，缓存里从新到旧是 ${order.join(", ")}。`));
    player.load(frames);
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: playExample }, "播放 LeetCode 示例"),
    el("span", { class: "label" }, "capacity ="), capacityInput,
    el("button", { onclick: () => { reset(); player.load([snap(`空缓存，capacity = ${capacity}。`)]); } }, "重置"),
    el("span", { class: "label" }, "key ="), keyInput,
    el("span", { class: "label" }, "value ="), valueInput,
    el("button", { onclick: run(frames => get(frames, Number(keyInput.value))) }, "get(key)"),
    el("button", { onclick: run(frames => put(frames, Number(keyInput.value), Number(valueInput.value))) }, "put(key, value)")));
  reset();
  player.load([snap("空缓存，capacity = 2。点“播放 LeetCode 示例”，或者自己 get / put。")]);
})();
