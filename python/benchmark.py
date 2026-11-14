# -*- coding: utf-8 -*-
"""
基准测试脚本
课题：多种排序算法在不同数据分布下的实测性能对比研究

运行方式：
    python benchmark.py

输出：
    results.csv  原始实测数据（规模、分布、算法、耗时、比较次数、移动/交换次数、选择器决策）
    终端同步打印汇总表。

对照对象：
    1. 四个手写固定算法：插入 / 归并 / 堆 / 快速排序；
    2. 自适应选择器：先提取有序度特征，再选择上述算法之一；
    3. 内置 sorted（Timsort）：工业级自适应排序，仅作参照，不作为赶超目标。

注意：
- 每次运行前重新生成数据（固定随机种子），结果可复现；
- 比较次数、移动/交换次数取单次运行值（同一输入下口径稳定）；
- 耗时取 REPEAT 次重复中的最优值，单位毫秒；
- 插入排序在 5 万、10 万规模下可能很慢，如超时可在 SIZES 中缩小规模；
- 选择器“是否选到最优固定算法”按本组各固定算法的实测最优耗时判定。
"""

import csv
import os
import time

from sorts import ALGORITHMS
from selector import adaptive_sort
from data_gen import generate, DISTRIBUTIONS, SIZES, REPEAT, SEED

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.join(HERE, "..", "results.csv")

HEADER = ["规模(n)", "数据分布", "分布说明", "算法", "平均耗时(ms)",
          "比较次数", "移动/交换次数", "选中算法", "是否选到最优固定算法",
          "特征(逆序比r/有序段比)", "重复次数", "随机种子"]


def _best_of_repeat(fn, data):
    """预热后重复 REPEAT 次，返回 (最优耗时ms, 末次调用输出)。"""
    fn(data)  # 预热，不计入计时
    best = None
    out = None
    for _ in range(REPEAT):
        t0 = time.perf_counter()
        out = fn(data)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        if best is None or elapsed_ms < best:
            best = elapsed_ms
    return best, out


def run_fixed(name, fn, data):
    ms, out = _best_of_repeat(fn, data)
    _, cmp_cnt, move_cnt = out
    return ms, cmp_cnt, move_cnt


def run_selector(data):
    ms, out = _best_of_repeat(lambda d: adaptive_sort(d), data)
    _, cmp_cnt, move_cnt, chosen, features = out
    return ms, cmp_cnt, move_cnt, chosen, features


def run_builtin(data):
    sorted(data)  # 预热
    best = None
    for _ in range(REPEAT):
        t0 = time.perf_counter()
        sorted(data)
        ms = (time.perf_counter() - t0) * 1000
        if best is None or ms < best:
            best = ms
    return best


def main():
    rows = []

    for size in SIZES:
        for kind, desc in DISTRIBUTIONS.items():
            data = generate(kind, size, seed=SEED)

            # 1. 四个固定算法
            fixed_times = {}
            for name, fn in ALGORITHMS.items():
                # 插入排序在超大规模下跳过，避免运行过久
                if name == "插入排序" and size > 10000:
                    continue
                ms, cmp_cnt, move_cnt = run_fixed(name, fn, data)
                fixed_times[name] = ms
                rows.append([
                    size, kind, desc, name, round(ms, 4),
                    cmp_cnt, move_cnt, "", "", "", REPEAT, SEED,
                ])
                print(f"n={size:<7} {desc:<6} {name:<5} "
                      f"{ms:10.3f} ms  比较={cmp_cnt}  移动={move_cnt}")

            # 2. 自适应选择器
            ms, cmp_cnt, move_cnt, chosen, feat = run_selector(data)
            best_fixed = min(fixed_times, key=fixed_times.get) if fixed_times else ""
            correct = "是" if chosen == best_fixed else "否"
            feat_str = f"r={feat['r']}, run={feat['run_ratio']}"
            rows.append([
                size, kind, desc, "自适应选择器", round(ms, 4),
                cmp_cnt, move_cnt, chosen, correct, feat_str, REPEAT, SEED,
            ])
            print(f"n={size:<7} {desc:<6} 自适应选择器  {ms:10.3f} ms  "
                  f"选中={chosen}  选到最优={correct}  {feat_str}")

            # 3. 内置 sorted 参照（只计时，不统计内部比较/移动）
            bms = run_builtin(data)
            rows.append([
                size, kind, desc, "内置sorted(Timsort参照)", round(bms, 4),
                "—", "—", "", "", "", REPEAT, SEED,
            ])
            print(f"n={size:<7} {desc:<6} 内置sorted参照  {bms:10.3f} ms")

    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)

    print(f"\n原始数据已写入: {os.path.abspath(OUT_CSV)}")


if __name__ == "__main__":
    main()
