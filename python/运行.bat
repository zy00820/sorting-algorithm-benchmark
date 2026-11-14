@echo off
rem 双击本文件即可运行基准测试；结果输出到上一级文件夹 results.csv
cd /d %~dp0
python benchmark.py
if errorlevel 1 (
    echo python 命令不可用，尝试 python3 ...
    python3 benchmark.py
)
pause
