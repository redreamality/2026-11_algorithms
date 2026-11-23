// 附录·选择题速查：出栈序列判定器。
// 1, 2, …, n 依次进栈，按输入的出栈序列逐个弹出；栈顶不是要弹的数就继续进栈，进完了还不是就不合法。
(() => {
  const root = document.getElementById("pop-check");
  const VALID_EXAMPLE = "4 5 3 2 1";
  const INVALID_EXAMPLE = "4 3 5 1 2";

  // 帧：{ waiting: 还没进栈的数, stack: 栈（底 → 顶）, popped: 已弹出的, target: 正在找的数, blocked: 是否卡住, verdict }
  function render(f) {
    const column = (title, items, cls) => el("div", { class: "part" }, el("span", { class: "label" }, title),
      el("div", { class: "row" }, items.length ? items : el("span", { class: "label" }, "（空）")));
    const stackBoxes = f.stack.map((value, index) => {
      const isTop = index === f.stack.length - 1;
      const cls = "small" + (isTop && f.blocked ? " blocked" : "") + (value === f.target && f.blocked ? " hot" : "");
      return box(value, cls);
    });
    return [
      el("div", { class: "pop-board" },
        column("还没进栈：", f.waiting.map(value => box(value, "small"))),
        el("div", { class: "part" }, el("span", { class: "label" }, "栈（上面是栈顶）："), el("div", { class: "stack-col" }, stackBoxes)),
        column("已弹出：", f.popped.map(value => box(value, "small done")))),
      el("p", { class: "stat" }, "要弹的数：", el("b", {}, f.target === null ? "—" : String(f.target)), "　结论：",
        el("span", { class: "verdict " + (f.verdict === "合法" ? "ok" : f.verdict === "不合法" ? "bad" : "") }, f.verdict || "…")),
    ];
  }

  const player = new Player(root, render);

  function parse(text) {
    const values = text.trim().split(/[\s,，]+/).filter(Boolean).map(Number);
    const n = values.length;
    if (n === 0 || n > 9) return null;
    const sorted = [...values].sort((a, b) => a - b);
    if (!sorted.every((value, index) => value === index + 1)) return null;
    return values;
  }

  function frames(text) {
    const sequence = parse(text);
    if (sequence === null) {
      return [{ say: `“${text}” 不是 1～n 的一个排列（n 在 1～9 之间，每个数恰好出现一次），请重新输入。`,
        waiting: [], stack: [], popped: [], target: null, blocked: false, verdict: "输入有误" }];
    }
    const n = sequence.length;
    const waiting = Array.from({ length: n }, (_, index) => index + 1);
    const stack = [], popped = [], result = [];
    const snap = (say, target, blocked = false, verdict = "") =>
      result.push({ say, waiting: [...waiting], stack: [...stack], popped: [...popped], target, blocked, verdict });
    snap(`1～${n} 依次进栈，目标出栈序列是 ${sequence.join(" ")}。从左到右一个个弹。`, null);
    for (const target of sequence) {
      while ((stack.length === 0 || stack[stack.length - 1] !== target) && waiting.length) {
        stack.push(waiting.shift());
        snap(`要弹 ${target}，栈顶不是它，继续进栈：${stack[stack.length - 1]} 进栈。`, target);
      }
      if (stack[stack.length - 1] !== target) {
        snap(`要弹 ${target}，可所有数都已经进栈，栈顶是 ${stack[stack.length - 1]}，${target} 被压在下面出不来：不合法。`, target, true, "不合法");
        return result;
      }
      popped.push(stack.pop());
      snap(`栈顶正好是 ${target}，弹出。`, target);
    }
    snap(`全部按顺序弹出，${sequence.join(" ")} 是合法的出栈序列。`, null, false, "合法");
    return result;
  }

  const input = el("input", { type: "text", value: VALID_EXAMPLE, "aria-label": "出栈序列" });
  const run = () => player.load(frames(input.value));
  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "出栈序列："), input,
    el("button", { onclick: run }, "模拟"),
    el("button", { onclick: () => { input.value = VALID_EXAMPLE; run(); } }, "合法的例子"),
    el("button", { onclick: () => { input.value = INVALID_EXAMPLE; run(); } }, "不合法的例子")));
  player.load([{ say: "输入一个出栈序列，点“模拟”。", waiting: [1, 2, 3, 4, 5], stack: [], popped: [], target: null, blocked: false, verdict: "" }]);
})();
