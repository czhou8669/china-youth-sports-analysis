#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目配置文件
包含路径设置、中文字体配置、人口经济常量等
"""

import os
import platform
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# ========== 路径配置 ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CHART_DIR = os.path.join(OUTPUT_DIR, "charts")
REPORT_DIR = os.path.join(OUTPUT_DIR, "reports")
MAP_DIR = os.path.join(BASE_DIR, "maps")

# 原始数据文件名（需放入 data/ 目录）
RAW_DATA_FILE = "全国群众体育赛事、青少年体育赛事、马拉松赛事信息.xlsx"
RAW_DATA_PATH = os.path.join(DATA_DIR, RAW_DATA_FILE)

# 清洗后数据输出路径
CLEANED_DATA_PATH = os.path.join(DATA_DIR, "青少年体育赛事_清洗后.csv")

# ========== 中文字体配置 ==========
def setup_chinese_font():
    """配置 matplotlib 中文字体，自动适配 macOS / Windows / Linux"""
    system = platform.system()

    font_candidates = {
        "Darwin": [  # macOS
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ],
        "Windows": [
            "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",   # 黑体
            "C:/Windows/Fonts/simsun.ttc",   # 宋体
        ],
        "Linux": [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ],
    }

    for font_path in font_candidates.get(system, []):
        if os.path.exists(font_path):
            plt.rcParams["font.sans-serif"] = [FontProperties(fname=font_path).get_name()]
            plt.rcParams["axes.unicode_minus"] = False
            return font_path

    # 兜底：尝试通用字体名
    plt.rcParams["font.sans-serif"] = ["SimHei", "PingFang SC", "Microsoft YaHei", "WenQuanYi Zen Hei"]
    plt.rcParams["axes.unicode_minus"] = False
    return None


# ========== 颜色配置 ==========
# 中国股市惯例：涨红跌绿。此处也用于一般高亮
COLOR_RED = "#dc2626"       # 涨/高
COLOR_GREEN = "#059669"     # 跌/低
COLOR_BLUE = "#1a56db"      # 主色
COLOR_DARK = "#1e293b"      # 深色文字
COLOR_BODY = "#334155"      # 正文
COLOR_LIGHT = "#64748b"     # 浅色文字
COLOR_BG = "#f1f5f9"        # 背景
COLOR_ACCENT = "#f59e0b"    # 强调
COLOR_PALETTE = ["#1a56db", "#dc2626", "#059669", "#f59e0b", "#8b5cf6",
                 "#ec4899", "#06b6d4", "#84cc16", "#f97316", "#6366f1"]


# ========== 人口与经济常量 ==========
# 数据来源：国家统计局2023年末常住人口（万人）、人均GDP（万元）
PROVINCE_DATA = {
    "北京市":         {"pop": 2185.8, "gdp_per": 19.03},
    "天津市":         {"pop": 1363.0, "gdp_per": 12.28},
    "河北省":         {"pop": 7393.0, "gdp_per": 5.93},
    "山西省":         {"pop": 3465.7, "gdp_per": 7.37},
    "内蒙古自治区":    {"pop": 2396.0, "gdp_per": 10.20},
    "辽宁省":         {"pop": 4182.0, "gdp_per": 6.21},
    "吉林省":         {"pop": 2339.4, "gdp_per": 5.53},
    "黑龙江省":       {"pop": 3062.0, "gdp_per": 4.44},
    "上海市":         {"pop": 2487.5, "gdp_per": 19.03},
    "江苏省":         {"pop": 8526.0, "gdp_per": 15.05},
    "浙江省":         {"pop": 6627.0, "gdp_per": 12.50},
    "安徽省":         {"pop": 6121.0, "gdp_per": 7.68},
    "福建省":         {"pop": 4183.0, "gdp_per": 12.99},
    "江西省":         {"pop": 4515.0, "gdp_per": 7.09},
    "山东省":         {"pop": 10122.9, "gdp_per": 9.07},
    "河南省":         {"pop": 9815.0, "gdp_per": 6.00},
    "湖北省":         {"pop": 5838.0, "gdp_per": 9.55},
    "湖南省":         {"pop": 6568.0, "gdp_per": 7.30},
    "广东省":         {"pop": 12706.0, "gdp_per": 10.60},
    "广西壮族自治区":  {"pop": 5025.0, "gdp_per": 5.40},
    "海南省":         {"pop": 1043.0, "gdp_per": 7.72},
    "重庆市":         {"pop": 3191.4, "gdp_per": 9.41},
    "四川省":         {"pop": 8368.0, "gdp_per": 7.18},
    "贵州省":         {"pop": 3865.0, "gdp_per": 5.28},
    "云南省":         {"pop": 4693.0, "gdp_per": 5.57},
    "西藏自治区":      {"pop": 365.0, "gdp_per": 6.58},
    "陕西省":         {"pop": 3956.0, "gdp_per": 8.54},
    "甘肃省":         {"pop": 2465.0, "gdp_per": 4.50},
    "青海省":         {"pop": 594.0, "gdp_per": 5.29},
    "宁夏回族自治区":  {"pop": 729.0, "gdp_per": 7.03},
    "新疆维吾尔自治区": {"pop": 2598.0, "gdp_per": 7.38},
}

# 长三角四省市
YRD_PROVINCES = ["上海市", "江苏省", "浙江省", "安徽省"]

# 直辖市
MUNICIPALITIES = ["上海市", "北京市", "天津市", "重庆市"]

# 球拍类项目
RACQUET_SPORTS = ["网球", "羽毛球", "乒乓球"]

# 团队球类项目
TEAM_BALL_SPORTS = ["足球", "篮球", "排球"]

# 新兴运动项目
EMERGING_SPORTS = ["街舞", "攀岩", "马术", "击剑", "冰球"]


def ensure_dirs():
    """确保所有输出目录存在"""
    for d in [DATA_DIR, OUTPUT_DIR, CHART_DIR, REPORT_DIR, MAP_DIR]:
        os.makedirs(d, exist_ok=True)
