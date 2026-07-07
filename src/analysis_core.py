#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心分析模块
包含地区分布、直辖市对比、消费结构、驱动力、新兴运动、月份分布等分析
"""

import pandas as pd
import numpy as np
from config import (MUNICIPALITIES, RACQUET_SPORTS, TEAM_BALL_SPORTS,
                    EMERGING_SPORTS, PROVINCE_DATA)


def analyze_regional_distribution(df):
    """一、地区分布分析"""
    print("\n" + "=" * 60)
    print("一、地区分布分析")
    print("=" * 60)

    prov_counts = df["省名称"].value_counts()
    total = len(df)

    print(f"\n全国青少年体育赛事总数: {total} 场")
    print(f"\n各省份赛事数量 TOP 10:")
    for i, (prov, count) in enumerate(prov_counts.head(10).items()):
        print(f"  {i+1:2d}. {prov}: {count} 场 ({count/total*100:.1f}%)")

    top3 = prov_counts.head(3).sum()
    print(f"\n前三省份合计占比: {top3/total*100:.1f}%")

    # 平均赛事规模
    avg_scale = df["赛事规模"].mean()
    med_scale = df["赛事规模"].median()
    print(f"\n全国平均赛事规模: {avg_scale:.0f} 人")
    print(f"全国中位数赛事规模: {med_scale:.0f} 人")
    print(f"最大值: {df['赛事规模'].max():.0f} 人（均值受极端值拉高）")

    return {
        "prov_counts": prov_counts,
        "total": total,
        "avg_scale": avg_scale,
        "median_scale": med_scale,
        "top3_ratio": top3 / total,
    }


def analyze_municipality_comparison(df):
    """二、直辖市赛事模式分化：广度型 vs 高度型"""
    print("\n" + "=" * 60)
    print("二、直辖市赛事模式分化")
    print("=" * 60)

    results = []
    for city in MUNICIPALITIES:
        sub = df[df["省名称"] == city]
        total = len(sub)
        avg = sub["赛事规模"].mean()
        med = sub["赛事规模"].median()
        vc = sub["赛事级别"].value_counts()

        city_result = {
            "城市": city,
            "赛事总数": total,
            "平均规模": avg,
            "中位数": med,
            "市级数": vc.get("市级", 0),
            "省级数": vc.get("省级", 0),
            "国家级数": vc.get("国家级", 0),
            "市级占比": vc.get("市级", 0) / total * 100 if total > 0 else 0,
            "国家级占比": vc.get("国家级", 0) / total * 100 if total > 0 else 0,
        }
        results.append(city_result)

        print(f"\n  {city}:")
        print(f"    总数: {total} 场 | 均值: {avg:.0f} 人 | 中位数: {med:.0f} 人")
        print(f"    市级: {vc.get('市级', 0)} ({city_result['市级占比']:.0f}%) | "
              f"省级: {vc.get('省级', 0)} | 国家级: {vc.get('国家级', 0)} ({city_result['国家级占比']:.0f}%)")

    # 运动项目对比（上海 vs 北京）
    print("\n  上海 TOP 5 运动项目:")
    sh_top = df[df["省名称"] == "上海市"]["运动项目"].value_counts().head(5)
    for sport, count in sh_top.items():
        print(f"    {sport}: {count} 场")

    print("\n  北京 TOP 5 运动项目:")
    bj_top = df[df["省名称"] == "北京市"]["运动项目"].value_counts().head(5)
    for sport, count in bj_top.items():
        print(f"    {sport}: {count} 场")

    return pd.DataFrame(results)


def analyze_consumption_structure(df):
    """三、消费结构因项目类型而分化"""
    print("\n" + "=" * 60)
    print("三、消费结构分析")
    print("=" * 60)

    # 运动项目热度 TOP 10
    sport_counts = df["运动项目"].value_counts()
    print(f"\n运动项目热度 TOP 10:")
    for i, (sport, count) in enumerate(sport_counts.head(10).items()):
        avg = df[df["运动项目"] == sport]["赛事规模"].mean()
        print(f"  {i+1:2d}. {sport}: {count} 场, 平均规模 {avg:.0f} 人")

    # 球拍类 vs 团队球类
    racquet = df[df["运动项目"].isin(RACQUET_SPORTS)]
    team_ball = df[df["运动项目"].isin(TEAM_BALL_SPORTS)]

    print(f"\n球拍类（网球/羽毛球/乒乓球）:")
    print(f"  赛事数: {len(racquet)} 场, 平均规模: {racquet['赛事规模'].mean():.0f} 人")

    print(f"\n团队球类（足球/篮球/排球）:")
    print(f"  赛事数: {len(team_ball)} 场, 平均规模: {team_ball['赛事规模'].mean():.0f} 人")

    print(f"\n  => 团队球类在赛事数量和平均规模上双重领先")

    return {
        "sport_counts": sport_counts,
        "racquet_count": len(racquet),
        "racquet_avg": racquet["赛事规模"].mean(),
        "team_ball_count": len(team_ball),
        "team_ball_avg": team_ball["赛事规模"].mean(),
    }


def analyze_driving_forces(df):
    """四、驱动力分层（基于课题调研框架）"""
    print("\n" + "=" * 60)
    print("四、驱动力分层")
    print("=" * 60)

    print("""
驱动力分析框架（结合课题调研）:

  第一层 — 个人偏好 / 学校要求
    → 青少年内生消费动力，个人偏好占主导

  第二层 — 家长经济状况
    → 掌握最终决策权与支付权，直接影响消费发生

  第三层 — 空间状况
    → 反映实体空间供需，物理上制约体育消费需求

应用案例：
  球拍类项目客单价高但赛事规模偏小 →
    进入门槛由家长决定（第二层），
    进一步投入由孩子兴趣驱动（第一层），
    华东经济水平覆盖+社区化场地促成小规模精品赛事（第三层）
    三者共同筛选出高黏性、高消费的核心用户群体。
    """)


def analyze_emerging_sports(df):
    """五、新兴运动的参与度"""
    print("\n" + "=" * 60)
    print("五、新兴运动分析")
    print("=" * 60)

    results = []
    for sport in EMERGING_SPORTS:
        sub = df[df["运动项目"] == sport]
        count = len(sub)
        avg = sub["赛事规模"].mean() if count > 0 else 0
        results.append({"项目": sport, "赛事数": count, "平均规模": avg})
        print(f"  {sport}: {count} 场, 平均规模 {avg:.0f} 人")

    print(f"\n  分析要点:")
    print(f"    - 击剑: 受众集中中高收入家庭，适合精品化私校渗透")
    print(f"    - 街舞: 群众基础好、场地门槛低，适合快速复制")
    print(f"    - 攀岩/街舞: 已入奥运，政策红利窗口期")
    print(f"    - 冰球: 场馆投入壁垒极高，扩张受场地制约")

    return pd.DataFrame(results)


def analyze_seasonality(df):
    """六、赛事节奏与学校日历"""
    print("\n" + "=" * 60)
    print("六、赛事月份分布")
    print("=" * 60)

    month_counts = df["月份"].value_counts().sort_index()
    print(f"\n各月份赛事数量:")
    for month, count in month_counts.items():
        bar = "█" * (count // 20)
        print(f"  {int(month):2d}月: {count:4d} 场 {bar}")

    summer = month_counts.get(7, 0) + month_counts.get(8, 0)
    winter = month_counts.get(1, 0) + month_counts.get(2, 0)
    print(f"\n  暑假(7-8月): {summer} 场 — 高峰")
    print(f"  寒假(1-2月): {winter} 场 — 低谷")

    # 11月上海异常
    nov = df[df["月份"] == 11]
    sh_nov = len(nov[nov["省名称"] == "上海市"])
    print(f"\n  注: 11月全国{len(nov)}场中上海占{sh_nov}场({sh_nov/len(nov)*100:.1f}%)")
    print(f"  → 主要来自'上海市第四届市民运动会'集中录入，非全国普遍现象")

    return month_counts


def run_core_analysis(df):
    """执行全部核心分析"""
    results = {}
    results["regional"] = analyze_regional_distribution(df)
    results["municipality"] = analyze_municipality_comparison(df)
    results["consumption"] = analyze_consumption_structure(df)
    analyze_driving_forces(df)
    results["emerging"] = analyze_emerging_sports(df)
    results["seasonality"] = analyze_seasonality(df)
    return results
