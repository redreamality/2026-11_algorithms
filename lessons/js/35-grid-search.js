// 动画：网格搜索。
// 岛屿数量：逐格扫描，遇到没访问过的陆地就从它出发 DFS，把整座岛染成同一种颜色（原地标记）。
// 腐烂的橘子：所有烂橘子同时入队（多源 BFS），一层一分钟，格子里的数字是它在第几分钟烂掉的。
(() => {
  const root = document.getElementById("grid");
  const DIRECTIONS = [[-1, 0], [1, 0], [0, -1], [0, 1]];  // 上、下、左、右
  const DIRECTION_NAMES = ["上", "下", "左", "右"];
  const ISLAND_MAP = [
    "110010",
    "100110",
    "001000",
    "101101",
    "100001",
  ].map(line => [...line].map(Number));
  const ORANGE_MAP = [
    [2, 1, 1, 0, 1],
    [1, 1, 0, 1, 1],
    [0, 1, 1, 1, 2],
    [1, 1, 0, 1, 1],
  ];
  const position = (row, col) => `(${row}, ${col})`;

  // cells[row][col] = { text, cls }，由各模式自己算好
  function render(frame) {
    const columnCount = frame.cells[0].length;
    const header = [el("span", {}), ...frame.cells[0].map((_, col) => el("span", { class: "label" }, `列 ${col}`))];
    const body = frame.cells.flatMap((line, row) => [el("span", { class: "label" }, `行 ${row}`),
      ...line.map(({ text, cls }, col) => box(text, `cell ${cls} ${frame.focus.some(([r, c]) => r === row && c === col) ? "focus" : ""}`))]);
    return [
      el("div", { class: "grid-board", style: `grid-template-columns: 44px repeat(${columnCount}, 40px)` }, header, body),
      el("div", { class: "row queue" }, el("span", { class: "label" }, frame.listName),
        frame.list.length ? frame.list.map(([row, col]) => box(position(row, col), "small")) : el("span", { class: "label" }, "空")),
      el("p", { class: "stat" }, frame.statName, el("b", { class: "answer" }, frame.answer)),
    ];
  }

  const player = new Player(root, render);

  function islandFrames() {
    const grid = ISLAND_MAP.map(line => [...line]);  // 0 水，1 没访问的陆地，负数 -k 表示已经标记成第 k 个岛
    const rowCount = grid.length, columnCount = grid[0].length;
    const stack = [];
    let islandCount = 0;
    const cellsNow = () => grid.map(line => line.map(value =>
      value === 0 ? { text: "0", cls: "water" } : value === 1 ? { text: "1", cls: "land" } : { text: String(-value), cls: `island island-${(-value - 1) % 5}` }));
    const snap = (say, focus = []) => ({ say, focus, cells: cellsNow(), list: [...stack],
      listName: "递归栈（右边是正在访问的格子）：", statName: "已发现的岛屿数 island_count = ", answer: islandCount });
    const frames = [snap("1 是陆地，0 是水。从左上角开始，一行一行地扫。")];

    function visit(row, col) {
      grid[row][col] = -islandCount;  // 原地标记：不再是 1，下次扫到就会跳过
      stack.push([row, col]);
      const landNeighbors = [], skipped = [];
      DIRECTIONS.forEach(([rowStep, colStep], index) => {
        const nextRow = row + rowStep, nextCol = col + colStep;
        const inside = nextRow >= 0 && nextRow < rowCount && nextCol >= 0 && nextCol < columnCount;
        if (inside && grid[nextRow][nextCol] === 1) landNeighbors.push(DIRECTION_NAMES[index]);
        else skipped.push(DIRECTION_NAMES[index] + (inside ? (grid[nextRow][nextCol] === 0 ? "是水" : "已标记") : "出界"));
      });
      frames.push(snap(`访问 ${position(row, col)}：标记成第 ${islandCount} 个岛。看四个方向：`
        + (landNeighbors.length ? `${landNeighbors.join("、")}是没访问的陆地，要去；` : "")
        + `${skipped.join("，")}。`, [[row, col]]));
      DIRECTIONS.forEach(([rowStep, colStep]) => {
        const nextRow = row + rowStep, nextCol = col + colStep;
        if (nextRow < 0 || nextRow >= rowCount || nextCol < 0 || nextCol >= columnCount) return;
        if (grid[nextRow][nextCol] !== 1) return;  // 可能在前面兄弟分支里已经被标记
        visit(nextRow, nextCol);
      });
      stack.pop();
      frames.push(snap(`${position(row, col)} 的四个方向都处理完，出栈。`, [[row, col]]));
    }

    for (let row = 0; row < rowCount; row++) {
      for (let col = 0; col < columnCount; col++) {
        if (grid[row][col] !== 1) continue;
        islandCount++;
        frames.push(snap(`扫到 ${position(row, col)}：是没访问过的陆地，说明发现了一个新岛屿，island_count 变成 ${islandCount}。`
          + "从这里出发 DFS，把整座岛都标记掉。", [[row, col]]));
        visit(row, col);
        frames.push(snap(`第 ${islandCount} 个岛标记完了。继续往后扫，水和已标记的格子都直接跳过。`));
      }
    }
    frames.push(snap(`整张网格扫完，一共 ${islandCount} 个岛屿。每一格最多被访问一次，所以是 O(行数 × 列数)。`));
    return frames;
  }

  function orangeFrames() {
    const grid = ORANGE_MAP.map(line => [...line]);
    const rowCount = grid.length, columnCount = grid[0].length;
    const rottenMinute = grid.map(line => line.map(value => (value === 2 ? 0 : null)));
    let rottenQueue = [], minutes = 0;
    let freshCount = grid.flat().filter(value => value === 1).length;
    const cellsNow = (newlyRotten = []) => grid.map((line, row) => line.map((value, col) => {
      if (value === 0) return { text: "", cls: "blank" };
      if (value === 1) return { text: "鲜", cls: "fresh" };
      const isNew = newlyRotten.some(([r, c]) => r === row && c === col);
      return { text: String(rottenMinute[row][col]), cls: "rotten" + (isNew ? " new" : "") };
    }));
    const snap = (say, focus = [], newlyRotten = []) => ({ say, focus, cells: cellsNow(newlyRotten), list: [...rottenQueue],
      listName: "rotten_queue（这一层的烂橘子）：", statName: `fresh_count = ${freshCount}，已经过的分钟数 minutes = `, answer: minutes });

    for (let row = 0; row < rowCount; row++)
      for (let col = 0; col < columnCount; col++)
        if (grid[row][col] === 2) rottenQueue.push([row, col]);
    const frames = [snap(`“鲜”是新鲜橘子，数字是烂橘子在第几分钟烂的（0 表示一开始就烂）。新鲜橘子有 ${freshCount} 个。`
      + `多源 BFS：把一开始就烂的 ${rottenQueue.length} 个橘子全部放进队列，它们同时出发。`, rottenQueue)];

    while (rottenQueue.length && freshCount > 0) {
      minutes++;
      const currentLayer = rottenQueue;
      frames.push(snap(`第 ${minutes} 分钟：队列里这一层有 ${currentLayer.length} 个烂橘子（框出来的），`
        + "每个都去看上下左右四个邻居。", currentLayer));
      rottenQueue = [];
      for (const [row, col] of currentLayer) {
        for (const [rowStep, colStep] of DIRECTIONS) {
          const nextRow = row + rowStep, nextCol = col + colStep;
          if (nextRow < 0 || nextRow >= rowCount || nextCol < 0 || nextCol >= columnCount) continue;
          if (grid[nextRow][nextCol] !== 1) continue;
          grid[nextRow][nextCol] = 2;  // 原地改成 2：既是“烂了”，也是“已访问”，不会被重复入队
          rottenMinute[nextRow][nextCol] = minutes;
          freshCount--;
          rottenQueue.push([nextRow, nextCol]);
        }
      }
      frames.push(snap(`第 ${minutes} 分钟结束：新烂了 ${rottenQueue.length} 个（深色），它们组成下一层，放进队列。`
        + `还剩 ${freshCount} 个新鲜的。`, [], rottenQueue));
    }
    frames.push(snap(freshCount > 0
      ? `队列空了，但还有 ${freshCount} 个新鲜橘子永远烂不到，答案是 -1。`
      : `新鲜橘子全部烂完，用了 ${minutes} 分钟。可以看到数字从烂橘子出发一圈一圈往外变大，这就是 BFS 的“层”。`));
    return frames;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(islandFrames()) }, "岛屿数量（DFS）"),
    el("button", { onclick: () => player.load(orangeFrames()) }, "腐烂的橘子（多源 BFS）")));
  player.load([{ say: "点上面的按钮开始。", focus: [], list: [], listName: "", statName: "", answer: "",
    cells: ISLAND_MAP.map(line => line.map(value => (value ? { text: "1", cls: "land" } : { text: "0", cls: "water" }))) }]);
})();
