#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式Excel字段分析器 - Claude Code专用
支持未知字段的交互式学习
"""

import sys
from pathlib import Path
from analyzer import ExcelAnalyzer


def analyze_with_learning(xlsx_path: str, output_dir: str = './analysis_output', topn: int = 10):
    """
    带交互式学习的分析流程

    Args:
        xlsx_path: Excel文件路径
        output_dir: 输出目录
        topn: Top值显示数量
    """

    xlsx_path = Path(xlsx_path)
    if not xlsx_path.exists():
        print(f"❌ 文件不存在: {xlsx_path}")
        return None

    print(f"\n{'='*60}")
    print(f"📊 Excel字段分析工具 v2.0")
    print(f"{'='*60}\n")

    # 创建分析器
    analyzer = ExcelAnalyzer()

    # 第一次分析
    print(f"🔍 正在分析: {xlsx_path.name}")
    result = analyzer.analyze_excel(str(xlsx_path), output_dir, topn)

    if not result['success']:
        print(f"❌ 分析失败: {result['message']}")
        return None

    # 检查未知字段
    unknown_fields = result.get('unknown_fields', [])

    if unknown_fields:
        print(f"\n{'='*60}")
        print(f"🔍 发现 {len(unknown_fields)} 个未知字段")
        print(f"{'='*60}")

        for idx, field in enumerate(unknown_fields, 1):
            print(f"\n{idx}. {field}")

        print(f"\n{'='*60}")
        response = input("是否为这些字段创建映射？(y/n): ").strip().lower()

        if response == 'y':
            print(f"\n开始学习新字段...\n")

            for cn_field in unknown_fields:
                print(f"{'─'*60}")
                print(f"字段: {cn_field}")
                print(f"{'─'*60}")

                # 智能建议英文名
                suggested_en = suggest_english_name(cn_field)
                en_name_input = input(f"英文字段名 [建议: {suggested_en}]: ").strip()
                en_name = en_name_input if en_name_input else suggested_en

                # 选择分组
                print("\n业务分组选项:")
                groups = [
                    "finance (财务数据: 保费、赔款、费用)",
                    "vehicle (车辆相关: 车牌、车型)",
                    "organization (机构信息: 三级机构、四级机构)",
                    "product (产品信息: 险类、险种)",
                    "time (时间日期)",
                    "flag (标识字段: 是否...)",
                    "partner (合作伙伴: 4S集团)",
                    "general (通用字段)"
                ]
                for i, g in enumerate(groups, 1):
                    print(f"  {i}. {g}")

                group_choice = input("\n选择分组 [1-8, 默认8]: ").strip()
                group_map = {
                    '1': 'finance', '2': 'vehicle', '3': 'organization',
                    '4': 'product', '5': 'time', '6': 'flag',
                    '7': 'partner', '8': 'general', '': 'general'
                }
                group = group_map.get(group_choice, 'general')

                # 选择数据类型
                print("\n数据类型选项:")
                print("  1. number (数值型)")
                print("  2. string (字符串)")
                print("  3. datetime (时间日期)")

                dtype_choice = input("\n选择类型 [1-3, 默认2]: ").strip()
                dtype_map = {
                    '1': 'number', '2': 'string', '3': 'datetime', '': 'string'
                }
                dtype = dtype_map.get(dtype_choice, 'string')

                # 可选说明
                description = input("\n说明（可选，直接回车跳过）: ").strip()

                # 保存映射
                analyzer.mapping_manager.add_custom_mapping(
                    cn_field=cn_field,
                    en_name=en_name,
                    group=group,
                    dtype=dtype,
                    description=description or f"{cn_field}的自定义映射"
                )

                print(f"✅ 已保存: {cn_field} → {en_name} ({group}, {dtype})")

            # 重新分析
            print(f"\n{'='*60}")
            print(f"🔄 使用新映射重新分析...")
            print(f"{'='*60}\n")

            # 重新创建分析器以加载新映射
            analyzer = ExcelAnalyzer()
            result = analyzer.analyze_excel(str(xlsx_path), output_dir, topn)

    # 显示最终结果
    if result['success']:
        print(f"\n{'='*60}")
        print(f"✅ 分析完成！")
        print(f"{'='*60}")
        print(f"📊 工作表数: {len(result['sheets'])}")
        print(f"   工作表: {', '.join(result['sheets'])}")
        print(f"\n📝 字段统计:")
        print(f"   总字段数: {result['field_stats']['total_fields']}")
        print(f"   ✓ 已映射: {result['field_stats']['mapped_count']}")
        print(f"   ? 未知字段: {result['field_stats']['unknown_count']}")

        if result['field_stats']['by_dtype']:
            print(f"\n📊 类型分布:")
            for dtype, count in result['field_stats']['by_dtype'].items():
                print(f"   {dtype}: {count}")

        if result['field_stats']['by_group']:
            print(f"\n🏷️  分组分布:")
            for group, count in result['field_stats']['by_group'].items():
                print(f"   {group}: {count}")

        print(f"\n📄 输出文件:")
        print(f"   HTML报告: {result['html_path']}")
        print(f"   JSON映射: {result['json_path']}")
        print(f"{'='*60}\n")

    return result


def suggest_english_name(cn_field: str) -> str:
    """基于中文字段名建议英文名"""
    import re

    # 简单的拼音映射（可以扩展）
    common_words = {
        '客户': 'customer',
        '等级': 'level',
        '满意度': 'satisfaction',
        '评分': 'score',
        '代理': 'agent',
        '代理商': 'agent',
        '风险': 'risk',
        '预警': 'warning',
        '标识': 'flag',
        '状态': 'status',
        '类型': 'type',
        '来源': 'source',
        '渠道': 'channel',
        '金额': 'amount',
        '数量': 'count',
        '比率': 'ratio',
        '占比': 'percentage',
        '名称': 'name',
        '编号': 'code',
        '地区': 'region',
        '省份': 'province',
        '城市': 'city',
    }

    # 尝试匹配常见词
    tokens = []
    remaining = cn_field

    for cn, en in sorted(common_words.items(), key=lambda x: len(x[0]), reverse=True):
        if cn in remaining:
            tokens.append(en)
            remaining = remaining.replace(cn, '')

    if tokens:
        return '_'.join(tokens)

    # 否则返回简单的字段名
    # 移除特殊字符
    clean = re.sub(r'[^\w]', '', cn_field)
    return f"field_{clean[:20]}"  # 限制长度


def main():
    """主程序"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python interactive_analyzer.py <Excel文件路径> [输出目录] [topn]")
        print("\n示例:")
        print("  python interactive_analyzer.py data.xlsx")
        print("  python interactive_analyzer.py data.xlsx ./output 20")
        sys.exit(1)

    xlsx_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './analysis_output'
    topn = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    try:
        result = analyze_with_learning(xlsx_path, output_dir, topn)
        if result and result['success']:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
