"""第 22 课实战：Python 项目里“前缀查询”真正是怎么写的。

大多数时候用不着手写 Trie，按场景选：
1. 判断一个字符串是不是某个前缀开头 → str.startswith，可以一次传一个 tuple 查多个前缀。
2. 词表不大（几万个以内）、要列出某个前缀下的所有词 → 排好序的 list + bisect。
   以 prefix 开头的词在排序后是连续的一段，二分找到起点，往后读到不再匹配为止。
3. 统计词频 → collections.Counter；要“按热度补全”就在候选里取 most_common。
4. 词表很大、前缀查询极频繁、还要省掉每次切片比较 → 才值得用 Trie（dsa/trie.py）。

运行：uv run examples/trie_in_practice.py
"""

from bisect import bisect_left
from collections import Counter


def words_with_prefix(sorted_words: list[str], prefix: str) -> list[str]:
    """场景二：sorted_words 已排好序。O(log n + 结果个数 · 前缀长度)。"""
    start = bisect_left(sorted_words, prefix)
    result = []
    for word in sorted_words[start:]:
        if not word.startswith(prefix):
            break
        result.append(word)
    return result


def autocomplete(history: Counter, prefix: str, limit: int) -> list[str]:
    """场景三：按搜索次数补全，次数相同按字典序。候选不多时直接排序就够了。"""
    candidates = [query for query in history if query.startswith(prefix)]
    candidates.sort(key=lambda query: (-history[query], query))
    return candidates[:limit]


def main() -> None:
    blocked_prefixes = ("/admin", "/internal", "/debug")
    paths = ["/home", "/admin/users", "/internal/metrics", "/api/orders"]
    allowed = [path for path in paths if not path.startswith(blocked_prefixes)]
    assert allowed == ["/home", "/api/orders"]
    print("放行的路径：", allowed)

    commands = sorted(["commit", "config", "clone", "checkout", "cherry-pick", "push", "pull"])
    assert words_with_prefix(commands, "c") == ["checkout", "cherry-pick", "clone", "commit", "config"]
    assert words_with_prefix(commands, "co") == ["commit", "config"]
    assert words_with_prefix(commands, "x") == []
    print("输入 co 时的命令补全：", words_with_prefix(commands, "co"))

    history = Counter()
    for query in ["python"] * 5 + ["pytest"] * 3 + ["pydantic"] * 3 + ["pandas"] * 4:
        history[query] += 1
    suggestions = autocomplete(history, "py", 2)
    assert suggestions == ["python", "pydantic"]
    print("输入 py 时的热门补全：", suggestions)


if __name__ == "__main__":
    main()
