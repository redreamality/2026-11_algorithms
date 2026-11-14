// 动画：滑动窗口三道题。窗口是 [windowStart, windowEnd] 这一段（两端都包含），画成蓝色。
// 每帧记录：数组、窗口两端、这一步刚进来或刚出去的格子（橙色）、统计行、到目前为止最好的答案。
(() => {
  const root = document.getElementById("window");

  function snap(say, values, windowStart, windowEnd, { hot = [], stat = "", bestLabel = "", best = null, bestRange = null } = {}) {
    return { say, values, windowStart, windowEnd, hot, stat, bestLabel, best, bestRange };
  }

  function render(frame) {
    const columns = frame.values.map((value, index) => {
      const inWindow = index >= frame.windowStart && index <= frame.windowEnd;
      const isHot = frame.hot.includes(index);
      const inBest = frame.bestRange && index >= frame.bestRange[0] && index <= frame.bestRange[1];
      const style = inBest ? "done" : [inWindow && "window", isHot && "hot"].filter(Boolean).join(" ");
      const labels = [];
      if (index === frame.windowStart) labels.push("起点");
      if (index === frame.windowEnd) labels.push("终点");
      return el("div", { class: "cell-column" },
        box(value, style),
        el("span", { class: "index" }, index),
        el("span", { class: "pointer" }, labels.join(" / ")));
    });
    return [
      el("div", { class: "cells" }, columns),
      el("p", { class: "stat" }, frame.stat),
      el("p", { class: "stat" }, frame.bestLabel, frame.best === null ? null : el("b", { class: "best" }, frame.best)),
    ];
  }

  const player = new Player(root, render);
  const quote = text => `"${text}"`;

  function longestSubstringFrames() {
    const text = "abcabcbb";
    const values = [...text];
    const charactersInWindow = new Set();
    let windowStart = 0, longestLength = 0, longestText = "";
    const extras = (hot = []) => ({
      hot,
      stat: `characters_in_window = {${[...charactersInWindow].join(", ")}}`,
      bestLabel: "目前最长：",
      best: longestLength ? `${quote(longestText)}（长度 ${longestLength}）` : "还没有",
    });
    const frames = [snap(`text = ${quote(text)}。窗口一开始是空的，“终点” window_end 每次右移一格，把一个新字符放进窗口。`,
      values, 0, -1, extras())];
    values.forEach((character, windowEnd) => {
      if (charactersInWindow.has(character)) {
        frames.push(snap(`window_end = ${windowEnd}，新字符 '${character}' 已经在窗口里了，放进来就会重复。先收缩：从左边一个个移出字符，直到窗口里没有 '${character}'。`,
          values, windowStart, windowEnd - 1, extras([windowEnd])));
        while (charactersInWindow.has(character)) {
          const removed = values[windowStart];
          charactersInWindow.delete(removed);
          windowStart++;
          frames.push(snap(`移出 '${removed}'，window_start 右移到 ${windowStart}。` +
            (charactersInWindow.has(character) ? `窗口里还有 '${character}'，继续收缩。` : `窗口里没有 '${character}' 了，停止收缩。`),
            values, windowStart, windowEnd - 1, extras([windowStart - 1, windowEnd])));
        }
      }
      charactersInWindow.add(character);
      const windowText = text.slice(windowStart, windowEnd + 1);
      const improved = windowText.length > longestLength;
      if (improved) { longestLength = windowText.length; longestText = windowText; }
      frames.push(snap(`把 '${character}' 放进窗口。窗口 ${quote(windowText)} 没有重复，长度 ${windowText.length}。` +
        (improved ? `比之前都长，记为目前最长。` : `没有超过目前最长的 ${longestLength}。`),
        values, windowStart, windowEnd, extras([windowEnd])));
    });
    const bestStart = text.indexOf(longestText);
    frames.push(snap(`window_end 走到头了。最长的无重复子串是 ${quote(longestText)}，长度 ${longestLength}。`,
      values, bestStart, bestStart + longestLength - 1, { ...extras(), bestRange: [bestStart, bestStart + longestLength - 1] }));
    return frames;
  }

  function minWindowFrames() {
    const source = "ADOBECODEBANC", target = "ABC";
    const values = [...source];
    const needCount = {};
    for (const character of target) needCount[character] = (needCount[character] || 0) + 1;
    let missingCount = target.length, windowStart = 0, bestStart = 0, bestLength = null;
    const extras = (hot = []) => ({
      hot,
      stat: `need_count = {${[...new Set(target)].map(character => `${character}: ${needCount[character]}`).join(", ")}}` +
        `（负数表示多了）　missing_count = ${missingCount}`,
      bestLabel: "目前最短：",
      best: bestLength === null ? "还没有" : `${quote(source.slice(bestStart, bestStart + bestLength))}（长度 ${bestLength}）`,
    });
    const frames = [snap(`source = ${quote(source)}，target = ${quote(target)}。窗口需要包含 A、B、C 各一个，现在一共还差 ${missingCount} 个。`,
      values, 0, -1, extras())];
    values.forEach((character, windowEnd) => {
      const before = needCount[character] || 0;
      if (before > 0) missingCount--;
      needCount[character] = before - 1;
      const kind = before > 0 ? `它是还缺的字符，missing_count 减 1，变成 ${missingCount}。`
        : target.includes(character) ? `窗口里已经有足够的 '${character}' 了，这个是多出来的，missing_count 不变。`
          : `它不在 target 里，对覆盖没有帮助，missing_count 不变。`;
      frames.push(snap(`window_end = ${windowEnd}，放进 '${character}'：${kind}`, values, windowStart, windowEnd, extras([windowEnd])));
      while (missingCount === 0) {
        const windowLength = windowEnd - windowStart + 1;
        const windowText = source.slice(windowStart, windowEnd + 1);
        const improved = bestLength === null || windowLength < bestLength;
        if (improved) { bestStart = windowStart; bestLength = windowLength; }
        const removed = values[windowStart];
        frames.push(snap(`missing_count = 0，窗口 ${quote(windowText)} 已经覆盖 target，长度 ${windowLength}。` +
          (improved ? "比之前都短，记为目前最短。" : "没有比目前最短的更短。") + `试着收缩：移出 '${removed}'。`,
          values, windowStart, windowEnd, extras([windowStart])));
        needCount[removed]++;
        if (needCount[removed] > 0) missingCount++;
        windowStart++;
        frames.push(snap(`移出 '${removed}'，window_start 右移到 ${windowStart}。` +
          (missingCount > 0 ? `窗口里又缺 '${removed}' 了，missing_count 变回 1，停止收缩，继续扩张。`
            : target.includes(removed) ? `窗口里还有别的 '${removed}'，仍然覆盖，继续收缩。` : `'${removed}' 不在 target 里，仍然覆盖，继续收缩。`),
          values, windowStart, windowEnd, extras([windowStart - 1])));
      }
    });
    const answer = source.slice(bestStart, bestStart + bestLength);
    frames.push(snap(`window_end 走到头了。最小覆盖子串是 ${quote(answer)}，长度 ${bestLength}。`,
      values, bestStart, bestStart + bestLength - 1, { ...extras(), bestRange: [bestStart, bestStart + bestLength - 1] }));
    return frames;
  }

  function minSubarrayFrames() {
    const numbers = [2, 3, 1, 2, 4, 3], target = 7;
    let windowStart = 0, windowSum = 0, shortestLength = null, shortestStart = 0;
    const extras = (hot = []) => ({
      hot,
      stat: `target = ${target}　window_sum = ${windowSum}`,
      bestLabel: "目前最短长度：",
      best: shortestLength === null ? "还没有" : shortestLength,
    });
    const frames = [snap(`numbers = [${numbers.join(", ")}]，target = ${target}。找和至少为 ${target} 的最短连续子数组。`,
      numbers, 0, -1, extras())];
    numbers.forEach((number, windowEnd) => {
      windowSum += number;
      frames.push(snap(`window_end = ${windowEnd}，放进 ${number}，window_sum = ${windowSum}。` +
        (windowSum >= target ? `已经够 ${target} 了，开始收缩。` : `还不够 ${target}，继续扩张。`),
        numbers, windowStart, windowEnd, extras([windowEnd])));
      while (windowSum >= target) {
        const windowLength = windowEnd - windowStart + 1;
        const improved = shortestLength === null || windowLength < shortestLength;
        if (improved) { shortestLength = windowLength; shortestStart = windowStart; }
        const removed = numbers[windowStart];
        windowSum -= removed;
        windowStart++;
        frames.push(snap(`窗口长度 ${windowLength}，和够了，` + (improved ? "记为目前最短。" : "没有更短。") +
          `移出 ${removed}，window_sum = ${windowSum}，window_start 右移到 ${windowStart}。` +
          (windowSum >= target ? "还够，继续收缩。" : "不够了，停止收缩。"),
          numbers, windowStart, windowEnd, extras([windowStart - 1])));
      }
    });
    frames.push(snap(`window_end 走到头了。最短长度是 ${shortestLength}，子数组是 [${numbers.slice(shortestStart, shortestStart + shortestLength).join(", ")}]。`,
      numbers, shortestStart, shortestStart + shortestLength - 1, { ...extras(), bestRange: [shortestStart, shortestStart + shortestLength - 1] }));
    return frames;
  }

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(longestSubstringFrames()) }, "无重复最长子串"),
    el("button", { onclick: () => player.load(minWindowFrames()) }, "最小覆盖子串"),
    el("button", { onclick: () => player.load(minSubarrayFrames()) }, "长度最小的子数组")));
  player.load([snap("点上面的按钮，选一道题开始演示。", [..."abcabcbb"], 0, -1)]);
})();
