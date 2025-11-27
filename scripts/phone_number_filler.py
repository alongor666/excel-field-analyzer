#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手机号码自动填充工具
自动检测并填充Excel/CSV文件中的空手机号码字段
使用未启用的100号段（10000000000-10099999999）
"""

import os
import sys
import random
import argparse
import pandas as pd
from pathlib import Path
from typing import List, Optional, Tuple


class PhoneNumberFiller:
    """手机号码自动填充器"""

    # 手机号码字段的常见关键词
    PHONE_KEYWORDS = [
        '手机', '电话', '联系方式', '联系电话', '移动电话',
        'phone', 'mobile', 'tel', 'telephone', 'contact'
    ]

    # 空值的各种表示形式
    EMPTY_VALUES = ['', 'nan', 'none', 'null', '无', '空', 'n/a', 'na']

    def __init__(self, prefix: str = '100'):
        """
        初始化填充器

        Args:
            prefix: 手机号码前缀（默认100，未启用号段）
        """
        if len(prefix) != 3:
            raise ValueError("手机号码前缀必须是3位数字")
        if not prefix.isdigit():
            raise ValueError("手机号码前缀必须是数字")
        if not prefix.startswith('1'):
            raise ValueError("手机号码必须以1开头")

        self.prefix = prefix
        print(f"📱 使用号段: {prefix}xxxxxxxx (中国未启用的{prefix[0:3]}号段)")

    def generate_phone_number(self) -> str:
        """
        生成一个11位的随机手机号码
        格式: {prefix} + 8位随机数字

        Returns:
            11位手机号码字符串
        """
        # 生成8位随机数字
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f"{self.prefix}{suffix}"

    def is_csv_file(self, file_path: Path) -> bool:
        """检测是否为CSV文件"""
        return file_path.suffix.lower() in ['.csv', '.txt']

    def detect_phone_fields(self, df: pd.DataFrame) -> List[str]:
        """
        自动检测可能的手机号码字段

        Args:
            df: DataFrame对象

        Returns:
            可能的手机号码字段名列表
        """
        phone_fields = []

        for col in df.columns:
            col_lower = str(col).lower()
            # 检查列名是否包含手机号关键词
            if any(keyword in col_lower for keyword in self.PHONE_KEYWORDS):
                phone_fields.append(col)

        return phone_fields

    def is_empty(self, value) -> bool:
        """
        判断值是否为空

        Args:
            value: 要检查的值

        Returns:
            是否为空
        """
        # pandas的NaN和None
        if pd.isna(value):
            return True

        # 字符串形式的空值
        if isinstance(value, str):
            value_lower = value.strip().lower()
            if value_lower in self.EMPTY_VALUES:
                return True

        return False

    def count_empty_phones(self, df: pd.DataFrame, field: str) -> int:
        """
        统计字段中的空值数量

        Args:
            df: DataFrame对象
            field: 字段名

        Returns:
            空值数量
        """
        return df[field].apply(self.is_empty).sum()

    def fill_phone_numbers(
        self,
        df: pd.DataFrame,
        field: str,
        preview: bool = False
    ) -> Tuple[pd.DataFrame, int]:
        """
        填充手机号码字段的空值

        Args:
            df: DataFrame对象
            field: 要填充的字段名
            preview: 是否为预览模式（不实际修改）

        Returns:
            (修改后的DataFrame, 填充数量)
        """
        if field not in df.columns:
            raise ValueError(f"字段 '{field}' 不存在于数据中")

        # 复制DataFrame以避免修改原数据
        result_df = df.copy()

        # 统计空值数量
        empty_mask = result_df[field].apply(self.is_empty)
        fill_count = empty_mask.sum()

        if fill_count == 0:
            print(f"✅ 字段 '{field}' 没有空值，无需填充")
            return result_df, 0

        if preview:
            print(f"🔍 预览模式: 将填充 {fill_count} 个空值")
            # 显示前5个要填充的示例
            sample_indices = result_df[empty_mask].head(5).index
            for idx in sample_indices:
                sample_phone = self.generate_phone_number()
                print(f"   行 {idx+2}: [空] → {sample_phone}")
            return result_df, fill_count

        # 实际填充
        for idx in result_df[empty_mask].index:
            result_df.at[idx, field] = self.generate_phone_number()

        print(f"✅ 成功填充 {fill_count} 个手机号码")

        return result_df, fill_count

    def load_file(self, file_path: Path, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        加载Excel或CSV文件

        Args:
            file_path: 文件路径
            sheet_name: Excel工作表名（仅用于Excel）

        Returns:
            DataFrame对象
        """
        print(f"📂 正在读取文件: {file_path.name}")

        if self.is_csv_file(file_path):
            # CSV文件
            df = pd.read_csv(file_path, dtype=str, encoding='utf-8-sig')
            print(f"   格式: CSV, 行数: {len(df)}, 列数: {len(df.columns)}")
        else:
            # Excel文件
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
                print(f"   格式: Excel, 工作表: {sheet_name}, 行数: {len(df)}, 列数: {len(df.columns)}")
            else:
                df = pd.read_excel(file_path, dtype=str)
                print(f"   格式: Excel, 行数: {len(df)}, 列数: {len(df.columns)}")

        return df

    def save_file(
        self,
        df: pd.DataFrame,
        original_path: Path,
        output_path: Optional[Path] = None,
        sheet_name: Optional[str] = None
    ) -> Path:
        """
        保存DataFrame到文件

        Args:
            df: DataFrame对象
            original_path: 原始文件路径
            output_path: 输出文件路径（可选）
            sheet_name: Excel工作表名（仅用于Excel）

        Returns:
            保存的文件路径
        """
        # 如果没有指定输出路径，生成默认路径
        if output_path is None:
            stem = original_path.stem
            suffix = original_path.suffix
            output_path = original_path.parent / f"{stem}_filled{suffix}"

        print(f"💾 正在保存文件: {output_path.name}")

        if self.is_csv_file(output_path):
            # 保存为CSV
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
        else:
            # 保存为Excel
            if sheet_name:
                # 如果指定了工作表，需要保留其他工作表
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                df.to_excel(output_path, index=False, engine='openpyxl')

        print(f"✅ 文件已保存: {output_path}")
        return output_path

    def process_file(
        self,
        file_path: str,
        field: Optional[str] = None,
        sheet_name: Optional[str] = None,
        output_path: Optional[str] = None,
        preview: bool = False,
        auto_detect: bool = True
    ) -> dict:
        """
        处理文件并填充手机号码

        Args:
            file_path: 输入文件路径
            field: 手机号码字段名（可选，自动检测）
            sheet_name: Excel工作表名（可选）
            output_path: 输出文件路径（可选）
            preview: 预览模式，不实际修改
            auto_detect: 是否自动检测手机号字段

        Returns:
            处理结果字典
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {
                    'success': False,
                    'message': f'文件不存在: {file_path}'
                }

            # 加载文件
            df = self.load_file(file_path, sheet_name)

            # 确定要处理的字段
            if field:
                # 用户指定了字段
                if field not in df.columns:
                    return {
                        'success': False,
                        'message': f'指定的字段 "{field}" 不存在。可用字段: {", ".join(df.columns)}'
                    }
                phone_fields = [field]
                print(f"🎯 使用指定字段: {field}")
            elif auto_detect:
                # 自动检测
                phone_fields = self.detect_phone_fields(df)
                if not phone_fields:
                    return {
                        'success': False,
                        'message': f'未检测到手机号码字段。请使用 --field 参数手动指定。可用字段: {", ".join(df.columns)}'
                    }
                print(f"🔍 自动检测到手机号字段: {', '.join(phone_fields)}")
            else:
                return {
                    'success': False,
                    'message': '请指定字段名或启用自动检测'
                }

            # 处理每个检测到的字段
            total_filled = 0
            for phone_field in phone_fields:
                empty_count = self.count_empty_phones(df, phone_field)
                print(f"\n📊 字段 '{phone_field}' 统计:")
                print(f"   总行数: {len(df)}")
                print(f"   空值数: {empty_count}")
                print(f"   空值率: {empty_count/len(df)*100:.2f}%")

                if empty_count > 0:
                    df, filled = self.fill_phone_numbers(df, phone_field, preview=preview)
                    total_filled += filled

            if total_filled == 0:
                return {
                    'success': True,
                    'message': '没有需要填充的空值',
                    'filled_count': 0
                }

            # 保存文件（非预览模式）
            if not preview:
                output = Path(output_path) if output_path else None
                saved_path = self.save_file(df, file_path, output, sheet_name)

                return {
                    'success': True,
                    'message': f'成功填充 {total_filled} 个手机号码',
                    'filled_count': total_filled,
                    'output_path': str(saved_path),
                    'phone_fields': phone_fields
                }
            else:
                return {
                    'success': True,
                    'message': f'预览完成，将填充 {total_filled} 个手机号码',
                    'filled_count': total_filled,
                    'phone_fields': phone_fields,
                    'preview': True
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'处理失败: {str(e)}'
            }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='自动填充Excel/CSV文件中的空手机号码字段',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 自动检测并填充手机号字段
  python phone_number_filler.py data.xlsx

  # 指定字段名
  python phone_number_filler.py data.xlsx --field "联系电话"

  # 指定Excel工作表
  python phone_number_filler.py data.xlsx --sheet "客户信息"

  # 预览模式（不实际修改）
  python phone_number_filler.py data.xlsx --preview

  # 指定输出文件
  python phone_number_filler.py data.xlsx --output result.xlsx

  # 使用自定义号段前缀（必须是1字头）
  python phone_number_filler.py data.xlsx --prefix 101
        """
    )

    parser.add_argument('file', help='输入文件路径 (Excel或CSV)')
    parser.add_argument('--field', '-f', help='手机号码字段名（不指定则自动检测）')
    parser.add_argument('--sheet', '-s', help='Excel工作表名（仅Excel文件）')
    parser.add_argument('--output', '-o', help='输出文件路径（默认添加_filled后缀）')
    parser.add_argument('--prefix', '-p', default='100', help='手机号码前缀（默认100）')
    parser.add_argument('--preview', action='store_true', help='预览模式，不实际修改文件')
    parser.add_argument('--no-auto-detect', action='store_true', help='禁用自动检测，必须手动指定字段')

    args = parser.parse_args()

    # 创建填充器
    try:
        filler = PhoneNumberFiller(prefix=args.prefix)
    except ValueError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

    # 处理文件
    result = filler.process_file(
        file_path=args.file,
        field=args.field,
        sheet_name=args.sheet,
        output_path=args.output,
        preview=args.preview,
        auto_detect=not args.no_auto_detect
    )

    # 输出结果
    print(f"\n{'='*60}")
    if result['success']:
        print(f"✅ {result['message']}")
        if not result.get('preview', False) and 'output_path' in result:
            print(f"📁 输出文件: {result['output_path']}")
    else:
        print(f"❌ {result['message']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
