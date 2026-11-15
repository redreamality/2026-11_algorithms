"""第 2 课实战：链表在真实项目里长什么样。

业务代码里几乎没人专门写一个 LinkedList 类，但“每个对象记着上一个 / 下一个是谁”的结构到处都是。
最典型的是版本历史（git 的提交、文档的修订记录）：
1. 每次提交只记“我的上一次提交是谁”（parent），整条历史就是一条单链表。
2. 分支只是一个指向最新提交的名字，相当于链表的 head。新提交 = 头部插入，O(1)。
3. 开新分支不复制历史：两个分支共用同一段尾巴。
4. 看历史就是沿着 parent 往回走，用生成器逐个产出，想看几条看几条。

另外两种常见需求，标准库有现成工具，后面专门讲，这里不用：
两端快速增删的队列用 collections.deque（第 3 课）；“最近使用”的排序用 collections.OrderedDict（第 30 课）。

运行：uv run examples/linked_list_in_practice.py
"""

from collections.abc import Iterator
from itertools import islice


class Commit:
    """一次提交：说明 + 指向上一次提交的 parent。第一次提交的 parent 是 None。建好以后不再修改。"""

    def __init__(self, message: str, parent: "Commit | None" = None) -> None:
        self.message = message
        self.parent = parent


def history(commit: Commit | None) -> Iterator[Commit]:
    """从 commit 沿着 parent 一路往回走，逐个产出提交。走几步花几步。"""
    while commit is not None:
        yield commit
        commit = commit.parent


def messages(commit: Commit | None) -> list[str]:
    return [each.message for each in history(commit)]


class Branch:
    """分支：一个指向最新提交的名字（链表的 head）。"""

    def __init__(self, head: Commit | None = None) -> None:
        self.head = head

    def commit(self, message: str) -> None:
        self.head = Commit(message, self.head)  # 头部插入：O(1)

    def undo_last(self) -> str:
        """撤销最近一次提交：head 退回 parent，O(1)。没有提交时抛 IndexError，和空 list 的 pop 一样。"""
        if self.head is None:
            raise IndexError("没有可以撤销的提交")
        undone, self.head = self.head, self.head.parent
        return undone.message


def merge_base(first: Commit | None, second: Commit | None) -> Commit | None:
    """两个提交最近的共同祖先（git merge-base）：先把 first 的整条历史放进 set，
    再从 second 往回走，第一个在 set 里的就是。O(m + n)。

    普通对象默认按“是不是同一个对象”判断相等，所以可以直接放进 set。
    """
    ancestors = set(history(first))
    return next((commit for commit in history(second) if commit in ancestors), None)


def main() -> None:
    main_branch = Branch()
    for message in ["初始化", "加登录页", "修复样式"]:
        main_branch.commit(message)

    feature = Branch(main_branch.head)  # 新分支直接指向同一个提交，历史一个都没复制
    feature.commit("加支付")
    main_branch.commit("改文案")

    assert messages(main_branch.head) == ["改文案", "修复样式", "加登录页", "初始化"]
    assert messages(feature.head) == ["加支付", "修复样式", "加登录页", "初始化"]
    assert feature.head.parent is main_branch.head.parent  # 两个分支共用同一段尾巴
    print("main：", messages(main_branch.head))
    print("feature：", messages(feature.head))

    # git log -2：只看最近两条。生成器是懒的，后面的提交根本不会被访问
    latest_two = [commit.message for commit in islice(history(main_branch.head), 2)]
    assert latest_two == ["改文案", "修复样式"]
    print("最近两条：", latest_two)

    base = merge_base(main_branch.head, feature.head)
    assert base is not None and base.message == "修复样式"
    print("两个分支从这里分叉：", base.message)

    assert main_branch.undo_last() == "改文案"
    assert messages(main_branch.head) == ["修复样式", "加登录页", "初始化"]
    assert messages(feature.head)[1:] == messages(main_branch.head)  # 撤销 main 不影响 feature
    print("撤销一次后的 main：", messages(main_branch.head))

    try:
        Branch().undo_last()
    except IndexError:
        pass
    else:
        raise AssertionError("空分支撤销应该抛 IndexError")


if __name__ == "__main__":
    main()
