// 动画：N 皇后。一行放一个，逐格尝试；冲突就跳过，放下去就进下一行，回来时撤销。
(() => {
  const root = document.getElementById("queens");
  let n = 4, queens, tries, undos, solutions;

  function snap(say, { tryAt = null, bad = null, hit = null } = {}) {
    return { say, n, queens: [...queens], tryAt, bad, hit, tries, undos, solutions };
  }

  function render(f) {
    const cells = [];
    for (let r = 0; r < f.n; r++) {
      cells.push(el("span", { class: "label" }, `第 ${r} 行`));
      for (let c = 0; c < f.n; c++) {
        const isQ = f.queens[r] === c;
        const at = p => p && p[0] === r && p[1] === c;
        const cls = [isQ && "queen", at(f.bad) && "found", (at(f.hit) || at(f.tryAt)) && "hot"].filter(Boolean).join(" ");
        cells.push(box(isQ ? "♛" : at(f.bad) ? "×" : "", "cell " + cls));
      }
    }
    return [
      el("div", { class: "board", style: `grid-template-columns: 50px repeat(${f.n}, 38px)` }, cells),
      el("p", { class: "stat" }, "尝试 ", el("b", { class: "tries" }, f.tries),
        " 次，撤销 ", el("b", { class: "undos" }, f.undos),
        " 次，找到解 ", el("b", { class: "solutions" }, f.solutions), " 个"),
    ];
  }

  const player = new Player(root, render);

  // 返回和 (r, c) 冲突的那个皇后，没有冲突返回 null
  function conflict(r, c) {
    for (let pr = 0; pr < r; pr++) {
      const pc = queens[pr];
      if (pc === c) return [pr, pc, "同一列"];
      if (Math.abs(pr - r) === Math.abs(pc - c)) return [pr, pc, "同一条斜线"];
    }
    return null;
  }

  function solve(fr, firstOnly) {
    let stop = false;
    function bt(r) {
      if (r === n) {
        solutions++;
        fr.push(snap(`${n} 行都放好了：找到第 ${solutions} 个解！` + (firstOnly ? "" : "记下来，继续回溯找下一个。")));
        if (firstOnly) stop = true;
        return;
      }
      for (let c = 0; c < n && !stop; c++) {
        tries++;
        const hit = conflict(r, c);
        if (hit) {
          fr.push(snap(`试第 ${r} 行第 ${c} 列：和第 ${hit[0]} 行的皇后在${hit[2]}，剪掉，不往下走。`,
            { bad: [r, c], hit: [hit[0], hit[1]] }));
          continue;
        }
        queens[r] = c;
        fr.push(snap(`试第 ${r} 行第 ${c} 列：没有冲突。① 选择：放下皇后，② 递归：去第 ${r + 1} 行。`));
        bt(r + 1);
        if (stop) return;
        queens.length = r;
        undos++;
        fr.push(snap(`③ 撤销：拿走第 ${r} 行第 ${c} 列的皇后，试这一行的下一格。`, { tryAt: [r, c] }));
      }
      if (!stop && r > 0) fr.push(snap(`第 ${r} 行每一格都试过了，退回第 ${r - 1} 行。`));
    }
    bt(0);
    fr.push(snap(firstOnly ? `停在第一个解。皇后所在列：[${queens.join(", ")}]` : `全部试完：${n} 皇后共 ${solutions} 个解。`));
  }

  const size = el("input", { type: "number", value: "4", min: "4", max: "5", "aria-label": "n" });
  const reset = () => {
    n = Math.min(5, Math.max(4, Number(size.value) || 4));
    size.value = n;
    queens = []; tries = undos = solutions = 0;
  };
  const run = firstOnly => () => {
    reset();
    const fr = [snap(`空的 ${n}×${n} 棋盘。从第 0 行开始，一行放一个皇后。`)];
    solve(fr, firstOnly);
    player.load(fr);
  };

  root.prepend(el("div", { class: "ops-bar" },
    el("span", { class: "label" }, "n ="), size,
    el("button", { onclick: run(true) }, "找第一个解"),
    el("button", { onclick: run(false) }, "找全部解")));
  reset();
  player.load([snap("空的 4×4 棋盘。点上面的按钮开始。")]);
})();
