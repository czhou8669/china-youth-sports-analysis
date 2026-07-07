#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 docs/README.pdf 全部页面拼接为单张 PNG 预览图。

用途：GitHub 内置 PDF 预览器对嵌入中文字体的 PDF 支持不佳，
      生成单张完整 PNG 预览图后可在 README 中直接展示整个报告。

依赖（需单独安装）：
    pip install pymupdf pillow
"""
import os
import fitz
from PIL import Image

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))


def pdf_to_single_preview(pdf_path, dpi=150):
    """将 PDF 全部页面拼接为单张垂直排列的 PNG 预览图"""
    doc = fitz.open(pdf_path)
    total = len(doc)
    print(f"  共 {total} 页，开始渲染...")

    # 渲染每一页为 PIL Image
    images = []
    for i in range(total):
        page = doc.load_page(i)
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        images.append(img)
        print(f"  已渲染第 {i + 1}/{total} 页")

    doc.close()

    # 垂直拼接所有页面
    total_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)
    result = Image.new("RGB", (total_width, total_height), (255, 255, 255))

    y_offset = 0
    for img in images:
        result.paste(img, (0, y_offset))
        y_offset += img.height

    # 保存
    img_path = pdf_path[:-4] + "_preview.png"
    result.save(img_path, "PNG", optimize=True)
    print(f"  已生成: {img_path} ({total_width}x{total_height})")
    return img_path


def main():
    pdf_path = os.path.join(DOCS_DIR, "README.pdf")
    if os.path.exists(pdf_path):
        print(f"[PDF预览] 处理: {os.path.basename(pdf_path)}")
        pdf_to_single_preview(pdf_path)
        print("[完成] 全部页面已拼接为单张预览图")
    else:
        print(f"[跳过] 文件不存在: {pdf_path}")


if __name__ == "__main__":
    main()
