#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全国青少年体育赛事数据分析 — 主入口
一键运行：数据清洗 → 核心分析 → 人口经济分析 → 长三角分析 → 可视化图表

使用方法:
    python main.py                # 运行全流程
    python main.py --clean-only   # 仅执行数据清洗
    python main.py --viz-only     # 仅生成图表（需先完成清洗）

依赖:
    pip install -r requirements.txt

数据准备:
    将原始Excel文件放入 data/ 目录
"""

import sys
import os

# 将项目根目录加入 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import setup_chinese_font, ensure_dirs, RAW_DATA_PATH, CLEANED_DATA_PATH
from src.data_cleaning import run_cleaning
from src.analysis_core import run_core_analysis
from src.analysis_economy import run_economy_analysis
from src.analysis_yrd import run_yrd_analysis
from src.visualization import run_all_visualizations


def check_data_file():
    """检查原始数据文件是否存在"""
    if not os.path.exists(RAW_DATA_PATH):
        print(f"[错误] 原始数据文件不存在: {RAW_DATA_PATH}")
        print(f"  请将Excel文件放入 data/ 目录")
        print(f"  文件名应为: 全国群众体育赛事、青少年体育赛事、马拉松赛事信息.xlsx")
        return False
    return True


def load_cleaned_data():
    """加载清洗后的数据"""
    if not os.path.exists(CLEANED_DATA_PATH):
        print("[提示] 未找到清洗后数据，正在执行清洗...")
        return run_cleaning()

    print(f"[数据加载] 读取清洗后数据: {CLEANED_DATA_PATH}")
    import pandas as pd
    df = pd.read_csv(CLEANED_DATA_PATH, encoding="utf-8-sig")
    print(f"  数据: {len(df)} 条, {df.shape[1]} 列")
    return df


def run_full_pipeline():
    """运行完整分析流程"""
    print("=" * 70)
    print("  全国青少年体育赛事数据分析（2023-2024）")
    print("  数据清洗 → 探索性分析 → 关联分析 → 长三角专题 → 可视化")
    print("=" * 70)

    # 0. 初始化
    ensure_dirs()
    setup_chinese_font()

    # 1. 数据检查
    if not check_data_file():
        return

    # 2. 数据清洗
    print("\n" + "━" * 70)
    print("  步骤 1/5: 数据清洗")
    print("━" * 70)
    df = run_cleaning()

    # 3. 核心分析
    print("\n" + "━" * 70)
    print("  步骤 2/5: 核心分析（地区分布/直辖市对比/消费结构/驱动力/新兴运动/月份）")
    print("━" * 70)
    core_results = run_core_analysis(df)

    # 4. 人口经济分析
    print("\n" + "━" * 70)
    print("  步骤 3/5: 人口与经济关联分析")
    print("━" * 70)
    economy_results = run_economy_analysis(df)
    prov_stats = economy_results["prov_stats"]

    # 5. 长三角专题分析
    print("\n" + "━" * 70)
    print("  步骤 4/5: 长三角专题分析")
    print("━" * 70)
    yrd_results = run_yrd_analysis(df, prov_stats)

    # 6. 可视化
    print("\n" + "━" * 70)
    print("  步骤 5/5: 生成可视化图表")
    print("━" * 70)
    run_all_visualizations(df, prov_stats)

    # 完成
    print("\n" + "=" * 70)
    print("  全部分析完成！")
    print("=" * 70)
    print(f"\n  输出文件:")
    print(f"    清洗数据:  {CLEANED_DATA_PATH}")
    print(f"    图表目录:  {os.path.join(os.path.dirname(__file__), 'output', 'charts')}/")
    print(f"\n  图表清单:")
    print(f"    01_省份分布地图.png       — 全国赛事省份分布热力地图（外部提供）")
    print(f"    02_运动项目热度.png       — 运动项目热度 TOP 15")
    print(f"    03_月份分布.png           — 全年赛事月份分布")
    print(f"    04_直辖市对比.png         — 直辖市赛事模式分化")
    print(f"    05_消费结构分化.png       — 球拍类 vs 团队球类")
    print(f"    06_新兴运动.png           — 新兴运动数量与规模")
    print(f"    07_赛事密度地图.png       — 各省份赛事密度热力地图（外部提供）")
    print(f"    08_GDP与赛事密度散点图.png — 经济关联四象限分析")
    print(f"    09_长三角vs全国.png       — 长三角 vs 全国对比（外部提供）")
    print(f"    10_长三角内部特征.png     — 长三角内部结构性分化（外部提供）")
    print(f"    11_上海vs北京项目对比.png  — 上海 vs 北京运动项目")
    print(f"    12_人口大省.png           — 人口大省（≥5000万）赛事密度")
    print(f"    13_人口小省.png           — 人口小省（<2000万）赛事密度")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--clean-only":
            ensure_dirs()
            setup_chinese_font()
            if check_data_file():
                run_cleaning()
        elif sys.argv[1] == "--viz-only":
            setup_chinese_font()
            df = load_cleaned_data()
            from src.analysis_economy import compute_province_density
            prov_stats = compute_province_density(df)
            run_all_visualizations(df, prov_stats)
        elif sys.argv[1] in ["-h", "--help"]:
            print(__doc__)
        else:
            print(f"未知参数: {sys.argv[1]}")
            print(__doc__)
    else:
        run_full_pipeline()


if __name__ == "__main__":
    main()
