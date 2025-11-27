#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手机号码自动填充工具
自动识别并填充空的手机号码字段，使用中国未启用的测试号段
"""

import os
import random
import pandas as pd
from pathlib import Path
from typing import List, Set, Tuple, Optional
import re


class PhoneFiller:
    """
    手机号码填充器

    功能：
    - 自动识别文件中的手机号码字段
    - 为空值生成虚拟的11位手机号码
    - 使用未启用的号段（100、102-109）避免与真实号码冲突
    """

    # 未启用的号段列表（优先级从高到低）
    UNUSED_PREFIXES = [
        '100',  # 最安全，明显的测试号段
        '102',  # 未分配
        '103',  # 未分配
        '104',  # 未分配
        '105',  # 未分配
        '106',  # 未分配（虽然用于短信通道，但不是11位手机号）
        '107',  # 未分配
        '108',  # 未分配
        '109',  # 未分配
    ]

    # 手机号码字段名称模式（用于自动识别）
    PHONE_FIELD_PATTERNS = [
        r'手机',
        r'电话',
        r'联系.*电话',
        r'联系.*方式',
        r'mobile',
        r'phone',
        r'tel',
        r'contact',
    ]

    def __init__(self, prefix: str = '100'):
        """
        初始化手机号码填充器

        Args:
            prefix: 使用的号段前缀（默认100）
        """
        if prefix not in self.UNUSED_PREFIXES:
            print(f"⚠️  警告: {prefix} 可能不是安全的测试号段")
            print(f"   推荐使用: {', '.join(self.UNUSED_PREFIXES[:3])}")

        self.prefix = prefix
        self.generated_numbers: Set[str] = set()

    def generate_phone(self) -> str:
        """
        生成一个唯一的11位手机号码

        格式: {prefix}XXXXXXXX (如: 10012345678)

        Returns:
            11位手机号码字符串
        """
        while True:
            # 生成后8位随机数字
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
            phone = f"{self.prefix}{suffix}"

            # 确保不重复
            if phone not in self.generated_numbers:
                self.generated_numbers.add(phone)
                return phone

    def is_phone_field(self, field_name: str) -> bool:
        """
        判断字段是否为手机号码字段

        Args:
            field_name: 字段名称

        Returns:
            True if 是手机号码字段
        """
        field_lower = field_name.lower()

        for pattern in self.PHONE_FIELD_PATTERNS:
            if re.search(pattern, field_lower, re.IGNORECASE):
                return True

        return False

    def detect_phone_columns(self, df: pd.DataFrame) -> List[str]:
        """
        检测DataFrame中的手机号码列

        Args:
            df: DataFrame对象

        Returns:
            手机号码列名列表
        """
        phone_columns = []

        for col in df.columns:
            if self.is_phone_field(col):
                phone_columns.append(col)

        return phone_columns

    def validate_phone_column(self, series: pd.Series) -> Tuple[bool, str]:
        """
        验证列是否确实包含手机号码数据

        Args:
            series: pandas Series对象

        Returns:
            (是否为手机号码列, 原因说明)
        """
        # 过滤掉空值和 'nan' 字符串
        non_null = series[
            series.notna() &
            (series != '') &
            (series != 'nan') &
            (series != 'NaN') &
            (series != 'None')
        ]

        if len(non_null) == 0:
            return True, "列全为空，假定为手机号码列"

        # 检查前10个非空值
        sample = non_null.head(10)

        # 检查是否符合手机号码格式（11位数字）
        phone_pattern = re.compile(r'^1\d{10}$')
        matches = 0

        for val in sample:
            # 处理各种类型
            if isinstance(val, (int, float)):
                val_str = f"{int(val)}"
            else:
                val_str = str(val).strip()

            if phone_pattern.match(val_str):
                matches += 1

        if matches >= len(sample) * 0.5:  # 至少50%符合格式
            return True, f"检测到 {matches}/{len(sample)} 个值符合手机号码格式"

        return False, f"仅 {matches}/{len(sample)} 个值符合格式，可能不是手机号码列"

    def fill_empty_phones(
        self,
        df: pd.DataFrame,
        column: str,
        inplace: bool = False
    ) -> Tuple[pd.DataFrame, int]:
        """
        填充指定列的空手机号码

        Args:
            df: DataFrame对象
            column: 列名
            inplace: 是否直接修改原DataFrame

        Returns:
            (处理后的DataFrame, 填充的数量)
        """
        if not inplace:
            df = df.copy()

        # 找到空值的索引（处理 NaN, 空字符串, 'nan' 字符串等情况）
        # 由于使用 dtype=str 读取，NaN 会被转为字符串 'nan'
        null_mask = (
            df[column].isna() |
            (df[column] == '') |
            (df[column] == ' ') |
            (df[column] == 'nan') |
            (df[column] == 'NaN') |
            (df[column] == 'None')
        )

        null_count = null_mask.sum()

        if null_count == 0:
            return df, 0

        # 生成手机号码并填充（保持为字符串格式）
        for idx in df[null_mask].index:
            df.loc[idx, column] = self.generate_phone()

        return df, null_count

    def process_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        auto_detect: bool = True,
        phone_columns: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> dict:
        """
        处理Excel或CSV文件，填充空的手机号码

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（默认覆盖原文件）
            auto_detect: 是否自动检测手机号码列
            phone_columns: 手动指定的手机号码列名列表
            dry_run: 仅预览不实际修改

        Returns:
            处理结果字典
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"文件不存在: {input_path}")

        # 读取文件
        # 注意：为了正确处理手机号码，需要将数字列读取为字符串
        # 这样可以避免科学计数法和精度损失问题
        if input_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(input_path, dtype=str)
            file_type = 'excel'
        elif input_path.suffix.lower() in ['.csv', '.txt']:
            df = pd.read_csv(input_path, dtype=str)
            file_type = 'csv'
        else:
            raise ValueError(f"不支持的文件格式: {input_path.suffix}")

        result = {
            'file': str(input_path),
            'file_type': file_type,
            'total_rows': len(df),
            'columns_processed': [],
            'total_filled': 0,
            'dry_run': dry_run
        }

        # 确定要处理的列
        if auto_detect:
            detected_columns = self.detect_phone_columns(df)
            columns_to_process = detected_columns
        else:
            columns_to_process = phone_columns or []

        if not columns_to_process:
            result['message'] = '未检测到手机号码列'
            return result

        # 处理每一列
        for col in columns_to_process:
            if col not in df.columns:
                print(f"⚠️  列 '{col}' 不存在，跳过")
                continue

            # 验证是否为手机号码列
            is_valid, reason = self.validate_phone_column(df[col])

            if not is_valid:
                print(f"⚠️  跳过列 '{col}': {reason}")
                continue

            # 填充空值
            if not dry_run:
                df, filled_count = self.fill_empty_phones(df, col, inplace=True)
            else:
                # 预览模式：只计数不修改
                null_mask = df[col].isna() | (df[col] == '') | (df[col] == ' ')
                filled_count = null_mask.sum()

            result['columns_processed'].append({
                'column': col,
                'filled_count': filled_count,
                'validation': reason
            })
            result['total_filled'] += filled_count

            print(f"✅ 列 '{col}': 填充 {filled_count} 个空值")

        # 保存文件
        if not dry_run and result['total_filled'] > 0:
            output_path = output_path or input_path
            output_path = Path(output_path)

            if file_type == 'excel':
                df.to_excel(output_path, index=False)
            else:
                df.to_csv(output_path, index=False)

            result['output_file'] = str(output_path)
            print(f"💾 已保存到: {output_path}")

        return result


def main():
    """命令行工具入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='自动填充Excel/CSV文件中的空手机号码',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 自动检测并填充
  python phone_filler.py data.xlsx

  # 预览模式（不修改文件）
  python phone_filler.py data.xlsx --dry-run

  # 指定输出文件
  python phone_filler.py data.xlsx -o output.xlsx

  # 使用其他号段前缀
  python phone_filler.py data.xlsx --prefix 102

  # 手动指定列名
  python phone_filler.py data.xlsx --columns 手机号 联系电话
        """
    )

    parser.add_argument('input', help='输入文件路径（支持 .xlsx, .xls, .csv）')
    parser.add_argument('-o', '--output', help='输出文件路径（默认覆盖原文件）')
    parser.add_argument('--prefix', default='100',
                       help='号段前缀（默认: 100）')
    parser.add_argument('--columns', nargs='+',
                       help='手动指定手机号码列名（默认自动检测）')
    parser.add_argument('--dry-run', action='store_true',
                       help='预览模式，不实际修改文件')
    parser.add_argument('--no-auto-detect', action='store_true',
                       help='禁用自动检测，必须手动指定列名')

    args = parser.parse_args()

    # 创建填充器
    filler = PhoneFiller(prefix=args.prefix)

    print(f"📱 手机号码填充工具")
    print(f"   使用号段: {args.prefix}XXXXXXXX")
    print(f"   输入文件: {args.input}")

    if args.dry_run:
        print(f"   模式: 预览（不修改文件）")

    print()

    # 处理文件
    try:
        result = filler.process_file(
            input_path=args.input,
            output_path=args.output,
            auto_detect=not args.no_auto_detect,
            phone_columns=args.columns,
            dry_run=args.dry_run
        )

        # 打印总结
        print()
        print("=" * 60)
        print(f"📊 处理总结")
        print(f"   文件: {result['file']}")
        print(f"   总行数: {result['total_rows']}")
        print(f"   处理列数: {len(result['columns_processed'])}")
        print(f"   总填充数: {result['total_filled']}")

        if result['dry_run']:
            print()
            print("💡 这是预览模式。使用 --dry-run=false 实际修改文件")

    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
