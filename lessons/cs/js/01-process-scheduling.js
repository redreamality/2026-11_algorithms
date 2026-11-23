// 动画：进程调度。按时间一格一格地模拟，每格一帧：此刻 CPU 上是谁、就绪队列、甘特图、每个进程的统计。
(() => {
  const root = document.getElementById("scheduler");
  const PROCESSES = [
    { name: "P1", job: "处理订单", arrive: 0, burst: 7 },
    { name: "P2", job: "发确认邮件", arrive: 2, burst: 4 },
    { name: "P3", job: "查库存", arrive: 4, burst: 1 },
    { name: "P4", job: "生成日报", arrive: 5, burst: 4 },
  ];
  const POLICIES = {
    FCFS: "FCFS 先来先服务",
    SJF: "SJF 短作业优先",
    SRTF: "SRTF 最短剩余时间优先",
    HRRN: "HRRN 高响应比优先",
    RR: "RR 时间片轮转",
  };
  const SVG = "http://www.w3.org/2000/svg";
  const name = i => PROCESSES[i].name;
  const format = x => Number(x.toFixed(2)).toString();

  function svgElement(tag, attrs, text) {
    const e = document.createElementNS(SVG, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    if (text != null) e.textContent = text;
    return e;
  }

  // 按算法从就绪队列里挑一个，返回 [下标在 queue 里的位置, 理由]
  function choose(policy, queue, remaining, time) {
    if (policy === "FCFS" || policy === "RR") return [0, "它排在队头"];
    const byArrival = (a, b) => PROCESSES[a].arrive - PROCESSES[b].arrive || a - b;
    if (policy === "HRRN") {
      const ratio = i => (time - PROCESSES[i].arrive + PROCESSES[i].burst) / PROCESSES[i].burst;
      const best = [...queue].sort((a, b) => ratio(b) - ratio(a) || byArrival(a, b))[0];
      const list = queue.map(i => `${name(i)} ${format(ratio(i))}`).join("、");
      return [queue.indexOf(best), `响应比最高（${list}）`];
    }
    const key = policy === "SJF" ? i => PROCESSES[i].burst : i => remaining[i];
    const best = [...queue].sort((a, b) => key(a) - key(b) || byArrival(a, b))[0];
    const word = policy === "SJF" ? "服务时间" : "剩余时间";
    const list = queue.map(i => `${name(i)}=${key(i)}`).join("、");
    return [queue.indexOf(best), `${word}最短（${list}）`];
  }

  function simulate(policy, quantum) {
    const n = PROCESSES.length;
    const remaining = PROCESSES.map(p => p.burst);
    const finish = Array(n).fill(null);
    const queue = [], gantt = [], frames = [];
    let running = null, used = 0;
    const snap = (time, say) => ({ time, say, running, queue: [...queue], remaining: [...remaining], finish: [...finish], gantt: [...gantt], policy });

    frames.push(snap(0, `用 ${POLICIES[policy]}${policy === "RR" ? `（时间片 = ${quantum}）` : ""} 调度这四个进程。`));
    for (let time = 0; time < 100; time++) {
      const notes = [];
      if (running !== null && remaining[running] === 0) {
        finish[running] = time;
        notes.push(`${name(running)} 跑完了`);
        running = null;
      }
      PROCESSES.forEach((p, i) => {
        if (p.arrive === time) { queue.push(i); notes.push(`${p.name} 到达，进入就绪队列`); }
      });
      if (policy === "RR" && running !== null && used === quantum) {
        notes.push(`${name(running)} 用完时间片，回到队尾`);
        queue.push(running);
        running = null;
      }
      if (policy === "SRTF" && running !== null && queue.length) {
        const challenger = queue[choose("SRTF", queue, remaining, time)[0]];
        if (remaining[challenger] < remaining[running]) {
          notes.push(`${name(challenger)} 剩余 ${remaining[challenger]}，比 ${name(running)} 剩余的 ${remaining[running]} 短，抢占`);
          queue.push(running);
          running = null;
        }
      }
      if (finish.every(f => f !== null)) {
        frames.push(snap(time, `t = ${time}：${notes.join("；")}。全部完成，看下面的表。`));
        break;
      }
      if (running === null && queue.length) {
        const [position, reason] = choose(policy, queue, remaining, time);
        running = queue.splice(position, 1)[0];
        used = 0;
        notes.push(`调度器选 ${name(running)}：${reason}`);
      } else if (running !== null) {
        notes.push(`${name(running)} 继续跑（还剩 ${remaining[running]}）`);
      } else {
        notes.push("就绪队列是空的，CPU 空闲");
      }
      gantt.push(running);
      frames.push(snap(time, `t = ${time}：${notes.join("；")}。`));
      if (running !== null) { remaining[running]--; used++; }
    }
    return frames;
  }

  // 甘特图：把相邻的同一进程合成一段
  function ganttChart(frame) {
    const unit = 32, left = 10, width = 560, height = 64;
    const svg = svgElement("svg", { class: "gantt", viewBox: `0 0 ${width} ${height}`, width });
    const segments = [];
    frame.gantt.forEach((who, t) => {
      const last = segments[segments.length - 1];
      if (last && last.who === who) last.end = t + 1;
      else segments.push({ who, start: t, end: t + 1 });
    });
    for (const s of segments) {
      const g = svgElement("g", { class: "seg" });
      const x = left + s.start * unit, w = (s.end - s.start) * unit;
      g.append(svgElement("rect", { x, y: 6, width: w, height: 28, class: s.who === null ? "idle" : "p" + (s.who + 1), "stroke-width": 1.5 }));
      g.append(svgElement("text", { x: x + w / 2, y: 25, "text-anchor": "middle" }, s.who === null ? "空" : name(s.who)));
      svg.append(g);
    }
    const ticks = new Set([0, ...segments.map(s => s.end)]);
    for (const t of ticks) svg.append(svgElement("text", { x: left + t * unit, y: 52, "text-anchor": "middle", class: "small" }, t));
    return svg;
  }

  function render(frame) {
    const done = frame.finish.every(f => f !== null);
    const rows = PROCESSES.map((p, i) => {
      const end = frame.finish[i];
      const turnaround = end === null ? null : end - p.arrive;
      return el("tr", { class: i === frame.running ? "hot" : "" },
        el("td", { class: i === frame.running ? "hot" : "" }, `${p.name} ${p.job}`),
        el("td", {}, p.arrive), el("td", {}, p.burst), el("td", {}, frame.remaining[i]),
        el("td", {}, end ?? "—"),
        el("td", {}, turnaround ?? "—"),
        el("td", {}, turnaround === null ? "—" : turnaround - p.burst));
    });
    const n = PROCESSES.length;
    const average = pick => format(PROCESSES.reduce((sum, p, i) => sum + pick(p, frame.finish[i]), 0) / n);
    return [
      el("div", { class: "row" },
        el("span", { class: "label" }, "CPU："),
        frame.running === null ? box("空闲", "empty") : box(name(frame.running), "running p" + (frame.running + 1)),
        el("span", { class: "label" }, "　就绪队列："),
        frame.queue.length ? frame.queue.map(i => box(name(i), "queued p" + (i + 1))) : el("span", { class: "label" }, "（空）")),
      ganttChart(frame),
      el("table", {},
        el("tr", {}, ...["进程", "到达", "服务", "剩余", "完成", "周转", "等待"].map(h => el("th", {}, h))),
        ...rows),
      done && el("p", { class: "stat" },
        "平均周转时间 = ", el("b", { class: "avg-turnaround" }, average((p, end) => end - p.arrive)),
        "，平均等待时间 = ", el("b", { class: "avg-wait" }, average((p, end) => end - p.arrive - p.burst))),
    ];
  }

  const player = new Player(root, render);
  const quantum = el("input", { type: "number", value: "2", min: "1", max: "10", "aria-label": "时间片" });
  const run = policy => () => player.load(simulate(policy, Math.max(1, Number(quantum.value) || 1)));
  const reset = () => player.load([{
    time: 0, running: null, queue: [], gantt: [], policy: null,
    remaining: PROCESSES.map(p => p.burst), finish: PROCESSES.map(() => null),
    say: "四个进程还没开始。点上面的按钮选一种调度算法。",
  }]);

  root.prepend(el("div", { class: "ops-bar" },
    ...Object.entries(POLICIES).map(([key, label]) => el("button", { onclick: run(key) }, label)),
    el("span", { class: "label" }, "时间片 ="), quantum,
    el("button", { onclick: reset }, "重置")));
  reset();
})();
