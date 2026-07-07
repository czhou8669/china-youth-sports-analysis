#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 docs/ 目录下的 PDF 转换为第一页预览 PNG。

用途：GitHub 内置 PDF 预览器对 reportlab 嵌入中文字体的 PDF 支持不佳，
      生成 PNG 预览图后可在 README 中直接展示。

依赖（需单独安装）：
    pip install pymupdf
"""
import os
import fitz

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))


def pdf_to_preview(pdf_path, dpi=150):
    """将 PDF 第一页渲染为 PNG 预览图"""
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_path = f"{pdf_path[:-4]}_page_1.png"
    pix.save(img_path)
    doc.close()
    print(f"  已生成: {img_path}")
    return img_path


def main():
    pdf_files = [
        os.path.join(DOCS_DIR, "README_原版.pdf"),
        os.path.join(DOCS_DIR, "README_修正版.pdf"),
    ]

    for pdf_path in pdf_files:
        if os.path.exists(pdf_path):
            print(f"[PDF预览] 处理: {os.path.basename(pdf_path)}")
            pdf_to_preview(pdf_path)
        else:
            print(f"[跳过] 文件不存在: {pdf_path}")


if __name__ == "__main__":
    main()
