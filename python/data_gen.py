# -*- coding: utf-8 -*-
"""
测试数据生成器
课题：多种排序算法在不同数据分布下的实测性能对比研究

四类数据分布：
1. random        随机排列
2. nearly_sorted 近乎有序（先排序，再交换少量随机位置）
3. reversed      完全逆序
4. few_unsorted  含少量乱序（基本有序，随机扰动少量元素）

固定随机种子，保证每次生成的数据一致、实验可复现。
"""

import random

SEED = 20260721

# 验证用种子：阈值在 SEED 样本上标定后，在该种子样本上做留出验证，避免同一批数据既调参又下结论。
VALIDATION_SEED = 20260901


def _shuffle_swap(a, k, rng):
    """在已排序数组上随机交换 k 对元素。"""
    n = len(a)
    for _ in range(k):
        i = rng.randrange(n)
        j = rng.randrange(n)
        a[i], a[j] = a[j], a[i]
    return a


def generate(kind, size, seed=SEED):
    """
    生成指定分布、指定规模的整数数组（返回新列表）。
    kind: random / nearly_sorted / reversed / few_unsorted
    """
    rng = random.Random(seed)
    base = list(range(size))

    if kind == "random":
        rng.shuffle(base)
        return base

    if kind == "reversed":
        return list(range(size - 1, -1, -1))

    if kind == "nearly_sorted":
        # 约 2% 的位置被交换，整体仍保持有序趋势
        swaps = max(1, size // 50)
        return _shuffle_swap(base, swaps, rng)

    if kind == "few_unsorted":
        # 约 1% 的元素被随机打乱到别处，其余保持有序
        perturb = max(1, size // 100)
        for _ in range(perturb):
            idx = rng.randrange(size)
            base[idx] = rng.randrange(size)
        return base

    raise ValueError(f"未知数据分布: {kind}")


DISTRIBUTIONS = {
    "random": "随机排列",
    "nearly_sorted": "近乎有序",
    "reversed": "完全逆序",
    "few_unsorted": "含少量乱序",
}

# 测试规模（元素个数）。可按本机性能增删。
SIZES = [1000, 5000, 10000, 50000, 100000]

# 每组重复次数，取平均以抵消偶然波动
REPEAT = 3
