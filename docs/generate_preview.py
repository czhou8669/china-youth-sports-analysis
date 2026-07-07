#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 docs/README.pdf 全部页面渲染为 PNG 预览图。

用途：GitHub 内置 PDF 预览器对嵌入中文字体的 PDF 支持不佳，
      生成 PNG 预览图后可在 README 中直接展示完整报告。

依赖（需单独安装）：
    pip install pymupdf
"""
import os
import fitz

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))


def pdf_to_preview(pdf_path, dpi=150):
    """将 PDF 全部页面渲染为 PNG 预览图"""
    doc = fitz.open(pdf_path)
    total = len(doc)
    print(f"  共 {total} 页")

    for i in range(total):
        page = doc.load_page(i)
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_path = f"{pdf_path[:-4]}_page_{i + 1}.png"
        pix.save(img_path)
        print(f"  已生成: {img_path}")

    doc.close()
    return total


def main():
    pdf_path = os.path.join(DOCS_DIR, "README.pdf")
    if os.path.exists(pdf_path):
        print(f"[PDF预览] 处理: {os.path.basename(pdf_path)}")
        total = pdf_to_preview(pdf_path)
        print(f"[完成] 共生成 {total} 页预览图")
    else:
        print(f"[跳过] 文件不存在: {pdf_path}")


if __name__ == "__main__":
    main()
