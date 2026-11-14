# -*- coding: utf-8 -*-
"""
排序算法实现（带比较次数与移动/交换次数统计）
课题：多种排序算法在不同数据分布下的实测性能对比研究

说明：
- 每个排序函数接收一个列表的副本，返回 (排序后列表, 比较次数, 移动/交换次数)。
- 统计口径在全项目内保持一致：
  * 比较次数：两个元素发生一次大小比较记 1 次；
  * 移动次数：元素被写入（赋值到数组位置）记 1 次；交换按两次写入计。
- 本文件只实现经典算法，不做性能上的黑魔法优化，保证对比口径一致、可复现。
"""

import copy


def _counted_bubble_sort(arr):
    """冒泡排序（基线对照，仅作参考，大规模数据不参与主对比）。"""
    a = copy.deepcopy(arr)
    n = len(a)
    cmp_cnt = 0
    swap_cnt = 0
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            cmp_cnt += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swap_cnt += 1
                swapped = True
        if not swapped:
            break
    return a, cmp_cnt, swap_cnt


def insertion_sort(arr):
    """插入排序：近有序数据下接近 O(n)。"""
    a = copy.deepcopy(arr)
    cmp_cnt = 0
    move_cnt = 0
    n = len(a)
    for i in range(1, n):
        key = a[i]
        move_cnt += 1
        j = i - 1
        while j >= 0:
            cmp_cnt += 1
            if a[j] > key:
                a[j + 1] = a[j]
                move_cnt += 1
                j -= 1
            else:
                break
        a[j + 1] = key
        move_cnt += 1
    return a, cmp_cnt, move_cnt


def merge_sort(arr):
    """归并排序：稳定排序，O(n log n)。"""
    a = copy.deepcopy(arr)
    cmp_cnt = 0
    move_cnt = 0

    def _sort(x):
        nonlocal cmp_cnt, move_cnt
        if len(x) <= 1:
            return x
        mid = len(x) // 2
        left = _sort(x[:mid])
        right = _sort(x[mid:])
        return _merge(left, right)

    def _merge(left, right):
        nonlocal cmp_cnt, move_cnt
        res = []
        i = j = 0
        while i < len(left) and j < len(right):
            cmp_cnt += 1
            if left[i] <= right[j]:
                res.append(left[i])
                move_cnt += 1
                i += 1
            else:
                res.append(right[j])
                move_cnt += 1
                j += 1
        res.extend(left[i:])
        res.extend(right[j:])
        move_cnt += len(left[i:]) + len(right[j:])
        return res

    result = _sort(a)
    return result, cmp_cnt, move_cnt


def heap_sort(arr):
    """堆排序：原地 O(n log n)，不稳定。"""
    a = copy.deepcopy(arr)
    cmp_cnt = 0
    swap_cnt = 0
    n = len(a)

    def sift_down(i, size):
        nonlocal cmp_cnt, swap_cnt
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        if l < size:
            cmp_cnt += 1
            if a[l] > a[largest]:
                largest = l
        if r < size:
            cmp_cnt += 1
            if a[r] > a[largest]:
                largest = r
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            swap_cnt += 1
            sift_down(largest, size)

    for i in range(n // 2 - 1, -1, -1):
        sift_down(i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        swap_cnt += 1
        sift_down(0, end)
    return a, cmp_cnt, swap_cnt


def quick_sort(arr):
    """
    快速排序（改进版）：三数取中选基准 + 三路划分 + 小区间切换插入排序。
    - 三数取中：在 lo、mid、hi 三处取中位数作基准，降低选到极端基准的概率；
    - 三路划分：把区间划分为 <基准、=基准、>基准 三段，相等元素不再重复参与递归，
      对含较多重复元素的数据更友好；
    - 小区间（长度 ≤ THRESHOLD）用插入排序，减少递归与基准开销。
    复杂度：平均 O(n log n)，最坏 O(n²)，不稳定；三路划分主要改善重复元素较多时的表现。
    """
    a = copy.deepcopy(arr)
    cmp_cnt = 0
    swap_cnt = 0
    THRESHOLD = 16

    def _insertion(lo, hi):
        nonlocal cmp_cnt, swap_cnt
        for i in range(lo + 1, hi + 1):
            key = a[i]
            j = i - 1
            while j >= lo:
                cmp_cnt += 1
                if a[j] > key:
                    a[j + 1] = a[j]
                    j -= 1
                else:
                    break
            a[j + 1] = key

    def _sort(lo, hi):
        nonlocal cmp_cnt, swap_cnt
        if hi - lo <= THRESHOLD:
            _insertion(lo, hi)
            return

        mid = (lo + hi) // 2
        # 三数取中：比较 lo、mid、hi，使 a[lo] ≤ a[mid] ≤ a[hi]，取 a[mid] 为基准
        cmp_cnt += 1
        if a[mid] < a[lo]:
            a[lo], a[mid] = a[mid], a[lo]
            swap_cnt += 1
        cmp_cnt += 1
        if a[hi] < a[lo]:
            a[lo], a[hi] = a[hi], a[lo]
            swap_cnt += 1
        cmp_cnt += 1
        if a[hi] < a[mid]:
            a[mid], a[hi] = a[hi], a[mid]
            swap_cnt += 1
        pivot = a[mid]

        # 三路划分：lt 左侧 < pivot，[lt, gt] 内 == pivot，gt 右侧 > pivot
        lt, i, gt = lo, lo, hi
        while i <= gt:
            cmp_cnt += 1
            if a[i] < pivot:
                a[i], a[lt] = a[lt], a[i]
                swap_cnt += 1
                lt += 1
                i += 1
            elif a[i] > pivot:
                a[i], a[gt] = a[gt], a[i]
                swap_cnt += 1
                gt -= 1
            else:
                i += 1

        if lo < lt - 1:
            _sort(lo, lt - 1)
        if gt + 1 < hi:
            _sort(gt + 1, hi)

    if len(a) > 1:
        _sort(0, len(a) - 1)
    return a, cmp_cnt, swap_cnt


# 参与主对比的算法注册表
ALGORITHMS = {
    "插入排序": insertion_sort,
    "归并排序": merge_sort,
    "堆排序": heap_sort,
    "快速排序": quick_sort,
}
