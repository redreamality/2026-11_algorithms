// 预备课动画：生成器每次 next() 跑到哪里暂停；yield from 怎么把 next() 转交给里层。
// 代码清单里，橙色 = 正在执行的行，蓝色 = 停在这一行（暂停中）。

function listing(lines, line, status) {
  const cls = status === "运行中" ? "hot" : status === "暂停" ? "idle" : "";
  return el("pre", { class: "listing" },
    lines.map((text, k) => el("span", { class: "line " + (k === line ? cls : "") }, text)));
}

function gotRow(got) {
  return el("div", { class: "row" },
    el("span", { class: "label" }, "调用者拿到："),
    el("span", { class: "got" }, got.length ? got.map(v => box(v)) : el("span", { class: "label" }, "（还没有）")));
}

// 动画一：count_down(3)
(() => {
  const root = document.getElementById("generator-demo");
  const LINES = ["def count_down(n):", "    while n > 0:", "        yield n", "        n -= 1"];
  let state;

  function snap(say) {
    return { say, ...structuredClone(state) };
  }

  function render(f) {
    return [
      el("div", { class: "panels" },
        el("div", { class: "panel" }, el("span", { class: "label" }, "生成器函数"), listing(LINES, f.line, f.status)),
        el("div", { class: "panel" },
          el("p", {}, "状态：", el("b", { class: "status" }, f.status)),
          el("p", {}, "局部变量 n = ", box(f.n == null ? "·" : f.n, "local-n " + (f.n == null ? "empty" : "")) ))),
      gotRow(f.got),
    ];
  }

  const player = new Player(root, render);

  function reset() {
    state = { line: -1, n: null, status: "未开始", got: [] };
    player.load([snap("numbers = count_down(3)：只是造出一个生成器对象，函数体一行都还没跑。点 next(numbers)。")]);
  }

  function nextCall() {
    const fr = [];
    if (state.status === "已结束") {
      fr.push(snap("生成器已经结束了：再调用 next() 也只会直接抛 StopIteration。"));
      return player.load(fr);
    }
    if (state.status === "未开始") {
      Object.assign(state, { status: "运行中", n: 3, line: 1 });
      fr.push(snap("第一次 next()：函数体这才开始执行，参数 n = 3。"));
    } else {
      Object.assign(state, { status: "运行中", line: 3 });
      state.n -= 1;
      fr.push(snap(`从上次暂停的 yield 后面接着跑：n -= 1，n 变成 ${state.n}。局部变量一直保留着。`));
      state.line = 1;
      fr.push(snap("回到 while 检查条件。"));
    }
    if (state.n > 0) {
      fr.push(snap(`${state.n} > 0 成立，进入循环。`));
      state.line = 2;
      fr.push(snap(`执行 yield n。`));
      state.status = "暂停";
      state.got.push(state.n);
      fr.push(snap(`yield ${state.n}：把 ${state.n} 交给调用者，函数停在这一行。这次 next() 返回 ${state.n}。`));
    } else {
      fr.push(snap("0 > 0 不成立，循环结束，函数体跑到了末尾。"));
      Object.assign(state, { status: "已结束", line: -1 });
      fr.push(snap("函数体跑完：这次 next() 抛出 StopIteration。for 循环看到它就正常结束。"));
    }
    player.load(fr);
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: nextCall }, "next(numbers)"),
    el("button", { onclick: reset }, "重新开始")));
  reset();
})();

// 动画二：yield from
(() => {
  const root = document.getElementById("yield-from-demo");
  const LINES = ["def numbers_then_letters():", "    yield from count_down(2)", '    yield from "ab"', '    yield "done"'];
  const STEPS = [
    { line: 1, inner: "count_down(2)", values: [2, 1] },
    { line: 2, inner: 'iter("ab")', values: ["a", "b"] },
    { line: 3, single: "done" },
  ];
  let state;

  function snap(say, innerActive) {
    return { say, innerActive: !!innerActive, ...structuredClone(state) };
  }

  function render(f) {
    const step = STEPS[f.step];
    let inner = el("p", { class: "label" }, "（现在没有里层）");
    if (step && !step.single && f.status !== "未开始") {
      inner = el("div", {},
        el("p", {}, "里层：", el("b", { class: "inner-name" }, step.inner), f.innerActive ? " ← 正在跑" : ""),
        el("div", { class: "row" },
          el("span", { class: "label" }, "会依次交出："),
          step.values.map((v, k) => box(v, k < f.pos ? "empty" : k === f.pos && f.innerActive ? "hot" : ""))));
    }
    const outerStatus = f.innerActive ? "暂停" : f.status;
    return [
      el("div", { class: "panels" },
        el("div", { class: "panel" },
          el("span", { class: "label" }, "外层生成器"), listing(LINES, f.status === "已结束" ? -1 : step ? step.line : -1, outerStatus),
          el("p", {}, "状态：", el("b", { class: "status" }, f.innerActive && f.status === "运行中" ? "运行中（等里层交值）" : f.status))),
        el("div", { class: "panel" }, inner)),
      gotRow(f.got),
    ];
  }

  const player = new Player(root, render);

  function reset() {
    state = { step: 0, pos: 0, status: "未开始", got: [] };
    player.load([snap("gen = numbers_then_letters()：只造出外层生成器，什么都没跑。点 next(gen)。")]);
  }

  function nextCall() {
    const fr = [];
    if (state.status === "已结束") {
      fr.push(snap("外层已经结束了：再调用 next() 也只会直接抛 StopIteration。"));
      return player.load(fr);
    }
    if (state.status === "未开始") {
      state.status = "运行中";
      fr.push(snap("第一次 next()：外层开始执行，来到 yield from count_down(2)，先造出里层生成器。"));
    } else if (STEPS[state.step].single) {
      state.status = "运行中";
      state.step += 1;
    } else {
      state.status = "运行中";
    }
    for (;;) {
      const step = STEPS[state.step];
      if (!step) {
        state.status = "已结束";
        fr.push(snap("外层的函数体也跑完了：这次 next() 抛出 StopIteration。"));
        break;
      }
      if (step.single) {
        state.status = "暂停";
        state.got.push(step.single);
        fr.push(snap(`外层自己 yield "${step.single}"：交给调用者，外层暂停。`));
        break;
      }
      if (state.pos < step.values.length) {
        const value = step.values[state.pos];
        fr.push(snap(`外层不自己干活，把这次 next() 原样转交给里层 ${step.inner}。`, true));
        state.status = "暂停";
        state.got.push(value);
        fr.push(snap(`里层交出 ${JSON.stringify(value)}，它原样穿过外层，交到调用者手里。外层停在 yield from 这一行。`, true));
        state.pos += 1;
        break;
      }
      fr.push(snap(`里层 ${step.inner} 没有值了（它抛出 StopIteration）。yield from 接住它、不往外抛，外层接着往下跑。`));
      state.step += 1;
      state.pos = 0;
      if (STEPS[state.step] && !STEPS[state.step].single) {
        fr.push(snap(`来到下一行，造出新的里层 ${STEPS[state.step].inner}。`));
      }
    }
    player.load(fr);
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: nextCall }, "next(gen)"),
    el("button", { onclick: reset }, "重新开始")));
  reset();
})();
