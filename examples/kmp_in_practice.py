"""第 23 课实战：Python 项目里“在文本里找子串”真正是怎么写的。

日常没人手写 KMP，按场景选：
1. 有没有 → pattern in text。
2. 第一次出现在哪 → text.find（找不到 -1）/ text.index（找不到抛 ValueError）。
3. 出现几次（不重叠）→ text.count。
4. 所有位置、要带上下文、要忽略大小写或匹配一类字符串 → re.finditer。
   要重叠的位置就用前瞻：re.finditer("(?=aa)", text)。
5. 同时找很多个关键词 → 把关键词拼成一个正则 "a|b|c"（re.escape 每个词），一次扫描。
CPython 的 str.find 用的是 Boyer-Moore 一类的算法加启发式，实际比 KMP 更快；
KMP 的价值在于最坏情况 O(n + m) 有保证，以及前缀表这个思路。

运行：uv run examples/kmp_in_practice.py
"""

import re


def error_lines(log: str) -> list[int]:
    """场景一：每个 ERROR 出现在第几行。finditer 给出位置，数一下前面有几个换行。"""
    return [log.count("\n", 0, match.start()) + 1 for match in re.finditer("ERROR", log)]


def mask_keywords(message: str, keywords: list[str]) -> str:
    """场景二：同时屏蔽多个敏感词，忽略大小写。拼成一个正则，只扫描一遍。"""
    pattern = re.compile("|".join(re.escape(keyword) for keyword in keywords), re.IGNORECASE)
    return pattern.sub(lambda match: "*" * len(match.group()), message)


def main() -> None:
    log = "INFO start\nERROR db timeout\nINFO retry\nERROR db timeout\nINFO ok\n"
    assert "ERROR" in log
    assert log.find("FATAL") == -1
    assert log.count("ERROR") == 2
    assert error_lines(log) == [2, 4]
    print("ERROR 出现在第几行：", error_lines(log))

    try:
        log.index("FATAL")
    except ValueError as error:
        assert str(error) == "substring not found"

    overlapping = [match.start() for match in re.finditer("(?=ATA)", "ATATATA")]
    assert overlapping == [0, 2, 4]
    assert "ATATATA".count("ATA") == 2  # count 不算重叠的
    print("ATATATA 里 ATA 的所有位置（含重叠）：", overlapping)

    masked = mask_keywords("Password is hunter2, PASSWORD again", ["password", "hunter2"])
    assert masked == "******** is *******, ******** again"
    print("屏蔽之后：", masked)


if __name__ == "__main__":
    main()
