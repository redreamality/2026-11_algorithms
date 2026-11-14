// 讲解页共用的动画小工具。
// 一段动画 = 一串“帧”（每帧是一份画面数据）+ 一个 render(帧) 函数；Player 负责一帧帧地放。
// 地址后面加 ?fast 会把帧间隔压到 10ms，给自动化测试用。

const FAST = new URLSearchParams(location.search).has("fast");

function el(tag, attrs, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === "class") e.className = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v);
  }
  for (const c of children.flat()) if (c != null && c !== false) e.append(c);
  return e;
}

function box(text, cls) {
  return el("span", { class: "box " + (cls || "") }, String(text));
}

class Player {
  constructor(root, render) {
    this.render = render;
    this.frames = [];
    this.i = 0;
    this.timer = null;
    this.stage = el("div", { class: "stage" });
    this.caption = el("p", { class: "caption" });
    this.prevBtn = el("button", { onclick: () => { this.stop(); this.go(this.i - 1); } }, "← 上一步");
    this.playBtn = el("button", { onclick: () => this.toggle() }, "▶ 播放");
    this.nextBtn = el("button", { onclick: () => { this.stop(); this.go(this.i + 1); } }, "下一步 →");
    this.speed = el("select", { "aria-label": "速度" },
      el("option", { value: "1200" }, "慢速"),
      el("option", { value: "600", selected: "" }, "中速"),
      el("option", { value: "200" }, "快速"));
    this.counter = el("span", { class: "label step" });
    root.append(this.stage, this.caption,
      el("div", { class: "controls" }, this.prevBtn, this.playBtn, this.nextBtn, this.speed, this.counter));
  }

  // 换一段新动画，自动开始播放
  load(frames) {
    this.stop();
    this.frames = frames;
    this.go(0);
    if (frames.length > 1) this.play();
  }

  go(i) {
    if (i < 0 || i >= this.frames.length) return;
    this.i = i;
    const f = this.frames[i];
    this.stage.replaceChildren(...[].concat(this.render(f)).filter(Boolean));
    this.caption.textContent = f.say || "";
    this.counter.textContent = `${i + 1} / ${this.frames.length}`;
    this.prevBtn.disabled = i === 0;
    this.nextBtn.disabled = i === this.frames.length - 1;
  }

  play() {
    if (this.i >= this.frames.length - 1) this.go(0);
    this.playBtn.textContent = "⏸ 暂停";
    const tick = () => {
      this.go(this.i + 1);
      if (this.i >= this.frames.length - 1) this.stop();
      else this.timer = setTimeout(tick, this.delay());
    };
    this.timer = setTimeout(tick, this.delay());
  }

  stop() {
    clearTimeout(this.timer);
    this.timer = null;
    this.playBtn.textContent = "▶ 播放";
  }

  toggle() {
    this.timer ? this.stop() : this.play();
  }

  delay() {
    return FAST ? 10 : Number(this.speed.value);
  }
}
