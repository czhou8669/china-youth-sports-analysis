#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualization chart generation module.
Uses matplotlib to generate all analysis charts, output to output/charts/.
Chart numbering is consistent with PDF report references.

Note: Charts 01 and 07 are China province choropleth maps, drawn by reading
maps/china_provinces.json and rendering with matplotlib Polygon — no external
GIS library dependency.
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

# Initialize font
setup_chinese_font()

# ========== Translation dictionaries (Chinese → English) ==========

SPORT_EN = {
    "足球": "Football", "篮球": "Basketball", "羽毛球": "Badminton",
    "乒乓球": "Table Tennis", "游泳": "Swimming", "网球": "Tennis",
    "排球": "Volleyball", "田径": "Track & Field", "跆拳道": "Taekwondo",
    "武术": "Martial Arts", "高尔夫球": "Golf", "马术": "Equestrian",
    "冰球": "Ice Hockey", "高山滑雪": "Alpine Skiing", "击剑": "Fencing",
    "棒球": "Baseball", "花样滑冰": "Figure Skating", "攀岩": "Rock Climbing",
    "街舞": "Breakdancing", "轮滑": "Roller Skating", "空手道": "Karate",
    "射箭": "Archery", "柔道": "Judo", "摔跤": "Wrestling",
    "拳击": "Boxing", "自行车": "Cycling", "健美操": "Aerobics",
    "体育舞蹈": "Dance Sport", "棋类": "Chess", "龙舟": "Dragon Boat",
    "毽球": "Shuttlecock", "门球": "Gateball", "台球": "Billiards",
    "保龄球": "Bowling", "橄榄球": "Rugby", "手球": "Handball",
    "曲棍球": "Hockey", "水球": "Water Polo", "潜水": "Diving",
    "滑雪": "Skiing", "滑冰": "Skating", "未知": "Unknown",
    # Extended sub-categories found in TOP 15 / charts
    "综合": "Multi-Discipline", "武术套路": "Wushu Routines",
    "武术散打": "Wushu Sanda", "围棋": "Go (Weiqi)", "象棋": "Chinese Chess",
    "国际象棋": "Chess", "体操": "Gymnastics", "举重": "Weightlifting",
    "射击": "Shooting", "赛艇": "Rowing", "皮划艇": "Canoeing/Kayaking",
}

PROVINCE_EN = {
    "北京市": "Beijing", "上海市": "Shanghai", "天津市": "Tianjin", "重庆市": "Chongqing",
    "浙江省": "Zhejiang", "江苏省": "Jiangsu", "安徽省": "Anhui",
    "广东省": "Guangdong", "福建省": "Fujian", "山东省": "Shandong",
    "河南省": "Henan", "湖北省": "Hubei", "湖南省": "Hunan",
    "四川省": "Sichuan", "河北省": "Hebei", "山西省": "Shanxi",
    "辽宁省": "Liaoning", "吉林省": "Jilin", "黑龙江省": "Heilongjiang",
    "陕西省": "Shaanxi", "甘肃省": "Gansu", "青海省": "Qinghai",
    "云南省": "Yunnan", "贵州省": "Guizhou", "海南省": "Hainan",
    "江西省": "Jiangxi", "内蒙古自治区": "Inner Mongolia",
    "新疆维吾尔自治区": "Xinjiang", "西藏自治区": "Tibet",
    "广西壮族自治区": "Guangxi", "宁夏回族自治区": "Ningxia",
}

LEVEL_EN = {"国家级": "National", "省级": "Provincial", "市级": "Municipal"}

# Province name mapping for map labels (short Chinese → English)
MAP_LABEL_EN = {
    "北京": "Beijing", "上海": "Shanghai", "天津": "Tianjin", "重庆": "Chongqing",
    "浙江": "Zhejiang", "江苏": "Jiangsu", "安徽": "Anhui",
    "广东": "Guangdong", "福建": "Fujian", "山东": "Shandong",
    "河南": "Henan", "湖北": "Hubei", "湖南": "Hunan",
    "四川": "Sichuan", "河北": "Hebei", "山西": "Shanxi",
    "辽宁": "Liaoning", "吉林": "Jilin", "黑龙江": "Heilongjiang",
    "陕西": "Shaanxi", "甘肃": "Gansu", "青海": "Qinghai",
    "云南": "Yunnan", "贵州": "Guizhou", "海南": "Hainan",
    "江西": "Jiangxi", "内蒙古": "Inner Mongolia",
    "新疆": "Xinjiang", "西藏": "Tibet",
    "广西": "Guangxi", "宁夏": "Ningxia",
    "台湾": "Taiwan", "香港": "Hong Kong", "澳门": "Macao",
}


def _en_sport(name):
    """Translate sport name to English."""
    return SPORT_EN.get(name, name)


def _en_prov(name):
    """Translate province name to English."""
    return PROVINCE_EN.get(name, name)


def _en_sports_list(names):
    """Translate a list of sport names."""
    return [_en_sport(s) for s in names]


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

    # Label provinces (translate to English)
    for feat in geo_data["features"]:
        name = feat["properties"]["name"]
        if not name:
            continue
        # Strip province-level suffixes to get a short Chinese form
        # e.g. "北京市" → "北京", "内蒙古自治区" → "内蒙古", "广西壮族自治区" → "广西"
        short = name
        for suffix in ["壮族自治区", "维吾尔自治区", "回族自治区", "特别行政区", "自治区", "省", "市"]:
            if short.endswith(suffix):
                short = short[: -len(suffix)]
                break
        # Translate to English
        label = MAP_LABEL_EN.get(short, short)
        centroid = feat["properties"].get("center") or feat["properties"].get("centroid")
        if centroid:
            ax.text(centroid[0], centroid[1], label,
                    ha="center", va="center", fontsize=6.5, color="#1e293b")

    ax.set_xlim(73, 135)
    ax.set_ylim(18, 54)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)

    # Custom legend
    from matplotlib.patches import Patch
    legend_patches = []
    n_bins = len(bins)
    for i, label in enumerate(legend_labels):
        legend_patches.append(Patch(facecolor=cmap((i + 1) / n_bins),
                                    edgecolor="white", label=label))
    ax.legend(handles=legend_patches, loc="lower left", fontsize=8,
              frameon=False, title="Event Count", title_fontsize=8)


def _save_fig(fig, filename):
    """Save chart"""
    path = os.path.join(CHART_DIR, filename)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [Chart] Saved: {filename}")
    return path


# ========== 图表函数 ==========

def chart_01_province_distribution(df):
    """Chart 01: National youth sports event provincial distribution (heatmap)"""
    fig, ax = plt.subplots(figsize=(12, 9))

    prov_counts = df["省名称"].value_counts()
    value_dict = prov_counts.to_dict()

    # 5-level color scale: 0-30 / 31-100 / 101-200 / 201-400 / 401+
    bins = [31, 101, 201, 401]
    cmap = LinearSegmentedColormap.from_list(
        "blue_white",
        ["#deebf7", "#9ecae1", "#4292c6", "#08519c", "#08306b"]
    )
    legend_labels = ["0–30", "31–100", "101–200", "201–400", "401+"]

    geo_data = _load_geojson()
    _draw_china_map(ax, geo_data, value_dict, bins, cmap, legend_labels,
                    title=None)
    fig.text(0.5, 0.91, "Source: National Mass Sports Events Database (2023-2024, 5,325 events total)",
             ha="center", fontsize=10, color=COLOR_LIGHT)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return _save_fig(fig, "01_省份分布地图.png")


def chart_02_sport_popularity(df):
    """Chart 02: Sports popularity TOP 15"""
    fig, ax = plt.subplots(figsize=(12, 6))

    sport_counts = df["运动项目"].value_counts().head(15)
    # Racket sports red, team ball sports blue, others gray
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
    ax.set_xticklabels(_en_sports_list(sport_counts.index), rotation=45, ha="right", fontsize=10)
    ax.set_ylabel("Number of Events", fontsize=11)
    ax.set_title("Sports Popularity TOP 15 (Red=Racket, Blue=Team Ball)", fontsize=14, fontweight="bold", pad=15)

    for bar, val in zip(bars, sport_counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{val}", ha="center", fontsize=9, color=COLOR_DARK)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "02_运动项目热度.png")


def chart_03_monthly_distribution(df):
    """Chart 03: Monthly event distribution"""
    fig, ax = plt.subplots(figsize=(10, 5))

    month_counts = df["月份"].value_counts().sort_index()
    months = list(range(1, 13))
    values = [month_counts.get(m, 0) for m in months]

    # Highlight summer/winter breaks
    colors = []
    for m in months:
        if m in [7, 8]:
            colors.append(COLOR_RED)      # Summer peak
        elif m in [1, 2]:
            colors.append(COLOR_GREEN)    # Winter trough
        elif m in [5, 10, 11]:
            colors.append(COLOR_ACCENT)   # Secondary peak
        else:
            colors.append(COLOR_BLUE)

    bars = ax.bar(months, values, color=colors, edgecolor="white", width=0.7)
    ax.set_xticks(months)
    ax.set_xticklabels([f"{m}" for m in months], fontsize=10)
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Number of Events", fontsize=11)
    ax.set_title("Annual Monthly Event Distribution (Red=Summer Peak, Green=Winter Trough, Orange=Secondary Peak)",
                 fontsize=12, fontweight="bold", pad=15)

    for bar, val in zip(bars, values):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
                    f"{val}", ha="center", fontsize=9, color=COLOR_DARK)

    # Annotate November Shanghai anomaly
    nov_total = month_counts.get(11, 0)
    sh_nov = len(df[(df["月份"] == 11) & (df["省名称"] == "上海市")])
    if nov_total > 0:
        ax.annotate(f"Shanghai: {sh_nov/nov_total*100:.0f}% of Nov",
                    xy=(11, nov_total), xytext=(11, nov_total + 120),
                    fontsize=9, ha="center", color=COLOR_RED,
                    arrowprops=dict(arrowstyle="->", color=COLOR_RED))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "03_月份分布.png")


def chart_04_municipality_comparison(df):
    """Chart 04: Municipality event model comparison (breadth vs height)"""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    cities = MUNICIPALITIES
    city_labels = [_en_prov(c) for c in cities]
    city_colors = [COLOR_RED, COLOR_BLUE, COLOR_BODY, COLOR_LIGHT]

    # Subplot 1: Total events vs average scale
    ax = axes[0]
    totals = [len(df[df["省名称"] == c]) for c in cities]
    avgs = [df[df["省名称"] == c]["赛事规模"].mean() for c in cities]
    x = np.arange(len(cities))
    w = 0.35
    ax.bar(x - w/2, totals, w, label="Total Events", color=COLOR_BLUE, edgecolor="white")
    ax.bar(x + w/2, avgs, w, label="Avg Scale", color=COLOR_RED, edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(city_labels, fontsize=10)
    ax.set_title("Total Events vs Avg Scale", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Subplot 2: Median comparison
    ax = axes[1]
    medians = [df[df["省名称"] == c]["赛事规模"].median() for c in cities]
    bars = ax.bar(city_labels, medians, color=city_colors, edgecolor="white")
    ax.set_title("Median Event Scale", fontsize=12, fontweight="bold")
    ax.set_ylabel("Participants", fontsize=10)
    for bar, val in zip(bars, medians):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{val:.0f}", ha="center", fontsize=10, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Subplot 3: Level structure stacked bar
    ax = axes[2]
    levels = ["国家级", "省级", "市级"]
    level_labels = ["National", "Provincial", "Municipal"]
    level_colors = [COLOR_RED, COLOR_ACCENT, COLOR_BLUE]
    bottom = np.zeros(len(cities))
    for level, lc, ll in zip(levels, level_colors, level_labels):
        vals = []
        for c in cities:
            sub = df[df["省名称"] == c]
            total = len(sub)
            val = len(sub[sub["赛事级别"] == level]) / total * 100 if total > 0 else 0
            vals.append(val)
        ax.bar(city_labels, vals, bottom=bottom, label=ll, color=lc, edgecolor="white")
        bottom += np.array(vals)
    ax.set_title("Event Level Structure (%)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Share (%)", fontsize=10)
    ax.legend(fontsize=9, loc="upper right")
    ax.set_ylim(0, 110)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle("Municipality Event Model Divergence: Breadth (Shanghai) vs Height (Beijing)",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save_fig(fig, "04_直辖市对比.png")


def chart_05_consumption_structure(df):
    """Chart 05: Consumption structure divergence (racket vs team ball sports)"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    racquet = df[df["运动项目"].isin(RACQUET_SPORTS)]
    team_ball = df[df["运动项目"].isin(TEAM_BALL_SPORTS)]

    categories = ["Racket\n(Tennis/Bdm/Tennis)", "Team Ball\n(Foot/Bball/Vball)"]
    counts = [len(racquet), len(team_ball)]
    avgs = [racquet["赛事规模"].mean(), team_ball["赛事规模"].mean()]

    x = np.arange(len(categories))
    w = 0.35
    ax = axes[0]
    bars1 = ax.bar(x - w / 2, counts, w, label="Event Count", color=COLOR_ACCENT, edgecolor="white")
    ax2 = ax.twinx()
    bars2 = ax2.bar(x + w / 2, avgs, w, label="Avg Scale", color=COLOR_BLUE, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylabel("Number of Events", fontsize=10, color=COLOR_ACCENT)
    ax2.set_ylabel("Average Scale (participants)", fontsize=10, color=COLOR_BLUE)
    ax.set_ylim(0, max(counts) * 1.15)
    ax2.set_ylim(0, max(avgs) * 1.15)
    ax.tick_params(axis="y", colors=COLOR_ACCENT)
    ax2.tick_params(axis="y", colors=COLOR_BLUE)
    ax.set_title("Racket vs Team Ball Sports", fontsize=13, fontweight="bold")

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
    sport_labels = _en_sports_list(sports)
    sport_avgs = [df[df["运动项目"] == s]["赛事规模"].mean() for s in sports]
    sport_counts = [len(df[df["运动项目"] == s]) for s in sports]
    colors = [COLOR_RED] * 3 + [COLOR_BLUE] * 3

    bars = ax.bar(sport_labels, sport_avgs, color=colors, edgecolor="white")
    ax.set_ylabel("Average Event Scale (participants)", fontsize=10)
    ax.set_title("Average Scale by Sport", fontsize=13, fontweight="bold")
    for bar, avg, cnt in zip(bars, sport_avgs, sport_counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{avg:.0f}\n({cnt} events)", ha="center", fontsize=9, color=COLOR_DARK)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle("Consumption Structure Diverges by Sport Type", fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save_fig(fig, "05_消费结构分化.png")


def chart_06_emerging_sports(df):
    """Chart 06: Emerging sports event count and scale"""
    fig, ax = plt.subplots(figsize=(10, 5))

    sports = EMERGING_SPORTS
    sport_labels = _en_sports_list(sports)
    counts = [len(df[df["运动项目"] == s]) for s in sports]
    avgs = [df[df["运动项目"] == s]["赛事规模"].mean() if c > 0 else 0 for s, c in zip(sports, counts)]

    x = np.arange(len(sports))
    w = 0.35
    bars1 = ax.bar(x - w/2, counts, w, label="Event Count", color=COLOR_BLUE, edgecolor="white")
    ax2 = ax.twinx()
    bars2 = ax2.bar(x + w/2, avgs, w, label="Avg Scale", color=COLOR_RED, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(sport_labels, fontsize=11)
    ax.set_ylabel("Number of Events", fontsize=10, color=COLOR_BLUE)
    ax2.set_ylabel("Average Scale (participants)", fontsize=10, color=COLOR_RED)
    ax.set_title("Emerging Sports: Event Count and Average Scale", fontsize=14, fontweight="bold", pad=15)

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
    """Chart 07: Provincial event density map (events per million people)"""
    fig, ax = plt.subplots(figsize=(12, 9))

    value_dict = prov_stats.set_index("省名称")["每百万人赛事数"].to_dict()

    # 5-level color scale: 0-3 / 3-8 / 8-15 / 15-25 / 25+
    bins = [3, 8, 15, 25]
    cmap = LinearSegmentedColormap.from_list(
        "orange_white",
        ["#fff5eb", "#fdd0a2", "#fd8d3c", "#d94801", "#7f2704"]
    )
    legend_labels = ["0–3", "3–8", "8–15", "15–25", "25+"]

    geo_data = _load_geojson()
    _draw_china_map(ax, geo_data, value_dict, bins, cmap, legend_labels,
                    title="Youth Sports Event Density (per million people)")
    fig.text(0.5, 0.91, "Event supply level after controlling for population size",
             ha="center", fontsize=10, color=COLOR_LIGHT)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return _save_fig(fig, "07_赛事密度地图.png")


def chart_08_gdp_scatter(prov_stats):
    """Chart 08: Per-capita GDP vs event density scatter plot + quadrants"""
    fig, ax = plt.subplots(figsize=(10, 8))

    data = prov_stats.dropna(subset=["人均GDP(万)", "每百万人赛事数"]).copy()
    corr = data[["人均GDP(万)", "每百万人赛事数"]].corr().iloc[0, 1]

    gdp_med = data["人均GDP(万)"].median()
    dens_med = data["每百万人赛事数"].median()

    # Quadrant coloring
    colors = []
    for _, r in data.iterrows():
        if r["人均GDP(万)"] >= gdp_med and r["每百万人赛事数"] >= dens_med:
            colors.append(COLOR_BLUE)    # Q1: High-High
        elif r["人均GDP(万)"] < gdp_med and r["每百万人赛事数"] >= dens_med:
            colors.append(COLOR_GREEN)   # Q2: Low-High (policy-driven)
        elif r["人均GDP(万)"] < gdp_med and r["每百万人赛事数"] < dens_med:
            colors.append(COLOR_LIGHT)   # Q3: Low-Low
        else:
            colors.append(COLOR_RED)     # Q4: High-Low (anomaly)

    ax.scatter(data["人均GDP(万)"], data["每百万人赛事数"], c=colors, s=80, edgecolors="white", zorder=5)

    # Label key provinces
    label_provinces = ["上海市", "北京市", "浙江省", "广东省", "江苏省", "福建省",
                       "山东省", "河南省", "新疆维吾尔自治区", "西藏自治区", "四川省"]
    for _, r in data.iterrows():
        if r["省名称"] in label_provinces:
            ax.annotate(_en_prov(r["省名称"]), (r["人均GDP(万)"], r["每百万人赛事数"]),
                        fontsize=8, ha="left", va="bottom",
                        xytext=(5, 5), textcoords="offset points")

    # Median lines
    ax.axvline(x=gdp_med, color=COLOR_LIGHT, linestyle="--", linewidth=1, alpha=0.5)
    ax.axhline(y=dens_med, color=COLOR_LIGHT, linestyle="--", linewidth=1, alpha=0.5)

    # Quadrant labels
    ax.text(0.98, 0.98, "Q1: High GDP + High Density", transform=ax.transAxes, fontsize=9,
            ha="right", va="top", color=COLOR_BLUE, fontweight="bold")
    ax.text(0.02, 0.98, "Q2: Low GDP + High Density\n(Policy-driven)", transform=ax.transAxes, fontsize=9,
            ha="left", va="top", color=COLOR_GREEN, fontweight="bold")
    ax.text(0.02, 0.02, "Q3: Low GDP + Low Density", transform=ax.transAxes, fontsize=9,
            ha="left", va="bottom", color=COLOR_LIGHT, fontweight="bold")
    ax.text(0.98, 0.02, "Q4: High GDP + Low Density\n(Data blind spot?)", transform=ax.transAxes, fontsize=9,
            ha="right", va="bottom", color=COLOR_RED, fontweight="bold")

    ax.set_xlabel("Per-capita GDP (10K CNY)", fontsize=12)
    ax.set_ylabel("Events per Million People", fontsize=12)
    ax.set_title(f"Per-capita GDP vs Event Density (r = {corr:.3f})", fontsize=14, fontweight="bold", pad=15)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "08_GDP与赛事密度散点图.png")


def chart_09_yrd_vs_national(df):
    """Chart 09: YRD vs National overall comparison (pie + density bar + avg scale bar)"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    yrd = df[df["省名称"].isin(YRD_PROVINCES)]
    national = df

    # Subplot 1: YRD share of national events (pie)
    ax = axes[0]
    yrd_share = len(yrd) / len(national) * 100
    other_share = 100 - yrd_share
    ax.pie([yrd_share, other_share],
           labels=["YRD", "Other Provinces"],
           colors=[COLOR_BLUE, "#deebf7"],
           autopct="%.1f%%", startangle=90,
           textprops={"fontsize": 11, "fontweight": "bold"})
    ax.set_title("YRD Share of National Events", fontsize=12, fontweight="bold")

    # Subplot 2: Events per million people comparison
    ax = axes[1]
    yrd_pop = sum(PROVINCE_DATA[p]["pop"] for p in YRD_PROVINCES)
    total_pop = sum(v["pop"] for v in PROVINCE_DATA.values())
    yrd_density = len(yrd) / yrd_pop * 100
    nat_density = len(national) / total_pop * 100
    bars = ax.bar(["YRD", "National Avg"], [yrd_density, nat_density],
                  color=[COLOR_BLUE, "#deebf7"], edgecolor="white", width=0.5)
    ax.set_ylabel("Events per Million People", fontsize=10)
    ax.set_title("Event Density Comparison", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, [yrd_density, nat_density]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{val:.1f}", ha="center", fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(yrd_density, nat_density) * 1.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Subplot 3: Average event scale comparison
    ax = axes[2]
    yrd_avg = yrd["赛事规模"].mean()
    nat_avg = national["赛事规模"].mean()
    bars = ax.bar(["YRD", "National Avg"], [yrd_avg, nat_avg],
                  color=[COLOR_BLUE, "#deebf7"], edgecolor="white", width=0.5)
    ax.set_ylabel("Average Participants", fontsize=10)
    ax.set_title("Average Event Scale", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, [yrd_avg, nat_avg]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{val:.0f}", ha="center", fontsize=12, fontweight="bold")
    ax.set_ylim(0, max(yrd_avg, nat_avg) * 1.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle("YRD vs National: Overall Event Characteristics",
                 fontsize=14, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save_fig(fig, "09_长三角vs全国.png")


def chart_10_yrd_internal(df):
    """Chart 10: YRD internal four-province comparison (2x2 subplots)"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    yrd_labels = [_en_prov(p) for p in YRD_PROVINCES]

    # Subplot 1 (top-left): Event count vs density per province
    ax = axes[0, 0]
    yrd_data = []
    for prov in YRD_PROVINCES:
        sub = df[df["省名称"] == prov]
        pop = PROVINCE_DATA[prov]["pop"]
        yrd_data.append({
            "Province": _en_prov(prov),
            "Events": len(sub),
            "PerMillion": len(sub) / pop * 100,
        })
    yrd_df = pd.DataFrame(yrd_data)

    x = np.arange(len(YRD_PROVINCES))
    w = 0.35
    bars1 = ax.bar(x - w/2, yrd_df["Events"], w, label="Event Count",
                   color=COLOR_BLUE, edgecolor="white")
    ax2 = ax.twinx()
    bars2 = ax2.bar(x + w/2, yrd_df["PerMillion"], w, label="Per Million",
                    color="#fdd0a2", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(yrd_labels, fontsize=11)
    ax.set_ylabel("Number of Events", fontsize=10, color=COLOR_BLUE)
    ax2.set_ylabel("Events per Million People", fontsize=10, color="#d94801")
    ax.set_title("Event Count vs Density by Province", fontsize=12, fontweight="bold")
    ax.legend(loc="upper left", fontsize=9)
    ax2.legend(loc="upper right", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax.tick_params(axis="y", colors=COLOR_BLUE)
    ax2.tick_params(axis="y", colors="#d94801")

    # Subplot 2 (top-right): Average event scale (red = below national average)
    ax = axes[0, 1]
    national_avg = df["赛事规模"].mean()
    avgs = [df[df["省名称"] == p]["赛事规模"].mean() for p in YRD_PROVINCES]
    bars = ax.bar(yrd_labels, avgs, color=COLOR_RED, edgecolor="white")
    ax.axhline(y=national_avg, color=COLOR_BLUE, linestyle="--", linewidth=1.5,
               label=f"National Avg {national_avg:.0f}")
    ax.set_ylabel("Average Participants", fontsize=10)
    ax.set_title("Average Event Scale (Red = Below National Avg)", fontsize=12, fontweight="bold")
    for bar, val in zip(bars, avgs):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"{val:.0f}", ha="center", fontsize=10, fontweight="bold")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Subplot 3 (bottom-left): Level structure stacked bar
    ax = axes[1, 0]
    levels = ["国家级", "省级", "市级"]
    level_labels = ["National", "Provincial", "Municipal"]
    level_colors = ["#08306b", "#4292c6", "#deebf7"]
    bottom = np.zeros(len(YRD_PROVINCES))
    for level, lc, ll in zip(levels, level_colors, level_labels):
        vals = []
        for prov in YRD_PROVINCES:
            sub = df[df["省名称"] == prov]
            total = len(sub)
            val = len(sub[sub["赛事级别"] == level]) / total * 100 if total > 0 else 0
            vals.append(val)
        ax.bar(yrd_labels, vals, bottom=bottom, label=ll, color=lc, edgecolor="white")
        bottom += np.array(vals)
    ax.set_ylabel("Share (%)", fontsize=10)
    ax.set_title("Event Level Structure by Province (%)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")
    ax.set_ylim(0, 110)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Subplot 4 (bottom-right): Monthly distribution by province (line chart)
    ax = axes[1, 1]
    months = list(range(1, 13))
    prov_colors = {"上海市": "#dc2626", "浙江省": "#1a56db",
                   "江苏省": "#059669", "安徽省": "#f59e0b"}
    for prov in YRD_PROVINCES:
        sub = df[df["省名称"] == prov]
        month_counts = sub["月份"].value_counts().sort_index()
        values = [month_counts.get(m, 0) for m in months]
        ax.plot(months, values, marker="o", linewidth=2, label=_en_prov(prov),
                color=prov_colors[prov], markersize=5)
    ax.set_xticks(months)
    ax.set_xticklabels([f"{m}" for m in months], fontsize=9)
    ax.set_xlabel("Month", fontsize=10)
    ax.set_ylabel("Number of Events", fontsize=10)
    ax.set_title("Monthly Event Distribution by Province", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.suptitle("YRD Internal Four-Province Comparison", fontsize=15, fontweight="bold", y=1.0)
    fig.tight_layout()
    return _save_fig(fig, "10_长三角内部特征.png")


def chart_11_sh_vs_bj_sports(df):
    """Chart 11: Shanghai vs Beijing sports structure comparison (1x2: popular + elite)"""
    sh_df = df[df["省名称"] == "上海市"]
    bj_df = df[df["省名称"] == "北京市"]

    sh_counts = sh_df["运动项目"].value_counts()
    bj_counts = bj_df["运动项目"].value_counts()

    # Sport categories: popular vs elite
    popular_sports = ["足球", "篮球", "羽毛球", "乒乓球", "游泳", "网球", "排球", "田径", "跆拳道", "武术"]
    elite_sports = ["高尔夫球", "马术", "冰球", "高山滑雪", "击剑", "棒球", "花样滑冰", "网球"]

    popular_labels = _en_sports_list(popular_sports)
    elite_labels = _en_sports_list(elite_sports)

    def get_counts(sports_list, counts):
        return [counts.get(s, 0) for s in sports_list]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6.5))
    w = 0.38

    # --- Subplot 1 (left): Popular sports dual bar ---
    ax1 = axes[0]
    sh_pop = get_counts(popular_sports, sh_counts)
    bj_pop = get_counts(popular_sports, bj_counts)
    x = np.arange(len(popular_sports))
    ax1.bar(x - w/2, sh_pop, w, label="Shanghai", color=COLOR_RED, edgecolor="white")
    ax1.bar(x + w/2, bj_pop, w, label="Beijing", color=COLOR_BLUE, edgecolor="white")
    ax1.set_xticks(x)
    ax1.set_xticklabels(popular_labels, rotation=30, ha="right", fontsize=10)
    ax1.set_ylabel("Number of Events", fontsize=11)
    ax1.set_title("1. Popular Sports: Football, Basketball, Swimming, etc.", fontsize=12, fontweight="bold")
    ax1.legend(fontsize=10, loc="upper right")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    # Annotate difference (number + sign only)
    for i, (s, b) in enumerate(zip(sh_pop, bj_pop)):
        if s > 0 or b > 0:
            diff = s - b
            color = COLOR_RED if diff > 0 else COLOR_BLUE
            label = f"{diff:+d}" if diff != 0 else "0"
            top = max(s, b)
            if top > 0:
                ax1.text(i, top + 1, label, ha="center", fontsize=9, color=color, fontweight="bold")

    # --- Subplot 2 (right): Elite sports dual bar ---
    ax2 = axes[1]
    sh_eli = get_counts(elite_sports, sh_counts)
    bj_eli = get_counts(elite_sports, bj_counts)
    x = np.arange(len(elite_sports))
    ax2.bar(x - w/2, sh_eli, w, label="Shanghai", color=COLOR_RED, edgecolor="white")
    ax2.bar(x + w/2, bj_eli, w, label="Beijing", color=COLOR_BLUE, edgecolor="white")
    ax2.set_xticks(x)
    ax2.set_xticklabels(elite_labels, rotation=30, ha="right", fontsize=10)
    ax2.set_ylabel("Number of Events", fontsize=11)
    ax2.set_title("2. Elite Sports: Golf, Equestrian, Ice & Snow, etc.", fontsize=12, fontweight="bold")
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

    fig.suptitle("Shanghai vs Beijing: Breadth vs Height Event Structure",
                 fontsize=14, fontweight="bold", y=1.0)
    fig.tight_layout()
    return _save_fig(fig, "11_上海vs北京项目对比.png")


def chart_12_big_population_provinces(prov_stats):
    """Chart 12: Populous provinces (>=50M) event density comparison"""
    fig, ax = plt.subplots(figsize=(10, 6))

    big_pop = prov_stats[prov_stats["人口(万)"] >= 5000].sort_values("每百万人赛事数", ascending=True)
    national_avg = prov_stats["每百万人赛事数"].mean()

    colors = [COLOR_BLUE if v >= national_avg else COLOR_LIGHT
              for v in big_pop["每百万人赛事数"]]
    bars = ax.barh(range(len(big_pop)), big_pop["每百万人赛事数"].values,
                   color=colors, edgecolor="white")
    ax.set_yticks(range(len(big_pop)))
    ax.set_yticklabels([_en_prov(p) for p in big_pop["省名称"].values], fontsize=11)
    ax.set_xlabel("Events per Million People", fontsize=12)
    ax.set_title("Populous Provinces (Pop. >= 50M) Event Density", fontsize=14, fontweight="bold", pad=15)

    ax.axvline(x=national_avg, color=COLOR_RED, linestyle="--", linewidth=1.5,
               label=f"National Avg {national_avg:.1f}")
    ax.legend(fontsize=10)

    for bar, val in zip(bars, big_pop["每百万人赛事数"].values):
        ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}", va="center", fontsize=10, color=COLOR_DARK)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "12_人口大省.png")


def chart_13_small_population_provinces(prov_stats):
    """Chart 13: Small provinces (<20M) event density comparison"""
    fig, ax = plt.subplots(figsize=(10, 5))

    small_pop = prov_stats[prov_stats["人口(万)"] < 2000].sort_values("每百万人赛事数", ascending=True)
    national_avg = prov_stats["每百万人赛事数"].mean()

    colors = [COLOR_BLUE if v >= national_avg else COLOR_LIGHT
              for v in small_pop["每百万人赛事数"]]
    bars = ax.barh(range(len(small_pop)), small_pop["每百万人赛事数"].values,
                   color=colors, edgecolor="white")
    ax.set_yticks(range(len(small_pop)))
    ax.set_yticklabels([_en_prov(p) for p in small_pop["省名称"].values], fontsize=11)
    ax.set_xlabel("Events per Million People", fontsize=12)
    ax.set_title("Small Provinces (Pop. < 20M) Event Density", fontsize=14, fontweight="bold", pad=15)

    ax.axvline(x=national_avg, color=COLOR_RED, linestyle="--", linewidth=1.5,
               label=f"National Avg {national_avg:.1f}")
    ax.legend(fontsize=10)

    for bar, val in zip(bars, small_pop["每百万人赛事数"].values):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}", va="center", fontsize=10, color=COLOR_DARK)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return _save_fig(fig, "13_人口小省.png")


def run_all_visualizations(df, prov_stats):
    """Generate all 13 visualization charts (code-generated, no external static files)"""
    ensure_dirs()
    print("\n[Visualization] Generating 13 charts...")

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

    print(f"\n[Visualization] All 13 charts generated in: {CHART_DIR}")
