"""第 38 课实战：二维 DP（编辑距离、最长公共子序列）在 Python 里真正怎么用。

最常见的两个需求，标准库 difflib 已经做好了：
1. “您是不是要找……”（命令拼错、搜索纠错）→ difflib.get_close_matches，相似度用 SequenceMatcher.ratio()。
2. 对比两份文本（配置、代码）→ difflib.unified_diff，输出和 git diff 一样的格式。
注意 difflib 算的不是严格的编辑距离，而是基于“最长匹配块”的相似度，速度快、结果符合直觉。

需要严格的“最少改几个字”时（例如“只纠正 1～2 个字以内的拼写错误”），自己写编辑距离：
二维表 O(m·n)，按行滚动只要 O(n) 空间。

运行：uv run examples/dp_2d_in_practice.py
"""

from difflib import SequenceMatcher, get_close_matches, unified_diff


def edit_distance(source: str, target: str) -> int:
    """把 source 改成 target 最少要几步（插入、删除、替换一个字符各算一步）。

    previous_row[j] = source 的前 i - 1 个字符变成 target 的前 j 个字符的最少步数；
    只用到上一行，所以不存整张表。
    """
    previous_row = list(range(len(target) + 1))  # 空串变成 target[:j] 要插入 j 次
    for i in range(1, len(source) + 1):
        current_row = [i] + [0] * len(target)  # source[:i] 变成空串要删除 i 次
        for j in range(1, len(target) + 1):
            if source[i - 1] == target[j - 1]:
                current_row[j] = previous_row[j - 1]
            else:
                current_row[j] = 1 + min(previous_row[j - 1],  # 替换
                                         previous_row[j],  # 删除 source[i - 1]
                                         current_row[j - 1])  # 插入 target[j - 1]
        previous_row = current_row
    return previous_row[-1]


def suggest_command(typed: str, commands: list[str], max_edits: int = 2) -> list[str]:
    """命令行“您是不是要找”：编辑距离不超过 max_edits 的命令，距离近的排前面。"""
    distances = [(edit_distance(typed, command), command) for command in commands]
    return [command for distance, command in sorted(distances) if distance <= max_edits]


def main() -> None:
    commands = ["install", "uninstall", "list", "freeze", "show", "search"]

    assert edit_distance("kitten", "sitting") == 3
    assert edit_distance("", "abc") == 3
    assert suggest_command("instal", commands) == ["install"]
    assert suggest_command("shwo", commands) == ["show"]
    assert suggest_command("xyz", commands) == []
    print("instal → 您是不是要找：", suggest_command("instal", commands))

    close = get_close_matches("instal", commands, n=2, cutoff=0.6)
    assert close[0] == "install"
    ratio = SequenceMatcher(None, "instal", "install").ratio()  # 第一个参数 None：不忽略任何字符
    assert round(ratio, 2) == 0.92
    print(f"difflib 的建议：{close}，相似度 {ratio:.2f}")

    old_config = ["host = localhost\n", "port = 8000\n", "debug = true\n"]
    new_config = ["host = localhost\n", "port = 8080\n", "debug = true\n", "workers = 4\n"]
    diff = list(unified_diff(old_config, new_config, "config.old", "config.new"))
    assert "-port = 8000\n" in diff and "+port = 8080\n" in diff and "+workers = 4\n" in diff
    print("配置文件对比：")
    print("".join(diff), end="")


if __name__ == "__main__":
    main()
