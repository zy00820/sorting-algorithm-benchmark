# -*- coding: utf-8 -*-
"""
自适应排序选择器（L3 升级模块）
课题：多种排序算法在不同数据分布下的实测性能对比研究

思路：
- 不预先知道数据分布，仅依据输入数组自身的有序度与重复度特征，挑选一种已实现的排序算法；
- 特征提取在原数组上只读完成，O(n)，其开销单独计入选择器总耗时；
- 本模块不发明新的排序算法，创新点在于“多特征 + 规则化选择策略”及对照实测。

特征说明：
- 相邻逆序比 r：a[i] > a[i+1] 的相邻对数 /(n-1)，越接近 0 越有序；
- 有序段占比 run_ratio：连续非递减段数量 / n，段越少越有序；
- 相邻相等比 dup_ratio：a[i] == a[i+1] 的相邻对数 /(n-1)，越高说明重复元素越多，
  此时三路划分的快速排序更有优势。

阈值说明：
- 下列阈值为初始标定值，需在第一份实测样本上复核，并在研究日志中记录调整过程；
- 验证结论须在另一份随机种子的数据上得出，避免用同一批数据既调阈值又下结论。
"""

from sorts import insertion_sort, merge_sort, quick_sort

# ---- 决策阈值（初始值，待实测标定）----
SMALL_N = 16            # 规模不超过该值时直接用插入排序
NEAR_SORTED_R = 0.05    # 相邻逆序比 ≤ 该值，视为近有序
REVERSED_R = 0.90       # 相邻逆序比 ≥ 该值，视为接近逆序

# 选择器可调用的固定算法（堆排序仅作对照，不进入选择策略）
_CANDIDATES = {
    "插入排序": insertion_sort,
    "归并排序": merge_sort,
    "快速排序": quick_sort,
}


def extract_features(arr):
    """
    只读提取特征，返回 (n, 相邻逆序比 r, 有序段占比 run_ratio, 相邻相等比 dup_ratio)。
    """
    n = len(arr)
    if n <= 1:
        return n, 0.0, 1.0, 0.0

    inv_adj = 0
    eq_adj = 0
    runs = 1
    for i in range(1, n):
        if arr[i] < arr[i - 1]:
            inv_adj += 1
            runs += 1
        elif arr[i] == arr[i - 1]:
            eq_adj += 1

    r = inv_adj / (n - 1)
    run_ratio = runs / n
    dup_ratio = eq_adj / (n - 1)
    return n, r, run_ratio, dup_ratio


def choose_algorithm(n, r, run_ratio, dup_ratio):
    """
    根据特征按规则选择算法，返回算法名。
    - 规模很小：插入排序；
    - 近有序（r 很低）：插入排序；
    - 接近逆序（r 很高）：归并排序；
    - 其余（含重复元素较多的情况）：三路划分快速排序。
    """
    if n <= SMALL_N:
        return "插入排序"
    if r <= NEAR_SORTED_R:
        return "插入排序"
    if r >= REVERSED_R:
        return "归并排序"
    return "快速排序"


def adaptive_sort(arr):
    """
    自适应选择排序：先提取特征并决策，再调用对应固定算法。
    返回：(排序后列表, 比较次数, 移动/交换次数, 选中算法, 特征字典)
    特征字典含 n、r、run_ratio、dup_ratio。
    """
    n, r, run_ratio, dup_ratio = extract_features(arr)
    chosen = choose_algorithm(n, r, run_ratio, dup_ratio)
    fn = _CANDIDATES[chosen]
    result, cmp_cnt, move_cnt = fn(arr)
    features = {
        "n": n,
        "r": round(r, 4),
        "run_ratio": round(run_ratio, 4),
        "dup_ratio": round(dup_ratio, 4),
    }
    return result, cmp_cnt, move_cnt, chosen, features
