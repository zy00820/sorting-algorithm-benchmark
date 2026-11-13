# -*- coding: utf-8 -*-
"""
基准测试脚本
课题：多种排序算法在不同数据分布下的实测性能对比研究

运行方式：
    python benchmark.py

输出：
    results.csv  原始实测数据（规模、分布、算法、平均耗时、比较次数、移动/交换次数）
    终端同步打印汇总表。

注意：
- 每次运行前会重新生成数据（固定随机种子），结果可复现；
- 比较次数、移动/交换次数取单次运行值（同一输入下口径稳定）；
- 耗时取 REPEAT 次重复的平均值，单位毫秒；
- 插入排序在 5 万、10 万规模下可能很慢，如超时可在 SIZES 中缩小规模。
"""

import csv
import os
import time

from sorts import ALGORITHMS
from data_gen import generate, DISTRIBUTIONS, SIZES, REPEAT, SEED

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.join(HERE, "..", "results.csv")


def run_one(algo_name, algo_fn, data):
    # 预热：首次调用可能触发解释器优化，不计入计时
    algo_fn(data)

    best = None
    cmp_cnt = 0
    move_cnt = 0
    for _ in range(REPEAT):
        t0 = time.perf_counter()
        _, cmp_cnt, move_cnt = algo_fn(data)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        if best is None or elapsed_ms < best:
            best = elapsed_ms
    return best, cmp_cnt, move_cnt


def main():
    rows = []
    header = ["规模(n)", "数据分布", "分布说明", "算法", "平均耗时(ms)",
              "比较次数", "移动/交换次数", "重复次数", "随机种子"]

    for size in SIZES:
        for kind, desc in DISTRIBUTIONS.items():
            data = generate(kind, size, seed=SEED)
            for algo_name, algo_fn in ALGORITHMS.items():
                # 插入排序在超大规模下跳过，避免运行过久
                if algo_name == "插入排序" and size > 10000:
                    continue
                ms, cmp_cnt, move_cnt = run_one(algo_name, algo_fn, data)
                rows.append([
                    size, kind, desc, algo_name,
                    round(ms, 4), cmp_cnt, move_cnt, REPEAT, SEED,
                ])
                print(f"n={size:<7} {desc:<6} {algo_name:<5} "
                      f"{ms:10.3f} ms  比较={cmp_cnt}  移动={move_cnt}")

    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"\n原始数据已写入: {os.path.abspath(OUT_CSV)}")


if __name__ == "__main__":
    main()
