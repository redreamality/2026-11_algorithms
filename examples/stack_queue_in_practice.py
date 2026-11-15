"""第 3 课实战：Python 项目里栈和队列真正是怎么写的。

没人专门写 Stack / Queue 类，直接用现成的：
1. 栈 → list：append 压栈，pop 弹栈，[-1] 看栈顶，都是 O(1)。
2. 单线程里的队列 → collections.deque（用法见讲解页）：append 进队尾，popleft 取队头，都是 O(1)。
   别用 list.pop(0)，它是 O(n)。
3. 多线程之间传任务 → 标准库 queue.Queue（自带锁，get 可以阻塞等待）。

运行：uv run examples/stack_queue_in_practice.py
"""

import queue
import threading
from collections import deque


def brackets_balanced(text: str) -> bool:
    """栈的经典用法：检查代码或模板里的括号是否配对。"""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for character in text:
        if character in "([{":
            stack.append(character)
        elif character in pairs:
            if not stack or stack.pop() != pairs[character]:
                return False
    return not stack


class UndoableText:
    """撤销 / 重做：两个栈。新编辑会清空重做栈。"""

    def __init__(self) -> None:
        self.text = ""
        self._undo: list[str] = []
        self._redo: list[str] = []

    def type(self, more: str) -> None:
        self._undo.append(self.text)
        self._redo.clear()
        self.text += more

    def undo(self) -> None:
        if self._undo:
            self._redo.append(self.text)
            self.text = self._undo.pop()

    def redo(self) -> None:
        if self._redo:
            self._undo.append(self.text)
            self.text = self._redo.pop()


def process_in_order(jobs: list[str]) -> list[str]:
    """单线程任务队列：先来先处理，处理中还可能产生新任务（排到队尾）。"""
    pending = deque(jobs)
    done = []
    while pending:
        job = pending.popleft()
        done.append(job)
        if job.startswith("下载"):
            pending.append(job.replace("下载", "解压"))  # 下载完了要解压
    return done


def run_with_worker_thread(jobs: list[str]) -> list[str]:
    """多线程：主线程往 queue.Queue 里放任务，工作线程取出来处理。None 表示收工。

    多线程不是这门课的内容，只需看懂：threading.Thread(target=worker) 造一个线程，start() 让它和主程序
    同时跑，join() 等它跑完；queue.Queue 的 put 放队尾、get 取队头，队列空时 get 会停下来等。
    worker 里的 while (job := tasks.get()) is not None 用了海象运算符：取一个任务，同时判断是不是 None。
    """
    tasks: queue.Queue[str | None] = queue.Queue()
    results: list[str] = []

    def worker() -> None:
        while (job := tasks.get()) is not None:
            results.append(job.upper())

    thread = threading.Thread(target=worker)
    thread.start()
    for job in jobs:
        tasks.put(job)
    tasks.put(None)
    thread.join()
    return results


def main() -> None:
    assert brackets_balanced("print(items[0])")
    assert not brackets_balanced("call(a[1)]")
    assert not brackets_balanced("((")
    print("括号检查：'print(items[0])' 配对，'call(a[1)]' 不配对")

    editor = UndoableText()
    for piece in ["Hello", ", ", "world"]:
        editor.type(piece)
    editor.undo()
    editor.undo()
    assert editor.text == "Hello"
    editor.redo()
    assert editor.text == "Hello, "
    print("撤销两次再重做一次：", repr(editor.text))

    order = process_in_order(["下载 a.zip", "发邮件", "下载 b.zip"])
    assert order == ["下载 a.zip", "发邮件", "下载 b.zip", "解压 a.zip", "解压 b.zip"]
    print("处理顺序：", order)

    assert run_with_worker_thread(["a", "b", "c"]) == ["A", "B", "C"]
    print("工作线程按顺序处理完 3 个任务")


if __name__ == "__main__":
    main()
