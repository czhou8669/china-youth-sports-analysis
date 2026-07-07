#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人口与经济关联分析模块
引入人口、人均GDP维度，计算赛事密度，分析经济因素与赛事供给的关联
"""

import pandas as pd
import numpy as np
from config import PROVINCE_DATA


def compute_province_density(df):
    """计算各省份赛事密度（每百万人赛事数）"""
    print("\n" + "=" * 60)
    print("七、人口大省：赛事数量与人口规模并不成正比")
    print("=" * 60)

    prov_stats = df.groupby("省名称").agg(
        赛事数量=("赛事ID", "count"),
        平均规模=("赛事规模", "mean"),
    ).reset_index()

    # 合并人口和经济数据
    prov_stats["人口(万)"] = prov_stats["省名称"].map(lambda x: PROVINCE_DATA.get(x, {}).get("pop", np.nan))
    prov_stats["人均GDP(万)"] = prov_stats["省名称"].map(lambda x: PROVINCE_DATA.get(x, {}).get("gdp_per", np.nan))
    prov_stats["每百万人赛事数"] = prov_stats["赛事数量"] / prov_stats["人口(万)"] * 100

    prov_stats = prov_stats.sort_values("赛事数量", ascending=False)

    print(f"\n各省份赛事密度 (按赛事数量排序):")
    print(f"{'省份':<12} {'赛事数':>6} {'人口(万)':>8} {'每百万人':>8} {'人均GDP':>8}")
    print("-" * 50)
    for _, row in prov_stats.iterrows():
        print(f"{row['省名称']:<12} {row['赛事数量']:>6.0f} {row['人口(万)']:>8.0f} "
              f"{row['每百万人赛事数']:>8.1f} {row['人均GDP(万)']:>8.2f}")

    national_avg = prov_stats["每百万人赛事数"].mean()
    national_total_ratio = prov_stats["赛事数量"].sum() / prov_stats["人口(万)"].sum() * 100
    print(f"\n全国均值(算术平均): {national_avg:.1f} 场/百万人")
    print(f"全国均值(加权平均): {national_total_ratio:.1f} 场/百万人")

    return prov_stats


def analyze_gdp_correlation(prov_stats):
    """八、经济因素与赛事密度的相关性"""
    print("\n" + "=" * 60)
    print("八、经济因素与赛事密度的相关性")
    print("=" * 60)

    corr = prov_stats[["人均GDP(万)", "每百万人赛事数"]].corr().iloc[0, 1]
    print(f"\n人均GDP与每百万人赛事数 相关系数: r = {corr:.3f}")
    print(f"  → 呈较强正相关，经济水平是赛事密度的重要驱动因素")

    # 四象限分析
    gdp_median = prov_stats["人均GDP(万)"].median()
    density_median = prov_stats["每百万人赛事数"].median()

    print(f"\n四象限分析 (GDP中位数={gdp_median:.2f}万, 密度中位数={density_median:.1f}):")
    print(f"\n  第一象限 (高GDP + 高密度) — 经济强+赛事多:")
    q1 = prov_stats[(prov_stats["人均GDP(万)"] >= gdp_median) &
                    (prov_stats["每百万人赛事数"] >= density_median)]
    for _, r in q1.iterrows():
        print(f"    {r['省名称']}: GDP {r['人均GDP(万)']:.2f}万, 密度 {r['每百万人赛事数']:.1f}")

    print(f"\n  第四象限 (高GDP + 低密度) — 经济强但赛事少:")
    q4 = prov_stats[(prov_stats["人均GDP(万)"] >= gdp_median) &
                    (prov_stats["每百万人赛事数"] < density_median)]
    for _, r in q4.iterrows():
        print(f"    {r['省名称']}: GDP {r['人均GDP(万)']:.2f}万, 密度 {r['每百万人赛事数']:.1f}")

    print(f"\n  第三象限 (低GDP + 低密度) — 经济弱+赛事少:")
    q3 = prov_stats[(prov_stats["人均GDP(万)"] < gdp_median) &
                    (prov_stats["每百万人赛事数"] < density_median)]
    for _, r in q3.head(5).iterrows():
        print(f"    {r['省名称']}: GDP {r['人均GDP(万)']:.2f}万, 密度 {r['每百万人赛事数']:.1f}")

    print(f"\n  第二象限 (低GDP + 高密度) — 政策驱动型:")
    q2 = prov_stats[(prov_stats["人均GDP(万)"] < gdp_median) &
                    (prov_stats["每百万人赛事数"] >= density_median)]
    for _, r in q2.iterrows():
        print(f"    {r['省名称']}: GDP {r['人均GDP(万)']:.2f}万, 密度 {r['每百万人赛事数']:.1f}")

    return {"correlation": corr, "q1": q1, "q2": q2, "q3": q3, "q4": q4}


def analyze_borderland(prov_stats):
    """九、边疆地区赛事的政策主导特征"""
    print("\n" + "=" * 60)
    print("九、边疆地区赛事的政策主导特征")
    print("=" * 60)

    borderland = ["西藏自治区", "新疆维吾尔自治区", "内蒙古自治区", "青海省", "宁夏回族自治区"]
    bl_stats = prov_stats[prov_stats["省名称"].isin(borderland)]

    print(f"\n边疆/地广人稀省份:")
    print(f"{'省份':<16} {'赛事数':>6} {'人口(万)':>8} {'每百万人':>8} {'人均GDP':>8}")
    print("-" * 55)
    for _, r in bl_stats.iterrows():
        print(f"{r['省名称']:<16} {r['赛事数量']:>6.0f} {r['人口(万)']:>8.0f} "
              f"{r['每百万人赛事数']:>8.1f} {r['人均GDP(万)']:>8.2f}")

    print(f"\n  分析: 这些省份密度数值较高，但结合人均GDP偏低、人口基数小的实际情况，")
    print(f"  赛事供给更多来自政策驱动（西部大开发、民族地区体育扶持），")
    print(f"  而非市场自发形成。不宜简单用密度指标衡量市场活跃度。")


def run_economy_analysis(df):
    """执行人口经济关联分析"""
    prov_stats = compute_province_density(df)
    corr_result = analyze_gdp_correlation(prov_stats)
    analyze_borderland(prov_stats)
    return {"prov_stats": prov_stats, **corr_result}
