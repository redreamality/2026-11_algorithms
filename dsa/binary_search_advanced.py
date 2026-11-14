"""第 32 课：二分进阶。讲解见 lessons/32-binary-search-advanced.html

规则：
- 每道题都要用二分写，目标是 O(log n)（二分答案的题是 O(n · log 答案范围)）。
  不要用 bisect 模块，也不要用 list.index 或从头扫一遍。
- 推荐的写法（第 6 课 lower_bound 的推广）：找“第一个满足条件的位置”。
  left 取答案可能的最小值，right 取答案可能的最大值（找下标时取 len(nums)，表示“一个都不满足”），
  循环条件 left < right；middle 满足条件就 right = middle，不满足就 left = middle + 1；
  循环结束时 left == right，就是答案。
- 搜索旋转排序数组这题用闭区间 [left, right]、循环条件 left <= right 更顺手，讲解里会说为什么。
- 变量名写完整：left、right、middle，不要写 l、r、m。
- 自查：uv run dsa/binary_search_advanced.py ，会打印每道题的「输入、期望、实际」。
"""


def first_position(nums: list[int], target: int) -> int:
    """target 在有序数组 nums 里第一次出现的下标，没有就返回 -1。

    例子：nums = [5, 7, 7, 8, 8, 10]，target = 8 → 3。
    思路：找“第一个 nums[i] >= target 的下标”（第 6 课的 lower_bound），
    再检查这个位置上是不是真的等于 target。O(log n)。
    """
    raise NotImplementedError


def last_position(nums: list[int], target: int) -> int:
    """target 在有序数组 nums 里最后一次出现的下标，没有就返回 -1。

    例子：nums = [5, 7, 7, 8, 8, 10]，target = 8 → 4。
    思路：找“第一个 nums[i] > target 的下标”，它的前一个位置就是最后一个 target（如果有的话）。O(log n)。
    """
    raise NotImplementedError


def search_range(nums: list[int], target: int) -> list[int]:
    """LeetCode 34 · 在排序数组中查找元素的第一个和最后一个位置。

    返回 [第一次出现的下标, 最后一次出现的下标]，没有就返回 [-1, -1]。
    例子：nums = [5, 7, 7, 8, 8, 10]，target = 8 → [3, 4]；target = 6 → [-1, -1]。
    思路：调用上面两个函数。O(log n)。
    """
    raise NotImplementedError


def search_rotated(nums: list[int], target: int) -> int:
    """LeetCode 33 · 搜索旋转排序数组。

    题意：一个升序、元素互不相同的数组，在某个位置被“切了一刀、两段对调”，
    例如 [0, 1, 2, 4, 5, 6, 7] 变成 [4, 5, 6, 7, 0, 1, 2]。在里面找 target 的下标，没有返回 -1。
    例子：nums = [4, 5, 6, 7, 0, 1, 2]，target = 0 → 4；target = 3 → -1。

    思路：闭区间 [left, right]。取 middle 之后，[left, middle] 和 [middle, right] 两半里
    至少有一半是完整有序的：nums[left] <= nums[middle] 说明左半边有序，否则右半边有序。
    target 落在有序那半边的数值范围里，就去那半边找；否则去另一半。O(log n)。
    """
    raise NotImplementedError


def find_peak_element(nums: list[int]) -> int:
    """LeetCode 162 · 寻找峰值。

    题意：峰值是严格大于左右邻居的元素。可以认为 nums[-1] 和 nums[n] 都是负无穷，
    相邻元素互不相等。返回任意一个峰值的下标。
    例子：[1, 2, 3, 1] → 2；[1, 2, 1, 3, 5, 6, 4] → 1 或 5 都对。

    思路：比较 nums[middle] 和 nums[middle + 1]。
    如果 nums[middle] > nums[middle + 1]，说明往左是“下坡的起点”，[left, middle] 里一定有峰，right = middle；
    否则右边在上坡，[middle + 1, right] 里一定有峰，left = middle + 1。O(log n)。
    """
    raise NotImplementedError


def hours_needed(piles: list[int], eating_speed: int) -> int:
    """按每小时吃 eating_speed 根的速度吃完所有香蕉要几个小时。

    每小时只能吃一堆；一堆不够 eating_speed 根，吃完这堆这一小时就结束了。
    所以一堆 pile 要 ceil(pile / eating_speed) 小时，可以写成 (pile + eating_speed - 1) // eating_speed。
    例子：piles = [3, 6, 7, 11]，eating_speed = 4 → 1 + 2 + 2 + 3 = 8。O(n)。
    """
    raise NotImplementedError


def min_eating_speed(piles: list[int], hours: int) -> int:
    """LeetCode 875 · 爱吃香蕉的珂珂。

    题意：要在 hours 小时内吃完所有香蕉，最小的整数速度是多少（保证 hours >= len(piles)）。
    例子：piles = [3, 6, 7, 11]，hours = 8 → 4；piles = [30, 11, 23, 4, 20]，hours = 5 → 30。

    思路（二分答案）：速度越快，用时越少，所以“这个速度来得及吗”是一串 False……False True……True。
    答案一定在 [1, max(piles)] 里（速度等于最大那堆时，每堆 1 小时，一定来得及）。
    二分找第一个来得及的速度，每次判断调用 hours_needed。O(n · log max(piles))。
    """
    raise NotImplementedError


def days_needed(weights: list[int], capacity: int) -> int:
    """船每天最多装 capacity 重的货，按顺序装（不能调换顺序），要几天运完。

    从第一件开始往当天的船上装，装不下了就换到下一天。假设 capacity >= max(weights)。
    例子：weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]，capacity = 15
    → [1, 2, 3, 4, 5]、[6, 7]、[8]、[9]、[10]，共 5 天。O(n)。
    """
    raise NotImplementedError


def ship_within_days(weights: list[int], days: int) -> int:
    """LeetCode 1011 · 在 D 天内送达包裹的能力。

    题意：按顺序运货，要在 days 天内运完，船的最小载重是多少。
    例子：weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]，days = 5 → 15。

    思路（二分答案）：载重越大，天数越少。答案在 [max(weights), sum(weights)] 里：
    载重小于最重的那件就永远装不上；载重等于总重时一天就能运完。
    二分找第一个“days_needed(weights, capacity) <= days”的 capacity。O(n · log sum(weights))。
    """
    raise NotImplementedError


# ---------- 自查 ----------

def report_case(title: str, input_text: str, expected, compute, is_correct=None) -> None:
    """is_correct：答案不唯一时，用它判断实际结果对不对；不给就和 expected 直接比较。"""
    try:
        actual = compute()
    except NotImplementedError:
        print(f"[还没实现] {title}  输入：{input_text}  期望：{expected}")
        return
    passed = is_correct(actual) if is_correct else actual == expected
    print(f"[{'通过' if passed else '不对'}] {title}  输入：{input_text}  期望：{expected}  实际：{actual}")


def is_peak_index(nums: list[int], index) -> bool:
    if not isinstance(index, int) or not 0 <= index < len(nums):
        return False
    left_neighbor = nums[index - 1] if index > 0 else float("-inf")
    right_neighbor = nums[index + 1] if index + 1 < len(nums) else float("-inf")
    return left_neighbor < nums[index] > right_neighbor


if __name__ == "__main__":
    SORTED_NUMS = [5, 7, 7, 8, 8, 10]
    for nums, target, expected in [(SORTED_NUMS, 8, 3), (SORTED_NUMS, 7, 1), (SORTED_NUMS, 6, -1), ([], 1, -1)]:
        report_case("first_position", f"nums={nums}, target={target}", expected, lambda: first_position(nums, target))
    for nums, target, expected in [(SORTED_NUMS, 8, 4), (SORTED_NUMS, 10, 5), (SORTED_NUMS, 11, -1), ([], 1, -1)]:
        report_case("last_position", f"nums={nums}, target={target}", expected, lambda: last_position(nums, target))
    for nums, target, expected in [(SORTED_NUMS, 8, [3, 4]), (SORTED_NUMS, 6, [-1, -1]), ([], 0, [-1, -1]), ([1], 1, [0, 0])]:
        report_case("search_range", f"nums={nums}, target={target}", expected, lambda: search_range(nums, target))

    for nums, target, expected in [
        ([4, 5, 6, 7, 0, 1, 2], 0, 4), ([4, 5, 6, 7, 0, 1, 2], 3, -1), ([1], 0, -1),
        ([4, 5, 6, 7, 9, 12, 0, 1, 2], 1, 7), ([3, 1], 1, 1), ([1, 3], 3, 1),
    ]:
        report_case("search_rotated", f"nums={nums}, target={target}", expected, lambda: search_rotated(nums, target))

    for nums, expected_text in [([1, 2, 3, 1], "2"), ([1, 2, 1, 3, 5, 6, 4], "1 或 5"), ([1], "0"), ([3, 2, 1], "0"), ([1, 2], "1")]:
        report_case("find_peak_element", f"nums={nums}", expected_text, lambda: find_peak_element(nums),
                    lambda index: is_peak_index(nums, index))

    for piles, eating_speed, expected in [([3, 6, 7, 11], 4, 8), ([3, 6, 7, 11], 11, 4), ([3, 6, 7, 11], 1, 27)]:
        report_case("hours_needed", f"piles={piles}, eating_speed={eating_speed}", expected,
                    lambda: hours_needed(piles, eating_speed))
    for piles, hours, expected in [([3, 6, 7, 11], 8, 4), ([30, 11, 23, 4, 20], 5, 30), ([30, 11, 23, 4, 20], 6, 23), ([1], 1, 1)]:
        report_case("min_eating_speed", f"piles={piles}, hours={hours}", expected, lambda: min_eating_speed(piles, hours))

    ONE_TO_TEN = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    for weights, capacity, expected in [(ONE_TO_TEN, 15, 5), (ONE_TO_TEN, 55, 1), ([3, 2, 2, 4, 1, 4], 6, 3)]:
        report_case("days_needed", f"weights={weights}, capacity={capacity}", expected,
                    lambda: days_needed(weights, capacity))
    for weights, days, expected in [(ONE_TO_TEN, 5, 15), ([3, 2, 2, 4, 1, 4], 3, 6), ([1, 2, 3, 1, 1], 4, 3), ([5], 1, 5)]:
        report_case("ship_within_days", f"weights={weights}, days={days}", expected, lambda: ship_within_days(weights, days))
