// 动画：用两个堆求数据流的中位数。左边是较小的一半（大顶堆），右边是较大的一半（小顶堆）。
// 为了好看，两边都画成从小到大排好的样子，两个堆顶紧挨着中间的竖线；橙色是这一步正在移动的数。
(() => {
  const root = document.getElementById("two-heaps");
  const EXAMPLE_STREAM = [5, 15, 1, 3, 8, 7, 9, 10];
  const MAX_COUNT = 12;
  let smallerHalf, largerHalf, medianText;

  // moving：{ side: "smaller" | "larger", index } 正在移动的那个数画在哪一边的第几格
  function snap(say, moving = null) {
    return { say, moving, smallerHalf: [...smallerHalf], largerHalf: [...largerHalf], medianText };
  }

  function halfView(frame, side) {
    const values = side === "smaller" ? frame.smallerHalf : frame.largerHalf;
    const topIndex = side === "smaller" ? values.length - 1 : 0;
    const title = side === "smaller"
      ? `较小的一半 · 大顶堆（${values.length} 个，堆顶在最右）`
      : `较大的一半 · 小顶堆（${values.length} 个，堆顶在最左）`;
    const cells = values.map((value, index) => {
      const isMoving = frame.moving && frame.moving.side === side && frame.moving.index === index;
      return box(value, [index === topIndex && "top", isMoving && "moving"].filter(Boolean).join(" "));
    });
    return el("div", { class: "half" },
      el("span", { class: "label" }, title),
      el("div", { class: `row ${side}-half`, style: side === "smaller" ? "justify-content:flex-end" : "" },
        cells.length ? cells : el("span", { class: "label" }, "（空）")));
  }

  function render(frame) {
    return [
      el("div", { class: "halves" }, halfView(frame, "smaller"), el("span", { class: "divider" }, "│"), halfView(frame, "larger")),
      el("p", { class: "stat" }, "目前的中位数：", el("b", { class: "median" }, frame.medianText)),
    ];
  }

  const player = new Player(root, render);

  // 插进有序数组，返回插入的位置（只是为了画图，真实的堆不需要整体有序）
  function insertSorted(values, value) {
    let index = 0;
    while (index < values.length && values[index] <= value) index++;
    values.splice(index, 0, value);
    return index;
  }

  function addNumber(frames, num) {
    if (smallerHalf.length + largerHalf.length >= MAX_COUNT) {
      frames.push(snap(`演示最多放 ${MAX_COUNT} 个数，先点“重置”吧。`));
      return;
    }
    medianText = "（正在调整两个堆，三步做完再算）";
    const insertedAt = insertSorted(smallerHalf, num);
    frames.push(snap(`新来 ${num}。① 先把它放进较小的一半（大顶堆）。`, { side: "smaller", index: insertedAt }));

    const movedUp = smallerHalf.pop();
    const movedTo = insertSorted(largerHalf, movedUp);
    const why = movedUp === num
      ? `这次送过去的正好是刚来的 ${num}：它比较小一半里原有的数都大，本来就属于较大的一半。`
      : `${num} 留在了较小的一半，换成原来的最大值 ${movedUp} 过去。`;
    frames.push(snap(`② 把较小一半的堆顶（最大值）${movedUp} 弹出，放进较大的一半。这样较小一半剩下的数都 ≤ 较大一半的数。${why}`,
      { side: "larger", index: movedTo }));

    if (largerHalf.length > smallerHalf.length) {
      const movedBack = largerHalf.shift();
      const backTo = insertSorted(smallerHalf, movedBack);
      frames.push(snap(`③ 较大的一半有 ${largerHalf.length + 1} 个，比较小的一半（${smallerHalf.length - 1} 个）多了，把它的堆顶（最小值）${movedBack} 挪回较小的一半。`,
        { side: "smaller", index: backTo }));
    } else {
      frames.push(snap(`③ 较大的一半有 ${largerHalf.length} 个，较小的一半有 ${smallerHalf.length} 个，较大的一半没有更多，不用挪回。`));
    }

    const total = smallerHalf.length + largerHalf.length;
    const smallerTop = smallerHalf[smallerHalf.length - 1];
    if (total % 2 === 1) {
      medianText = String(smallerTop);
      frames.push(snap(`现在一共 ${total} 个（奇数），较小的一半多 1 个，它的堆顶 ${smallerTop} 就在正中间：中位数 = ${smallerTop}。`));
    } else {
      const largerTop = largerHalf[0];
      medianText = String((smallerTop + largerTop) / 2);
      frames.push(snap(`现在一共 ${total} 个（偶数），两边一样多：中位数 = (${smallerTop} + ${largerTop}) / 2 = ${medianText}。`));
    }
  }

  function reset() {
    smallerHalf = [];
    largerHalf = [];
    medianText = "（还没有数）";
  }

  const valueInput = el("input", { type: "number", value: "6", "aria-label": "值" });
  const addOne = () => {
    const frames = [snap("加入前的样子。")];
    addNumber(frames, Number(valueInput.value));
    player.load(frames);
  };
  const playExample = () => {
    reset();
    const frames = [snap(`两个堆都是空的。依次加入 ${EXAMPLE_STREAM.join(", ")}。`)];
    for (const num of EXAMPLE_STREAM) addNumber(frames, num);
    const all = [...smallerHalf, ...largerHalf];
    frames.push(snap(`全部加入完毕。所有数排好序是 ${all.join(", ")}，正中间两个是 ${smallerHalf[smallerHalf.length - 1]} 和 ${largerHalf[0]}，正好是两个堆顶：中位数 = ${medianText}。`));
    player.load(frames);
  };
  const resetAndShow = () => {
    reset();
    player.load([snap("两个堆都是空的。点“播放示例数据流”，或者输入一个值点“加入”。")]);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: playExample }, "播放示例数据流"),
    el("span", { class: "label" }, "值 ="), valueInput,
    el("button", { onclick: addOne }, "加入"),
    el("button", { onclick: resetAndShow }, "重置")));
  resetAndShow();
})();
