// 动画：位运算三招。每一行是一个数的二进制，左边高位、右边低位（第 0 位在最右）。
// 绿色 one = 这一位是 1，橙色 hot = 这一步刚变化的位，红色 gone = 这一步被清掉的 1。
(() => {
  const root = document.getElementById("bits");

  // 第 k 位的取值；画的时候从高位 width - 1 画到低位 0
  const bitAt = (value, k) => (value >> k) & 1;

  function render(f) {
    const cells = [];
    if (f.header) {
      cells.push(el("span", { class: "label num" }, "第 k 位"));
      for (let k = f.width - 1; k >= 0; k--) cells.push(el("span", { class: "label" }, `${k}`));
      cells.push(el("span", { class: "label num" }, "对应元素 items[k]"));
      for (let k = f.width - 1; k >= 0; k--) cells.push(el("span", { class: "label" }, f.header[k]));
    }
    for (const row of f.rows) {
      cells.push(el("span", { class: "num " + (row.rowClass || "") }, row.label));
      for (let k = f.width - 1; k >= 0; k--) {
        const bit = bitAt(row.value, k);
        const extra = (row.marks && row.marks[k]) || "";
        cells.push(box(bit, [bit ? "one" : "", extra, row.fade ? "fade" : ""].join(" ")));
      }
    }
    return [
      el("div", { class: "bits", style: `grid-template-columns: 170px repeat(${f.width}, 34px)` }, cells),
      f.chips && el("div", { class: "chips" }, f.chips.map(c => box(c.text, "subset " + (c.cls || "")))),
      f.extra && el("p", { class: "stat" }, f.extra),
    ];
  }

  const player = new Player(root, render);
  const binary = (value, width) => value.toString(2).padStart(width, "0");

  // ---------- 异或抵消：只出现一次的数字 ----------
  function xorCancel() {
    const numbers = [4, 1, 2, 1, 2], width = 3;
    const shown = [];
    let running = 0;
    const snap = (say, resultMarks = {}, extra = "") => ({
      say, extra, width,
      rows: [...shown.map(r => ({ ...r })), { label: `异或结果 = ${running}`, value: running, marks: resultMarks, rowClass: "result" }],
    });
    const fr = [snap("numbers = [4, 1, 2, 1, 2]。异或结果从 0 开始，把每个数依次异或进来。")];
    numbers.forEach((number, index) => {
      const before = running;
      running ^= number;
      const flipped = {};
      for (let k = 0; k < width; k++) if (bitAt(number, k)) flipped[k] = "hot";
      shown.forEach(r => { r.marks = {}; });
      shown.push({ label: `numbers[${index}] = ${number}`, value: number, marks: flipped });
      const seenBefore = numbers.slice(0, index).includes(number);
      fr.push(snap(`${binary(before, width)} ^ ${binary(number, width)} = ${binary(running, width)}：` +
        `${number} 里是 1 的位（橙色）在结果里翻转一次，现在结果是 ${running}。` +
        (seenBefore ? ` ${number} 第二次出现，它第一次翻过的位又翻回去了。` : ""), flipped));
    });
    shown.forEach(r => { r.marks = {}; r.fade = numbers.filter(n => n === r.value).length === 2; });
    fr.push(snap(`全部异或完：成对的 1 和 2（变淡的行）各自抵消成 0，剩下的 ${running} 就是只出现一次的数。`,
      {}, `答案 = ${running}`));
    return fr;
  }

  // ---------- n & (n - 1)：数 1 的个数 ----------
  function dropLowestBit() {
    let number = 44;
    const width = 6, start = number;
    let removed = 0;
    const fr = [{ say: `number = ${start}，二进制 ${binary(start, width)}。反复执行 number &= number - 1，每次去掉最低位的那个 1。`,
      width, rows: [{ label: `number = ${number}`, value: number }] }];
    while (number) {
      const minus = number - 1, after = number & minus;
      const lowest = Math.log2(number & -number);
      const borrowed = {};
      for (let k = 0; k <= lowest; k++) borrowed[k] = "hot";
      removed++;
      fr.push({
        say: `number - 1：最低位的 1（第 ${lowest} 位）变 0，它右边的 0 全变 1（橙色）。两者相与，第 ${lowest} 位的 1 被清掉（红色），这是第 ${removed} 次。`,
        width,
        rows: [
          { label: `number = ${number}`, value: number, marks: { [lowest]: "gone" } },
          { label: `number - 1 = ${minus}`, value: minus, marks: borrowed },
          { label: `相与 = ${after}`, value: after, rowClass: "result" },
        ],
        extra: `已去掉 ${removed} 个 1`,
      });
      number = after;
    }
    fr.push({ say: `number 变成 0，停下。一共去掉 ${removed} 次，所以 ${start} 的二进制里有 ${removed} 个 1。循环次数只和 1 的个数有关。`,
      width, rows: [{ label: "number = 0", value: 0, rowClass: "result" }], extra: `答案 = ${removed}` });
    return fr;
  }

  // ---------- 位掩码枚举子集 ----------
  function maskSubsets() {
    const items = [1, 2, 3], width = items.length;
    const header = items.map((item, k) => `${item}`);
    const found = [];
    const fr = [{ say: "items = [1, 2, 3]。bit_mask 的第 k 位是 1，就选 items[k]。表头写的是每一位对应的元素（第 0 位在最右）。",
      width, header, rows: [{ label: "bit_mask = 0", value: 0 }], chips: [] }];
    for (let bitMask = 0; bitMask < 1 << width; bitMask++) {
      const subset = items.filter((_, k) => bitAt(bitMask, k));
      const text = `[${subset.join(", ")}]`;
      found.push(text);
      fr.push({
        say: `bit_mask = ${bitMask}，二进制 ${binary(bitMask, width)}：` +
          (subset.length ? `是 1 的位对应 ${subset.join("、")}，子集是 ${text}。` : "没有一位是 1，是空集 []。"),
        width, header, rows: [{ label: `bit_mask = ${bitMask}`, value: bitMask }],
        chips: found.map((t, k) => ({ text: t, cls: k === found.length - 1 ? "hot" : "" })),
        extra: `已列出 ${found.length} 个子集`,
      });
    }
    fr.push({ say: `bit_mask 从 0 数到 ${(1 << width) - 1}，正好得到全部 2^${width} = ${1 << width} 个子集，不重不漏。`,
      width, header, rows: [{ label: `bit_mask = ${(1 << width) - 1}`, value: (1 << width) - 1 }],
      chips: found.map(t => ({ text: t })), extra: `共 ${found.length} 个子集` });
    return fr;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(xorCancel()) }, "异或抵消"),
    el("button", { onclick: () => player.load(dropLowestBit()) }, "去掉最低位的 1"),
    el("button", { onclick: () => player.load(maskSubsets()) }, "位掩码枚举子集")));
  player.load([xorCancel()[0]]);
})();
