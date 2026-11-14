"""第 30 课实战：Python 项目里 LRU 缓存真正是怎么写的。

很少有人在业务代码里手写“哈希表 + 双向链表”。按场景选：
1. 给一个纯函数的结果做缓存（参数相同，结果就相同）→ 标准库装饰器 functools.lru_cache。
   一行代码，自带命中率统计 cache_info()，清空用 cache_clear()。
2. 要自己控制缓存的读写（按用户 ID 缓存、手动失效某一项）→ collections.OrderedDict。
   它内部就是“哈希表 + 双向链表”：move_to_end(key) 挪到最新，popitem(last=False) 弹出最旧的。

运行：uv run examples/lru_cache_in_practice.py
"""

from collections import OrderedDict
from functools import lru_cache

exchange_rate_requests: list[str] = []


@lru_cache(maxsize=2)
def exchange_rate(currency: str) -> float:
    """场景一：查汇率很慢（假装要请求外部服务），同一种货币一会儿内结果不变，适合缓存。"""
    exchange_rate_requests.append(currency)
    return {"USD": 7.1, "EUR": 7.7, "JPY": 0.047}[currency]


class SessionStore:
    """场景二：服务端最多保存 capacity 个登录会话，满了踢掉最久没活动的那个。"""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._sessions: OrderedDict[str, str] = OrderedDict()  # 会话 ID -> 用户名，越靠后越新

    def login(self, session_id: str, user_name: str) -> str | None:
        """登记一个会话；如果因此踢掉了别人，返回被踢掉的会话 ID。"""
        self._sessions[session_id] = user_name
        self._sessions.move_to_end(session_id)  # 重复登录也算一次活动
        if len(self._sessions) > self.capacity:
            evicted_session_id, _ = self._sessions.popitem(last=False)  # 弹出最旧的
            return evicted_session_id
        return None

    def user_of(self, session_id: str) -> str | None:
        """用会话 ID 查用户。查到就算一次活动，挪到最新。"""
        if session_id not in self._sessions:
            return None
        self._sessions.move_to_end(session_id)
        return self._sessions[session_id]

    def logout(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)  # 主动失效一项：lru_cache 做不到这件事

    def active_sessions(self) -> list[str]:
        """从最旧到最新。"""
        return list(self._sessions)


def main() -> None:
    for currency in ["USD", "EUR", "USD", "JPY", "EUR"]:
        exchange_rate(currency)
    # USD 第二次命中缓存；JPY 进来时满了，淘汰最久没用的 EUR，所以 EUR 第二次要重新请求
    assert exchange_rate_requests == ["USD", "EUR", "JPY", "EUR"]
    info = exchange_rate.cache_info()
    assert (info.hits, info.misses, info.currsize) == (1, 4, 2)
    print("真正发出去的汇率请求：", exchange_rate_requests)
    print("缓存统计：", info)

    store = SessionStore(capacity=2)
    assert store.login("s1", "张三") is None
    assert store.login("s2", "李四") is None
    assert store.user_of("s1") == "张三"  # s1 有活动，s2 变成最旧的
    assert store.login("s3", "王五") == "s2"
    assert store.user_of("s2") is None
    assert store.active_sessions() == ["s1", "s3"]
    store.logout("s1")
    assert store.active_sessions() == ["s3"]
    print("会话满了被踢掉的：s2；张三登出后剩下：", store.active_sessions())


if __name__ == "__main__":
    main()
