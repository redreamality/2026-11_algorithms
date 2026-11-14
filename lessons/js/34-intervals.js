// 动画：区间问题。
// 合并区间：按起点排序后从上往下扫，红线是结果里最后一段的终点 current_end，底下一行是 merged_intervals。
// 会议室 II：按开始时间排序，最小堆里放“各间会议室什么时候空出来”，堆的最大大小就是答案。
(() => {
  const root = document.getElementById("intervals");
  const TIME_LIMIT = 20;  // 时间轴 0..20
  const MERGE_INPUT = [["A", 8, 10], ["B", 1, 3], ["C", 15, 18], ["D", 2, 6], ["E", 9, 12], ["F", 16, 17]];
  const MEETINGS = [["A", 1, 10], ["B", 2, 7], ["C", 3, 19], ["D", 8, 12], ["E", 10, 20], ["F", 11, 18]];
  const percent = time => (time / TIME_LIMIT * 100) + "%";
  const segment = (start, end, extraClass = "") =>
    el("span", { class: "seg " + extraClass, style: `left:${percent(start)};width:${percent(end - start)}` }, `${start}–${end}`);

  function render(frame) {
    const rows = frame.order.map(([name, start, end]) => {
      const rowClass = name === frame.current ? "cur" : frame.done.includes(name) ? "done" : "";
      return el("div", { class: "act " + rowClass, "data-name": name },
        el("span", { class: "act-name" }, name),
        el("div", { class: "track" }, segment(start, end),
          frame.redLine !== null && el("span", { class: "endline", style: `left:${percent(frame.redLine)}` })),
        el("span", { class: "room-tag" }, frame.roomOf[name] ? `会议室 ${frame.roomOf[name]}` : ""));
    });
    const extra = frame.mode === "merge"
      ? el("div", { class: "act result" },
          el("span", { class: "act-name" }, "合"),
          el("div", { class: "track" }, frame.merged.map(([start, end], index) =>
            segment(start, end, index === frame.merged.length - 1 && frame.current ? "last" : ""))),
          el("span", { class: "room-tag" }, "merged_intervals"))
      : el("div", { class: "row heap" }, el("span", { class: "label" }, "最小堆（各间会议室空出来的时间，最小的在最左）："),
          frame.heap.length ? frame.heap.map(end => box(end, "small")) : el("span", { class: "label" }, "空"));
    const stat = frame.mode === "merge"
      ? el("p", { class: "stat" }, "结果：", el("b", { class: "answer" }, JSON.stringify(frame.merged).replaceAll(",", ", ")))
      : el("p", { class: "stat" }, "同时在用的会议室最多 ", el("b", { class: "answer" }, frame.maxRooms), " 间");
    return [el("div", { class: "timeline" }, rows, extra), stat];
  }

  const player = new Player(root, render);

  function mergeFrames() {
    const sorted = [...MERGE_INPUT].sort((first, second) => first[1] - second[1]);
    const merged = [], done = [];
    let order = MERGE_INPUT;
    const snap = (say, current = null) => ({
      mode: "merge", say, current, order, done: [...done], roomOf: {}, heap: [], maxRooms: 0,
      merged: merged.map(pair => [...pair]), redLine: merged.length ? merged[merged.length - 1][1] : null,
    });
    const frames = [snap("原始顺序是乱的：A 和 E 重叠，但中间隔着别的区间，直接扫看不出来。")];
    order = sorted;
    frames.push(snap("第一步：按起点从小到大排序。排好后，能和某段重叠的区间一定紧挨在它后面。"));
    for (const [name, start, end] of sorted) {
      if (!merged.length) {
        frames.push(snap(`${name}（${start}–${end}）：结果还是空的，直接放进去，作为第一段。`, name));
        merged.push([start, end]);
      } else {
        const last = merged[merged.length - 1];
        if (start <= last[1]) {
          const newEnd = Math.max(last[1], end);
          frames.push(snap(`${name}（${start}–${end}）：起点 ${start} <= 最后一段的终点 ${last[1]}（红线），重叠。`
            + `把最后一段的终点改成 max(${last[1]}, ${end}) = ${newEnd}。`, name));
          last[1] = newEnd;
        } else {
          frames.push(snap(`${name}（${start}–${end}）：起点 ${start} > 最后一段的终点 ${last[1]}（红线），接不上。`
            + `后面的起点只会更大，最后一段不会再变长了，${name} 作为新的一段追加。`, name));
          merged.push([start, end]);
        }
      }
      done.push(name);
      frames.push(snap(`处理完 ${name}，结果现在是 ${JSON.stringify(merged).replaceAll(",", ", ")}。`));
    }
    frames.push(snap(`扫完了，合并结果：${JSON.stringify(merged).replaceAll(",", ", ")}。`));
    return frames;
  }

  function meetingFrames() {
    const sorted = [...MEETINGS].sort((first, second) => first[1] - second[1]);
    const heap = [], roomOf = {}, done = [];  // heap 里放 [结束时间, 会议室编号]，用排好序的数组模拟最小堆
    let maxRooms = 0, roomCount = 0;
    const snap = (say, current = null, redLine = null) => ({
      mode: "rooms", say, current, order: sorted, done: [...done], roomOf: { ...roomOf },
      heap: heap.map(([end]) => end), maxRooms, merged: [], redLine,
    });
    const frames = [snap("6 场会议，已经按开始时间排好。堆里放“正在使用的会议室什么时候空出来”。")];
    for (const [name, start, end] of sorted) {
      if (heap.length && heap[0][0] <= start) {
        const [freeAt, room] = heap.shift();
        roomOf[name] = room;
        frames.push(snap(`${name}（${start}–${end}）：堆顶 ${freeAt} <= 开始时间 ${start}，会议室 ${room} 已经空了，弹出，让 ${name} 接着用。`, name, start));
      } else {
        roomOf[name] = ++roomCount;
        frames.push(snap(heap.length
          ? `${name}（${start}–${end}）：堆顶 ${heap[0][0]} > 开始时间 ${start}，最早空出来的会议室都还在用，只能新开会议室 ${roomCount}。`
          : `${name}（${start}–${end}）：堆是空的，开第 1 间会议室。`, name, start));
      }
      heap.push([end, roomOf[name]]);
      heap.sort((first, second) => first[0] - second[0]);
      maxRooms = Math.max(maxRooms, heap.length);
      done.push(name);
      frames.push(snap(`把 ${name} 的结束时间 ${end} 放进堆。堆里有 ${heap.length} 个，说明此刻有 ${heap.length} 间会议室在用。`));
    }
    frames.push(snap(`全部安排完：堆最大时有 ${maxRooms} 个元素，所以至少需要 ${maxRooms} 间会议室。`));
    return frames;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(mergeFrames()) }, "合并区间"),
    el("button", { onclick: () => player.load(meetingFrames()) }, "会议室 II")));
  player.load([{ mode: "merge", say: "点上面的按钮开始。", current: null, order: MERGE_INPUT, done: [], roomOf: {},
    heap: [], maxRooms: 0, merged: [], redLine: null }]);
})();
