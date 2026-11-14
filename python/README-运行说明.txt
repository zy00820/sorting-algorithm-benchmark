排序算法基准测试 · 运行说明
====================================

一、环境准备（只需一次）
1. 安装 Python 3.10 或以上版本：https://www.python.org/downloads/
   Windows 安装时务必勾选 “Add Python to PATH”。
2. 验证：打开终端（Windows 用 PowerShell/CMD，Mac 用终端），输入
       python --version
   能显示版本号即可；Windows 若提示找不到命令，改用 python3 --version。
3. 本项目仅使用 Python 标准库，不需要 pip 安装任何第三方包。

二、文件说明
  sorts.py      四种排序算法实现（插入/归并/堆/快速排序），带比较、移动次数统计
  data_gen.py   四类数据分布生成（固定随机种子，可复现）
  selector.py   自适应选择器：提取有序度特征，按规则从候选算法中选择一种执行
  benchmark.py  基准测试主程序：计时、计数，导出 results.csv

三、运行步骤
方式一（Windows 双击运行，推荐不熟命令行时使用）：
  直接双击 python 文件夹里的 运行.bat，等待跑完，窗口停住后按任意键关闭。

方式二（命令行）：
1. 解压后进入 python 文件夹，在终端中执行：
       cd 解压路径/python
2. 运行测试：
       python benchmark.py
   （Windows 不行就换 python3 benchmark.py）
3. 运行结束后，在 python 文件夹的上一级生成 results.csv，即原始测试数据。

四、测试内容
  数据分布：随机排列 / 近乎有序 / 完全逆序 / 含少量乱序
  对照对象：四种固定算法、自适应选择器、内置 sorted（Timsort，仅作参照）
  评价指标：运行时间(ms)、比较次数、移动/交换次数；
            选择器另记录选中算法、是否选到最优固定算法、有序度特征。
  测试规模与重复次数在 data_gen.py 顶部的 SIZES、REPEAT 中调整。

五、选择器阈值（需复核）
  selector.py 顶部的 SMALL_N、NEAR_SORTED_R、REVERSED_R 为初始标定值。
  先在默认种子样本上跑一遍，结合结果复核阈值，并在研究日志中记录调整原因；
  验证结论应在 data_gen.py 中的 VALIDATION_SEED 样本上得出，避免同一批数据既调参又下结论。

六、跑完之后
1. 打开 results.csv，将数值回填到研究报告第 5 章表格；
2. 依据数据绘制“规模—耗时”折线图与同规模跨算法对比柱状图；
3. 若逆序数据下插入排序运行过久，可在 data_gen.py 的 SIZES 中删去较大规模。

七、常见问题
  python 不是内部或外部命令：重装 Python 并勾选 Add to PATH，或改用 python3。
  程序卡住很久：多为插入排序在大数据量下 O(n²)，缩小 SIZES 规模即可。
  终端中文乱码：不影响 results.csv 中的数据本身。

八、口径提醒
  比较次数：两元素发生一次大小比较记 1 次；
  移动/交换次数：统计口径以 sorts.py 内实现为准，全项目保持一致。
  排序算法为经典公开算法；本项目创新点在有序度特征驱动的选择策略与对照实测，
  不要写成“发明了新排序算法”。内置 sorted 为工业级实现，仅作参照，不作为赶超目标。
