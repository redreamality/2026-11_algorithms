"""计算机基础第 9 课实战：用标准库 sqlite3 看事务的原子性，以及怎么防超卖。

1. 原子性：下单 = 扣库存 + 写订单 + 扣余额。中途出错就 ROLLBACK，前面做过的步骤全部撤销。
2. 防超卖：商品只剩 1 件，两个连接同时来买。
   - 「先读、在程序里减 1、再写回」：两边都卖出去了（丢失修改）。
   - UPDATE … SET stock = stock - 1 WHERE id = ? AND stock > 0：让数据库去算，第二个人改了 0 行。
   - 乐观锁：多一列 version，写的时候核对版本号，改了 0 行就说明有人先改了。

注意：SQLite 的隔离模型和 MySQL InnoDB 不同。它没有行锁，写时锁住整个数据库文件，
同一时刻只有一个事务能写；也不能设置读已提交、可重复读这些级别。
所以隔离级别只在讲解页的动画里演示，这里只演示和数据库种类无关的两种做法。

运行：uv run examples/transaction_in_practice.py
"""

import sqlite3
import tempfile
from pathlib import Path


def connect(path: Path) -> sqlite3.Connection:
    # isolation_level=None：不让 sqlite3 模块自动开事务，BEGIN / COMMIT / ROLLBACK 都由我们自己写
    return sqlite3.connect(path, isolation_level=None)


def create_shop(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, balance INTEGER NOT NULL);
        CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER NOT NULL,
                               stock INTEGER NOT NULL, version INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
                             product_id INTEGER, quantity INTEGER);
        INSERT INTO users VALUES (1, '用户 1', 300), (2, '用户 2', 50);
        INSERT INTO products VALUES (42, '保温杯', 99, 10, 1);
    """)


def one(conn: sqlite3.Connection, sql: str, *args):
    return conn.execute(sql, args).fetchone()[0]


class OrderFailed(Exception):
    pass


def place_order(conn: sqlite3.Connection, user_id: int, product_id: int) -> None:
    """下单的三步放在一个事务里：任何一步失败都整体回滚。"""
    conn.execute("BEGIN")
    try:
        price = one(conn, "SELECT price FROM products WHERE id = ?", product_id)
        # ① 扣库存
        if conn.execute("UPDATE products SET stock = stock - 1 WHERE id = ? AND stock > 0",
                        (product_id,)).rowcount == 0:
            raise OrderFailed("卖完了")
        # ② 写订单
        conn.execute("INSERT INTO orders (user_id, product_id, quantity) VALUES (?, ?, 1)",
                     (user_id, product_id))
        # ③ 扣余额：余额不够时改了 0 行
        if conn.execute("UPDATE users SET balance = balance - ? WHERE id = ? AND balance >= ?",
                        (price, user_id, price)).rowcount == 0:
            raise OrderFailed("余额不够")
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")  # 撤销 ① 和 ②
        raise


def demo_atomicity(path: Path) -> None:
    conn = connect(path)
    create_shop(conn)

    place_order(conn, user_id=1, product_id=42)
    assert one(conn, "SELECT stock FROM products WHERE id = 42") == 9
    assert one(conn, "SELECT balance FROM users WHERE id = 1") == 201
    assert one(conn, "SELECT COUNT(*) FROM orders") == 1
    print("用户 1 下单成功：stock 10 → 9，余额 300 → 201，订单 1 条")

    try:
        place_order(conn, user_id=2, product_id=42)  # 余额只有 50，第 ③ 步会失败
    except OrderFailed as e:
        print(f"用户 2 下单失败（{e}），已回滚")
    else:
        raise AssertionError("用户 2 余额不够，应该失败")
    assert one(conn, "SELECT stock FROM products WHERE id = 42") == 9  # 第 ① 步扣的库存被撤销了
    assert one(conn, "SELECT COUNT(*) FROM orders") == 1               # 第 ② 步写的订单也没了
    assert one(conn, "SELECT balance FROM users WHERE id = 2") == 50
    print("回滚后：stock 还是 9，订单还是 1 条，用户 2 余额还是 50（原子性）")
    conn.close()


def demo_oversell(path: Path) -> None:
    """商品 42 只剩 1 件，连接 a、b 代表两个同时处理下单的线程，语句交错执行。"""
    setup = connect(path)
    create_shop(setup)
    reset = lambda: setup.execute("UPDATE products SET stock = 1, version = 1 WHERE id = 42")
    a, b = connect(path), connect(path)

    # 错误写法：先读、在程序里减 1、再写回
    reset()
    stock_a = one(a, "SELECT stock FROM products WHERE id = 42")  # 1
    stock_b = one(b, "SELECT stock FROM products WHERE id = 42")  # 1，A 还没写回
    sold = 0
    for conn, seen in ((a, stock_a), (b, stock_b)):
        if seen > 0:
            conn.execute("UPDATE products SET stock = ? WHERE id = 42", (seen - 1,))
            sold += 1
    assert sold == 2 and one(setup, "SELECT stock FROM products WHERE id = 42") == 0
    print("先读再写回：卖出 2 件，库存却只从 1 变成 0（丢失修改，超卖了 1 件）")

    # 正确写法一：让数据库去算，并带上 stock > 0
    reset()
    sql = "UPDATE products SET stock = stock - 1 WHERE id = ? AND stock > 0"
    assert a.execute(sql, (42,)).rowcount == 1
    assert b.execute(sql, (42,)).rowcount == 0  # 改了 0 行：卖完了
    assert one(setup, "SELECT stock FROM products WHERE id = 42") == 0
    print("stock = stock - 1 AND stock > 0：A 改了 1 行，B 改了 0 行，只卖出 1 件")

    # 正确写法二：乐观锁，写的时候核对版本号
    reset()
    read = "SELECT stock, version FROM products WHERE id = 42"
    write = "UPDATE products SET stock = ?, version = version + 1 WHERE id = 42 AND version = ?"
    stock_a, version_a = a.execute(read).fetchone()  # (1, 1)
    stock_b, version_b = b.execute(read).fetchone()  # (1, 1)
    assert a.execute(write, (stock_a - 1, version_a)).rowcount == 1
    assert b.execute(write, (stock_b - 1, version_b)).rowcount == 0  # 版本号对不上：有人先改了
    stock_b, version_b = b.execute(read).fetchone()                  # 重读
    assert (stock_b, version_b) == (0, 2)  # 库存为 0，B 告诉顾客卖完了
    print("乐观锁：A 写成功（version 1 → 2），B 写了 0 行，重读发现已卖完")

    for conn in (a, b, setup):
        conn.close()


def main() -> None:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        demo_atomicity(Path(tmp) / "atomic.db")
        demo_oversell(Path(tmp) / "oversell.db")
    print("全部检查通过")


if __name__ == "__main__":
    main()
