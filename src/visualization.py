#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化图表生成模块
使用 matplotlib 生成全部分析图表，输出到 output/charts/ 目录
图表编号与 PDF 报告中的引用一致

注：图01、图07 为中国省份地图（choropleth），由代码读取 maps/china_provinces.json
并用 matplotlib Polygon 绘制，无外部 GIS 库依赖。
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

from config import (CHART_DIR, COLOR_BLUE, COLOR_RED, COLOR_GREEN, COLOR_DARK,
                    COLOR_BODY, COLOR_LIGHT, COLOR_BG, COLOR_ACCENT, COLOR_PALETTE,
                    YRD_PROVINCES, MUNICIPALITIES, RACQUET_SPORTS, TEAM_BALL_SPORTS,
                    EMERGING_SPORTS, PROVINCE_DATA, MAP_DIR,
                    setup_chinese_font, ensure_dirs)

# 初始化字体
setup_chinese_font()


# ========== 地图绘制辅助 ==========

def _load_geojson():
    """加载中国省份 GeoJSON"""
    geo_path = os.path.join(MAP_DIR, "china_provinces.json")
    if not os.path.exists(geo_path):
        raise FileNotFoundError(
            f"未找到地图数据: {geo_path}\n"
            f"请下载中国省份 GeoJSON 至此路径，或从以下地址获取：\n"
            f"https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json"
        )
    with open(geo_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _draw_china_map(ax, geo_data, value_dict, bins, cmap, legend_labels, title):
    """通用中国省份地图绘制函数

    Args:
        ax: matplotlib axes
        geo_data: GeoJSON dict
        value_dict: {省名称: 数值}
        bins: 分级阈值列表
        cmap: matplotlib colormap 名称或对象
        legend_labels: 图例标签列表，与 bins 对应
        title: 子图标题
    """
    # 配色：缺失值用最浅色
    norm = BoundaryNorm(bins + [bins[-1] * 2 + 1], cmap.N) if hasattr(cmap, "N") else None

    for feat in geo_data["features"]:
        name = feat["properties"]["name"]
        # 名称兼容：GeoJSON 用"省"结尾，去掉
        clean_name = name
        if clean_name not in value_dict:
            # 尝试去掉"省"或"市"匹配
            for suffix in ["省", "市", "自治区", "壮族自治区", "回族自治区", "维吾尔自治区"]:
                candidate = clean_name.replace(suffix, "")
                if candidate in value_dict:
                    clean_name = candidate
                    break

        val = value_dict.get(clean_name, None)
        # 缺失值用最浅
        if val is None:
            color = cmap(0.05)
        else:
            # 找到该值对应的 bin
            idx = 0
            for i, b in enumerate(bins):
                if val >= b:
                    idx = i + 1
            idx = min(idx, len(bins))
            color = cmap(idx / len(bins))

        # 绘制多边形
        geom = feat["geometry"]
        if geom["type"] == "MultiPolygon":
            polygons = geom["coordinates"]
        else:
            polygons = [geom["coordinates"]]

        for poly in polygons:
            for ring in poly:
                if len(ring) < 3:
                    continue
                patch = MplPolygon(ring, closed=True, facecolor=color,
                                   edgecolor="white", linewidth=0.4)
                ax.add_patch(patch)

    # 标注省名（仅在中心点位置标注）
    for feat in geo_data["features"]:
        name = feat["properties"]["name"]
        # 简化显示名
        short = name
        for suffix in ["壮族自治区", "维吾尔自治区", "回族自治区", "自治区"]:
            short = short.replace(suffix, "")
        if len(short) > 4:
            short = short[:3]
        centroid = feat["properties"].get("center") or feat["properties"].get("centroid")
        if centroid:
            ax.text(centroid[0], centroid[1], short,
                    ha="center", va="center", fontsize=7, color="#1e293b")

    ax.set_xlim(73, 135)
    ax.set_ylim(18, 54)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)

    # 自定义图例
    from matplotlib.patches import Patch
    legend_patches = []
    n_bins = len(bins)
    for i, label in enumerate(legend_labels):
        legend_patches.append(Patch(facecolor=cmap((i + 1) / n_bins),
                                    edgecolor="white", label=label))
    ax.legend(handles=legend_patches, loc="lower left", fontsize=8,
              frameon=False, title="赛事数量", title_fontsize=8)


def _save_fig(fig, filename):
    """保存图表"""
    path = os.path.join(CHART_DIR, filename)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [图表] 已保存: {filename}")
    return path


# ========== 图表函数 ==========

def chart_01_province_distribution(df):
    """图01: 全国青少年体育赛事省份分布地图（热力地图）"""
    fig, ax = plt.subplots(figsize=(12, 9))

    prov_counts = df["省名称"].value_counts()
    value_dict = prov_counts.to_dict()

    # 5 级分色：0-30 / 31-100 / 101-200 / 201-400 / 401+
    bins = [31, 101, 201, 401]
    cmap = LinearSegmentedColormap.from_list(
        "blue_white",
        ["#deebf7", "#9ecae1", "#4292c6", "#08519c", "#08306b"]
    )
    legend_labels = ["0–30场", "31–100场", "101–200场", "201–400场", "401场以上"]

    geo_data = _load_geojson()
    _draw_china_map(ax, geo_data, value_dict, bins, cmap, legend_labels,
                    title=None)
    fig.text(0.5, 0.91, "数据来源：全国群众体育赛事数据库（2024年，共5325场）",
             ha="center", fontsize=10, color=COLOR_LIGHT)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return _save_fig(fig, "01_省份分布地图.png")


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
    """图07: 各省份赛事密度地图（热力地图，按每百万人赛事数分级）"""
    fig, ax = plt.subplots(figsize=(12, 9))

    value_dict = prov_stats.set_index("省名称")["每百万人赛事数"].to_dict()

    # 5 级分色：0-3 / 3-8 / 8-15 / 15-25 / 25+
    bins = [3, 8, 15, 25]
    cmap = LinearSegmentedColormap.from_list(
        "orange_white",
        ["#fff5eb", "#fdd0a2", "#fd8d3c", "#d94801", "#7f2704"]
    )
    legend_labels = ["0–3", "3–8", "8–15", "15–25", "25以上"]

    geo_data = _load_geojson()
    _draw_china_map(ax, geo_data, value_dict, bins, cmap, legend_labels,
                    title="2024年全国青少年体育赛事密度（每百万人）")
    fig.text(0.5, 0.91, "消除人口基数差异后的赛事供给水平",
             ha="center", fontsize=10, color=COLOR_LIGHT)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return _save_fig(fig, "07_赛事密度地图.png")


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
    """图09: 长三角 vs 全国 整体特征对比（饼图+密度柱+平均规模柱）"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    yrd = df[df["省名称"].isin(YRD_PROVINCES)]
    national = df

    # 子图1: 长三角赛事占全国比重（饼图）
    ax = axes[0]
    yrd_share = len(yrd) / len(national) * 100
    other_share = 100 - yrd_share
    ax.pie([yrd_share, other_share],
           labels=["长三角", "其他省份"],
           colors=[COLOR_BLUE, "#deebf7"],
           autopct="%.1f%%", startangle=90,
           textprops={"fontsize": 11, "fontweight": "bold"})
    ax.set_title("长三角赛事占全国比重", fontsize=12, fontweight="bold")

    # 子图2: 每百万人赛事密度对比
    ax = axes[1]
    yrd_pop = sum(PROVINCE_DATA[p]["pop"] for p in YRD_PROVINCES)
    total_pop = sum(v["pop"] for v in PROVINCE_DATA.values())
    yrd_density = len(yrd) / yrd_pop * 100
    nat_density = len(national) / total_pop * 100
    bars = ax.bar(["长三角整体", "全国均值"], [yrd_density, nat_density],
                  color=[COLOR_BLUE, "#deebf7"], edgecolor="white", width=0.5)
    ax.set_ylabel("每百万人赛事数", fontsize=10)
    ax.set_title("每百万人赛事密度对比", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, [yrd_density, nat_density]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{val:.1f}", ha="center", fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(yrd_density, nat_density) * 1.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 子图3: 平均赛事规模对比
    ax = axes[2]
    yrd_avg = yrd["赛事规模"].mean()
    nat_avg = national["赛事规模"].mean()
    bars = ax.bar(["长三角", "全国均值"], [yrd_avg, nat_avg],
                  color=[COLOR_BLUE, "#deebf7"], edgecolor="white", width=0.5)
    ax.set_ylabel("平均参赛人数（人）", fontsize=10)
    ax.set_title("平均赛事规模对比（人）", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, [yrd_avg, nat_avg]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{val:.0f}人", ha="center", fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(yrd_avg, nat_avg) * 1.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle("长三角 vs 全国：赛事整体特征对比",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save_fig(fig, "09_长三角vs全国.png")


def chart_10_yrd_internal(df):
    """图10: 长三角内部四省赛事特征对比（2×2 子图）"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 子图1（左上）: 各省赛事数量 vs 每百万人赛事数
    ax = axes[0, 0]
    yrd_data = []
    for prov in YRD_PROVINCES:
        sub = df[df["省名称"] == prov]
        pop = PROVINCE_DATA[prov]["pop"]
        yrd_data.append({
            "省/市": prov,
            "赛事数量": len(sub),
            "每百万人": len(sub) / pop * 100,
        })
    yrd_df = pd.DataFrame(yrd_data)

    x = np.arange(len(YRD_PROVINCES))
    w = 0.35
    bars1 = ax.bar(x - w/2, yrd_df["赛事数量"], w, label="赛事数量",
                   color=COLOR_BLUE, edgecolor="white")
    ax2 = ax.twinx()
    bars2 = ax2.bar(x + w/2, yrd_df["每百万人"], w, label="每百万人赛事数",
                    color="#fdd0a2", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(YRD_PROVINCES, fontsize=11)
    ax.set_ylabel("赛事数量（场）", fontsize=10, color=COLOR_BLUE)
    ax2.set_ylabel("每百万人赛事数", fontsize=10, color="#d94801")
    ax.set_title("各省赛事数量 vs 密度", fontsize=12, fontweight="bold")
    ax.legend(loc="upper left", fontsize=9)
    ax2.legend(loc="upper right", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax.tick_params(axis="y", colors=COLOR_BLUE)
    ax2.tick_params(axis="y", colors="#d94801")

    # 子图2（右上）: 各省平均赛事规模（低于全国均值红色高亮）
    ax = axes[0, 1]
    national_avg = df["赛事规模"].mean()
    avgs = [df[df["省名称"] == p]["赛事规模"].mean() for p in YRD_PROVINCES]
    bars = ax.bar(YRD_PROVINCES, avgs, color=COLOR_RED, edgecolor="white")
    ax.axhline(y=national_avg, color=COLOR_BLUE, linestyle="--", linewidth=1.5,
               label=f"全国均值 {national_avg:.0f}人")
    ax.set_ylabel("平均参赛人数（人）", fontsize=10)
    ax.set_title("各省平均赛事规模（红=低于全国均值）", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, avgs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{val:.0f}", ha="center", fontsize=10, fontweight="bold")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 子图3（左下）: 级别结构堆叠柱状图
    ax = axes[1, 0]
    levels = ["国家级", "省级", "市级"]
    level_colors = ["#08306b", "#4292c6", "#deebf7"]
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
    ax.set_title("各省赛事级别结构（%）", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")
    ax.set_ylim(0, 110)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 子图4（右下）: 各省赛事月份分布（折线图）
    ax = axes[1, 1]
    months = list(range(1, 13))
    prov_colors = {"上海市": "#dc2626", "浙江省": "#1a56db",
                   "江苏省": "#059669", "安徽省": "#f59e0b"}
    for prov in YRD_PROVINCES:
        sub = df[df["省名称"] == prov]
        month_counts = sub["月份"].value_counts().sort_index()
        values = [month_counts.get(m, 0) for m in months]
        ax.plot(months, values, marker="o", linewidth=2, label=prov,
                color=prov_colors[prov], markersize=5)
    ax.set_xticks(months)
    ax.set_xticklabels([f"{m}月" for m in months], fontsize=9)
    ax.set_ylabel("赛事数量（场）", fontsize=10)
    ax.set_title("各省赛事月份分布", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle("长三角内部四省赛事特征对比", fontsize=15, fontweight="bold", y=1.0)
    fig.tight_layout()
    return _save_fig(fig, "10_长三角内部特征.png")


def chart_11_sh_vs_bj_sports(df):
    """图11: 上海 vs 北京 运动项目结构对比（1×2 布局：普及型 + 精英型）"""
    sh_df = df[df["省名称"] == "上海市"]
    bj_df = df[df["省名称"] == "北京市"]

    sh_counts = sh_df["运动项目"].value_counts()
    bj_counts = bj_df["运动项目"].value_counts()

    # 项目分类：大众普及型 vs 高端精英型
    popular_sports = ["足球", "篮球", "羽毛球", "乒乓球", "游泳", "网球", "排球", "田径", "跆拳道", "武术"]
    elite_sports = ["高尔夫球", "马术", "冰球", "高山滑雪", "击剑", "棒球", "花样滑冰", "网球"]

    def get_counts(sports_list, counts):
        return [counts.get(s, 0) for s in sports_list]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
    w = 0.38

    # --- 子图1（左）：大众普及型项目双柱对比 ---
    ax1 = axes[0]
    sh_pop = get_counts(popular_sports, sh_counts)
    bj_pop = get_counts(popular_sports, bj_counts)
    x = np.arange(len(popular_sports))
    ax1.bar(x - w/2, sh_pop, w, label="上海", color=COLOR_RED, edgecolor="white")
    ax1.bar(x + w/2, bj_pop, w, label="北京", color=COLOR_BLUE, edgecolor="white")
    ax1.set_xticks(x)
    ax1.set_xticklabels(popular_sports, rotation=30, ha="right", fontsize=10)
    ax1.set_ylabel("赛事数量（场）", fontsize=11)
    ax1.set_title("① 普及型项目：足球·篮球·游泳等大众运动", fontsize=12, fontweight="bold")
    ax1.legend(fontsize=10, loc="upper right")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    # 标注差值（仅显示数字与符号，不带"差"字）
    for i, (s, b) in enumerate(zip(sh_pop, bj_pop)):
        if s > 0 or b > 0:
            diff = s - b
            color = COLOR_RED if diff > 0 else COLOR_BLUE
            label = f"{diff:+d}" if diff != 0 else "0"
            top = max(s, b)
            if top > 0:
                ax1.text(i, top + 1, label, ha="center", fontsize=9, color=color, fontweight="bold")

    # --- 子图2（右）：高端精英型项目双柱对比 ---
    ax2 = axes[1]
    sh_eli = get_counts(elite_sports, sh_counts)
    bj_eli = get_counts(elite_sports, bj_counts)
    x = np.arange(len(elite_sports))
    ax2.bar(x - w/2, sh_eli, w, label="上海", color=COLOR_RED, edgecolor="white")
    ax2.bar(x + w/2, bj_eli, w, label="北京", color=COLOR_BLUE, edgecolor="white")
    ax2.set_xticks(x)
    ax2.set_xticklabels(elite_sports, rotation=30, ha="right", fontsize=10)
    ax2.set_ylabel("赛事数量（场）", fontsize=11)
    ax2.set_title("② 精英型项目：高尔夫·马术·冰雪等高门槛运动", fontsize=12, fontweight="bold")
    ax2.legend(fontsize=10, loc="upper right")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    for i, (s, b) in enumerate(zip(sh_eli, bj_eli)):
        if s > 0 or b > 0:
            diff = s - b
            color = COLOR_BLUE if diff > 0 else COLOR_RED
            label = f"{diff:+d}" if diff != 0 else "0"
            top = max(s, b)
            if top > 0:
                ax2.text(i, top + 1, label, ha="center", fontsize=9, color=color, fontweight="bold")

    fig.suptitle("上海 vs 北京：广度型 vs 高度型 赛事结构对比",
                 fontsize=14, fontweight="bold", y=1.0)
    fig.tight_layout()
    return _save_fig(fig, "11_上海vs北京项目对比.png")


def chart_12_big_population_provinces(prov_stats):
    """图12: 人口大省（≥5000万）赛事密度对比"""
    fig, ax = plt.subplots(figsize=(10, 6))

    big_pop = prov_stats[prov_stats["人口(万)"] >= 5000].sort_values("每百万人赛事数", ascending=True)
    national_avg = prov_stats["每百万人赛事数"].mean()

    colors = [COLOR_BLUE if v >= national_avg else COLOR_LIGHT
              for v in big_pop["每百万人赛事数"]]
    bars = ax.barh(range(len(big_pop)), big_pop["每百万人赛事数"].values,
                   color=colors, edgecolor="white")
    ax.set_yticks(range(len(big_pop)))
    ax.set_yticklabels(big_pop["省名称"].values, fontsize=11)
    ax.set_xlabel("每百万人赛事数（场）", fontsize=12)
    ax.set_title("人口大省（≥5000万）赛事密度对比", fontsize=14, fontweight="bold", pad=15)

    ax.axvline(x=national_avg, color=COLOR_RED, linestyle="--", linewidth=1.5,
               label=f"全国均值 {national_avg:.1f}")
    ax.legend(fontsize=10)

    for bar, val in zip(bars, big_pop["每百万人赛事数"].values):
        ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}", va="center", fontsize=10, color=COLOR_DARK)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "12_人口大省.png")


def chart_13_small_population_provinces(prov_stats):
    """图13: 人口小省（<2000万）赛事密度对比"""
    fig, ax = plt.subplots(figsize=(10, 5))

    small_pop = prov_stats[prov_stats["人口(万)"] < 2000].sort_values("每百万人赛事数", ascending=True)
    national_avg = prov_stats["每百万人赛事数"].mean()

    colors = [COLOR_BLUE if v >= national_avg else COLOR_LIGHT
              for v in small_pop["每百万人赛事数"]]
    bars = ax.barh(range(len(small_pop)), small_pop["每百万人赛事数"].values,
                   color=colors, edgecolor="white")
    ax.set_yticks(range(len(small_pop)))
    ax.set_yticklabels(small_pop["省名称"].values, fontsize=11)
    ax.set_xlabel("每百万人赛事数（场）", fontsize=12)
    ax.set_title("人口小省（<2000万）赛事密度对比", fontsize=14, fontweight="bold", pad=15)

    ax.axvline(x=national_avg, color=COLOR_RED, linestyle="--", linewidth=1.5,
               label=f"全国均值 {national_avg:.1f}")
    ax.legend(fontsize=10)

    for bar, val in zip(bars, small_pop["每百万人赛事数"].values):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}", va="center", fontsize=10, color=COLOR_DARK)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "13_人口小省.png")


def run_all_visualizations(df, prov_stats):
    """生成全部 13 张可视化图表（均由代码生成，无外部静态文件）"""
    ensure_dirs()
    print("\n[可视化] 开始生成 13 张图表...")

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
    chart_12_big_population_provinces(prov_stats)
    chart_13_small_population_provinces(prov_stats)

    print(f"\n[可视化] 全部 13 张图表已生成至: {CHART_DIR}")
