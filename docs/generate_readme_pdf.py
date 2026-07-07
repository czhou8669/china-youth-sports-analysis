#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成修正后的全国青少年体育赛事数据分析 README PDF"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ========== 字体注册 ==========
pdfmetrics.registerFont(TTFont('STHeiti', '/System/Library/Fonts/STHeiti Medium.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('AU', '/Library/Fonts/Arial Unicode.ttf'))

# ========== 颜色定义 ==========
C_PRIMARY = colors.HexColor('#1a56db')
C_DARK = colors.HexColor('#1e293b')
C_BODY = colors.HexColor('#334155')
C_LIGHT = colors.HexColor('#64748b')
C_BG = colors.HexColor('#f1f5f9')
C_ACCENT = colors.HexColor('#dc2626')
C_GREEN = colors.HexColor('#059669')
C_BORDER = colors.HexColor('#cbd5e1')
C_TABLE_HEAD = colors.HexColor('#1e3a5f')
C_TABLE_ALT = colors.HexColor('#f8fafc')

# ========== 样式定义 ==========
ST_TITLE = ParagraphStyle('Title', fontName='STHeiti', fontSize=20, leading=28,
                           textColor=C_DARK, alignment=TA_CENTER, spaceAfter=4*mm)
ST_SUBTITLE = ParagraphStyle('Subtitle', fontName='AU', fontSize=10, leading=16,
                              textColor=C_LIGHT, alignment=TA_CENTER, spaceAfter=10*mm)
ST_H1 = ParagraphStyle('H1', fontName='STHeiti', fontSize=14, leading=20,
                        textColor=C_PRIMARY, spaceBefore=10*mm, spaceAfter=5*mm)
ST_H2 = ParagraphStyle('H2', fontName='STHeiti', fontSize=12, leading=18,
                        textColor=C_DARK, spaceBefore=6*mm, spaceAfter=3*mm)
ST_BODY = ParagraphStyle('Body', fontName='AU', fontSize=9.5, leading=16,
                          textColor=C_BODY, alignment=TA_JUSTIFY, spaceAfter=3*mm,
                          firstLineIndent=0)
ST_BODY_NI = ParagraphStyle('BodyNI', fontName='AU', fontSize=9.5, leading=16,
                             textColor=C_BODY, alignment=TA_JUSTIFY, spaceAfter=3*mm)
ST_BULLET = ParagraphStyle('Bullet', fontName='AU', fontSize=9.5, leading=16,
                            textColor=C_BODY, leftIndent=8*mm, spaceAfter=2*mm)
ST_NOTE = ParagraphStyle('Note', fontName='AU', fontSize=8.5, leading=14,
                          textColor=C_LIGHT, spaceAfter=3*mm, leftIndent=6*mm)
ST_FOOTER = ParagraphStyle('Footer', fontName='AU', fontSize=9, leading=14,
                            textColor=C_LIGHT, alignment=TA_CENTER, spaceBefore=8*mm)
ST_TABLE_CELL = ParagraphStyle('TCell', fontName='AU', fontSize=8.5, leading=13,
                                textColor=C_BODY, alignment=TA_CENTER)
ST_TABLE_HEAD = ParagraphStyle('THead', fontName='STHeiti', fontSize=8.5, leading=13,
                                textColor=colors.white, alignment=TA_CENTER)
ST_HIGHLIGHT = ParagraphStyle('HL', fontName='AU', fontSize=9.5, leading=16,
                               textColor=C_ACCENT, spaceAfter=3*mm)

def P(text, style=ST_BODY):
    return Paragraph(text, style)

def make_table(data, col_widths=None, header_bg=C_TABLE_HEAD):
    """创建标准表格"""
    if col_widths is None:
        n = len(data[0])
        col_widths = [170*mm / n] * n
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'AU'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]
    # 交替行颜色
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), C_TABLE_ALT))
    t.setStyle(TableStyle(style_cmds))
    return t

def section_box(title_text):
    """创建章节标题带背景色"""
    t = Table([[Paragraph(title_text, ParagraphStyle('SB', fontName='STHeiti', fontSize=12,
               leading=18, textColor=colors.white))]], colWidths=[170*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t

# ========== 构建文档 ==========
def build_doc(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=18*mm, bottomMargin=18*mm,
                            title='全国青少年体育赛事数据分析（2023-2024）')

    story = []

    # ===== 封面标题 =====
    story.append(Spacer(1, 30*mm))
    story.append(P('全国青少年体育赛事数据分析', ParagraphStyle('BigTitle', fontName='STHeiti',
              fontSize=26, leading=36, textColor=C_DARK, alignment=TA_CENTER, spaceAfter=6*mm)))
    # 修正点1：标题年份
    story.append(P('（2023-2024）', ParagraphStyle('YearTitle', fontName='STHeiti',
              fontSize=18, leading=26, textColor=C_PRIMARY, alignment=TA_CENTER, spaceAfter=12*mm)))
    story.append(P('基于5325条全国青少年体育赛事数据，结合青少年体育消费行为研究视角，运用Python进行数据清洗、'
                   '探索性分析与可视化，并引入人口、经济维度进行多变量关联分析，专项深入长三角区域特征研究。',
                   ST_SUBTITLE))
    story.append(Spacer(1, 15*mm))

    # ===== 项目背景 =====
    story.append(PageBreak())
    story.append(section_box('项目背景'))
    story.append(Spacer(1, 3*mm))
    story.append(P('本项目数据来源于全国群众体育赛事数据库，从赛事供给侧数据中理解青少年体育参与和消费行为的规律。'))

    # ===== 数据说明 =====
    story.append(section_box('数据说明'))
    story.append(Spacer(1, 3*mm))
    ds_data = [
        [P('字段', ST_TABLE_HEAD), P('说明', ST_TABLE_HEAD)],
        [P('数据来源', ST_TABLE_CELL), P('全国群众体育赛事数据库', ST_TABLE_CELL)],
        [P('数据量', ST_TABLE_CELL), P('5325条（2023年2742条 + 2024年2583条）', ST_TABLE_CELL)],
        [P('覆盖范围', ST_TABLE_CELL), P('全国31省/市/自治区，39个运动项目', ST_TABLE_CELL)],
        [P('核心字段', ST_TABLE_CELL), P('省市区、赛事级别、运动项目、赛事规模、开始/结束时间', ST_TABLE_CELL)],
    ]
    story.append(make_table(ds_data, [35*mm, 135*mm]))

    # 时间口径注
    story.append(Spacer(1, 3*mm))
    note_box = Table([[
        Paragraph('<b>注：</b>本次分析使用的是2023年与2024年两年合并的青少年体育赛事数据，'
                  '共5325条（其中2023年2742条，2024年2583条）。2025年数据因存在样本截断、'
                  '缺少上海数据及部分非青少年赛事混入等质量问题，未纳入分析。',
                  ParagraphStyle('NoteBox', fontName='AU', fontSize=8.5, leading=14, textColor=C_BODY))
    ]], colWidths=[170*mm])
    note_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(note_box)

    # ===== 数据质量问题 =====
    story.append(section_box('数据质量问题'))
    story.append(Spacer(1, 3*mm))
    story.append(P('在分析过程中对数据进行了交叉核验，发现该数据库存在以下几类系统性问题：'))

    story.append(P('<b>一、省级覆盖严重不足</b>', ST_H2))
    story.append(P('经与各省体育局公开资料核对，广东、江苏、四川三省偏差尤为突出：'))
    dq_data = [
        [P('省份', ST_TABLE_HEAD), P('数据库赛事数', ST_TABLE_HEAD), P('可考证实际规模', ST_TABLE_HEAD), P('来源', ST_TABLE_HEAD)],
        [P('广东省', ST_TABLE_CELL), P('24场', ST_TABLE_CELL), P('广州单市2024年举办省级以上赛事142项、大型群众性活动近200项', ST_TABLE_CELL), P('广东省体育局官网', ST_TABLE_CELL)],
        [P('江苏省', ST_TABLE_CELL), P('134场', ST_TABLE_CELL), P('仅"跟着赛事去旅行"清单就达502项次', ST_TABLE_CELL), P('江苏省体育局', ST_TABLE_CELL)],
        [P('四川省', ST_TABLE_CELL), P('131场', ST_TABLE_CELL), P('省级决算明确记载完成省级青少年赛事活动869场', ST_TABLE_CELL), P('四川省财政厅部门决算', ST_TABLE_CELL)],
    ]
    story.append(make_table(dq_data, [20*mm, 25*mm, 85*mm, 40*mm]))

    story.append(P('<b>二、直辖市赛事级别分类混乱</b>', ST_H2))
    story.append(P('上海、天津、重庆在行政上均为直辖市，不存在"省级"层级，但数据库中均出现了"省级"赛事记录；'
                   '更值得注意的是，上海全年767场赛事中没有任何一场被归类为国家级，这与上海作为全国体育中心城市的'
                   '实际情况明显不符。四个直辖市的级别分布如下：'))
    zx_data = [
        [P('直辖市', ST_TABLE_HEAD), P('市级', ST_TABLE_HEAD), P('省级（分类异常）', ST_TABLE_HEAD), P('国家级', ST_TABLE_HEAD)],
        [P('上海市', ST_TABLE_CELL), P('606场', ST_TABLE_CELL), P('161场', ST_TABLE_CELL), P('0场（明显异常）', ST_TABLE_CELL)],
        [P('北京市', ST_TABLE_CELL), P('434场', ST_TABLE_CELL), P('19场', ST_TABLE_CELL), P('38场', ST_TABLE_CELL)],
        [P('天津市', ST_TABLE_CELL), P('105场', ST_TABLE_CELL), P('49场', ST_TABLE_CELL), P('10场', ST_TABLE_CELL)],
        [P('重庆市', ST_TABLE_CELL), P('24场', ST_TABLE_CELL), P('28场', ST_TABLE_CELL), P('4场', ST_TABLE_CELL)],
    ]
    story.append(make_table(zx_data, [35*mm, 40*mm, 50*mm, 45*mm]))

    story.append(P('<b>三、其他字段质量问题</b>', ST_H2))
    for item in [
        '16个字段（官网、微博、赞助级别等）全部为空，实为无效字段',
        '赛事持续时间字段几乎全部缺失，无法使用',
        '部分运动项目字段填写的是活动全称（如"活力浦东系列赛"）而非标准项目名，导致分类分析时出现噪音',
        '赛事级别存在"A""A(A1)""C（属地办赛）"等非标准值，需人工清洗统一',
    ]:
        story.append(Paragraph('<font color="#1a56db">\u25aa</font>&nbsp;&nbsp;' + item, ST_BULLET))

    story.append(Spacer(1, 3*mm))
    story.append(P('综合以上问题，该数据库的覆盖范围可能仅限于特定渠道上报的赛事，大量省级、市级及社会机构'
                   '主办的赛事并未纳入。因此本分析中涉及的省际排名和密度比较，结论需谨慎对待。数据质量的'
                   '系统性缺陷本身也是一个值得关注的发现——它反映出全国青少年体育赛事的统计口径尚不统一，'
                   '数据治理仍有较大提升空间。'))

    # ===== 技术栈 =====
    story.append(section_box('技术栈'))
    story.append(Spacer(1, 3*mm))
    for item in [
        'Python 3.x',
        'pandas — 数据清洗与聚合',
        'matplotlib — 静态可视化',
        'pyecharts — 交互式中国地图',
        'openpyxl — Excel文件读取',
    ]:
        story.append(Paragraph('<font color="#1a56db">\u25aa</font>&nbsp;&nbsp;' + item, ST_BULLET))

    # ===== 数据清洗过程 =====
    story.append(section_box('数据清洗过程'))
    story.append(Spacer(1, 3*mm))
    for item in [
        '删除无效列：官网、微博、微信、赞助级别等16列全部为空，直接删除',
        '统一地区字段：省/市编码列（如SH、110000）与中文名称列并存，删除编码列保留中文',
        '修复赛事级别异常值：将"C（属地办赛）"统一为市级，"A (A1)"统一为国家级',
        '时间字段处理：转为datetime格式，计算持续天数、提取月份',
        '空值处理：87条运动项目空值填为"未知"，赛事规模转为数值型',
        '噪音过滤：运动项目分析时过滤含引号的活动全称字段',
    ]:
        story.append(Paragraph('<font color="#1a56db">\u25aa</font>&nbsp;&nbsp;' + item, ST_BULLET))

    # ===== 核心分析结论 =====
    story.append(PageBreak())
    story.append(section_box('核心分析结论'))
    story.append(Spacer(1, 3*mm))

    story.append(P('<b>一、地区分布：东部高度集中</b>', ST_H2))
    story.append(P('上海、山东、浙江位居全国前三，合计占全国赛事总量约40%，反映华东地区市场规模广阔的特征。'
                   '上海以767场位居第一，体现上海市的青少年体育市场庞大且实力雄厚，在全国范围内起到带头作用。'
                   '同时上海平均赛事规模209人，远低于全国均值548人，赛事密度高、规模小，呈现出精品化、社区化的特征。'))
    # 修正点4：补充中位数
    story.append(P('<b>注：</b>全国赛事规模均值548人受极端值拉高明显（最大值91000人），中位数仅为230人；'
                   '上海中位数更低至50人。后续涉及赛事规模的比较中，均值与中位数差异较大时以中位数补充参考。',
                   ST_NOTE))

    story.append(P('<b>二、直辖市赛事模式分化：广度型 vs 高度型</b>', ST_H2))
    story.append(P('四个直辖市在赛事总量、平均规模和级别结构上呈现出截然不同的发展路径。上海以767场位居'
                   '全国第一，但平均规模仅209人、中位数低至50人，运动项目以区级社区健身系列活动（如浦东新区'
                   '67场、徐汇区33场）为骨架，呈现出典型的"广度覆盖"特征。北京赛事总数491场，但平均规模'
                   '526人、中位数300人，运动项目中高尔夫球（70场）、马术（28场）等高消费项目集中，国家级'
                   '赛事38场（8%），呈现出"高度精英"特征。'))
    zx_cmp_data = [
        [P('直辖市', ST_TABLE_HEAD), P('赛事总数', ST_TABLE_HEAD), P('平均规模', ST_TABLE_HEAD),
         P('中位数', ST_TABLE_HEAD), P('市级占比', ST_TABLE_HEAD), P('国家级占比', ST_TABLE_HEAD)],
        [P('上海市', ST_TABLE_CELL), P('767场', ST_TABLE_CELL), P('209人', ST_TABLE_CELL),
         P('50人', ST_TABLE_CELL), P('79%', ST_TABLE_CELL), P('0%（数据缺失）', ST_TABLE_CELL)],
        [P('北京市', ST_TABLE_CELL), P('491场', ST_TABLE_CELL), P('526人', ST_TABLE_CELL),
         P('300人', ST_TABLE_CELL), P('88%', ST_TABLE_CELL), P('8%（38场）', ST_TABLE_CELL)],
        [P('天津市', ST_TABLE_CELL), P('164场', ST_TABLE_CELL), P('332人', ST_TABLE_CELL),
         P('160人', ST_TABLE_CELL), P('64%', ST_TABLE_CELL), P('6%（10场）', ST_TABLE_CELL)],
        [P('重庆市', ST_TABLE_CELL), P('56场', ST_TABLE_CELL), P('366人', ST_TABLE_CELL),
         P('265人', ST_TABLE_CELL), P('43%', ST_TABLE_CELL), P('7%（4场）', ST_TABLE_CELL)],
    ]
    story.append(make_table(zx_cmp_data, [22*mm, 22*mm, 24*mm, 20*mm, 22*mm, 32*mm]))
    story.append(Spacer(1, 2*mm))
    story.append(P('两种模式反映了不同的城市体育发展战略：上海侧重通过高频次、小规模的社区赛事实现广泛覆盖，'
                   '北京则侧重通过高规格、大规模赛事打造标杆效应。上海数据库中国家级赛事为0系数据录入问题，'
                   '但即便修正后，上海在赛事高度上与北京仍可能存在差距——北京高尔夫球70场、马术28场等高消费'
                   '项目的集中度，在上海数据中没有对应体现。'))

    story.append(P('<b>三、消费结构因项目类型而分化</b>', ST_H2))
    story.append(P('运动项目按器械依赖度可分为两类，消费结构存在差异：'))
    cs_data = [
        [P('项目类型', ST_TABLE_HEAD), P('代表项目', ST_TABLE_HEAD), P('平均赛事规模', ST_TABLE_HEAD), P('主要消费构成', ST_TABLE_HEAD)],
        [P('球拍类（高器械）', ST_TABLE_CELL), P('网球、羽毛球、乒乓球', ST_TABLE_CELL), P('约296人', ST_TABLE_CELL), P('装备器械与培训费相辅相成', ST_TABLE_CELL)],
        [P('团队球类（低器械）', ST_TABLE_CELL), P('足球、篮球、排球', ST_TABLE_CELL), P('约713人', ST_TABLE_CELL), P('培训费为主，装备居后', ST_TABLE_CELL)],
    ]
    story.append(make_table(cs_data, [35*mm, 50*mm, 30*mm, 55*mm]))
    story.append(Spacer(1, 2*mm))
    story.append(P('球拍类运动因器械成本较高，在费用上制约了参与人数，赛事规模明显偏小，但消费客单价更高。'
                   '服装鞋类是所有项目的共同消费，不随项目类型变化。从全国运动项目热度来看，足球以537场'
                   '位居第一，篮球411场次之，乒乓球247场、羽毛球202场、网球197场紧随其后——团队球类在'
                   '赛事数量和平均规模上双重领先，进一步印证了其作为体育消费基本盘的定位。'))

    story.append(P('<b>四、驱动力分层</b>', ST_H2))
    story.append(P('结合课题调研，青少年体育参与存在三层驱动力：'))
    for item in [
        '个人偏好 / 学校要求：作为青少年内生消费动力发挥作用，个人偏好占主导',
        '家长经济状况：掌握最终决策权与支付权，直接影响了消费的发生过程',
        '空间状况：反映实体空间的供需情况，物理上制约体育消费需求',
    ]:
        story.append(Paragraph('<font color="#1a56db">\u25aa</font>&nbsp;&nbsp;' + item, ST_BULLET))
    story.append(P('这一框架可以解释球拍类项目客单价高但赛事规模偏小的现象——进入门槛由家长决定，'
                   '但进一步投入由孩子兴趣驱动，在费用和成本上制约人数峰值，供需条件上提高价格。'
                   '华东地区如上海、杭州等城市的经济状况覆盖相应球类运动，社区化特征促成小规模赛事，'
                   '三者因素共同筛选出高黏性、高消费的核心用户群体。'))

    story.append(P('<b>五、新兴运动的参与度在上升</b>', ST_H2))
    story.append(P('街舞、攀岩、马术、击剑、冰球等新兴项目已形成一定赛事基础，共同特征是社交属性强、'
                   '个性化突出、与国际潮流接轨。这不仅是经济水平提升的体现，也反映出当下青少年将运动选择'
                   '与个人兴趣、社交圈层挂钩的倾向。从消费心理角度看，参与小众体育项目有利于在社会比较中'
                   '形成身份区分，这也在一定程度上驱动了新兴项目的消费意愿。'))
    em_data = [
        [P('新兴项目', ST_TABLE_HEAD), P('赛事数', ST_TABLE_HEAD), P('平均规模', ST_TABLE_HEAD)],
        [P('击剑', ST_TABLE_CELL), P('52场', ST_TABLE_CELL), P('309人', ST_TABLE_CELL)],
        [P('街舞', ST_TABLE_CELL), P('47场', ST_TABLE_CELL), P('692人', ST_TABLE_CELL)],
        [P('马术', ST_TABLE_CELL), P('44场', ST_TABLE_CELL), P('182人', ST_TABLE_CELL)],
        [P('冰球', ST_TABLE_CELL), P('43场', ST_TABLE_CELL), P('387人', ST_TABLE_CELL)],
        [P('攀岩', ST_TABLE_CELL), P('28场', ST_TABLE_CELL), P('273人', ST_TABLE_CELL)],
    ]
    story.append(make_table(em_data, [60*mm, 50*mm, 60*mm]))

    story.append(P('<b>六、赛事节奏与学校日历高度绑定</b>', ST_H2))
    story.append(P('全年赛事高峰集中在7-8月（暑假），次高峰在5月、10-11月（学期中后期），低谷在1-2月'
                   '（寒假及春节）。赛事分布规律与青少年的时间安排直接相关，假期和学期中后期是参赛条件'
                   '最集中的时段。'))
    # 修正点3：补充11月上海驱动说明
    story.append(P('<b>注：</b>11月全国593场赛事中，上海市占286场（48.2%），主要来自"上海市第四届市民运动会"'
                   '系列赛事的集中录入。因此11月的高峰在一定程度上受上海单市数据驱动，并非全国普遍现象，'
                   '在解读月份分布时需注意这一结构特征。', ST_NOTE))

    # ===== 人口与经济关联分析 =====
    story.append(PageBreak())
    story.append(section_box('人口与经济关联分析'))
    story.append(Spacer(1, 3*mm))

    story.append(P('<b>七、人口大省：赛事数量与人口规模并不成正比</b>', ST_H2))
    story.append(P('消除人口基数差异后，上海（每百万人30.8场）、北京（22.5场）、浙江（10.4场）位居前列，'
                   '与人均GDP排名高度吻合；而河南（1.8场）、湖北（1.3场）、福建（1.1场）远低于全国均值'
                   '（3.8场），体现了内陆省份赛事供给相对不足的现状。广东（0.2场）数值极低，结合交叉核验'
                   '结果，主要反映的是数据覆盖缺口而非真实市场状况。'))

    story.append(P('<b>八、经济因素与赛事密度的相关性</b>', ST_H2))
    story.append(P('以各省人均GDP为横轴、每百万人赛事数为纵轴，计算相关系数为0.73，呈现较强正相关。'
                   '四象限分析显示两类值得关注的省份：'))
    for item in [
        '高GDP、低赛事密度（广东、江苏、福建等）：考虑数据覆盖缺口，实际情况可能被低估；'
        '即便修正后，这类省份仍可能存在赛事市场化程度不足的问题',
        '低GDP、高赛事密度（新疆、贵州、内蒙古等）：结合西部政策背景，赛事供给更多来自政策输入而非市场自发',
    ]:
        story.append(Paragraph('<font color="#1a56db">\u25aa</font>&nbsp;&nbsp;' + item, ST_BULLET))

    story.append(P('<b>九、边疆地区赛事的政策主导特征</b>', ST_H2))
    story.append(P('西藏、新疆、内蒙古等地广人稀省份的每百万人赛事密度数值较高，但结合当地人均GDP偏低、'
                   '人口基数小的实际情况，这类省份的赛事供给更多来自西部大开发、民族地区体育扶持等政策导向，'
                   '而非市场自发形成。这类地区的赛事逻辑与东部省份不同，不宜简单用密度指标衡量市场活跃度，'
                   '需结合当地政策背景、人口结构和实际消费能力具体判断。'))

    story.append(PageBreak())

    # ===== 长三角专题分析 =====
    story.append(section_box('长三角专题分析'))
    story.append(Spacer(1, 3*mm))

    story.append(P('<b>十、长三角 vs 全国：高密度、小规模、精品化</b>', ST_H2))
    story.append(P('长三角四省市（上海、江苏、浙江、安徽）以占全国16.9%的人口贡献了31.2%的赛事，'
                   '每百万人赛事密度7.0场，是全国均值3.8场的1.9倍。同时长三角平均赛事规模（约333人）'
                   '低于全国均值（548人），呈现出高频次、小规模的精品化特征，与长三角整体经济发展水平'
                   '和中产家庭消费偏好高度吻合。'))

    story.append(P('<b>十一、长三角内部：上海浙江 vs 江苏安徽的结构性分化</b>', ST_H2))
    story.append(P('长三角内部存在明显的两极分化，上海和浙江构成赛事核心，江苏和安徽密度显著偏低：'))
    # 修正点2：补充国家级列
    yz_data = [
        [P('省/市', ST_TABLE_HEAD), P('赛事数量', ST_TABLE_HEAD), P('每百万人赛事数', ST_TABLE_HEAD),
         P('平均规模', ST_TABLE_HEAD), P('市级占比', ST_TABLE_HEAD), P('省级占比', ST_TABLE_HEAD),
         P('国家级占比', ST_TABLE_HEAD)],
        [P('上海市', ST_TABLE_CELL), P('767场', ST_TABLE_CELL), P('30.8', ST_TABLE_CELL),
         P('209人', ST_TABLE_CELL), P('79%', ST_TABLE_CELL), P('21%', ST_TABLE_CELL), P('0%', ST_TABLE_CELL)],
        [P('浙江省', ST_TABLE_CELL), P('689场', ST_TABLE_CELL), P('10.4', ST_TABLE_CELL),
         P('417人', ST_TABLE_CELL), P('67%', ST_TABLE_CELL), P('24%', ST_TABLE_CELL), P('8%', ST_TABLE_CELL)],
        [P('江苏省', ST_TABLE_CELL), P('134场', ST_TABLE_CELL), P('1.6', ST_TABLE_CELL),
         P('536人', ST_TABLE_CELL), P('26%', ST_TABLE_CELL), P('60%', ST_TABLE_CELL), P('14%', ST_TABLE_CELL)],
        [P('安徽省', ST_TABLE_CELL), P('72场', ST_TABLE_CELL), P('1.2', ST_TABLE_CELL),
         P('477人', ST_TABLE_CELL), P('76%', ST_TABLE_CELL), P('21%', ST_TABLE_CELL), P('3%', ST_TABLE_CELL)],
    ]
    story.append(make_table(yz_data, [20*mm, 22*mm, 28*mm, 22*mm, 22*mm, 22*mm, 22*mm]))
    story.append(Spacer(1, 2*mm))
    story.append(P('上海和浙江的市级赛事占比均超过65%，赛事分布社区化、精品化；江苏省级赛事占比高达60%'
                   '（80场），在长三角内一枝独秀（上海21%、浙江24%、安徽21%），说明江苏赛事供给高度依赖'
                   '省级行政驱动，与沪浙以市级社区赛事为主的市场化生态存在结构性差异。这一特征意味着江苏面临的'
                   '不仅是数量缺口，更是赛事驱动机制的转型需求——从行政主导向市场主导过渡，可能是释放江苏赛事'
                   '潜力的前提。安徽市级赛事占比76%，结构上与上海接近，但赛事总量和密度均处于长三角末位，'
                   '反映其体育消费市场仍处于早期发展阶段。江苏国家级赛事占比14%（19场），是长三角内国家级赛事'
                   '占比最高的省份，反映了其在国家级赛事承办上具有一定优势。考虑到江苏数据存在覆盖缺口，实际'
                   '赛事数量可能远高于134场，但江苏赛事市场化程度低于上海、浙江的结构性差距在现有数据中仍有体现。'))
    story.append(P('另外，上海数据库中未录入任何国家级赛事，与其全国体育中心城市的定位明显不符，'
                   '这是数据质量问题而非真实情况的反映（见数据质量说明）。'))

    story.append(PageBreak())

    # ===== 初步建议 =====
    story.append(section_box('初步建议'))
    story.append(Spacer(1, 3*mm))

    story.append(P('<b>1. 项目类型与营销方式的匹配</b>', ST_H2))
    story.append(P('球拍类项目（网球、羽毛球、乒乓球）平均赛事规模296人，参与人群相对集中、家庭消费能力较强，'
                   '客单价高但人数天花板低，适合走"赛事IP品牌化"路线——通过赛事冠名、装备展销、培训引流一体化'
                   '实现变现，营销渠道以俱乐部和私校社群为主。团队球类（足球、篮球、排球）平均规模713人，'
                   '足球537场、篮球411场在赛事数量上同样领先，参与基数大、覆盖面广，适合作为青训体系入口和'
                   '品牌曝光阵地，营销渠道以校园和体校体系为主，适合长线投资。两类项目的定价模型也应分化：'
                   '球拍类走高客单价、低人数的精品路线，团队球类走低客单价、高人数的规模路线。'))

    story.append(P('<b>2. 直辖市赛事模式分化：广度型、高度型与追赶型，各自对应不同策略</b>', ST_H2))
    story.append(P('四大直辖市在赛事总量、规模和级别结构上呈现出三种截然不同的发展路径，对应不同的策略方向。'
                   '上海以767场位居全国第一，但中位数仅50人，79%为市级赛事，以区级社区健身活动为骨架，'
                   '是典型的"广度覆盖型"——优势是高频次触达大量家庭，社群黏性强；如果要提升品牌价值，'
                   '建议在社区赛事基础上叠加少量标杆性精品赛事，形成"大众铺底+精品拔高"的双层结构。'
                   '北京491场但中位数300人、国家级赛事38场（8%），高尔夫球70场、马术28场等高消费项目'
                   '集中，是典型的"高度精英型"——已有一定的赛事高度，下一步可考虑将精英赛事资源向更多'
                   '运动项目扩散，扩大受益人群。天津164场、中位数160人，介于广度和高度之间，可作为'
                   '"中转枢纽"承接京津赛事资源的外溢和梯度下沉。重庆56场、但国家级占比7%（4场），'
                   '赛事总量少但已有一定高度，属于"追赶型"——宜优先扩大赛事总量，在增量中逐步提升规格，'
                   '而非急于对标京沪的精英赛事。四种模式反映了不同的城市体育发展战略，策略制定时不宜混为一谈。'))

    story.append(P('<b>3. 新兴项目：区分群众基础与政策红利，分赛道切入</b>', ST_H2))
    story.append(P('街舞、攀岩、马术、击剑、冰球等新兴项目已形成一定赛事基础，但不同项目的特征差异显著，'
                   '不宜笼统对待。击剑52场但平均规模仅309人，受众集中在中高收入家庭，适合走精品化私校渗透'
                   '路线；街舞47场但平均规模达692人，群众基础更好、场地门槛低（仅需空地），适合快速复制和'
                   '规模化推广。攀岩和街舞已进入奥运会，正处于政策红利窗口期，有政策对接优势。冰球43场但'
                   '场馆投入壁垒极高，扩张速度受制于场地供给。建议根据自身资源禀赋选择切入点：有场馆资源的'
                   '可押注冰球、马术等高壁垒项目，有社群运营能力的可优先布局街舞、攀岩等低门槛项目。'))

    story.append(P('<b>4. 基于人口、经济与赛事关联分析的地区差异化策略</b>', ST_H2))
    for item in [
        '高GDP、低赛事密度地区（广东、江苏、福建等）：需区分"真实供给不足"和"统计盲区"。广东每百万人'
        '仅0.2场，结合交叉核验（广州单市2024年实际举办省级以上赛事142项），主要是数据覆盖缺口而非'
        '市场空白。但即便修正后，这类经济强省的赛事市场化程度仍有提升空间，值得加强商业赛事和品牌赛事'
        '的投资布局',
        '人口大省、赛事密度低的内陆地区（河南、湖北等）：人口基数大但赛事相对稀少，短期内不宜直接投入'
        '赛事，应先做体育消费基础设施（场馆、培训体系），培育市场承接能力后再引入赛事，中长期存在增长空间',
        '边疆及地广人稀地区（西藏、新疆、内蒙古等）：赛事供给受政策驱动，与东部省份市场逻辑不同，'
        '策略上需结合当地政策方向、人口结构和实际消费能力具体分析，不能套用东部市场经验',
    ]:
        story.append(Paragraph('<font color="#1a56db">\u25aa</font>&nbsp;&nbsp;' + item, ST_BULLET))

    story.append(P('<b>5. 长三角协同发展：以沪浙带动苏皖，推动江苏赛事市场化转型</b>', ST_H2))
    story.append(P('长三角内部的赛事密度分化折射出经济发展的不均衡。上海和浙江已形成以市级社区赛事为主的'
                   '市场化生态，而江苏省级赛事占比高达60%（80场），赛事供给高度依赖行政驱动。这意味着'
                   '长三角协同发展时，江苏面临的不仅是数量缺口，更是赛事驱动机制的转型需求。具体协同机制'
                   '可从三个层面推进：一是统一赛事日历，避免长三角内档期冲突，实现资源错峰配置；二是联合'
                   '申办大型赛事，以跨城联办模式提升整体吸引力；三是赛事积分互通，推动选手和观众跨城流动。'
                   '借助高铁1小时通勤圈，上海、杭州的成熟赛事品牌可沿沪宁线梯度下沉至苏州、南京，再延伸至'
                   '合肥，为品牌扩大覆盖半径提供低成本的增量市场。但前提是江苏需同步推进赛事市场化改革，'
                   '否则行政驱动的赛事生态难以与沪浙的市场化体系有效对接。'))

    story.append(P('<b>6. 赛事季节性运营：填补寒假低谷，错峰布局暑期高峰</b>', ST_H2))
    story.append(P('全年赛事高峰集中在7-8月（暑假），次高峰在5月、10-11月，低谷在1-2月（寒假及春节）。'
                   '赛事分布与学校日历高度绑定，这意味着暑期是资源竞争最激烈的时段，需要差异化定位才能突围。'
                   '1-2月低谷期可布局室内赛事（乒乓球、羽毛球、击剑等）填补空白，利用寒假窗口开展集训型'
                   '或选拔型赛事。5月和10月学期中后期适合做周末型赛事，避免与课业冲突。赛事档期规划本身'
                   '就是一种竞争策略——在非高峰时段精准触达目标人群，可能比在暑期扎堆获得更高的投入产出比。'))

    story.append(P('<b>7. 体教融合：以校园赛事为入口，构建赛事金字塔</b>', ST_H2))
    story.append(P('"双减"政策后，学校课后体育时段成为青少年体育赛事和培训的增量入口。当前数据库中的赛事'
                   '以市级和省级为主，校内联赛和区级赛事的覆盖可能不足。从赛事体系建设的角度，可探索'
                   '"校内联赛→区级→市级→省级→国家级"的金字塔结构，将商业赛事与教育系统赛事衔接。对赛事'
                   '主办方而言，与教育部门合作采购青少年体育服务、将赛事嵌入学校体育课程体系，是触达大规模'
                   '青少年群体的低成本路径。这一方向也与"驱动力分层"中"学校要求"作为内生消费动力的发现'
                   '相呼应——学校是青少年体育参与的第一触点，赛事运营应重视这一渠道。'))

    # ===== 文件结构 =====
    story.append(PageBreak())
    story.append(section_box('文件结构'))
    story.append(Spacer(1, 3*mm))
    fs_text = (
        '<font name="AU" size="9" color="#334155">'
        '├── 青少年体育赛事数据分析.ipynb &nbsp;&nbsp;&nbsp; # 完整分析代码<br/>'
        '├── data/<br/>'
        '│ &nbsp;&nbsp; └── 青少年体育赛事_清洗后.csv &nbsp;&nbsp;&nbsp; # 清洗后数据（2023-2024年）<br/>'
        '├── images/<br/>'
        '│ &nbsp;&nbsp; ├── 01_省份分布.png<br/>'
        '│ &nbsp;&nbsp; ├── 02_运动项目热度.png<br/>'
        '│ &nbsp;&nbsp; ├── 03_月份分布.png<br/>'
        '│ &nbsp;&nbsp; ├── 04_上海深度分析.png<br/>'
        '│ &nbsp;&nbsp; ├── 05_消费结构分化.png<br/>'
        '│ &nbsp;&nbsp; ├── 06_上海市场特征.png<br/>'
        '│ &nbsp;&nbsp; ├── 07_新兴运动.png<br/>'
        '│ &nbsp;&nbsp; ├── 09_人口大省赛事对比.png<br/>'
        '│ &nbsp;&nbsp; ├── 10_人口小省赛事密度.png<br/>'
        '│ &nbsp;&nbsp; ├── 11_GDP与赛事密度散点图.png<br/>'
        '│ &nbsp;&nbsp; ├── 12_长三角vs全国.png<br/>'
        '│ &nbsp;&nbsp; ├── 13_长三角内部差异.png<br/>'
        '│ &nbsp;&nbsp; └── 14_上海vs江苏项目对比.png<br/>'
        '├── maps/<br/>'
        '│ &nbsp;&nbsp; ├── map_赛事数量.html<br/>'
        '│ &nbsp;&nbsp; ├── map_赛事密度.html<br/>'
        '│ &nbsp;&nbsp; └── map_人均GDP.html<br/>'
        '└── README.md'
        '</font>'
    )
    story.append(P(fs_text, ST_BODY_NI))

    # 生成
    doc.build(story)
    print(f'PDF已生成: {output_path}')

if __name__ == '__main__':
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.pdf')
    build_doc(output)
