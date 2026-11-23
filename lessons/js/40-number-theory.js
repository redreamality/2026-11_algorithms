// 动画：主线“幸运卡”的三步。
// 辗转相除 gcd(190, 28)；埃氏筛 1..20；快速幂 7^9 mod 11。
// 表格类动画：橙色 hot = 这一步正在算的行，绿色 done = 结论。
// 筛法：橙色 current = 当前质数，红色 gone = 这一步刚划掉，灰色 crossed = 之前划掉，绿色 prime = 质数。
(() => {
  const root = document.getElementById("number-theory");

  function renderTable(f) {
    return el("table", { class: "nt-table" },
      el("tr", {}, f.headers.map(h => el("th", {}, h))),
      f.rows.map(row => el("tr", { class: row.cls || "" }, row.cells.map(c => el("td", {}, String(c))))));
  }

  function renderGrid(f) {
    return el("div", { class: "nt-grid" },
      f.cards.map((state, index) => box(index + 1, "card " + state)));
  }

  function render(f) {
    return [
      f.kind === "grid" ? renderGrid(f) : renderTable(f),
      f.extra && el("p", { class: "stat" }, f.extra),
    ];
  }

  const player = new Player(root, render);

  // ---------- 辗转相除 ----------
  function gcdFrames() {
    const headers = ["first", "second", "first % second"];
    let first = 190, second = 28;
    const rows = [];
    const snap = (say, extra = "") => ({ say, extra, headers, rows: rows.map(r => ({ ...r })) });
    const fr = [snap("约分 28 / 190 要先求 gcd(190, 28)。规则：gcd(first, second) = gcd(second, first % second)，第二个数变成 0 就停。")];
    while (second) {
      const remainder = first % second;
      rows.forEach(r => { r.cls = ""; });
      rows.push({ cells: [first, second, remainder], cls: "hot" });
      fr.push(snap(`${first} % ${second} = ${remainder}，所以 gcd(${first}, ${second}) = gcd(${second}, ${remainder})。` +
        (remainder === 0 ? "余数是 0 了，下一行第二个数就是 0。" : "")));
      [first, second] = [second, remainder];
    }
    rows.forEach(r => { r.cls = ""; });
    rows.push({ cells: [first, second, "停"], cls: "done" });
    fr.push(snap(`第二个数是 0，停。gcd(190, 28) = ${first}，所以 28 / 190 约分成 14 / 95。只用了 ${rows.length - 1} 次取模。`,
      `gcd(190, 28) = ${first}`));
    return fr;
  }

  // ---------- 埃氏筛 ----------
  function sieveFrames() {
    const limit = 20;
    // cards[i] 对应编号 i + 1
    const cards = Array(limit).fill("");
    cards[0] = "crossed";
    const fr = [];
    const snap = (say, extra = "") => ({ kind: "grid", say, extra, cards: [...cards] });
    const crossedCount = () => cards.filter(s => s === "crossed" || s === "gone").length;
    fr.push(snap("卡片 1..20。1 不是质数，先划掉。其余先都当成质数候选。"));
    for (let prime = 2; prime <= limit; prime++) {
      if (prime * prime > limit) {
        fr.push(snap(`prime = ${prime}：${prime} × ${prime} = ${prime * prime} > 20，后面的数划不掉任何东西了，停。`));
        break;
      }
      if (cards[prime - 1] === "crossed") {
        fr.push(snap(`prime = ${prime}：${prime} 已经被划掉，是合数，跳过。`));
        continue;
      }
      cards[prime - 1] = "current";
      fr.push(snap(`prime = ${prime}：没被划掉，所以 ${prime} 是质数。从 ${prime} × ${prime} = ${prime * prime} 开始划掉它的倍数。`));
      for (let multiple = prime * prime; multiple <= limit; multiple += prime) {
        cards.forEach((s, i) => { if (s === "gone") cards[i] = "crossed"; });
        if (cards[multiple - 1] === "crossed") {
          fr.push(snap(`${multiple} = ${prime} × ${multiple / prime}，早就被更小的质数划掉了，不用管。`));
        } else {
          cards[multiple - 1] = "gone";
          fr.push(snap(`划掉 ${multiple} = ${prime} × ${multiple / prime}。`, `已划掉 ${crossedCount()} 张`));
        }
      }
      cards.forEach((s, i) => { if (s === "gone") cards[i] = "crossed"; });
      cards[prime - 1] = "prime";
    }
    const primes = [];
    cards.forEach((s, i) => { if (s !== "crossed") { cards[i] = "prime"; primes.push(i + 1); } });
    fr.push(snap(`没被划掉的都是质数：${primes.join("、")}，共 ${primes.length} 张幸运卡。`,
      `幸运卡 ${primes.length} 张`));
    return fr;
  }

  // ---------- 快速幂 ----------
  function powFrames() {
    const modulus = 11;
    let base = 7, exponent = 9, result = 1, power = 1;
    const headers = ["exponent（二进制）", "最低位", "base", "result"];
    const rows = [];
    const snap = (say, extra = "") => ({ say, extra, headers, rows: rows.map(r => ({ ...r })) });
    const fr = [snap("算 7^9 mod 11。9 的二进制是 1001 = 8 + 1，所以 7^9 = 7^8 × 7^1。result 从 1 开始。")];
    while (exponent > 0) {
      const bit = exponent & 1;
      const before = result;
      if (bit) result = result * base % modulus;
      rows.forEach(r => { r.cls = ""; });
      rows.push({ cells: [exponent.toString(2), bit, `${base}（7^${power}）`, result], cls: "hot" });
      fr.push(snap(bit
        ? `最低位是 1：把 base = ${base}（代表 7^${power}）乘进结果，${before} × ${base} % 11 = ${result}。`
        : `最低位是 0：base = ${base}（代表 7^${power}）不乘进结果，result 还是 ${result}。`));
      const nextBase = base * base % modulus;
      fr.push(snap(`base 平方：${base} × ${base} % 11 = ${nextBase}（代表 7^${power * 2}）；exponent 右移一位，` +
        `${exponent.toString(2)} → ${(exponent >> 1).toString(2)}。`));
      base = nextBase;
      power *= 2;
      exponent >>= 1;
    }
    rows.forEach(r => { r.cls = ""; });
    rows.push({ cells: ["0", "", "", result], cls: "done" });
    fr.push(snap(`exponent 变成 0，停。7^9 mod 11 = ${result}。只循环了 4 次（9 的二进制位数），而不是乘 8 次。` +
      ` 由费马小定理，这也是 7 在 mod 11 下的逆元：7 × ${result} = ${7 * result} ≡ 1。`, `7^9 mod 11 = ${result}`));
    return fr;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(gcdFrames()) }, "辗转相除"),
    el("button", { onclick: () => player.load(sieveFrames()) }, "埃氏筛"),
    el("button", { onclick: () => player.load(powFrames()) }, "快速幂")));
  player.load([gcdFrames()[0]]);
})();
