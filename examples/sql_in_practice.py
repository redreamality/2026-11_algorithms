"""计算机基础第 7 课实战：SQL。讲解见 lessons/cs/07-sql.html

只用标准库 sqlite3，在内存库里建网店的三张表（users / products / orders），插入讲解页里那组数据，
把正文里出现的每条查询都执行一遍，用 assert 检查结果。

讲解页以 MySQL 为准。SQLite 和 MySQL 不一样的地方，在对应的查询旁边用注释标出来了。

运行：uv run examples/sql_in_practice.py
"""

import sqlite3

SCHEMA = """
CREATE TABLE users (
  id   INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  city TEXT                          -- 允许为 NULL：周八没填城市
);
CREATE TABLE products (
  id    INTEGER PRIMARY KEY,
  name  TEXT NOT NULL UNIQUE,
  price INTEGER NOT NULL,
  stock INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE orders (
  id         INTEGER PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id),
  product_id INTEGER NOT NULL REFERENCES products(id),
  quantity   INTEGER NOT NULL,
  created_at TEXT NOT NULL
);
"""

DATA = """
INSERT INTO users VALUES
  (1, '张三', '北京'), (2, '李四', '上海'), (3, '王五', '北京'),
  (4, '赵六', '广州'), (5, '孙七', '深圳'), (6, '周八', NULL);
INSERT INTO products VALUES
  (1, '键盘', 199, 30), (2, '鼠标', 99, 50), (3, '显示器', 999, 5),
  (4, '耳机', 299, 0), (5, 'U盘', 49, 100);
INSERT INTO orders VALUES
  (1, 1, 1, 1, '2026-11-01'), (2, 1, 2, 2, '2026-11-03'),
  (3, 2, 3, 1, '2026-11-05'), (4, 3, 2, 1, '2026-11-08'),
  (5, 4, 5, 2, '2026-10-28'), (6, 4, 2, 1, '2026-11-12'),
  (7, 5, 4, 1, '2026-11-15'), (8, 2, 5, 4, '2026-11-18');
"""


def make_db() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys = ON")  # SQLite 默认不检查外键，要手动打开；MySQL InnoDB 默认就检查
    db.executescript(SCHEMA)
    db.executescript(DATA)
    return db


def rows(db: sqlite3.Connection, sql: str) -> list[tuple]:
    return db.execute(sql).fetchall()


def names(db: sqlite3.Connection, sql: str) -> list:
    return [r[0] for r in rows(db, sql)]


def check_where(db):
    """第 4 节：WHERE、IN、BETWEEN、LIKE、ORDER BY、LIMIT、DISTINCT"""
    assert rows(db, "SELECT name, price, stock FROM products WHERE price > 100 AND stock > 0") == [
        ("键盘", 199, 30), ("显示器", 999, 5)]
    assert rows(db, "SELECT name, price, stock FROM products WHERE price > 500 OR stock = 0") == [
        ("显示器", 999, 5), ("耳机", 299, 0)]
    assert names(db, "SELECT name FROM users WHERE city IN ('北京', '广州')") == ["张三", "王五", "赵六"]
    # BETWEEN 两头都包含
    assert rows(db, "SELECT name, price FROM products WHERE price BETWEEN 99 AND 299") == [
        ("键盘", 199), ("鼠标", 99), ("耳机", 299)]
    assert names(db, "SELECT name FROM products WHERE name LIKE '%盘' ORDER BY id") == ["键盘", "U盘"]
    assert names(db, "SELECT name FROM products WHERE name LIKE '_标' ORDER BY id") == ["鼠标"]
    assert names(db, "SELECT name FROM products WHERE name LIKE '_器' ORDER BY id") == []  # _ 恰好一个字符，显示器是三个字
    assert names(db, "SELECT name FROM products WHERE name LIKE '%器' ORDER BY id") == ["显示器"]
    assert rows(db, "SELECT COUNT(1) FROM users") == [(6,)]
    assert rows(db, "SELECT name, price FROM products ORDER BY price DESC LIMIT 3") == [
        ("显示器", 999), ("耳机", 299), ("键盘", 199)]
    # LIMIT 1, 2：跳过 1 行再取 2 行（MySQL 和 SQLite 都支持这种写法，等价于 LIMIT 2 OFFSET 1）
    assert rows(db, "SELECT name, price FROM products ORDER BY price DESC LIMIT 1, 2") == [
        ("耳机", 299), ("键盘", 199)]
    assert rows(db, "SELECT name, price FROM products ORDER BY price DESC LIMIT 2 OFFSET 1") == [
        ("耳机", 299), ("键盘", 199)]
    # DISTINCT 把所有 NULL 看成一样，所以结果里有一行 NULL
    assert sorted(names(db, "SELECT DISTINCT city FROM users"), key=str) == sorted(
        ["北京", "上海", "广州", "深圳", None], key=str)


def check_null(db):
    """第 5 节：NULL 的坑"""
    assert names(db, "SELECT name FROM users WHERE city <> '北京' ORDER BY id") == ["李四", "赵六", "孙七"]
    assert names(db, "SELECT name FROM users WHERE city = NULL") == []
    assert names(db, "SELECT name FROM users WHERE city IS NULL") == ["周八"]
    assert names(db, "SELECT name FROM users WHERE city <> '北京' OR city IS NULL ORDER BY id") == [
        "李四", "赵六", "孙七", "周八"]
    assert rows(db, "SELECT NULL = NULL, NULL IS NULL, 1 + NULL") == [(None, 1, None)]


def check_group(db):
    """第 6 节：聚合、GROUP BY、HAVING"""
    assert rows(db, "SELECT COUNT(*) AS all_rows, COUNT(city) AS has_city, "
                    "COUNT(DISTINCT city) AS cities FROM users") == [(6, 5, 4)]
    assert rows(db, "SELECT SUM(stock), AVG(price), MAX(price), MIN(price) FROM products") == [(185, 329.0, 999, 49)]
    assert rows(db, "SELECT user_id, COUNT(*) AS cnt, SUM(quantity) AS qty FROM orders "
                    "GROUP BY user_id ORDER BY user_id") == [(1, 2, 3), (2, 2, 5), (3, 1, 1), (4, 2, 3), (5, 1, 1)]
    assert rows(db, "SELECT user_id, COUNT(*) AS cnt FROM orders GROUP BY user_id "
                    "HAVING COUNT(*) >= 2 ORDER BY user_id") == [(1, 2), (2, 2), (4, 2)]
    assert rows(db, "SELECT user_id, COUNT(*) AS cnt FROM orders WHERE created_at >= '2026-11-01' "
                    "GROUP BY user_id HAVING COUNT(*) >= 2 ORDER BY user_id") == [(1, 2), (2, 2)]
    # 聚合函数不能写在 WHERE 里（MySQL：Invalid use of group function）
    try:
        db.execute("SELECT user_id FROM orders WHERE COUNT(*) >= 2 GROUP BY user_id")
        raise AssertionError("聚合函数写在 WHERE 里应当报错")
    except sqlite3.OperationalError:
        pass


def check_join(db):
    """第 7 节：JOIN"""
    assert rows(db, "SELECT COUNT(*) FROM users, orders") == [(48,)]  # 笛卡尔积 6 × 8
    assert rows(db, "SELECT COUNT(*) FROM users CROSS JOIN orders") == [(48,)]
    assert rows(db, "SELECT o.id, u.name, o.quantity FROM orders o JOIN users u ON o.user_id = u.id "
                    "ORDER BY o.id") == [(1, "张三", 1), (2, "张三", 2), (3, "李四", 1), (4, "王五", 1),
                                         (5, "赵六", 2), (6, "赵六", 1), (7, "孙七", 1), (8, "李四", 4)]
    assert rows(db, "SELECT u.name, o.id FROM users u LEFT JOIN orders o ON o.user_id = u.id "
                    "ORDER BY u.id, o.id") == [("张三", 1), ("张三", 2), ("李四", 3), ("李四", 8), ("王五", 4),
                                               ("赵六", 5), ("赵六", 6), ("孙七", 7), ("周八", None)]
    assert rows(db, "SELECT u.id, u.name FROM users u LEFT JOIN orders o ON o.user_id = u.id "
                    "WHERE o.id IS NULL") == [(6, "周八")]
    # 每个用户下了几单：COUNT(o.id) 给周八 0，COUNT(*) 会错算成 1
    assert rows(db, "SELECT u.name, COUNT(o.id) AS n, COUNT(*) AS star FROM users u "
                    "LEFT JOIN orders o ON o.user_id = u.id GROUP BY u.id ORDER BY u.id") == [
        ("张三", 2, 2), ("李四", 2, 2), ("王五", 1, 1), ("赵六", 2, 2), ("孙七", 1, 1), ("周八", 0, 1)]
    # 右表的条件写在 WHERE 里，会把 LEFT JOIN 补出来的 NULL 行过滤掉，退化成内连接
    assert rows(db, "SELECT u.name, o.id FROM users u LEFT JOIN orders o ON o.user_id = u.id "
                    "WHERE o.created_at >= '2026-11-10' ORDER BY o.id") == [("赵六", 6), ("孙七", 7), ("李四", 8)]
    assert rows(db, "SELECT u.name, o.id FROM users u LEFT JOIN orders o ON o.user_id = u.id "
                    "AND o.created_at >= '2026-11-10' ORDER BY u.id") == [
        ("张三", None), ("李四", 8), ("王五", None), ("赵六", 6), ("孙七", 7), ("周八", None)]
    # RIGHT JOIN 把两张表换个位置就是 LEFT JOIN。SQLite 3.39 起才支持 RIGHT / FULL JOIN
    if sqlite3.sqlite_version_info >= (3, 39, 0):
        assert sorted(rows(db, "SELECT u.name, o.id FROM orders o RIGHT JOIN users u ON o.user_id = u.id"),
                      key=str) == sorted(rows(db, "SELECT u.name, o.id FROM users u LEFT JOIN orders o "
                                                  "ON o.user_id = u.id"), key=str)


def check_main_query(db):
    """第 8 节和动画的主查询：各城市 11 月的销售额，取前两名"""
    main = """
      SELECT u.city, SUM(o.quantity * p.price) AS total
      FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN products p ON o.product_id = p.id
      WHERE o.created_at >= '2026-11-01'
      GROUP BY u.city
      HAVING SUM(o.quantity * p.price) > 200
      ORDER BY total DESC
      LIMIT 2"""
    assert rows(db, main) == [("上海", 1195), ("北京", 496)]
    # 去掉 HAVING 和 LIMIT，看每个城市的总额
    assert rows(db, """SELECT u.city, SUM(o.quantity * p.price) AS total FROM orders o
        JOIN users u ON o.user_id = u.id JOIN products p ON o.product_id = p.id
        WHERE o.created_at >= '2026-11-01' GROUP BY u.city ORDER BY total DESC""") == [
        ("上海", 1195), ("北京", 496), ("深圳", 299), ("广州", 99)]
    # 正确写法：WHERE 里重复写表达式
    assert rows(db, "SELECT name, price * 0.8 AS sale FROM products WHERE price * 0.8 < 100") == [
        ("鼠标", 79.2), ("U盘", 39.2)]
    # 注意：SQLite 允许在 WHERE 里用 SELECT 的别名（它自己的扩展），MySQL 会报 Unknown column 'sale'
    assert rows(db, "SELECT name, price * 0.8 AS sale FROM products WHERE sale < 100") == [
        ("鼠标", 79.2), ("U盘", 39.2)]


def check_subquery_union(db):
    """第 10、11 节：子查询、IN 与 EXISTS、UNION"""
    assert names(db, "SELECT name FROM users WHERE id IN "
                     "(SELECT user_id FROM orders WHERE product_id = 2)") == ["张三", "王五", "赵六"]
    assert names(db, "SELECT name FROM users u WHERE EXISTS "
                     "(SELECT 1 FROM orders o WHERE o.user_id = u.id AND o.product_id = 2)") == ["张三", "王五", "赵六"]
    assert rows(db, "SELECT AVG(price) FROM products") == [(329.0,)]
    assert rows(db, "SELECT name, price FROM products WHERE price > (SELECT AVG(price) FROM products)") == [
        ("显示器", 999)]
    assert names(db, "SELECT u.name FROM users u WHERE NOT EXISTS "
                     "(SELECT 1 FROM orders o WHERE o.user_id = u.id)") == ["周八"]
    assert names(db, "SELECT name FROM users WHERE id NOT IN (SELECT user_id FROM orders)") == ["周八"]
    # NOT IN 的子查询里只要有一个 NULL，就一行也查不出来
    assert names(db, "SELECT name FROM users WHERE city NOT IN (SELECT city FROM users WHERE id >= 5)") == []
    union_all = names(db, "SELECT city FROM users WHERE id <= 2 UNION ALL SELECT city FROM users WHERE id IN (2, 3)")
    assert union_all == ["北京", "上海", "上海", "北京"]
    union = names(db, "SELECT city FROM users WHERE id <= 2 UNION SELECT city FROM users WHERE id IN (2, 3)")
    assert sorted(union) == ["上海", "北京"]  # UNION 去重；结果顺序不保证


def check_constraints():
    """第 3 节：约束会拦下不合法的写入"""
    db = make_db()
    bad = [
        "INSERT INTO users VALUES (1, '重复的主键', '杭州')",                 # PRIMARY KEY
        "INSERT INTO users (id, name, city) VALUES (7, NULL, '杭州')",        # NOT NULL
        "INSERT INTO products (id, name, price) VALUES (6, '鼠标', 59)",      # UNIQUE
        "INSERT INTO orders VALUES (9, 99, 1, 1, '2026-11-20')",              # FOREIGN KEY：没有 99 号用户
        "DELETE FROM users WHERE id = 1",                                     # FOREIGN KEY：张三还有订单
    ]
    for sql in bad:
        try:
            db.execute(sql)
            raise AssertionError("应当被约束拦下：" + sql)
        except sqlite3.IntegrityError:
            pass
    db.execute("INSERT INTO products (id, name, price) VALUES (6, '鼠标垫', 19)")
    assert rows(db, "SELECT stock FROM products WHERE id = 6") == [(0,)]   # DEFAULT 0


def check_delete_drop():
    """第 12 节：DELETE / TRUNCATE / DROP。SQLite 没有 TRUNCATE，不带 WHERE 的 DELETE 会被它自动优化成清空"""
    db = make_db()
    cur = db.execute("DELETE FROM orders WHERE created_at < '2026-11-01'")
    assert cur.rowcount == 1
    assert rows(db, "SELECT COUNT(*) FROM orders") == [(7,)]
    db.execute("DELETE FROM orders")
    assert rows(db, "SELECT COUNT(*) FROM orders") == [(0,)]                # 表还在，只是空了
    db.execute("DROP TABLE orders")
    try:
        db.execute("SELECT COUNT(*) FROM orders")
        raise AssertionError("DROP 之后表应当不存在")
    except sqlite3.OperationalError:
        pass
    # DELETE 是 DML，在事务里可以回滚
    db = make_db()
    db.execute("BEGIN")
    db.execute("DELETE FROM orders")
    db.execute("ROLLBACK")
    assert rows(db, "SELECT COUNT(*) FROM orders") == [(8,)]


def check_self_test(db):
    """讲解页「自测」里每道题的答案"""
    assert rows(db, "SELECT COUNT(*) FROM users u LEFT JOIN orders o ON o.user_id = u.id") == [(9,)]
    assert rows(db, "SELECT COUNT(*) FROM users u JOIN orders o ON o.user_id = u.id") == [(8,)]
    assert rows(db, "SELECT user_id FROM orders GROUP BY user_id HAVING COUNT(*) >= 2 ORDER BY user_id") == [
        (1,), (2,), (4,)]
    assert names(db, "SELECT name FROM users WHERE city <> '上海' ORDER BY id") == ["张三", "王五", "赵六", "孙七"]
    assert rows(db, "SELECT COUNT(*), COUNT(city), COUNT(DISTINCT city) FROM users") == [(6, 5, 4)]
    assert names(db, "SELECT name FROM products WHERE name LIKE '_盘' OR price BETWEEN 199 AND 299 "
                     "ORDER BY id") == ["键盘", "耳机", "U盘"]
    assert sorted(rows(db, "SELECT u.city, COUNT(*) AS n FROM orders o JOIN users u ON o.user_id = u.id "
                           "GROUP BY u.city HAVING COUNT(*) >= 2")) == sorted([("北京", 3), ("上海", 2), ("广州", 2)])


def main():
    db = make_db()
    check_self_test(db)
    check_where(db)
    check_null(db)
    check_group(db)
    check_join(db)
    check_main_query(db)
    check_subquery_union(db)
    check_constraints()
    check_delete_drop()
    print("全部查询结果和讲解页一致。")


if __name__ == "__main__":
    main()
