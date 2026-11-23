# 算法与数据结构：系统学习

## 目标

打牢计算机基础：理解常见数据结构和算法的**原理**和**复杂度**，并能用 Python 自己实现出来。
用户以前学过，现在有些生疏。讲解要通俗、简短，**千万不要写复杂**。

## 学法（每课一个循环）

1. 浏览器打开 `lessons/index.html`，读一课讲解，大约 10 分钟。
2. 补全 `dsa/` 里对应的骨架，把 `raise NotImplementedError` 换成自己的实现。
3. 跑这一课的测试，直到全部通过。
4. 让 agent review 代码，然后在下面的进度表里打勾。

开始第 00 课之前，先扫一遍预备课 `lessons/python-basics.html`（Python 基础）。每课开头的「开始前要会」会链接回预备课的对应小节和前面的课。

## 怎么运行

```bash
cd ~/agents/projects/2026-11_algorithms
uv run pytest tests/test_dynamic_array.py   # 只跑某一课
uv run pytest                               # 全部
```

还没写的课，测试会报 `NotImplementedError`，这是正常的。下面三组测试检查讲解页和实战脚本本身，应该一直是绿的：

- `tests/test_lessons.py`：链接和引用的文件都存在。
- `tests/test_examples.py`：`examples/` 里每个实战脚本都能端到端跑通（脚本自带 assert）。单独看某一个：`uv run examples/bst_in_practice.py`。
- `tests/e2e/`：用真浏览器点动画按钮，检查画面停在对的状态。新机器上第一次跑之前先执行 `uv run playwright install chromium`。

## 路线图与进度

| 阶段 | 课 | 讲解 | 骨架 + 测试 | 完成 |
|---|---|---|---|---|
| 预备 | Python 基础 | ✅ | ✅ `python_basics.py` | ☐ |
| | ACM 模式输入输出 | ✅ | ✅ `acm_io.py` | ☐ |
| 1 基础 | 00 复杂度 | ✅ | ✅ `complexity.py` | ☐ |
| | 01 动态数组 | ✅ | ✅ `dynamic_array.py` | ☐ |
| | 02 单链表 | ✅ | ✅ `linked_list.py` | ☐ |
| | 03 栈与队列（含环形队列） | ✅ | ✅ `stack_queue.py` | ☐ |
| | 04 哈希表（拉链法） | ✅ | ✅ `hash_table.py` | ☐ |
| 2 递归、排序与查找 | 05 递归与分治 | ✅ | ✅ `recursion.py` | ☐ |
| | 06 二分查找 | ✅ | ✅ `binary_search.py` | ☐ |
| | 07 简单排序（插入、选择）与稳定性 | ✅ | ✅ `simple_sorts.py` | ☐ |
| | 08 归并排序 | ✅ | ✅ `merge_sort.py` | ☐ |
| | 09 快速排序 | ✅ | ✅ `quick_sort.py` | ☐ |
| 3 树 | 10 二叉树与递归遍历 | ✅ | ✅ `binary_tree.py` | ☐ |
| | 11 二叉搜索树 | ✅ | ✅ `bst.py` | ☐ |
| | 12 堆与优先队列（含堆排序） | ✅ | ✅ `heap.py` | ☐ |
| 4 图 | 13 图的表示、BFS、DFS | ✅ | ✅ `graph.py` | ☐ |
| | 14 拓扑排序 | ✅ | ✅ `topo_sort.py` | ☐ |
| | 15 并查集 | ✅ | ✅ `union_find.py` | ☐ |
| | 16 最短路径（Dijkstra） | ✅ | ✅ `dijkstra.py` | ☐ |
| | 17 最小生成树（Kruskal） | ✅ | ✅ `kruskal.py` | ☐ |
| 5 算法设计 | 18 贪心 | ✅ | ✅ `greedy.py` | ☐ |
| | 19 动态规划（一）：从递归到记忆化 | ✅ | ✅ `dp_memo.py` | ☐ |
| | 20 动态规划（二）：背包与序列 | ✅ | ✅ `dp_knapsack.py` | ☐ |
| | 21 回溯 | ✅ | ✅ `backtracking.py` | ☐ |
| 选修 | 22 Trie | ✅ | ✅ `trie.py` | ☐ |
| | 23 KMP | ✅ | ✅ `kmp.py` | ☐ |
| | 24 平衡树思路（AVL 旋转） | ✅ | ✅ `avl.py` | ☐ |
| 6 高频面试题型 | 25 双指针 | ✅ | `two_pointers.py`（无单测） | ☐ |
| | 26 滑动窗口 | ✅ | `sliding_window.py` | ☐ |
| | 27 前缀和与哈希计数 | ✅ | `prefix_sum.py` | ☐ |
| | 28 单调栈 | ✅ | `monotonic_stack.py` | ☐ |
| | 29 链表高频技巧 | ✅ | `linked_list_patterns.py` | ☐ |
| | 30 LRU 缓存 | ✅ | `lru_cache.py` | ☐ |
| | 31 二叉树高频题 | ✅ | `tree_patterns.py` | ☐ |
| | 32 二分进阶 | ✅ | `binary_search_advanced.py` | ☐ |
| | 33 堆与 Top K | ✅ | `top_k.py` | ☐ |
| | 34 区间问题 | ✅ | `intervals.py` | ☐ |
| | 35 网格搜索 | ✅ | `grid_search.py` | ☐ |
| | 36 回溯高频题 | ✅ | `backtracking_patterns.py` | ☐ |
| | 37 一维 DP 高频题 | ✅ | `dp_1d.py` | ☐ |
| | 38 二维 DP 高频题 | ✅ | `dp_2d.py` | ☐ |
| | 39 位运算技巧 | ✅ | `bit_manipulation.py` | ☐ |
| 7 笔试模板 | 40 数论模板（gcd、筛法、取模、快速幂、逆元、组合数） | ✅ | ✅ `number_theory.py` | ☐ |
| | 41 差分数组 | ✅ | ✅ `difference_array.py` | ☐ |
| | 42 树状数组（Fenwick Tree） | ✅ | ✅ `fenwick_tree.py` | ☐ |
| | 43 区间 DP | ✅ | ✅ `interval_dp.py` | ☐ |
| | 44 状压 DP | ✅ | ✅ `bitmask_dp.py` | ☐ |
| | 45 树形 DP | ✅ | ✅ `tree_dp.py` | ☐ |
| | 46 最短路变种（0-1 BFS、Floyd、Bellman-Ford） | ✅ | ✅ `shortest_path_variants.py` | ☐ |
| 附录 | 选择题速查 | ✅ | ✅ `cheatsheet.py` | ☐ |

第 7 阶段和 ACM 预备课是 2026-11-22 按[牛客蚂蚁笔试攻略](https://www.nowcoder.com/discuss/767459618661355520)补的：笔试是 ACM 模式（自己读 stdin），编程题常考能默写的模板。

### 另一个系列：计算机基础（`lessons/cs/`）

笔试选择题的「基础分」：操作系统、计算机网络、数据库。浏览器打开 `lessons/cs/index.html`。来源是用户给的[牛客蚂蚁笔试攻略](https://www.nowcoder.com/discuss/767459618661355520)，配套题单是牛客「操作系统专项」(test/607)、「计算机网络专项」(test/146643)、「数据库专项」(test/606)。这三个题单要登录后随机组卷，拿不到原题，所以知识点按这些题库的高频题型提炼。

| 科目 | 课 | 页面 |
|---|---|---|
| 操作系统 | 1 进程与调度 · 2 虚拟内存 · 3 锁与死锁 | `01-process-scheduling` `02-virtual-memory` `03-deadlock` |
| 计算机网络 | 4 分层与 IP · 5 TCP · 6 HTTP | `04-network-layers` `05-tcp` `06-http` |
| 数据库 | 7 SQL · 8 索引 · 9 事务 | `07-sql` `08-index` `09-transaction` |

和算法课的不同：这个系列不写骨架和单测，每课 = 讲解（多张内联 SVG 图）+ 交互动画（`lessons/cs/js/`，配 `tests/e2e/test_csNN_*.py`）+「题单怎么考」（题型 → 本课小节）+ 折叠答案的自测题。第 7～9 课另有 sqlite3 实战脚本（`examples/sql_in_practice.py` 等），由 `tests/test_examples.py` 自动跑。

写这个系列的约定（用户 2026-11-22 要求）：语言友好易懂；每课 self-contain，先理清概念依赖再由浅入深；从题单提炼知识点并把题和知识点对应起来；多用 SVG 画图。整个系列用「一家小网店」作主线例子，一课之内用同一组数据讲到底。每课负责定义哪些概念、各课之间的依赖，见目录页的依赖图。样式在 `lessons/cs/cs.css`（SVG 配色 class：obj / hot / ok / bad / muted / plain）。

**为什么是这个顺序**：后一课要用到前一课。复杂度是尺子；数组（连续格子）和链表（指针串联）是两种最基本的存法，后面的结构都由它们拼成（哈希表 = 数组 + 链表）。递归必须在归并排序和树之前。图把前面全用上（BFS 靠队列、Dijkstra 靠堆、Kruskal 靠排序 + 并查集）。贪心、DP、回溯放最后，是把见过的具体算法抽象成方法。2026-11-10 把“递归”从第 17 课提前到第 05 课。

参考书（可选，不必通读）：《算法》（Sedgewick）讲得直观，适合配合阅读；《算法导论》留给想看证明的时候查。

## 现状（2026-11-10）

- 第 00～24 课的讲解、动画、骨架和测试都写好了，用户还没开始写代码。
- 测试已经用一份参考实现验证过（00～02 课 57 个；03～24 课的每一课都由作者和审查者各写一份参考实现跑通）。参考实现故意没有放进仓库，避免剧透。在仓库里跑单测，失败的全是 `NotImplementedError`。
- 2026-11-10：用户指出讲解页“没有动画就失去了用 HTML 的意义”。三课都补上了可逐步播放的交互动画，配 17 个 e2e 测试。
- 2026-11-10：用户要求把后面的课一次做完，并说测试可以简单些。03～24 课由并行 agent 写完，每课再由另一个 agent 独立审查和修正。`test_lessons.py` 加上 e2e 一共 87 个测试，全部通过。

- 2026-11-10：加了第六阶段「高频面试题型」（25～39 课），由 5 个并行 agent 写完。按用户的新要求：讲解不过分省略（每题按“题意 → 暴力为什么慢 → 关键观察 → 为什么对 → 复杂度”展开），命名用完整英文单词，**不写单元测试**。自查方式是 `uv run dsa/<文件>.py`，文件末尾的 `__main__` 会逐例打印期望和实际，期望值都已经用仓库外的参考实现核对过。动画仍然各配一个 e2e。

- 2026-11-10：用户指出代码“不实用，实际 Python 编程没人这么写”，要求改成能端到端使用的代码。全部 40 课改成两层：讲解页先有「实战里怎么写」（标准库 / sortedcontainers 的真实做法 + 业务小例子，完整版在 `examples/<名字>_in_practice.py`）；手写骨架改成地道 Python 接口（例如第 11 课从 `BST.insert/contains` 改成 `TreeMap(MutableMapping)`，支持 `tree[key]`、`in`、`for`、floor、区间查询），`__main__` 里有端到端业务例子。第 11 课是样板，其余由 8 个并行 agent 按样板改写。

- 2026-11-15：用户读了几课后提出两点：一是 `yield from`、`setdefault`、非标准库这些写法要在用之前讲；二是讲某课时前序知识必须已经讲完。于是新增预备课 `lessons/python-basics.html`（20 个小节，各有锚点；配生成器 / `yield from` 两个动画、`dsa/python_basics.py` 书店练习、测试和实战脚本），每课开头加了 `.prereq`「开始前要会」，链接到预备课锚点和前序课。8 个并行 agent 逐课审查并修正了「先用后讲」（例如堆讲之前就用 `heapq`、队列讲之前就用 `deque`）。`test_lessons.py` 新增两项检查：锚点链接必须存在，每课必须有「开始前要会」。

- 2026-11-22：新增「计算机基础」系列（`lessons/cs/`，9 课，见上文）。第 1 课由主会话写作样板，第 2～9 课由 8 个并行 agent 按同一份说明写完。每课 10～15 张 SVG 图、1～2 个动画、8 道自测题，正文和测试里的数字都用仓库外的参考实现核对过。`test_lessons.py` 改成 `rglob`，会一并检查 `lessons/cs/`。系列相关的 107 个测试（e2e、链接、sqlite3 实战脚本）全部通过；每页 id 不重复，跨课锚点都存在。还没提交，用户也还没读。

## 下一步

- 用户：先扫一遍预备课，再从第 00 课开始，按顺序学。
- 用户：计算机基础系列从 `lessons/cs/index.html` 开始读，每课读完去刷对应的牛客专项题单。
- agent：课已经全部铺完。用户学完一课后，review 代码，再根据反馈调整后面几课的难度和篇幅。

## 给接手 agent 的约定

- **实用优先**（用户 2026-11-10 要求）：每课先讲真实项目里怎么写（能用标准库就用标准库），再讲原理和手写。手写接口要像标准库那样用：实现 `__len__`/`__iter__`/`__getitem__` 等协议、继承 `collections.abc`、异常和标准库一致、返回值不打印、遍历用生成器。讲解页里的代码要完整、能直接运行，不放 `cur = ...` 这种半截片段。新依赖只有 `sortedcontainers`，加别的先问用户。
- **知识连贯**（用户 2026-11-15 要求）：第 N 课（讲解、动画、骨架、实战脚本）只能依赖预备课和第 0～N-1 课。后面才讲的东西最多写一句预告（“第 12 课会讲的堆……”），本课的代码和练习不能用。`deque`、`heapq`、`bisect`、`OrderedDict`、`graphlib` 这类数据结构工具，在讲原理的那一课首次出现。
- **Python 写法先讲后用**（同上）：课里用到预备课没讲的 Python 写法或库，要么补进 `lessons/python-basics.html`（加一个带 `id` 的小节），要么在本课第一次用之前就地讲清楚。每课开头的 `<p class="prereq">开始前要会：…</p>` 要同步更新。
- 每课固定三件套：`lessons/NN-名字.html`、`dsa/名字.py`、`tests/test_名字.py`，外加实战脚本 `examples/名字_in_practice.py`。新课要在 `lessons/index.html` 和上面的进度表里各加一项。
- 讲解页风格：开头一句话总结，然后是一个类比、一张用 `.box` 格子画的示意图、一张复杂度表、常见的坑、练习说明，最后是 2～3 道用 `<details>` 折叠答案的自测题。只用 `lessons/style.css`，不引外部资源。
- **每课必须有交互动画**，这是用户用 HTML 的根本原因。核心操作要能一步步看清楚。做法：在 `lessons/js/NN-名字.js` 里，把每个操作生成一串帧（画面快照 + 一句解释），交给 `lessons/anim.js` 的 `Player` 播放（上一步 / 播放 / 下一步 / 速度）。动画保持简单：方块、箭头、高亮，不做花哨效果。
- 动画必须配 e2e 测试（每课一个 `tests/e2e/test_NN_名字.py`，00～02 课在 `test_animations.py`；pytest-playwright），页面地址加 `?fast` 让每帧只停 10ms。写完动画后截图自己看一遍：上次截图就发现过箭头画错的问题，而测试没有拦住。
- 用户要求（2026-11-10）：讲解要把话说明白，不要过分省略或跳步；代码命名用完整英文单词（`window_start`、`previous_node`），不用 `res`、`cands`、`l`/`r` 这类缩写。
- 页面里凡是出现 `dsa/xxx.py`、`tests/test_xxx.py` 形式的文字，`test_lessons.py` 都会去查文件在不在，所以不要写“dsa/文件名.py”这类占位路径，要写一个真实存在的文件名。
- 动画的 render 返回的数组要先摊平：`Player` 只展开一层，嵌套的数组会被当成字符串显示出来。
- 骨架里只写函数签名、docstring（说明要求和复杂度）和文件顶部的规则，**不写实现**。
- 写测试时，先在仓库外的临时目录里用一份参考实现跑通，保证测试本身没错，再交给用户。
- review 用户代码时，看三点：正确性、复杂度是否达标、边界情况。先指出问题，让用户自己改，不要直接替用户重写。
