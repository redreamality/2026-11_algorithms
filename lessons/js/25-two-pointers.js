// 动画：双指针三道题。盛最多水、两数之和 II 用对撞指针，移动零用快慢指针。
// 每帧记录：数组的值、每个下标头上的指针名、每格的高亮样式、（盛水题）水的范围和高度、统计行。
(() => {
  const root = document.getElementById("pointers");
  const BAR_SCALE = 10;   // 盛水题里，高度 1 画成 10px

  function snap(say, values, { pointers = {}, styles = {}, water = null, stat = "", best = null } = {}) {
    return { say, values: [...values], pointers, styles, water, stat, best };
  }

  function render(frame) {
    const tallest = Math.max(...frame.values, 1);
    const columns = frame.values.map((value, index) => {
      const parts = [];
      if (frame.water) {
        const [waterLeft, waterRight, waterLevel] = frame.water;
        const inside = index >= waterLeft && index <= waterRight;
        const isEnd = index === waterLeft || index === waterRight;
        // 两端的竖线外侧没有水：左端的水从竖线中间开始，右端的水到竖线中间为止
        const waterStyle = `height:${waterLevel * BAR_SCALE}px` +
          (index === waterLeft ? ";left:50%" : "") + (index === waterRight ? ";right:50%" : "");
        parts.push(el("div", { class: "bar-area", style: `height:${tallest * BAR_SCALE}px` },
          inside && waterLevel > 0 ? el("div", { class: "water", style: waterStyle }) : null,
          el("div", { class: "pillar" + (isEnd ? " hot" : ""), style: `height:${value * BAR_SCALE}px` })));
      }
      parts.push(box(value, frame.styles[index] || ""));
      parts.push(el("span", { class: "index" }, index));
      parts.push(el("span", { class: "pointer" }, (frame.pointers[index] || []).join(" / ")));
      return el("div", { class: "cell-column" }, parts);
    });
    return [el("div", { class: "cells" }, columns),
      el("p", { class: "stat" }, frame.stat, frame.best === null ? null : el("b", { class: "best" }, frame.best))];
  }

  // 把 {名字: 下标} 变成 {下标: [名字, ...]}，两个指针指向同一格时都显示出来
  function pointerLabels(positions) {
    const labels = {};
    for (const [name, index] of Object.entries(positions)) (labels[index] = labels[index] || []).push(name);
    return labels;
  }

  // 对撞指针：left 左边和 right 右边的格子都已被排除，画成灰色
  function outsideStyles(length, left, right, insideStyle = {}) {
    const styles = {};
    for (let index = 0; index < length; index++) {
      if (index < left || index > right) styles[index] = "out";
      else if (insideStyle[index]) styles[index] = insideStyle[index];
    }
    return styles;
  }

  function maxWaterFrames() {
    const heights = [1, 8, 6, 2, 5, 4, 8, 3, 7];
    const frames = [snap("heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]。left 从最左边、right 从最右边出发，此时两根竖线距离最远。",
      heights, { pointers: pointerLabels({ left: 0, right: heights.length - 1 }), stat: "最大面积：", best: 0 })];
    let left = 0, right = heights.length - 1, bestArea = 0, bestPair = null;
    while (left < right) {
      const waterHeight = Math.min(heights[left], heights[right]);
      const area = waterHeight * (right - left);
      const improved = area > bestArea;
      if (improved) { bestArea = area; bestPair = [left, right]; }
      const moveLeft = heights[left] < heights[right];
      const reason = moveLeft
        ? `左边（高 ${heights[left]}）更矮：它和最远的搭档已经算过了，换别的搭档只会更小，扔掉它，left 右移。`
        : heights[left] === heights[right]
          ? `两边一样高（都是 ${heights[left]}）：两根都已经和最远的搭档算过了，扔掉哪一根都不会错过答案，这里扔掉右边，right 左移。`
          : `右边（高 ${heights[right]}）更矮：它和最远的搭档已经算过了，换别的搭档只会更小，扔掉它，right 左移。`;
      frames.push(snap(
        `left = ${left}，right = ${right}：水高取较矮的 ${waterHeight}，宽 ${right - left}，面积 ${area}。` +
        (improved ? `比之前都大，最大面积更新为 ${bestArea}。` : `没有超过最大面积 ${bestArea}。`) + reason,
        heights, {
          pointers: pointerLabels({ left, right }),
          styles: outsideStyles(heights.length, left, right, { [left]: "hot", [right]: "hot" }),
          water: [left, right, waterHeight],
          stat: `当前面积：${area}　最大面积：`,
          best: bestArea,
        }));
      if (moveLeft) left++; else right--;
    }
    frames.push(snap(`left 和 right 相遇，结束。最大面积 ${bestArea}，由下标 ${bestPair[0]} 和 ${bestPair[1]} 两根竖线组成。`,
      heights, {
        pointers: pointerLabels({ left: bestPair[0], right: bestPair[1] }),
        styles: { [bestPair[0]]: "done", [bestPair[1]]: "done" },
        water: [bestPair[0], bestPair[1], Math.min(heights[bestPair[0]], heights[bestPair[1]])],
        stat: "最大面积：",
        best: bestArea,
      }));
    return frames;
  }

  function twoSumFrames() {
    const numbers = [1, 2, 4, 6, 8, 11, 15], target = 10;
    const frames = [snap(`numbers = [${numbers.join(", ")}]（已排序），target = ${target}。left 指向最小的数，right 指向最大的数。`,
      numbers, { pointers: pointerLabels({ left: 0, right: numbers.length - 1 }), stat: `target = ${target}` })];
    let left = 0, right = numbers.length - 1;
    while (left < right) {
      const pairSum = numbers[left] + numbers[right];
      const shared = {
        pointers: pointerLabels({ left, right }),
        stat: `target = ${target}　当前和：${pairSum}`,
      };
      if (pairSum === target) {
        frames.push(snap(`${numbers[left]} + ${numbers[right]} = ${target}，等于 target。找到了，返回 [${left}, ${right}]。`,
          numbers, { ...shared, styles: outsideStyles(numbers.length, left, right, { [left]: "done", [right]: "done" }) }));
        return frames;
      }
      const say = pairSum < target
        ? `${numbers[left]} + ${numbers[right]} = ${pairSum}，比 ${target} 小。${numbers[right]} 已经是剩下最大的数，${numbers[left]} 和谁相加都不够，排除它：left 右移。`
        : `${numbers[left]} + ${numbers[right]} = ${pairSum}，比 ${target} 大。${numbers[left]} 已经是剩下最小的数，${numbers[right]} 和谁相加都太大，排除它：right 左移。`;
      frames.push(snap(say, numbers, { ...shared, styles: outsideStyles(numbers.length, left, right, { [left]: "hot", [right]: "hot" }) }));
      if (pairSum < target) left++; else right--;
    }
    return frames;
  }

  function moveZeroesFrames() {
    const numbers = [0, 1, 0, 3, 12, 0, 5];
    const settledStyles = slow => {
      const styles = {};
      for (let index = 0; index < slow; index++) styles[index] = "done";
      return styles;
    };
    const frames = [snap(`numbers = [${numbers.join(", ")}]。slow 指向“下一个非零数该放的位置”，fast 从头往后扫。绿色是已经放好的非零数。`,
      numbers, { pointers: pointerLabels({ slow: 0, fast: 0 }) })];
    let slow = 0;
    for (let fast = 0; fast < numbers.length; fast++) {
      if (numbers[fast] === 0) {
        frames.push(snap(`fast = ${fast} 遇到 0：什么也不做，fast 继续往后走。slow 停在 ${slow}，等着放下一个非零数。`,
          numbers, { pointers: pointerLabels({ slow, fast }), styles: { ...settledStyles(slow), [fast]: "hot" } }));
        continue;
      }
      frames.push(snap(`fast = ${fast} 遇到非零数 ${numbers[fast]}：把它和 slow = ${slow} 位置的 ${numbers[slow]} 交换。`,
        numbers, { pointers: pointerLabels({ slow, fast }), styles: { ...settledStyles(slow), [slow]: "hot", [fast]: "hot" } }));
      [numbers[slow], numbers[fast]] = [numbers[fast], numbers[slow]];
      slow++;
      frames.push(snap(`交换完成，${numbers[slow - 1]} 放好了。slow 右移到 ${slow}。`,
        numbers, { pointers: pointerLabels({ slow, fast }), styles: settledStyles(slow) }));
    }
    frames.push(snap(`fast 扫完了。前 ${slow} 格是非零数，顺序和原来一样；后面全是 0。结果：[${numbers.join(", ")}]`,
      numbers, { pointers: pointerLabels({ slow }), styles: settledStyles(slow) }));
    return frames;
  }

  const player = new Player(root, render);

  root.prepend(el("div", { class: "ops-bar" },
    el("button", { onclick: () => player.load(maxWaterFrames()) }, "盛最多水"),
    el("button", { onclick: () => player.load(twoSumFrames()) }, "两数之和 II"),
    el("button", { onclick: () => player.load(moveZeroesFrames()) }, "移动零")));
  player.load([snap("点上面的按钮，选一道题开始演示。", [1, 8, 6, 2, 5, 4, 8, 3, 7])]);
})();
