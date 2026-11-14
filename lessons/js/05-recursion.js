// 动画：看调用栈怎么一层层压入、再一层层弹出。栈画成竖着的一摞，最上面是正在跑的那一层。
(() => {
  const root = document.getElementById("callstack");
  let stack, calls, deepest;

  function snap(say) {
    return { say, stack: structuredClone(stack), calls, deepest };
  }

  function render(f) {
    const rows = f.stack.map((s, k) => {
      const top = k === f.stack.length - 1;
      return el("div", { class: "row frame" },
        box(s.call, s.ret != null ? "found" : top ? "hot" : ""),
        el("span", { class: "label" }, s.ret != null ? `返回 ${s.ret}` : s.wait ? `等 ${s.wait} 的结果…` : top ? "← 正在跑" : ""));
    }).reverse();
    return [
      el("div", { class: "stack" }, rows.length ? rows : el("p", { class: "label" }, "（调用栈是空的）")),
      el("p", { class: "label" }, "↑ 栈顶（最新的调用）　　↓ 栈底（最早的调用）"),
      el("p", { class: "stat" }, "调用次数 = ", el("b", { class: "calls" }, f.calls), "　最深 = ", el("b", { class: "depth" }, f.deepest), " 层"),
    ];
  }

  const player = new Player(root, render);

  function enter(fr, call) {
    stack.push({ call });
    calls++;
    deepest = Math.max(deepest, stack.length);
    fr.push(snap(`调用 ${call}：压入调用栈。`));
    return stack[stack.length - 1];
  }

  function leave(fr, me, ret, why) {
    me.ret = ret;
    fr.push(snap(`${why}，${me.call} 返回 ${ret}。`));
    stack.pop();
    if (stack.length) stack[stack.length - 1].wait = null;  // 父层拿到结果，接着跑
    fr.push(snap(`${me.call} 弹出栈，回到调用它的那一层。`));
    return ret;
  }

  function fact(fr, n) {
    const me = enter(fr, `factorial(${n})`);
    if (n <= 1) return leave(fr, me, 1, `基线条件：n = ${n} ≤ 1，直接得到 1`);
    me.wait = `factorial(${n - 1})`;
    fr.push(snap(`n > 1：先要算 factorial(${n - 1})，自己停在这里等。`));
    const r = fact(fr, n - 1);
    me.wait = null;
    return leave(fr, me, n * r, `拿到 factorial(${n - 1}) = ${r}，算 ${n} × ${r} = ${n * r}`);
  }

  function fib(fr, n) {
    const me = enter(fr, `fib(${n})`);
    if (n <= 1) return leave(fr, me, n, `基线条件：n = ${n} ≤ 1，直接得到 ${n}`);
    me.wait = `fib(${n - 1})`;
    fr.push(snap(`先算 fib(${n - 1})。`));
    const a = fib(fr, n - 1);
    me.wait = `fib(${n - 2})`;
    fr.push(snap(`fib(${n - 1}) = ${a}。再算 fib(${n - 2})，注意它前面其实已经算过了。`));
    const b = fib(fr, n - 2);
    me.wait = null;
    return leave(fr, me, a + b, `${a} + ${b} = ${a + b}`);
  }

  const nInput = el("input", { type: "number", value: "4", min: "0", max: "6", "aria-label": "n" });
  const run = (op, name) => () => {
    const n = Math.max(0, Math.min(6, Number(nInput.value) || 0));
    nInput.value = n;
    stack = []; calls = 0; deepest = 0;
    const fr = [snap(`准备调用 ${name}(${n})。`)];
    const r = op(fr, n);
    fr.push(snap(`全部算完：${name}(${n}) = ${r}。一共调用了 ${calls} 次，栈最深 ${deepest} 层。`));
    player.load(fr);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "n ="), nInput,
    el("button", { onclick: run(fact, "factorial") }, "factorial(n)"),
    el("button", { onclick: run(fib, "fib") }, "fib(n)"),
    el("span", { class: "label" }, "（n 最大 6）")));
  stack = []; calls = 0; deepest = 0;
  player.load([snap("选一个 n，点 factorial(n) 或 fib(n)。")]);
})();
