"""第 22 课（选修）：Trie（字典树），做成一个能直接用的“搜索框自动补全”。讲解见 lessons/22-trie.html

实际项目里，词表不大时直接用排好序的 list + bisect 找前缀（见 examples/trie_in_practice.py）；
词表大、前缀查询多、还要带权重排序时，才值得手写 Trie。这里的 Trie 按 Python 的习惯来：
word in trie、len(trie)、for word in trie、del trie[word]，另外加上前缀查询和按热度补全。

规则：
- 每个节点用一个 dict 存孩子：键是一个字符，值是下一个 TrieNode。
- 单词结束的地方 count 大于 0。count 记这个词被 add 了几次（搜索次数），
  只走到半路的节点 count 是 0，所以 "car" 存进去以后，"ca" 只是前缀，不是单词。
- 不要在内部另外用 list / set 存整个单词，所有信息都在树上。
- 同时维护 _size（不同单词的个数），让 len() 是 O(1)。
- 下面复杂度里的 L 是单词（或前缀）的长度，和树里一共有多少个单词无关。

写完后运行 uv run dsa/trie.py，看端到端的例子；再跑 uv run pytest tests/test_trie.py。
"""

from collections.abc import Iterable, Iterator


class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.count = 0  # 有几次单词在这里结束；0 表示这里不是单词的结尾


class Trie:
    def __init__(self, words: Iterable[str] = ()) -> None:
        self.root = TrieNode()
        self._size = 0
        for word in words:
            self.add(word)

    def __len__(self) -> int:
        """不同单词的个数。重复 add 同一个词不会变多。"""
        return self._size

    def __repr__(self) -> str:
        return f"Trie({list(self)!r})"

    def add(self, word: str, times: int = 1) -> None:
        """记录 word 出现了 times 次（比如被搜索了几次）。缺的节点一路新建。O(L)。

        第一次出现的词让 len 加一；再 add 只增加它的 count。
        """
        raise NotImplementedError

    def __contains__(self, word: object) -> bool:
        """word in trie：是否作为完整单词 add 过。不是 str 时返回 False。O(L)。"""
        raise NotImplementedError

    def count(self, word: str) -> int:
        """word 被 add 了几次，没有就是 0。O(L)。"""
        raise NotImplementedError

    def __delitem__(self, word: str) -> None:
        """del trie[word]：删除整个词（不管 count 是多少）。不在树里抛 KeyError(word)。O(L)。

        要从下往上把不再通向任何单词的节点剪掉，否则 has_prefix 会对已删光的前缀误报 True。
        """
        raise NotImplementedError

    def has_prefix(self, prefix: str) -> bool:
        """是否有某个单词以 prefix 开头。空前缀：树里有词就是 True。O(L)。"""
        raise NotImplementedError

    def starts_with(self, prefix: str) -> Iterator[str]:
        """按字典序逐个产出以 prefix 开头的单词（生成器）。prefix 本身是单词时也要产出。

        先走 O(L) 到前缀节点，再深度优先遍历它下面的子树，孩子按字符从小到大走，结果自然有序。
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[str]:
        """for word in trie：按字典序产出全部单词。就是 starts_with("")。"""
        return self.starts_with("")

    def complete(self, prefix: str, limit: int = 5) -> list[str]:
        """自动补全：以 prefix 开头、count 最大的 limit 个词。count 相同按字典序。

        提示：heapq.nsmallest(limit, 候选, key=lambda word: (-count, word))。
        """
        raise NotImplementedError


if __name__ == "__main__":

    def show(title, compute, expected):
        """运行一个例子，打印期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    # 端到端场景：搜索框的自动补全。用历史搜索记录建树，次数越多越靠前。
    def search_history():
        trie = Trie()
        for query, times in [("python", 50), ("pytest", 30), ("pydantic", 30), ("pandas", 40),
                             ("py", 5), ("rust", 20)]:
            trie.add(query, times)
        return trie

    show("一共几个不同的搜索词", lambda: len(search_history()), 6)
    show("输入 py 时的补全（按热度，前 3 个）", lambda: search_history().complete("py", 3),
         ["python", "pydantic", "pytest"])
    show("以 py 开头的全部词（字典序）", lambda: list(search_history().starts_with("py")),
         ["py", "pydantic", "pytest", "python"])
    show("'pyt' 是完整的搜索词吗", lambda: "pyt" in search_history(), False)
    show("有以 'pyt' 开头的词吗", lambda: search_history().has_prefix("pyt"), True)

    def remove_rust():
        trie = search_history()
        del trie["rust"]
        return trie.has_prefix("r"), len(trie)

    show("删掉 rust 后还有 r 开头的吗、还剩几个", remove_rust, (False, 5))
