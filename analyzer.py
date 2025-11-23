#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel字段分析引擎 - Claude Code Skill版本
支持多源字段映射配置、交互式学习和AI批量映射生成
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import Counter

# 导入AI映射器
try:
    from ai_mapper import AIFieldMapper
    AI_MAPPER_AVAILABLE = True
except ImportError:
    AI_MAPPER_AVAILABLE = False
    print("⚠️ AI映射器未加载，批量学习功能不可用")

# 导入质量检查器
try:
    from mapping_validator import MappingValidator
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False
    print("⚠️ 质量检查器未加载，映射质量验证功能不可用")


class FieldMappingManager:
    """字段映射管理器 - 支持多源配置"""

    def __init__(self, skill_dir: Path):
        self.skill_dir = skill_dir
        self.mappings_dir = skill_dir / 'field_mappings'
        self.combined_mappings = {}
        self.load_all_mappings()

    def load_all_mappings(self):
        """加载所有映射配置文件"""
        if not self.mappings_dir.exists():
            return

        for json_file in self.mappings_dir.glob('*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    mappings = config.get('mappings', {})
                    # 合并到总映射表（后加载的会覆盖先加载的）
                    self.combined_mappings.update(mappings)
            except Exception as e:
                print(f"⚠️ 加载映射文件失败 {json_file.name}: {e}")

    def get_mapping(self, cn_field: str) -> Optional[Dict]:
        """获取字段映射"""
        return self.combined_mappings.get(cn_field)

    def add_custom_mapping(self, cn_field: str, en_name: str, group: str, dtype: str, description: str = ""):
        """添加自定义映射并保存"""
        custom_file = self.mappings_dir / 'custom.json'

        # 读取现有配置
        if custom_file.exists():
            with open(custom_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {
                "domain": "custom",
                "description": "用户自定义字段映射",
                "version": "1.0",
                "mappings": {},
                "learn_history": []
            }

        # 添加新映射
        config['mappings'][cn_field] = {
            "en_name": en_name,
            "group": group,
            "dtype": dtype,
            "description": description or f"{cn_field}的自定义映射"
        }

        # 记录学习历史
        config['learn_history'].append({
            "cn_field": cn_field,
            "en_name": en_name,
            "learned_at": datetime.now().isoformat()
        })

        # 保存
        with open(custom_file, 'w', encoding='utf-8') as f:
            json.dump(config, ensure_ascii=False, indent=2, fp=f)

        # 更新内存中的映射
        self.combined_mappings[cn_field] = config['mappings'][cn_field]

    def get_phrase_to_token_dict(self) -> Dict[str, str]:
        """生成短语到token的字典（兼容旧版）"""
        result = {}
        for cn_field, mapping in self.combined_mappings.items():
            result[cn_field] = mapping['en_name']
        return result

    def batch_learn_fields(self, unknown_fields: List[str], df: pd.DataFrame = None) -> Dict[str, Dict[str, str]]:
        """
        使用AI批量学习未知字段

        Args:
            unknown_fields: 未知字段列表
            df: 包含这些字段的DataFrame

        Returns:
            生成的字段映射
        """
        if not AI_MAPPER_AVAILABLE:
            print("❌ AI映射器不可用，无法进行批量学习")
            return {}

        ai_mapper = AIFieldMapper()
        mappings = ai_mapper.batch_analyze_fields(unknown_fields, df)

        # 批量保存到custom.json
        for cn_field, mapping in mappings.items():
            self.add_custom_mapping(
                cn_field=cn_field,
                en_name=mapping['en_name'],
                group=mapping['group'],
                dtype=mapping['dtype'],
                description=mapping['description']
            )

        return mappings


class ExcelAnalyzer:
    """Excel字段分析器 - 增强版"""

    def __init__(self, skill_dir: Optional[Path] = None):
        if skill_dir is None:
            skill_dir = Path(__file__).parent

        self.mapping_manager = FieldMappingManager(skill_dir)
        self.phrase_to_token = self.mapping_manager.get_phrase_to_token_dict()

    def is_csv_file(self, file_path: Path) -> bool:
        """检测是否为CSV文件"""
        return file_path.suffix.lower() in ['.csv', '.txt']

    def load_sheet(self, file_path: Path, sheet_name: str = None) -> pd.DataFrame:
        """读取指定工作表或CSV文件"""
        if self.is_csv_file(file_path):
            # CSV文件
            df = pd.read_csv(file_path, dtype=str, encoding='utf-8-sig')
        else:
            # Excel文件
            df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)

        df = df.map(lambda x: str(x).strip() if pd.notna(x) else x)

        # 识别时间列
        time_cols = [c for c in df.columns if ('时间' in str(c)) or ('日期' in str(c))]
        for c in time_cols:
            df[c] = pd.to_datetime(df[c], errors='coerce')

        # 识别数值列
        num_like = [c for c in df.columns if any(k in str(c) for k in [
            '金额', '保费', 'NCD', '费用', '总费用', '赔款', '赔付',
            '案件数', '频度', '系数', '评分', '(万)', '（万）', '率'
        ])]
        for c in num_like:
            s = df[c].str.replace(',', '', regex=False)
            df[c] = pd.to_numeric(s, errors='coerce')

        return df

    def summarize_columns(self, df: pd.DataFrame, topn: int = 10) -> Dict[str, Dict[str, Any]]:
        """生成列级摘要"""
        summary: Dict[str, Dict[str, Any]] = {}
        for c in df.columns:
            col = df[c]
            n = len(col)
            na = int(col.isna().sum())
            non_na = n - na
            uniq = int(col.nunique(dropna=True))
            freq: Any = None
            numeric_stats: Optional[Dict[str, float]] = None

            if np.issubdtype(col.dtype, np.datetime64):
                freq = Counter(col.dt.date.astype('str')).most_common(topn)
            elif np.issubdtype(col.dtype, np.number):
                valid = col.dropna()
                if len(valid):
                    numeric_stats = {
                        'min': float(valid.min()),
                        'max': float(valid.max()),
                        'mean': float(valid.mean()),
                        'sum': float(valid.sum()),
                    }
                freq = Counter(valid.astype('float').round(2).astype('str')).most_common(topn) if len(valid) else []
            else:
                freq = Counter(col.dropna().astype('str')).most_common(topn)

            summary[c] = {
                'rows': n,
                'non_null': non_na,
                'null': na,
                'null_pct': round(na / n * 100, 6) if n else 0.0,
                'unique': uniq,
                'top_values': freq,
                'numeric_stats': numeric_stats,
                'dtype': str(col.dtype),
            }
        return summary

    def derive_group(self, col: str) -> str:
        """根据列名关键词归类"""
        name = str(col)
        if ('时间' in name) or ('日期' in name):
            return 'time'
        if '机构' in name:
            return 'organization'
        if ('保费' in name) or ('费用' in name) or ('NCD' in name):
            return 'finance'
        if ('险' in name):
            return 'product'
        if ('是否' in name):
            return 'flag'
        if ('4S' in name) or ('集团' in name):
            return 'partner'
        if ('车牌' in name):
            return 'vehicle'
        if ('车' in name):
            return 'vehicle'
        return 'general'

    def dtype_to_role(self, dtype_str: str) -> str:
        """dtype映射为role"""
        if dtype_str.startswith('float') or dtype_str.startswith('int'):
            return 'measure'
        return 'dimension'

    def dtype_to_kind(self, dtype_str: str) -> str:
        """dtype映射为kind"""
        if dtype_str.startswith('float') or dtype_str.startswith('int'):
            return 'number'
        if 'datetime' in dtype_str:
            return 'datetime'
        return 'string'

    def default_aggregation(self, role: str) -> str:
        """默认聚合方式"""
        return 'sum' if role == 'measure' else 'none'

    def generate_alias_from_cn(self, col: str) -> tuple[str, bool]:
        """
        根据中文列名生成英文别名
        返回: (英文名, 是否在映射库中找到)
        """
        text = str(col)

        # 优先完全匹配
        mapping = self.mapping_manager.get_mapping(text)
        if mapping:
            return mapping['en_name'], True

        # 短语匹配（贪婪最长）
        phrases = sorted(self.phrase_to_token.items(), key=lambda kv: len(kv[0]), reverse=True)
        tokens: list[str] = []
        for ph, tk in phrases:
            if ph in text and tk not in tokens:
                tokens.append(tk)
                text = text.replace(ph, '')

        if tokens:
            return '_'.join(tokens), True

        return 'unknown_field', False

    def build_field_mapping(self, sheet_summary: Dict[str, Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[str]]:
        """
        生成字段映射列表
        返回: (映射列表, 未知字段列表)
        """
        mapping: List[Dict[str, Any]] = []
        used_names: Dict[str, int] = {}
        unknown_fields: List[str] = []

        for idx, (col, s) in enumerate(sheet_summary.items()):
            dtype_str = str(s['dtype'])

            # 优先使用映射库中的信息（包括英文名）
            field_mapping = self.mapping_manager.get_mapping(str(col))
            if field_mapping:
                # ✅ 使用映射库中的英文名、group、dtype和description
                field_en = field_mapping['en_name']
                group = field_mapping.get('group', self.derive_group(col))
                kind = field_mapping.get('dtype', self.dtype_to_kind(dtype_str))
                desc = field_mapping.get('description', str(col))
                found = True
            else:
                # 如果映射库中没有，才使用自动生成
                field_en, found = self.generate_alias_from_cn(str(col))
                if not found:
                    unknown_fields.append(str(col))

                # 使用自动推断
                group = self.derive_group(col)
                kind = self.dtype_to_kind(dtype_str)
                # 生成描述
                if kind == 'number':
                    desc = f"数值字段（{col}），可用于按时间/机构等维度进行汇总分析。"
                elif kind == 'datetime':
                    desc = f"时间字段（{col}），可用于时间序列统计与趋势分析。"
                else:
                    desc = f"分类/文本字段（{col}），可用于分组与维度统计。"

            role = self.dtype_to_role(dtype_str)

            # 🆕 专业role/aggregation规则（覆盖默认行为）
            col_name = str(col)

            # 1. 评分/等级/分数/级别 字段应为维度（dimension），而非度量
            if any(keyword in col_name for keyword in ['评分', '等级', '分数', '级别']):
                role = 'dimension'

            # 2. 系数字段也应为维度或使用平均值聚合
            if '系数' in col_name:
                role = 'dimension'

            # 3. 比例/折扣/系数字段如果是度量，应使用平均值聚合（不应求和）
            aggregation = self.default_aggregation(role)
            if role == 'measure':
                if any(keyword in col_name for keyword in ['比例', '折扣', '系数', 'NCD', '优待']):
                    aggregation = 'avg'
                # 保费/金额/费用等确保使用sum（这是默认值，但显式确认）
                elif any(keyword in col_name for keyword in ['保费', '金额', '费用', '价格', '赔款', '手续费', '税']):
                    aggregation = 'sum'

            # 确保英文名唯一
            if field_en in used_names:
                used_names[field_en] += 1
                field_en = f"{field_en}_{used_names[field_en]}"
            else:
                used_names[field_en] = 0

            notes = []
            null_pct = s.get('null_pct', 0.0)
            if null_pct > 0:
                notes.append(f"空值率约 {null_pct}%")
            if kind == 'number' and s.get('numeric_stats'):
                ns = s['numeric_stats']
                if ns['min'] < 0:
                    notes.append("存在负数，可能为冲销/退款/批改")

            mapping.append({
                'field_name': field_en,
                'cn_name': str(col),
                'source_column': str(col),
                'group': group,
                'dtype': kind,
                'role': role,
                'aggregation': aggregation,
                'description': desc,
                'notes': '；'.join(notes) if notes else '',
                'is_mapped': found
            })

        return mapping, unknown_fields

    def html_escape(self, text: str) -> str:
        """HTML 转义"""
        return (
            str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
        )

    def build_html_report(self, xlsx_path: Path, sheets: list, summaries: Dict[str, Dict[str, Dict[str, Any]]], topn: int) -> str:
        """生成HTML报告"""
        file_type = "CSV" if self.is_csv_file(xlsx_path) else "Excel"
        title = f"{file_type} 字段分析报告"
        generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        head = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{self.html_escape(title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; margin: 24px; color: #1e293b; }}
    h1 {{ font-size: 22px; margin-bottom: 8px; }}
    h2 {{ font-size: 18px; margin-top: 24px; margin-bottom: 8px; }}
    .meta {{ color: #475569; font-size: 14px; margin-bottom: 16px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 8px 0 24px; font-size: 14px; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f1f5f9; font-weight: 600; }}
    .code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace; background: #f8fafc; border: 1px solid #e2e8f0; padding: 4px 6px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>{self.html_escape(title)}</h1>
  <div class="meta">数据文件：<span class="code">{self.html_escape(str(xlsx_path))}</span> | 生成时间：{self.html_escape(generated_at)} | 工作表数量：{len(sheets)}（{self.html_escape(', '.join(sheets))}） | Top 值展示：前 {topn} 项</div>
"""
        parts = [head]

        for sheet in sheets:
            parts.append(f"<h2>工作表：{self.html_escape(sheet)}</h2>")
            parts.append("<table>")
            parts.append("<thead><tr>\n"
                         "<th>列名</th>\n"
                         "<th>行数</th>\n"
                         "<th>非空</th>\n"
                         "<th>空值</th>\n"
                         "<th>空值率</th>\n"
                         "<th>唯一值</th>\n"
                         "<th>类型</th>\n"
                         "<th>数值统计</th>\n"
                         "<th>Top 值</th>\n"
                         "</tr></thead>")
            parts.append("<tbody>")

            summary = summaries[sheet]
            for col_name, s in summary.items():
                stats = s.get('numeric_stats')
                stats_str = ''
                if stats:
                    stats_str = f"min={stats['min']:.4f}; max={stats['max']:.4f}; mean={stats['mean']:.4f}; sum={stats['sum']:.4f}"
                tv = s.get('top_values') or []
                tv_str = ', '.join([f"{self.html_escape(v)}({cnt})" for v, cnt in tv])
                parts.append(
                    "<tr>" +
                    f"<td>{self.html_escape(col_name)}</td>" +
                    f"<td>{s['rows']}</td>" +
                    f"<td>{s['non_null']}</td>" +
                    f"<td>{s['null']}</td>" +
                    f"<td>{s['null_pct']}%</td>" +
                    f"<td>{s['unique']}</td>" +
                    f"<td>{self.html_escape(s['dtype'])}</td>" +
                    f"<td>{self.html_escape(stats_str)}</td>" +
                    f"<td>{tv_str}</td>" +
                    "</tr>"
                )
            parts.append("</tbody>")
            parts.append("</table>")

        parts.append("</body></html>")
        return '\n'.join(parts)

    def analyze_excel(self, xlsx_path: str, output_dir: str, topn: int = 10) -> Dict[str, Any]:
        """分析Excel或CSV文件"""
        try:
            xlsx_path = Path(xlsx_path)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            print(f"📊 开始分析: {xlsx_path.name}")

            # 检测文件类型
            if self.is_csv_file(xlsx_path):
                # CSV文件，视为单个工作表
                sheets = [xlsx_path.stem]  # 使用文件名作为工作表名
                print(f"📄 文件类型: CSV")
            else:
                # Excel文件，加载工作簿
                xls = pd.ExcelFile(xlsx_path)
                sheets = xls.sheet_names
                print(f"📄 工作表: {', '.join(sheets)}")

            summaries: Dict[str, Dict[str, Dict[str, Any]]] = {}
            total_rows = 0
            total_cols = 0

            for sheet in sheets:
                if self.is_csv_file(xlsx_path):
                    # CSV文件不需要sheet_name参数
                    df = self.load_sheet(xlsx_path)
                else:
                    # Excel文件需要sheet_name参数
                    df = self.load_sheet(xlsx_path, sheet)

                summary = self.summarize_columns(df, topn=topn)
                summaries[sheet] = summary
                total_rows += len(df)
                total_cols += len(df.columns)

            # 生成输出文件名
            base = xlsx_path.stem
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            html_filename = f"{base}_{timestamp}_分析报告.html"
            json_filename = f"{base}_{timestamp}_字段映射.json"

            html_path = output_dir / html_filename
            json_path = output_dir / json_filename

            # 生成HTML报告
            html = self.build_html_report(xlsx_path, sheets, summaries, topn)
            html_path.write_text(html, encoding='utf-8')
            print(f"✅ HTML报告: {html_path}")

            # 生成字段映射
            first_sheet = sheets[0]
            field_map, unknown_fields = self.build_field_mapping(summaries[first_sheet])

            # 🤖 AI批量学习未知字段
            if unknown_fields and AI_MAPPER_AVAILABLE:
                print(f"\n🔍 发现 {len(unknown_fields)} 个未知字段")
                print("💡 使用AI自动生成字段映射...")

                # 获取DataFrame用于样本分析
                if self.is_csv_file(xlsx_path):
                    df_for_learning = self.load_sheet(xlsx_path)
                else:
                    df_for_learning = self.load_sheet(xlsx_path, first_sheet)

                # AI批量学习
                learned_mappings = self.mapping_manager.batch_learn_fields(unknown_fields, df_for_learning)

                if learned_mappings:
                    print(f"✅ 已生成 {len(learned_mappings)} 个字段映射并保存到 custom.json")

                    # 重新生成字段映射（包含新学习的字段）
                    field_map, unknown_fields = self.build_field_mapping(summaries[first_sheet])

            json_path.write_text(json.dumps(field_map, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"✅ 字段映射: {json_path}")

            # 🔍 映射质量检查
            quality_report_path = None
            if VALIDATOR_AVAILABLE and field_map:
                print(f"\n🔍 进行映射质量检查...")
                validator = MappingValidator()
                validation_result = validator.batch_validate(field_map)

                # 生成质量报告
                quality_report_filename = f"{base}_{timestamp}_质量检查报告.md"
                quality_report_path = output_dir / quality_report_filename
                validator.generate_report(validation_result, quality_report_path)

                stats = validation_result['stats']
                print(f"✅ 质量检查完成:")
                print(f"   平均分: {stats['avg_score']}/100")
                print(f"   优秀: {stats['excellent']}  良好: {stats['good']}  一般: {stats['fair']}  较差: {stats['poor']}")
                if stats['needs_review']:
                    print(f"   ⚠️  需要审核: {len(stats['needs_review'])} 个字段")
                print(f"   报告: {quality_report_path}")

            # 统计信息
            field_stats = {
                'total_fields': len(field_map),
                'by_dtype': {},
                'by_group': {},
                'unknown_count': len(unknown_fields),
                'mapped_count': len(field_map) - len(unknown_fields)
            }

            for field in field_map:
                dtype = field['dtype']
                group = field['group']
                field_stats['by_dtype'][dtype] = field_stats['by_dtype'].get(dtype, 0) + 1
                field_stats['by_group'][group] = field_stats['by_group'].get(group, 0) + 1

            result = {
                'success': True,
                'message': f'成功分析 {len(sheets)} 个工作表',
                'sheets': sheets,
                'total_rows': total_rows,
                'total_cols': total_cols,
                'html_path': str(html_path),
                'json_path': str(json_path),
                'field_stats': field_stats,
                'unknown_fields': unknown_fields,
                'topn': topn
            }

            # 添加质量报告路径
            if quality_report_path:
                result['quality_report_path'] = str(quality_report_path)

            return result

        except Exception as e:
            return {
                'success': False,
                'message': f'分析失败: {str(e)}'
            }


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python analyzer.py <文件路径(Excel/CSV)> [输出目录] [topn]")
        print("支持格式: .xlsx, .xls, .csv, .txt")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './output'
    topn = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    analyzer = ExcelAnalyzer()
    result = analyzer.analyze_excel(file_path, output_dir, topn)

    if result['success']:
        print(f"\n✅ 分析完成！")
        print(f"未知字段数: {len(result['unknown_fields'])}")
        if result['unknown_fields']:
            print(f"未知字段: {', '.join(result['unknown_fields'])}")
    else:
        print(f"\n❌ {result['message']}")
