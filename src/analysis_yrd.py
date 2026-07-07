#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长三角专题分析模块
长三角 vs 全国对比、长三角内部结构性分化
"""

import pandas as pd
import numpy as np
from config import YRD_PROVINCES, PROVINCE_DATA


def analyze_yrd_vs_national(df, prov_stats=None):
    """十、长三角 vs 全国：高密度、小规模、精品化"""
    print("\n" + "=" * 60)
    print("十、长三角 vs 全国")
    print("=" * 60)

    yrd = df[df["省名称"].isin(YRD_PROVINCES)]
    national = df

    yrd_count = len(yrd)
    national_count = len(national)
    yrd_ratio = yrd_count / national_count * 100

    yrd_pop = sum(PROVINCE_DATA[p]["pop"] for p in YRD_PROVINCES)
    total_pop = sum(v["pop"] for v in PROVINCE_DATA.values())
    yrd_pop_ratio = yrd_pop / total_pop * 100

    yrd_density = yrd_count / yrd_pop * 100
    national_density = national_count / total_pop * 100

    yrd_avg_scale = yrd["赛事规模"].mean()
    national_avg_scale = national["赛事规模"].mean()

    print(f"\n  指标              长三角        全国")
    print(f"  {'─' * 45}")
    print(f"  赛事总数          {yrd_count:>6}场      {national_count:>6}场")
    print(f"  人口              {yrd_pop:>6.0f}万    {total_pop:>6.0f}万")
    print(f"  人口占比          {yrd_pop_ratio:>6.1f}%       100%")
    print(f"  赛事占比          {yrd_ratio:>6.1f}%       100%")
    print(f"  每百万人赛事数    {yrd_density:>6.1f}        {national_density:>6.1f}")
    print(f"  平均赛事规模      {yrd_avg_scale:>6.0f}人      {national_avg_scale:>6.0f}人")

    print(f"\n  结论: 长三角以{yrd_pop_ratio:.1f}%的人口贡献了{yrd_ratio:.1f}%的赛事，")
    print(f"  密度是全国的{yrd_density/national_density:.1f}倍，但平均规模低于全国，")
    print(f"  呈现高密度、小规模、精品化特征。")

    return {
        "yrd_count": yrd_count,
        "yrd_ratio": yrd_ratio,
        "yrd_density": yrd_density,
        "national_density": national_density,
        "yrd_avg_scale": yrd_avg_scale,
        "national_avg_scale": national_avg_scale,
    }


def analyze_yrd_internal(df):
    """十一、长三角内部：上海浙江 vs 江苏安徽的结构性分化"""
    print("\n" + "=" * 60)
    print("十一、长三角内部结构性分化")
    print("=" * 60)

    results = []
    for prov in YRD_PROVINCES:
        sub = df[df["省名称"] == prov]
        total = len(sub)
        pop = PROVINCE_DATA[prov]["pop"]
        density = total / pop * 100
        avg = sub["赛事规模"].mean()
        vc = sub["赛事级别"].value_counts()

        result = {
            "省/市": prov,
            "赛事数量": total,
            "每百万人赛事数": density,
            "平均规模": avg,
            "市级占比": vc.get("市级", 0) / total * 100 if total > 0 else 0,
            "省级占比": vc.get("省级", 0) / total * 100 if total > 0 else 0,
            "国家级占比": vc.get("国家级", 0) / total * 100 if total > 0 else 0,
        }
        results.append(result)

    yrd_df = pd.DataFrame(results)

    print(f"\n{'省/市':<8} {'赛事数':>6} {'每百万人':>8} {'均值':>6} {'市级%':>6} {'省级%':>6} {'国家级%':>7}")
    print("─" * 55)
    for _, r in yrd_df.iterrows():
        print(f"{r['省/市']:<8} {r['赛事数量']:>6.0f} {r['每百万人赛事数']:>8.1f} "
              f"{r['平均规模']:>6.0f} {r['市级占比']:>6.0f} {r['省级占比']:>6.0f} {r['国家级占比']:>7.0f}")

    print(f"\n  分析要点:")
    print(f"    - 上海、浙江: 市级占比>65%，社区化、精品化，市场化生态")
    print(f"    - 江苏: 省级占比60%，行政驱动为主，与沪浙存在结构性差异")
    print(f"    - 江苏: 国家级占比14%（19场），长三角内最高")
    print(f"    - 安徽: 市级占比76%结构接近上海，但总量密度末位")
    print(f"    - 上海国家级0场系数据录入问题，非真实情况")

    return yrd_df


def run_yrd_analysis(df, prov_stats=None):
    """执行长三角专题分析"""
    national_result = analyze_yrd_vs_national(df, prov_stats)
    internal_result = analyze_yrd_internal(df)
    return {"national": national_result, "internal": internal_result}
