#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化图表生成模块
使用 matplotlib 生成全部分析图表，输出到 output/charts/ 目录
图表编号与 PDF 报告中的引用一致
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from config import (CHART_DIR, COLOR_BLUE, COLOR_RED, COLOR_GREEN, COLOR_DARK,
                    COLOR_BODY, COLOR_LIGHT, COLOR_BG, COLOR_ACCENT, COLOR_PALETTE,
                    YRD_PROVINCES, MUNICIPALITIES, RACQUET_SPORTS, TEAM_BALL_SPORTS,
                    EMERGING_SPORTS, PROVINCE_DATA, setup_chinese_font, ensure_dirs)

# 初始化字体
setup_chinese_font()


def _save_fig(fig, filename):
    """保存图表"""
    path = os.path.join(CHART_DIR, filename)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [图表] 已保存: {filename}")
    return path


def chart_01_province_distribution(df):
    """图01: 各省份赛事数量分布（TOP 15 + 长尾）"""
    fig, ax = plt.subplots(figsize=(12, 6))

    prov_counts = df["省名称"].value_counts().head(20)
    colors = [COLOR_BLUE if i < 3 else COLOR_BODY if i < 10 else COLOR_LIGHT
              for i in range(len(prov_counts))]

    bars = ax.barh(range(len(prov_counts)), prov_counts.values, color=colors, edgecolor="white")
    ax.set_yticks(range(len(prov_counts)))
    ax.set_yticklabels(prov_counts.index, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("赛事数量（场）", fontsize=11)
    ax.set_title("全国青少年体育赛事省份分布 TOP 20", fontsize=14, fontweight="bold", pad=15)

    # 标注数值
    for bar, val in zip(bars, prov_counts.values):
        ax.text(bar.get_width() + 8, bar.get_y() + bar.get_height()/2,
                f"{val}", va="center", fontsize=9, color=COLOR_DARK)

    # 标注前三占比
    total = len(df)
    top3 = prov_counts.head(3).sum()
    ax.text(0.98, 0.95, f"前三占比: {top3/total*100:.1f}%", transform=ax.transAxes,
            fontsize=10, ha="right", va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=COLOR_BG, edgecolor=COLOR_LIGHT))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "01_省份分布.png")


def chart_02_sport_popularity(df):
    """图02: 运动项目热度 TOP 15"""
    fig, ax = plt.subplots(figsize=(12, 6))

    sport_counts = df["运动项目"].value_counts().head(15)
    # 球拍类红色，团队球类蓝色，其他灰色
    colors = []
    for s in sport_counts.index:
        if s in RACQUET_SPORTS:
            colors.append(COLOR_RED)
        elif s in TEAM_BALL_SPORTS:
            colors.append(COLOR_BLUE)
        else:
            colors.append(COLOR_BODY)

    bars = ax.bar(range(len(sport_counts)), sport_counts.values, color=colors, edgecolor="white")
    ax.set_xticks(range(len(sport_counts)))
    ax.set_xticklabels(sport_counts.index, rotation=45, ha="right", fontsize=10)
    ax.set_ylabel("赛事数量（场）", fontsize=11)
    ax.set_title("运动项目热度 TOP 15（红=球拍类，蓝=团队球类）", fontsize=14, fontweight="bold", pad=15)

    for bar, val in zip(bars, sport_counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{val}", ha="center", fontsize=9, color=COLOR_DARK)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "02_运动项目热度.png")


def chart_03_monthly_distribution(df):
    """图03: 各月份赛事数量分布"""
    fig, ax = plt.subplots(figsize=(10, 5))

    month_counts = df["月份"].value_counts().sort_index()
    months = list(range(1, 13))
    values = [month_counts.get(m, 0) for m in months]

    # 寒暑假高亮
    colors = []
    for m in months:
        if m in [7, 8]:
            colors.append(COLOR_RED)      # 暑假高峰
        elif m in [1, 2]:
            colors.append(COLOR_GREEN)    # 寒假低谷
        elif m in [5, 10, 11]:
            colors.append(COLOR_ACCENT)   # 次高峰
        else:
            colors.append(COLOR_BLUE)

    bars = ax.bar(months, values, color=colors, edgecolor="white", width=0.7)
    ax.set_xticks(months)
    ax.set_xticklabels([f"{m}月" for m in months], fontsize=10)
    ax.set_ylabel("赛事数量（场）", fontsize=11)
    ax.set_title("全年赛事月份分布（红=暑假高峰，绿=寒假低谷，橙=次高峰）",
                 fontsize=13, fontweight="bold", pad=15)

    for bar, val in zip(bars, values):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
                    f"{val}", ha="center", fontsize=9, color=COLOR_DARK)

    # 标注11月上海异常
    nov_total = month_counts.get(11, 0)
    sh_nov = len(df[(df["月份"] == 11) & (df["省名称"] == "上海市")])
    if nov_total > 0:
        ax.annotate(f"11月上海占{sh_nov/nov_total*100:.0f}%",
                    xy=(11, nov_total), xytext=(11, nov_total + 120),
                    fontsize=9, ha="center", color=COLOR_RED,
                    arrowprops=dict(arrowstyle="->", color=COLOR_RED))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "03_月份分布.png")


def chart_04_municipality_comparison(df):
    """图04: 直辖市赛事模式对比（广度型 vs 高度型）"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    cities = MUNICIPALITIES
    city_colors = [COLOR_RED, COLOR_BLUE, COLOR_BODY, COLOR_LIGHT]

    # 子图1: 赛事总数 vs 平均规模
    ax = axes[0]
    totals = [len(df[df["省名称"] == c]) for c in cities]
    avgs = [df[df["省名称"] == c]["赛事规模"].mean() for c in cities]
    x = np.arange(len(cities))
    w = 0.35
    ax.bar(x - w/2, totals, w, label="赛事总数", color=COLOR_BLUE, edgecolor="white")
    ax.bar(x + w/2, avgs, w, label="平均规模", color=COLOR_RED, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(cities, fontsize=10)
    ax.set_title("赛事总数 vs 平均规模", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 子图2: 中位数对比
    ax = axes[1]
    medians = [df[df["省名称"] == c]["赛事规模"].median() for c in cities]
    bars = ax.bar(cities, medians, color=city_colors, edgecolor="white")
    ax.set_title("赛事规模中位数", fontsize=12, fontweight="bold")
    ax.set_ylabel("人", fontsize=10)
    for bar, val in zip(bars, medians):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{val:.0f}", ha="center", fontsize=10, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 子图3: 级别结构堆叠柱状图
    ax = axes[2]
    levels = ["国家级", "省级", "市级"]
    level_colors = [COLOR_RED, COLOR_ACCENT, COLOR_BLUE]
    bottom = np.zeros(len(cities))
    for level, lc in zip(levels, level_colors):
        vals = []
        for c in cities:
            sub = df[df["省名称"] == c]
            total = len(sub)
            val = len(sub[sub["赛事级别"] == level]) / total * 100 if total > 0 else 0
            vals.append(val)
        ax.bar(cities, vals, bottom=bottom, label=level, color=lc, edgecolor="white")
        bottom += np.array(vals)
    ax.set_title("赛事级别结构（%）", fontsize=12, fontweight="bold")
    ax.set_ylabel("占比 (%)", fontsize=10)
    ax.legend(fontsize=9, loc="upper right")
    ax.set_ylim(0, 110)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle("直辖市赛事模式分化：广度型（上海） vs 高度型（北京）",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save_fig(fig, "04_直辖市对比.png")


def chart_05_consumption_structure(df):
    """图05: 消费结构分化（球拍类 vs 团队球类）"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    racquet = df[df["运动项目"].isin(RACQUET_SPORTS)]
    team_ball = df[df["运动项目"].isin(TEAM_BALL_SPORTS)]

    categories = ["球拍类\n(网/羽/乒)", "团队球类\n(足/篮/排)"]
    counts = [len(racquet), len(team_ball)]
    avgs = [racquet["赛事规模"].mean(), team_ball["赛事规模"].mean()]

    x = np.arange(len(categories))
    w = 0.35
    ax = axes[0]
    bars1 = ax.bar(x - w / 2, counts, w, label="赛事数量", color=COLOR_ACCENT, edgecolor="white")
    ax2 = ax.twinx()
    bars2 = ax2.bar(x + w / 2, avgs, w, label="平均规模", color=COLOR_BLUE, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylabel("赛事数量（场）", fontsize=10, color=COLOR_ACCENT)
    ax2.set_ylabel("平均规模（人）", fontsize=10, color=COLOR_BLUE)
    ax.set_ylim(0, max(counts) * 1.15)
    ax2.set_ylim(0, max(avgs) * 1.15)
    ax.tick_params(axis="y", colors=COLOR_ACCENT)
    ax2.tick_params(axis="y", colors=COLOR_BLUE)
    ax.set_title("球拍类 vs 团队球类", fontsize=13, fontweight="bold")

    for bar, val in zip(bars1, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 8,
                f"{val}", ha="center", fontsize=10, color=COLOR_ACCENT)
    for bar, val in zip(bars2, avgs):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 8,
                 f"{val:.0f}", ha="center", fontsize=10, color=COLOR_BLUE)

    ax.legend(loc="upper left", fontsize=9)
    ax2.legend(loc="upper right", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    ax = axes[1]
    sports = RACQUET_SPORTS + TEAM_BALL_SPORTS
    sport_avgs = [df[df["运动项目"] == s]["赛事规模"].mean() for s in sports]
    sport_counts = [len(df[df["运动项目"] == s]) for s in sports]
    colors = [COLOR_RED] * 3 + [COLOR_BLUE] * 3

    bars = ax.bar(sports, sport_avgs, color=colors, edgecolor="white")
    ax.set_ylabel("平均赛事规模（人）", fontsize=10)
    ax.set_title("各项目平均赛事规模", fontsize=13, fontweight="bold")
    for bar, avg, cnt in zip(bars, sport_avgs, sport_counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{avg:.0f}\n({cnt}场)", ha="center", fontsize=9, color=COLOR_DARK)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle("消费结构因项目类型而分化", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save_fig(fig, "05_消费结构分化.png")


def chart_06_emerging_sports(df):
    """图06: 新兴运动赛事数量与规模"""
    fig, ax = plt.subplots(figsize=(10, 5))

    sports = EMERGING_SPORTS
    counts = [len(df[df["运动项目"] == s]) for s in sports]
    avgs = [df[df["运动项目"] == s]["赛事规模"].mean() if c > 0 else 0 for s, c in zip(sports, counts)]

    x = np.arange(len(sports))
    w = 0.35
    bars1 = ax.bar(x - w/2, counts, w, label="赛事数量", color=COLOR_BLUE, edgecolor="white")
    ax2 = ax.twinx()
    bars2 = ax2.bar(x + w/2, avgs, w, label="平均规模", color=COLOR_RED, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(sports, fontsize=11)
    ax.set_ylabel("赛事数量（场）", fontsize=10, color=COLOR_BLUE)
    ax2.set_ylabel("平均规模（人）", fontsize=10, color=COLOR_RED)
    ax.set_title("新兴运动：赛事数量与平均规模", fontsize=14, fontweight="bold", pad=15)

    for bar, val in zip(bars1, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{val}", ha="center", fontsize=10, color=COLOR_BLUE, fontweight="bold")
    for bar, val in zip(bars2, avgs):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{val:.0f}", ha="center", fontsize=10, color=COLOR_RED, fontweight="bold")

    ax.legend(loc="upper left", fontsize=9)
    ax2.legend(loc="upper right", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "06_新兴运动.png")


def chart_07_province_density(prov_stats):
    """图07: 各省份每百万人赛事数（密度）"""
    fig, ax = plt.subplots(figsize=(12, 7))

    data = prov_stats.dropna(subset=["每百万人赛事数"]).sort_values("每百万人赛事数", ascending=True)
    national_avg = data["每百万人赛事数"].mean()

    colors = []
    for _, r in data.iterrows():
        if r["每百万人赛事数"] >= national_avg:
            colors.append(COLOR_BLUE)
        else:
            colors.append(COLOR_LIGHT)

    bars = ax.barh(range(len(data)), data["每百万人赛事数"].values, color=colors, edgecolor="white")
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels(data["省名称"].values, fontsize=9)
    ax.set_xlabel("每百万人赛事数（场）", fontsize=11)
    ax.set_title("各省份赛事密度（每百万人赛事数）", fontsize=14, fontweight="bold", pad=15)

    ax.axvline(x=national_avg, color=COLOR_RED, linestyle="--", linewidth=1.5, label=f"全国均值 {national_avg:.1f}")
    ax.legend(fontsize=10)

    for bar, val in zip(bars, data["每百万人赛事数"].values):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}", va="center", fontsize=8, color=COLOR_DARK)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "07_省份赛事密度.png")


def chart_08_gdp_scatter(prov_stats):
    """图08: 人均GDP与赛事密度散点图 + 四象限"""
    fig, ax = plt.subplots(figsize=(10, 8))

    data = prov_stats.dropna(subset=["人均GDP(万)", "每百万人赛事数"]).copy()
    corr = data[["人均GDP(万)", "每百万人赛事数"]].corr().iloc[0, 1]

    gdp_med = data["人均GDP(万)"].median()
    dens_med = data["每百万人赛事数"].median()

    # 四象限着色
    colors = []
    for _, r in data.iterrows():
        if r["人均GDP(万)"] >= gdp_med and r["每百万人赛事数"] >= dens_med:
            colors.append(COLOR_BLUE)    # Q1: 高高
        elif r["人均GDP(万)"] < gdp_med and r["每百万人赛事数"] >= dens_med:
            colors.append(COLOR_GREEN)   # Q2: 低高（政策驱动）
        elif r["人均GDP(万)"] < gdp_med and r["每百万人赛事数"] < dens_med:
            colors.append(COLOR_LIGHT)   # Q3: 低低
        else:
            colors.append(COLOR_RED)     # Q4: 高低（异常）

    ax.scatter(data["人均GDP(万)"], data["每百万人赛事数"], c=colors, s=80, edgecolors="white", zorder=5)

    # 标注关键省份
    label_provinces = ["上海市", "北京市", "浙江省", "广东省", "江苏省", "福建省",
                       "山东省", "河南省", "新疆维吾尔自治区", "西藏自治区", "四川省"]
    for _, r in data.iterrows():
        if r["省名称"] in label_provinces:
            ax.annotate(r["省名称"], (r["人均GDP(万)"], r["每百万人赛事数"]),
                        fontsize=8, ha="left", va="bottom",
                        xytext=(5, 5), textcoords="offset points")

    # 中位线
    ax.axvline(x=gdp_med, color=COLOR_LIGHT, linestyle="--", linewidth=1, alpha=0.5)
    ax.axhline(y=dens_med, color=COLOR_LIGHT, linestyle="--", linewidth=1, alpha=0.5)

    # 象限标注
    ax.text(0.98, 0.98, "Q1: 高GDP+高密度", transform=ax.transAxes, fontsize=9,
            ha="right", va="top", color=COLOR_BLUE, fontweight="bold")
    ax.text(0.02, 0.98, "Q2: 低GDP+高密度\n(政策驱动)", transform=ax.transAxes, fontsize=9,
            ha="left", va="top", color=COLOR_GREEN, fontweight="bold")
    ax.text(0.02, 0.02, "Q3: 低GDP+低密度", transform=ax.transAxes, fontsize=9,
            ha="left", va="bottom", color=COLOR_LIGHT, fontweight="bold")
    ax.text(0.98, 0.02, "Q4: 高GDP+低密度\n(数据盲区?)", transform=ax.transAxes, fontsize=9,
            ha="right", va="bottom", color=COLOR_RED, fontweight="bold")

    ax.set_xlabel("人均GDP（万元）", fontsize=12)
    ax.set_ylabel("每百万人赛事数（场）", fontsize=12)
    ax.set_title(f"人均GDP与赛事密度关联分析（r = {corr:.3f}）", fontsize=14, fontweight="bold", pad=15)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "08_GDP与赛事密度散点图.png")


def chart_09_yrd_vs_national(df):
    """图09: 长三角 vs 全国对比"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    yrd = df[df["省名称"].isin(YRD_PROVINCES)]
    national = df

    # 子图1: 赛事占比 vs 人口占比
    ax = axes[0]
    yrd_pop = sum(PROVINCE_DATA[p]["pop"] for p in YRD_PROVINCES)
    total_pop = sum(v["pop"] for v in PROVINCE_DATA.values())
    labels = ["长三角", "其他地区"]
    pop_vals = [yrd_pop / total_pop * 100, (1 - yrd_pop / total_pop) * 100]
    event_vals = [len(yrd) / len(national) * 100, (1 - len(yrd) / len(national)) * 100]

    x = np.arange(2)
    w = 0.35
    ax.bar(x - w/2, pop_vals, w, label="人口占比", color=COLOR_LIGHT, edgecolor="white")
    ax.bar(x + w/2, event_vals, w, label="赛事占比", color=COLOR_BLUE, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(["长三角", "其他地区"], fontsize=11)
    ax.set_ylabel("占比 (%)", fontsize=10)
    ax.set_title("人口占比 vs 赛事占比", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 子图2: 赛事密度对比
    ax = axes[1]
    yrd_density = len(yrd) / yrd_pop * 100
    nat_density = len(national) / total_pop * 100
    bars = ax.bar(["长三角", "全国"], [yrd_density, nat_density],
                  color=[COLOR_BLUE, COLOR_LIGHT], edgecolor="white")
    ax.set_ylabel("每百万人赛事数", fontsize=10)
    ax.set_title("赛事密度对比", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, [yrd_density, nat_density]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{val:.1f}", ha="center", fontsize=12, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 子图3: 平均规模对比
    ax = axes[2]
    yrd_avg = yrd["赛事规模"].mean()
    nat_avg = national["赛事规模"].mean()
    bars = ax.bar(["长三角", "全国"], [yrd_avg, nat_avg],
                  color=[COLOR_RED, COLOR_LIGHT], edgecolor="white")
    ax.set_ylabel("平均赛事规模（人）", fontsize=10)
    ax.set_title("平均赛事规模对比", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, [yrd_avg, nat_avg]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                f"{val:.0f}", ha="center", fontsize=12, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle("长三角 vs 全国：高密度、小规模、精品化", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save_fig(fig, "09_长三角vs全国.png")


def chart_10_yrd_internal(df):
    """图10: 长三角内部结构性差异"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 子图1: 四省市赛事数量与密度
    ax = axes[0]
    yrd_data = []
    for prov in YRD_PROVINCES:
        sub = df[df["省名称"] == prov]
        pop = PROVINCE_DATA[prov]["pop"]
        yrd_data.append({
            "省/市": prov,
            "赛事数量": len(sub),
            "每百万人": len(sub) / pop * 100,
            "平均规模": sub["赛事规模"].mean(),
        })
    yrd_df = pd.DataFrame(yrd_data)

    x = np.arange(len(YRD_PROVINCES))
    w = 0.35
    bars1 = ax.bar(x - w/2, yrd_df["赛事数量"], w, label="赛事数量", color=COLOR_BLUE, edgecolor="white")
    ax2 = ax.twinx()
    bars2 = ax2.bar(x + w/2, yrd_df["每百万人"], w, label="每百万人", color=COLOR_RED, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(YRD_PROVINCES, fontsize=11)
    ax.set_ylabel("赛事数量（场）", fontsize=10, color=COLOR_BLUE)
    ax2.set_ylabel("每百万人赛事数", fontsize=10, color=COLOR_RED)
    ax.set_title("长三角四省市：数量与密度", fontsize=12, fontweight="bold")

    for bar, val in zip(bars1, yrd_df["赛事数量"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{val:.0f}", ha="center", fontsize=9, color=COLOR_BLUE)
    for bar, val in zip(bars2, yrd_df["每百万人"]):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f"{val:.1f}", ha="center", fontsize=9, color=COLOR_RED)
    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)

    # 子图2: 级别结构堆叠柱状图
    ax = axes[1]
    levels = ["国家级", "省级", "市级"]
    level_colors = [COLOR_RED, COLOR_ACCENT, COLOR_BLUE]
    bottom = np.zeros(len(YRD_PROVINCES))
    for level, lc in zip(levels, level_colors):
        vals = []
        for prov in YRD_PROVINCES:
            sub = df[df["省名称"] == prov]
            total = len(sub)
            val = len(sub[sub["赛事级别"] == level]) / total * 100 if total > 0 else 0
            vals.append(val)
        ax.bar(YRD_PROVINCES, vals, bottom=bottom, label=level, color=lc, edgecolor="white")
        bottom += np.array(vals)
    ax.set_ylabel("占比 (%)", fontsize=10)
    ax.set_title("赛事级别结构（江苏60%省级一枝独秀）", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.set_ylim(0, 110)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle("长三角内部：上海浙江 vs 江苏安徽的结构性分化", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save_fig(fig, "10_长三角内部差异.png")


def chart_11_sh_vs_bj_sports(df):
    """图11: 上海 vs 北京 运动项目对比"""
    fig, ax = plt.subplots(figsize=(12, 6))

    sh_sports = df[df["省名称"] == "上海市"]["运动项目"].value_counts().head(10)
    bj_sports = df[df["省名称"] == "北京市"]["运动项目"].value_counts().head(10)

    all_sports = list(dict.fromkeys(list(sh_sports.index) + list(bj_sports.index)))[:12]
    sh_vals = [sh_sports.get(s, 0) for s in all_sports]
    bj_vals = [bj_sports.get(s, 0) for s in all_sports]

    x = np.arange(len(all_sports))
    w = 0.35
    ax.bar(x - w/2, sh_vals, w, label="上海", color=COLOR_RED, edgecolor="white")
    ax.bar(x + w/2, bj_vals, w, label="北京", color=COLOR_BLUE, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(all_sports, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("赛事数量（场）", fontsize=11)
    ax.set_title("上海 vs 北京：运动项目结构对比", fontsize=14, fontweight="bold", pad=15)
    ax.legend(fontsize=11)

    ax.text(0.98, 0.95, "上海: 社区化、多元化（广度型）\n北京: 高消费、精英化（高度型）",
            transform=ax.transAxes, fontsize=9, ha="right", va="top",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=COLOR_BG, edgecolor=COLOR_LIGHT))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "11_上海vs北京项目对比.png")


def run_all_visualizations(df, prov_stats):
    """生成全部可视化图表"""
    ensure_dirs()
    print("\n[可视化] 开始生成图表...")

    chart_01_province_distribution(df)
    chart_02_sport_popularity(df)
    chart_03_monthly_distribution(df)
    chart_04_municipality_comparison(df)
    chart_05_consumption_structure(df)
    chart_06_emerging_sports(df)
    chart_07_province_density(prov_stats)
    chart_08_gdp_scatter(prov_stats)
    chart_09_yrd_vs_national(df)
    chart_10_yrd_internal(df)
    chart_11_sh_vs_bj_sports(df)

    print(f"\n[可视化] 全部图表已生成至: {CHART_DIR}")
