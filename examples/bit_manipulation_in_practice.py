"""第 39 课实战：位运算在 Python 项目里出现在哪。

1. 权限、开关、选项组合 → enum.Flag。每个成员占一位，| 组合、& 判断、~ 去掉，比一堆布尔字段省事。
2. 数一个整数里有几个 1 → int.bit_count()（Python 3.10+），不用自己写循环。
3. IP 地址和子网掩码 → 标准库 ipaddress。“这个 IP 在不在网段里”底层就是 ip & 掩码 == 网段地址。
4. 状态压缩：元素不超过二三十个时，用一个整数表示一个集合（第 k 位是 1 表示含第 k 个元素），
   并集是 |，交集是 &，判断“全都覆盖”是 == 全 1。比 set 快，还能当字典的键、当 DP 的下标。

运行：uv run examples/bit_manipulation_in_practice.py
"""

import ipaddress
from enum import Flag, auto


class Permission(Flag):
    READ = auto()  # 0b001
    WRITE = auto()  # 0b010
    DELETE = auto()  # 0b100
    EDITOR = READ | WRITE
    ADMIN = READ | WRITE | DELETE


def can(granted: Permission, needed: Permission) -> bool:
    """needed 里的每一位 granted 都要有：(granted & needed) == needed。Flag 的 in 就是这么实现的。"""
    return needed in granted


def ip_in_network(ip_text: str, network_text: str) -> bool:
    """手写版：IP 与掩码按位与，结果等于网段地址就在网段里。和 ipaddress 的 in 结果一致。"""
    network = ipaddress.ip_network(network_text)
    ip_as_int = int(ipaddress.ip_address(ip_text))
    return ip_as_int & int(network.netmask) == int(network.network_address)


def smallest_team(required_skills: list[str], candidates: dict[str, list[str]]) -> list[str]:
    """状态压缩：选最少的人，让大家的技能合起来覆盖 required_skills。

    每个技能对应一位，每个人的技能变成一个整数。枚举所有人的子集（第 k 位是 1 表示选第 k 个人），
    把选中的人的技能 | 起来，等于“全 1”就覆盖了。人数为 n 时共 2^n 个子集，适合 n 不超过 20 左右。
    """
    skill_bit = {skill: 1 << position for position, skill in enumerate(required_skills)}
    all_skills = (1 << len(required_skills)) - 1
    names = list(candidates)
    skill_masks = [sum(skill_bit[skill] for skill in candidates[name] if skill in skill_bit) for name in names]

    best_team_mask = None
    for team_mask in range(1 << len(names)):
        covered = 0
        for person_index in range(len(names)):
            if team_mask >> person_index & 1:
                covered |= skill_masks[person_index]
        if covered == all_skills and (best_team_mask is None
                                      or team_mask.bit_count() < best_team_mask.bit_count()):
            best_team_mask = team_mask
    if best_team_mask is None:
        return []
    return [name for person_index, name in enumerate(names) if best_team_mask >> person_index & 1]


def main() -> None:
    user = Permission.READ | Permission.WRITE
    assert user == Permission.EDITOR
    assert can(user, Permission.READ) and not can(user, Permission.DELETE)
    assert can(Permission.ADMIN, Permission.EDITOR)
    user &= ~Permission.WRITE  # 收回写权限
    assert user == Permission.READ
    print("编辑者的权限值：", Permission.EDITOR.value, "=", bin(Permission.EDITOR.value))

    assert (0b1011_0110).bit_count() == 5
    feature_switches = 0b1010_0001  # 第 0、5、7 号功能开着
    assert feature_switches.bit_count() == 3
    assert feature_switches >> 5 & 1 == 1
    print("打开的功能个数：", feature_switches.bit_count())

    network = ipaddress.ip_network("192.168.1.0/24")
    assert ipaddress.ip_address("192.168.1.77") in network
    assert ip_in_network("192.168.1.77", "192.168.1.0/24")
    assert not ip_in_network("192.168.2.1", "192.168.1.0/24")
    assert ip_in_network("10.1.2.3", "10.0.0.0/8") == (ipaddress.ip_address("10.1.2.3") in ipaddress.ip_network("10.0.0.0/8"))
    print("192.168.1.0/24 的掩码：", network.netmask, "可用地址", network.num_addresses - 2, "个")

    team = smallest_team(
        ["前端", "后端", "数据库", "运维"],
        {"alice": ["前端"], "bob": ["后端", "数据库"], "carol": ["前端", "运维"], "dave": ["运维", "数据库"]},
    )
    assert team == ["bob", "carol"]
    assert smallest_team(["前端", "安全"], {"alice": ["前端"]}) == []
    print("覆盖全部技能的最小团队：", team)


if __name__ == "__main__":
    main()
