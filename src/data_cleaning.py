#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗模块
从原始Excel中提取青少年体育赛事数据，执行清洗与标准化
"""

import pandas as pd
import numpy as np
from config import RAW_DATA_PATH, CLEANED_DATA_PATH, ensure_dirs


def load_raw_data():
    """加载原始Excel数据"""
    print(f"[数据加载] 正在读取: {RAW_DATA_PATH}")
    df = pd.read_excel(RAW_DATA_PATH, sheet_name="赛事数据")
    print(f"  原始数据: {df.shape[0]} 行, {df.shape[1]} 列")
    return df


def filter_youth_events(df):
    """筛选青少年体育赛事"""
    df = df[df["赛事类别"] == "青少年体育赛事"].copy()
    print(f"[筛选] 青少年体育赛事: {len(df)} 条")
    return df


def drop_empty_columns(df):
    """删除全空列（官网、微博、微信等16个无效字段）"""
    empty_cols = df.columns[df.isna().all()].tolist()
    print(f"[清洗] 删除全空列 ({len(empty_cols)} 列): {empty_cols[:5]}...")
    return df.drop(columns=empty_cols)


def drop_code_columns(df):
    """删除地区编码列，保留中文名称列"""
    code_patterns = ["省编码", "市编码", "区编码", "省/市编码"]
    code_cols = [c for c in df.columns if any(p in c for p in code_patterns)]
    if code_cols:
        print(f"[清洗] 删除编码列: {code_cols}")
        df = df.drop(columns=code_cols)
    return df


def clean_event_level(df):
    """修复赛事级别异常值"""
    level_mapping = {
        "C（属地办赛）": "市级",
        "C": "市级",
        "A (A1)": "国家级",
        "A(A1)": "国家级",
        "A": "国家级",
        "B": "省级",
    }
    before = df["赛事级别"].nunique()
    df["赛事级别"] = df["赛事级别"].replace(level_mapping)
    # 过滤掉仍为非标准值的记录
    valid_levels = ["国家级", "省级", "市级"]
    invalid_mask = ~df["赛事级别"].isin(valid_levels)
    if invalid_mask.sum() > 0:
        print(f"[清洗] 赛事级别非标准值 {invalid_mask.sum()} 条，归为'市级'")
        df.loc[invalid_mask, "赛事级别"] = "市级"
    after = df["赛事级别"].nunique()
    print(f"[清洗] 赛事级别: {before} 种 -> {after} 种 (国家级/省级/市级)")
    return df


def process_time_fields(df):
    """处理时间字段：转datetime、提取年份和月份"""
    df["开始时间"] = pd.to_datetime(df["赛事开始时间"], errors="coerce")
    df["结束时间"] = pd.to_datetime(df["赛事结束时间"], errors="coerce")
    df["年份"] = df["开始时间"].dt.year
    df["月份"] = df["开始时间"].dt.month

    # 计算持续天数（大量缺失，仅计算有值的）
    df["持续天数"] = (df["结束时间"] - df["开始时间"]).dt.days + 1
    valid_duration = df["持续天数"].notna().sum()
    print(f"[清洗] 时间字段处理完成，持续天数有效值: {valid_duration}/{len(df)}")
    return df


def process_scale(df):
    """赛事规模转数值型"""
    df["赛事规模"] = pd.to_numeric(df["赛事规模"], errors="coerce")
    print(f"[清洗] 赛事规模: 均值{df['赛事规模'].mean():.0f}人, "
          f"中位数{df['赛事规模'].median():.0f}人, "
          f"最大{df['赛事规模'].max():.0f}人")
    return df


def fill_missing_sport(df):
    """运动项目空值填充"""
    na_count = df["运动项目"].isna().sum()
    if na_count > 0:
        print(f"[清洗] 运动项目空值 {na_count} 条，填为'未知'")
        df["运动项目"] = df["运动项目"].fillna("未知")
    return df


def clean_sport_names(df):
    """清洗运动项目名称中的噪音（活动全称）"""
    # 过滤含引号或过长的非标准项目名
    noise_mask = df["运动项目"].str.contains(r'["""\']', regex=True, na=False)
    if noise_mask.sum() > 0:
        print(f"[清洗] 运动项目含噪音值 {noise_mask.sum()} 条，标记为'其他'")
        df.loc[noise_mask, "运动项目"] = "其他"
    return df


def run_cleaning():
    """执行完整数据清洗流程"""
    ensure_dirs()

    # 1. 加载原始数据
    df = load_raw_data()

    # 2. 筛选青少年体育赛事
    df = filter_youth_events(df)

    # 3. 删除全空列
    df = drop_empty_columns(df)

    # 4. 删除编码列
    df = drop_code_columns(df)

    # 5. 修复赛事级别
    df = clean_event_level(df)

    # 6. 处理时间字段
    df = process_time_fields(df)

    # 7. 赛事规模转数值
    df = process_scale(df)

    # 8. 填充运动项目空值
    df = fill_missing_sport(df)

    # 9. 清洗运动项目名称
    df = clean_sport_names(df)

    # 10. 保存清洗后数据
    df.to_csv(CLEANED_DATA_PATH, index=False, encoding="utf-8-sig")
    print(f"\n[完成] 清洗后数据已保存: {CLEANED_DATA_PATH}")
    print(f"  最终数据: {len(df)} 条, {df.shape[1]} 列")
    print(f"  年份分布: {df['年份'].value_counts().sort_index().to_dict()}")
    print(f"  省份数: {df['省名称'].nunique()}")
    print(f"  运动项目数: {df['运动项目'].nunique()}")

    return df


if __name__ == "__main__":
    run_cleaning()
