"""计算机基础第 8 课实战：索引与查询优化。讲解见 lessons/cs/08-index.html

只用标准库 sqlite3，在内存库里造一张 5 万行的网店订单表 orders，
用 EXPLAIN QUERY PLAN 看 SQLite 打算怎么执行每条查询，并用 assert 检查计划里的关键字：

  1. 没有索引：           SCAN orders                         （全表扫描）
  2. 按主键查：           SEARCH orders USING INTEGER PRIMARY KEY
  3. 建了 user_id 索引：  SEARCH orders USING INDEX idx_user_id (user_id=?)
  4. 只要索引里有的列：   SEARCH orders USING COVERING INDEX ...（覆盖索引，不回表）
  5. 对列做运算：         又变回 SCAN orders                  （索引失效）
  6. 联合索引最左前缀：   括号里列出用上了哪几列；跳过最左列就用不上

和 MySQL EXPLAIN 的对应（讲解页第 13 节有表）：
  SCAN 表           ≈ type = ALL
  SEARCH ... INDEX  ≈ type = ref / range，key = 索引名
  COVERING INDEX    ≈ Extra 里的 Using index

运行：uv run examples/index_in_practice.py
"""

import random
import sqlite3
import time

ROWS = 50_000
STATUSES = ["unpaid", "paid", "shipped", "refund"]


def build() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.execute("""
        CREATE TABLE orders (
          id         INTEGER PRIMARY KEY,   -- SQLite 里它就是聚簇的主键（rowid）
          user_id    INTEGER NOT NULL,
          product_id INTEGER NOT NULL,
          quantity   INTEGER NOT NULL,
          status     TEXT    NOT NULL,      -- 本课新增：unpaid / paid / shipped / refund
          created_at TEXT    NOT NULL
        )""")
    rng = random.Random(8)
    rows = [
        (
            i,
            rng.randint(1, 5000),                      # 5000 个用户，平均每人 10 单
            rng.randint(1, 5),
            rng.randint(1, 4),
            rng.choice(STATUSES),
            f"2026-{rng.randint(1, 11):02d}-{rng.randint(1, 28):02d}",
        )
        for i in range(1, ROWS + 1)
    ]
    db.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", rows)
    return db


def plan(db: sqlite3.Connection, sql: str) -> str:
    """EXPLAIN QUERY PLAN 每一行的最后一列是说明文字，把它们拼成一行返回。"""
    return " | ".join(row[-1] for row in db.execute("EXPLAIN QUERY PLAN " + sql))


def timed(db: sqlite3.Connection, sql: str, repeat: int = 20) -> float:
    start = time.perf_counter()
    for _ in range(repeat):
        db.execute(sql).fetchall()
    return (time.perf_counter() - start) / repeat * 1000


def show(title: str, db: sqlite3.Connection, sql: str) -> str:
    p = plan(db, sql)
    print(f"\n[{title}]\n  {sql}\n  -> {p}")
    return p


def main() -> None:
    db = build()
    print(f"orders 表：{db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]} 行")

    by_user = "SELECT * FROM orders WHERE user_id = 7"

    # 1. 没有任何二级索引：只能全表扫描
    p = show("1 没有索引", db, by_user)
    assert p.startswith("SCAN orders"), p
    before_ms = timed(db, by_user)

    # 2. 主键本身就是一棵按 id 排好序的树
    p = show("2 按主键查", db, "SELECT * FROM orders WHERE id = 12345")
    assert "SEARCH orders USING INTEGER PRIMARY KEY (rowid=?)" in p, p
    p = show("2 按主键范围查", db, "SELECT * FROM orders WHERE id BETWEEN 100 AND 200")
    assert "SEARCH orders USING INTEGER PRIMARY KEY (rowid>? AND rowid<?)" in p, p

    # 3. 给 user_id 建二级索引
    db.execute("CREATE INDEX idx_user_id ON orders(user_id)")
    p = show("3 建索引后", db, by_user)
    assert "SEARCH orders USING INDEX idx_user_id (user_id=?)" in p, p
    after_ms = timed(db, by_user)
    print(f"  耗时：没索引 {before_ms:.3f} ms，有索引 {after_ms:.3f} ms（只供参考，不同机器不同）")
    expected = db.execute("SELECT id FROM orders NOT INDEXED WHERE user_id = 7 ORDER BY id").fetchall()
    assert db.execute("SELECT id FROM orders WHERE user_id = 7 ORDER BY id").fetchall() == expected

    # 4. 覆盖索引：要的列（user_id，以及二级索引里自带的主键 id）索引里都有，不用回表
    p = show("4 覆盖索引", db, "SELECT id, user_id FROM orders WHERE user_id = 7")
    assert "USING COVERING INDEX idx_user_id (user_id=?)" in p, p
    # 要 quantity：索引里没有，得拿 id 回主键树取整行 → 普通 USING INDEX
    p = show("4 要回表", db, "SELECT id, quantity FROM orders WHERE user_id = 7")
    assert "USING INDEX idx_user_id" in p and "COVERING" not in p, p

    # 5. 对索引列做运算 / 套函数：索引失效
    p = show("5 对列做运算", db, "SELECT * FROM orders WHERE user_id + 1 = 8")
    assert p.startswith("SCAN orders"), p
    p = show("5 把运算移到右边", db, "SELECT * FROM orders WHERE user_id = 8 - 1")
    assert "USING INDEX idx_user_id (user_id=?)" in p, p
    p = show("5 OR 连了没索引的列", db, "SELECT * FROM orders WHERE user_id = 7 OR quantity = 3")
    assert p.startswith("SCAN orders"), p

    # 6. 联合索引 (user_id, status, created_at) 与最左前缀
    db.execute("DROP INDEX idx_user_id")
    db.execute("CREATE INDEX idx_u_s_c ON orders(user_id, status, created_at)")
    cases = [
        ("user_id = 7", "(user_id=?)"),
        ("user_id = 7 AND status = 'paid'", "(user_id=? AND status=?)"),
        ("status = 'paid' AND user_id = 7", "(user_id=? AND status=?)"),  # 写的顺序无所谓
        ("user_id = 7 AND status = 'paid' AND created_at > '2026-11-01'",
         "(user_id=? AND status=? AND created_at>?)"),
        ("user_id = 7 AND created_at > '2026-11-01'", "(user_id=?)"),        # 跳过了 status
        ("user_id > 5 AND status = 'paid'", "(user_id>?)"),                   # 范围之后停下
        ("user_id = 7 AND status = 'paid' AND substr(created_at, 6, 2) = '11'",
         "(user_id=? AND status=?)"),                                         # 第三列套了函数
    ]
    for where, used in cases:
        p = show("6 联合索引", db, f"SELECT * FROM orders WHERE {where}")
        assert f"USING INDEX idx_u_s_c {used}" in p, (where, p)
    # 不带最左列 user_id：用不上
    for where in ["status = 'paid'", "user_id + 1 = 8"]:
        p = show("6 用不上", db, f"SELECT * FROM orders WHERE {where}")
        assert p.startswith("SCAN orders") and "idx_u_s_c" not in p, (where, p)
    # 查的列都在联合索引里：覆盖索引
    p = show("6 覆盖索引", db, "SELECT status, created_at FROM orders WHERE user_id = 7")
    assert "USING COVERING INDEX idx_u_s_c (user_id=?)" in p, p

    # 索引只是加速，结果必须和全表扫描一样
    where = "user_id = 7 AND created_at > '2026-11-01'"
    fast = db.execute(f"SELECT id FROM orders WHERE {where} ORDER BY id").fetchall()
    slow = db.execute(f"SELECT id FROM orders NOT INDEXED WHERE {where} ORDER BY id").fetchall()
    assert fast == slow

    print("\n全部检查通过")


if __name__ == "__main__":
    main()
