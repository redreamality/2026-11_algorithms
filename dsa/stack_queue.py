"""第 3 课：栈与队列。讲解见 lessons/03-stack-queue.html

实际项目里：栈直接用 list（append / pop / [-1]），队列直接用 collections.deque
（append / popleft），见 examples/stack_queue_in_practice.py。
这里自己写一遍，接口和标准库的习惯一致，写完就能直接用：
- Stack：push、pop、peek，外加 len(stack)、if stack、for value in stack（从栈顶到栈底）。
- CircularQueue：方法名和 deque 一样，append 放队尾、popleft 取队头、peek 看队头，
  外加 len(queue)、if queue、for value in queue（从队头到队尾）。

规则：
- Stack 直接用 Python 的 list 存元素，list 的末尾就是栈顶。
- CircularQueue 用一个定长的 list（self._data）当环：
  只记 head（队头下标）和 size（元素个数），队尾下标靠算：(head + size) % capacity。
- 不许用 list.pop(0)、insert(0, x)、collections.deque，那样就不是环形队列了。
- 队列满了就换一个两倍长的新 list，按队列顺序把元素搬过去，head 归零。
- 空的时候 pop / peek / popleft 抛 IndexError，和 list、deque 一样。

写完后运行 uv run dsa/stack_queue.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_stack_queue.py。
"""

from collections.abc import Iterator


class Stack:
    def __init__(self, items=()) -> None:
        self._items: list = []
        for item in items:
            self.push(item)

    def __repr__(self) -> str:
        return f"Stack({self._items!r})"

    def __len__(self) -> int:
        """元素个数。有了 __len__，空栈在 if 里自动为假。O(1)。"""
        raise NotImplementedError

    def __iter__(self) -> Iterator:
        """for value in stack：从栈顶到栈底依次产出，不弹出。O(n)。"""
        raise NotImplementedError

    def push(self, value) -> None:
        """压到栈顶。均摊 O(1)。"""
        raise NotImplementedError

    def pop(self):
        """弹出并返回栈顶。O(1)。空栈抛 IndexError。"""
        raise NotImplementedError

    def peek(self):
        """返回栈顶但不弹出。O(1)。空栈抛 IndexError。"""
        raise NotImplementedError


class CircularQueue:
    def __init__(self, items=(), capacity: int = 4) -> None:
        self._data: list = [None] * capacity
        self._head = 0  # 队头所在的下标
        self._size = 0
        for item in items:
            self.append(item)

    def __repr__(self) -> str:
        return f"CircularQueue({list(self)!r})"

    @property
    def capacity(self) -> int:
        return len(self._data)

    def __len__(self) -> int:
        """元素个数。O(1)。"""
        raise NotImplementedError

    def __iter__(self) -> Iterator:
        """for value in queue：从队头到队尾依次产出，不取出。第 k 个在 (head + k) % capacity。O(n)。"""
        raise NotImplementedError

    def append(self, value) -> None:
        """放到队尾。满了先扩容成两倍。均摊 O(1)。"""
        raise NotImplementedError

    def popleft(self):
        """取出并返回队头。O(1)。空队列抛 IndexError。"""
        raise NotImplementedError

    def peek(self):
        """返回队头但不取出。O(1)。空队列抛 IndexError。"""
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

    # 端到端场景一：编辑器的撤销。每次编辑压栈，撤销时弹出最近的一次。
    def undo_twice():
        history = Stack()
        for edit in ["输入 Hello", "加粗", "改成红色"]:
            history.push(edit)
        undone = [history.pop(), history.pop()]
        return undone, history.peek(), len(history)

    show("撤销两次：先撤最近的", undo_twice, (["改成红色", "加粗"], "输入 Hello", 1))

    def brackets_balanced(text):
        """括号匹配：遇到左括号压栈，遇到右括号看栈顶是不是配对的左括号。"""
        pairs = {")": "(", "]": "[", "}": "{"}
        stack = Stack()
        for character in text:
            if character in "([{":
                stack.push(character)
            elif character in pairs:
                if not stack or stack.pop() != pairs[character]:
                    return False
        return not stack

    show("括号匹配 'print(items[0])'", lambda: brackets_balanced("print(items[0])"), True)
    show("括号匹配 'call(a[1)]'", lambda: brackets_balanced("call(a[1)]"), False)

    # 端到端场景二：打印机任务队列，先提交的先打印。
    def print_jobs():
        jobs = CircularQueue(["合同.pdf", "发票.pdf"])
        jobs.append("报告.docx")
        first = jobs.popleft()
        for name in ["照片1.jpg", "照片2.jpg", "照片3.jpg"]:  # 超过初始容量 4，要扩容
            jobs.append(name)
        return first, list(jobs), jobs.capacity

    show("提交、打印、再提交之后", print_jobs,
         ("合同.pdf", ["发票.pdf", "报告.docx", "照片1.jpg", "照片2.jpg", "照片3.jpg"], 8))
