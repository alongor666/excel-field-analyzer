#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字段映射质量检查器
评估中文->英文映射的准确性、合理性和规范性
"""

import json
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
from collections import Counter


class MappingValidator:
    """字段映射质量检查器"""

    def __init__(self):
        # 英文命名规范
        self.naming_pattern = re.compile(r'^[a-z][a-z0-9_]*$')

        # 车险业务领域词汇表（用于验证术语准确性）
        self.domain_terms = {
            # 时间相关
            'time': ['time', 'date', 'datetime', 'start', 'end', 'confirm', 'refresh', 'signing'],
            # 机构相关
            'organization': ['organization', 'branch', 'center', 'company', 'department', 'agent', 'broker'],
            # 财务相关
            'finance': ['premium', 'fee', 'amount', 'cost', 'price', 'commission', 'discount', 'tax', 'vat', 'ncd', 'ratio', 'coefficient'],
            # 产品相关
            'product': ['insurance', 'policy', 'coverage', 'product', 'insured_amount', 'endorsement'],
            # 车辆相关
            'vehicle': ['vehicle', 'car', 'license_plate', 'vin', 'engine', 'model', 'brand', 'seats', 'tonnage', 'displacement', 'weight'],
            # 标识相关
            'flag': ['is', 'has', 'flag', 'type', 'category', 'level', 'status', 'indicator'],
            # 客户相关
            'general': ['customer', 'client', 'name', 'id_number', 'age', 'gender', 'source', 'nature', 'applicant', 'insured', 'owner'],
        }

        # 常见映射模式（中文关键词 -> 预期英文术语）
        self.expected_mappings = {
            '时间': 'time',
            '日期': 'date',
            '保费': 'premium',
            '费用': 'fee',
            '机构': 'organization',
            '支公司': 'branch',
            '险种': 'insurance_type',
            '车牌': 'license_plate',
            '客户': 'customer',
            '保单': 'policy',
            '业务员': 'agent',
            '是否': 'is',
            '标识': 'flag',
            '金额': 'amount',
            '折扣': 'discount',
            '系数': 'coefficient',
            '确认': 'confirm',
            '投保': 'insure',
            '被保险人': 'insured',
            '投保人': 'applicant',
            '证件号': 'id_number',
            '年龄': 'age',
            '性别': 'gender',
            '车型': 'vehicle_model',
            '车架号': 'vin',
            '发动机': 'engine',
            '签单': 'signing',
            '批改': 'endorsement',
            '保额': 'insured_amount',
            '手续费': 'commission',
            '比例': 'ratio',
            '座位': 'seats',
            '吨位': 'tonnage',
            '排量': 'displacement',
        }

    def check_naming_convention(self, en_name: str) -> Tuple[bool, str]:
        """
        检查英文命名规范

        Returns:
            (是否符合规范, 问题描述)
        """
        if not en_name:
            return False, "英文字段名为空"

        if not self.naming_pattern.match(en_name):
            return False, "不符合snake_case命名规范（应为小写字母、数字和下划线）"

        if len(en_name) > 50:
            return False, f"字段名过长({len(en_name)}字符)，建议不超过50字符"

        if en_name.startswith('_') or en_name.endswith('_'):
            return False, "字段名不应以下划线开头或结尾"

        if '__' in en_name:
            return False, "字段名包含连续下划线"

        # ⚠️ 严格禁止：占位符后缀（专业标准）
        if en_name in ['field', 'unknown_field'] or en_name.startswith('field_'):
            return False, "❌ 严重：使用了通用占位符'field'，完全缺乏业务语义"

        # ⚠️ 严格禁止：_field 后缀
        if en_name.endswith('_field'):
            return False, f"❌ 严重：使用占位符后缀'_field'，应改为明确的业务术语（如{en_name.replace('_field', '')}）"

        # ⚠️ 严格禁止：数字后缀（表示重复定义）
        if re.search(r'_field_\d+$', en_name):
            return False, f"❌ 严重：包含'_field_数字'后缀，存在字段重复或命名冲突"

        # 警告：纯数字后缀（可能的重复）
        if re.search(r'_\d+$', en_name) and not en_name.endswith('_3'):  # customer_category_3 这种例外
            # 降低评分但不完全禁止
            pass

        return True, ""

    def check_group_consistency(self, cn_name: str, en_name: str, group: str) -> Tuple[bool, str]:
        """
        检查分组一致性

        Returns:
            (是否一致, 问题描述)
        """
        if group not in self.domain_terms:
            return False, f"未知分组'{group}'"

        # 检查英文名是否包含该分组的领域术语
        en_tokens = set(en_name.lower().split('_'))
        group_terms = set(self.domain_terms[group])

        # 至少有一个领域术语匹配
        if en_tokens & group_terms:
            return True, ""

        # 特殊情况：通用分组允许任何术语
        if group == 'general':
            return True, ""

        return False, f"字段名缺少'{group}'分组的领域术语（如：{', '.join(list(group_terms)[:3])}）"

    def check_semantic_accuracy(self, cn_name: str, en_name: str) -> Tuple[int, List[str]]:
        """
        检查语义准确性

        Returns:
            (准确度评分 0-100, 问题列表)
        """
        score = 100
        issues = []

        # 检查关键词映射
        for cn_keyword, expected_en in self.expected_mappings.items():
            if cn_keyword in cn_name:
                if expected_en not in en_name.lower():
                    score -= 15
                    issues.append(f"中文包含'{cn_keyword}'但英文缺少'{expected_en}'")

        # 检查是否包含中文
        if re.search(r'[\u4e00-\u9fff]', en_name):
            score -= 30
            issues.append("英文字段名包含中文字符")

        # 检查是否过于简化
        if len(en_name.split('_')) == 1 and len(cn_name) > 4:
            score -= 10
            issues.append(f"中文'{cn_name}'较长但英文'{en_name}'过于简化")

        # 检查是否有数字后缀（可能是重复字段）
        if re.search(r'_\d+$', en_name):
            score -= 5
            issues.append("字段名有数字后缀，可能存在重复定义")

        return max(0, score), issues

    def check_dtype_consistency(self, cn_name: str, dtype: str, en_name: str) -> Tuple[bool, str]:
        """
        检查数据类型一致性（专业标准）

        Returns:
            (是否一致, 问题描述)
        """
        issues = []

        # ⚠️ 严格：保单号/批单号/证件号必须是 string（前导零/字母问题）
        if any(keyword in cn_name for keyword in ['保单号', '批单号', '证件号', '单号']):
            if dtype == 'number':
                issues.append(f"❌ 严重：'{cn_name}'标记为number，应为string（可能包含字母或前导零，number会丢失）")

        # ⚠️ 严格：时间/日期/起期必须为 datetime
        if any(keyword in cn_name for keyword in ['时间', '日期', '起期', '止期', '生效', '到期']):
            if dtype != 'datetime':
                issues.append(f"❌ 严重：'{cn_name}'应为datetime类型，实际为{dtype}")

        # ⚠️ 严格："是否"类必须为 bool 或 enum
        if cn_name.startswith('是否'):
            if dtype not in ['bool', 'boolean', 'enum']:
                issues.append(f"❌ 严重：'{cn_name}'应为bool或enum类型，不应使用string（当前：{dtype}）")

        # ⚠️ 金额字段必须有单位标注（_yuan后缀或格式说明）
        if any(keyword in cn_name for keyword in ['保费', '费用', '金额', '价格', '赔款', '手续费', '税']):
            if dtype == 'number' and not ('_yuan' in en_name or '_amount' in en_name):
                issues.append(f"⚠️ 金额字段'{cn_name}'缺少单位标注（建议：{en_name}_yuan 或 currency_yuan格式）")

        # ⚠️ 比例/系数字段需要明确格式
        if any(keyword in cn_name for keyword in ['比例', '折扣', '系数']):
            if dtype == 'number' and not any(suffix in en_name for suffix in ['_ratio', '_percent', '_coefficient', '_rate']):
                issues.append(f"⚠️ '{cn_name}'缺少格式标注（建议：_percent、_ratio 或 _coefficient）")

        # 评分/等级/分数不应该是单纯的度量值
        if any(keyword in cn_name for keyword in ['评分', '等级', '分数', '级别']):
            # 这个在 validate_mapping 中处理 role 检查
            pass

        if issues:
            return False, '; '.join(issues)

        return True, ""

    def validate_mapping(self, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证单个字段映射

        Args:
            mapping: 字段映射字典，包含 cn_name, field_name, group, dtype 等

        Returns:
            验证结果字典
        """
        cn_name = mapping.get('cn_name', '')
        en_name = mapping.get('field_name', '')
        group = mapping.get('group', 'general')
        dtype = mapping.get('dtype', 'string')

        result = {
            'cn_name': cn_name,
            'en_name': en_name,
            'group': group,
            'dtype': dtype,
            'overall_score': 100,
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'quality_level': 'excellent'  # excellent/good/fair/poor
        }

        # 1. 检查命名规范
        naming_ok, naming_issue = self.check_naming_convention(en_name)
        if not naming_ok:
            # 占位符问题非常严重，扣更多分
            if '严重' in naming_issue or 'field' in naming_issue.lower():
                result['overall_score'] -= 40
            else:
                result['overall_score'] -= 20
            result['issues'].append(f"命名规范: {naming_issue}")

        # 2. 检查分组一致性
        group_ok, group_issue = self.check_group_consistency(cn_name, en_name, group)
        if not group_ok:
            result['overall_score'] -= 15
            result['warnings'].append(f"分组一致性: {group_issue}")

        # 3. 检查语义准确性
        semantic_score, semantic_issues = self.check_semantic_accuracy(cn_name, en_name)
        result['overall_score'] = min(result['overall_score'], semantic_score)
        result['issues'].extend(semantic_issues)

        # 4. 检查类型一致性
        dtype_ok, dtype_issue = self.check_dtype_consistency(cn_name, dtype, en_name)
        if not dtype_ok:
            result['overall_score'] -= 20  # 提升惩罚力度
            result['issues'].append(f"类型一致性: {dtype_issue}")

        # 5. 🆕 检查 role 和 aggregation 合理性（专业标准）
        role = mapping.get('role', 'dimension')
        aggregation = mapping.get('aggregation', 'none')

        # ⚠️ 评分/等级/系数不应该是 measure+sum
        if any(keyword in cn_name for keyword in ['评分', '等级', '分数', '级别', '系数']):
            if role == 'measure' and aggregation == 'sum':
                result['overall_score'] -= 25
                result['issues'].append(
                    f"❌ 严重：'{cn_name}'不应设置为 role:measure + aggregation:sum，"
                    f"应为维度（dimension）或使用avg聚合"
                )

        # ⚠️ 比例/系数应该用 avg 而非 sum
        if any(keyword in cn_name for keyword in ['比例', '系数', '折扣', '率']):
            if dtype == 'number' and aggregation == 'sum':
                result['overall_score'] -= 15
                result['warnings'].append(
                    f"⚠️ '{cn_name}'使用sum聚合不合理，系数类字段应使用avg或none"
                )

        # ⚠️ 保费/金额/费用应该用 sum（这个是正确的）
        if any(keyword in cn_name for keyword in ['保费', '费用', '金额', '价格', '赔款', '手续费', '税']):
            if role == 'measure' and aggregation != 'sum':
                result['warnings'].append(
                    f"⚠️ '{cn_name}'是金额字段，建议使用sum聚合"
                )

        # 6. 生成改进建议
        if result['overall_score'] < 70:
            result['suggestions'].append("建议人工审核此映射")

            # 基于中文生成建议的英文名
            suggested_en = self._suggest_better_mapping(cn_name)
            if suggested_en and suggested_en != en_name:
                result['suggestions'].append(f"建议英文名: {suggested_en}")

        # 7. 确定质量等级（专业标准，更严格）
        score = result['overall_score']
        if score >= 95:  # 提高优秀标准
            result['quality_level'] = 'excellent'
        elif score >= 80:  # 提高良好标准
            result['quality_level'] = 'good'
        elif score >= 65:  # 提高一般标准
            result['quality_level'] = 'fair'
        else:
            result['quality_level'] = 'poor'

        # 8. 🆕 特殊标记：严重问题
        critical_issues = [issue for issue in result['issues'] if '❌ 严重' in issue]
        if critical_issues:
            result['has_critical_issues'] = True
            # 有严重问题的不能是优秀
            if result['quality_level'] == 'excellent':
                result['quality_level'] = 'good'

        return result

    def _suggest_better_mapping(self, cn_name: str) -> str:
        """基于中文名建议更好的英文映射"""
        tokens = []
        remaining = cn_name

        # 按长度降序匹配关键词
        sorted_keywords = sorted(self.expected_mappings.keys(), key=len, reverse=True)

        for keyword in sorted_keywords:
            if keyword in remaining:
                tokens.append(self.expected_mappings[keyword])
                remaining = remaining.replace(keyword, '', 1)

        if tokens:
            return '_'.join(tokens)
        return ''

    def batch_validate(self, mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量验证字段映射

        Args:
            mappings: 字段映射列表

        Returns:
            批量验证结果
        """
        results = []
        stats = {
            'total': len(mappings),
            'excellent': 0,
            'good': 0,
            'fair': 0,
            'poor': 0,
            'avg_score': 0,
            'needs_review': [],
            'critical_issues_count': 0  # 🆕 严重问题计数
        }

        total_score = 0

        for mapping in mappings:
            result = self.validate_mapping(mapping)
            results.append(result)

            # 统计
            stats[result['quality_level']] += 1
            total_score += result['overall_score']

            # 🆕 统计严重问题
            if result.get('has_critical_issues', False):
                stats['critical_issues_count'] += 1

            # 需要审核的映射（提高阈值到80，更严格）
            if result['overall_score'] < 80:
                stats['needs_review'].append({
                    'cn_name': result['cn_name'],
                    'en_name': result['en_name'],
                    'score': result['overall_score'],
                    'issues': result['issues'],
                    'warnings': result.get('warnings', []),
                    'suggestions': result.get('suggestions', [])
                })

        stats['avg_score'] = round(total_score / len(mappings), 2) if mappings else 0

        return {
            'results': results,
            'stats': stats
        }

    def generate_report(self, validation_result: Dict[str, Any], output_path: Path = None) -> str:
        """
        生成质量检查报告（Markdown格式）

        Args:
            validation_result: 批量验证结果
            output_path: 报告输出路径（可选）

        Returns:
            Markdown格式的报告内容
        """
        stats = validation_result['stats']
        results = validation_result['results']

        report_lines = [
            "# 字段映射质量检查报告（专业标准）\n",
            f"**生成时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**检查标准**: 命名规范、类型准确性、单位标注、聚合合理性\n",
            "---\n",
            "## 📊 总体统计\n",
            f"- **总字段数**: {stats['total']}",
            f"- **平均质量分**: {stats['avg_score']}/100",
            f"- **优秀 (≥95分)**: {stats['excellent']} 个",
            f"- **良好 (80-94分)**: {stats['good']} 个",
            f"- **一般 (65-79分)**: {stats['fair']} 个",
            f"- **较差 (<65分)**: {stats['poor']} 个",
            f"- **❌ 严重问题字段**: {stats.get('critical_issues_count', 0)} 个",
            f"- **⚠️ 需要审核 (<80分)**: {len(stats['needs_review'])} 个\n",
        ]

        # 需要审核的映射
        if stats['needs_review']:
            report_lines.append("## ⚠️ 需要人工审核的映射（<80分）\n")
            for i, item in enumerate(stats['needs_review'][:20], 1):  # 只显示前20个
                report_lines.append(f"### {i}. {item['cn_name']} → `{item['en_name']}` (评分: {item['score']})\n")

                if item['issues']:
                    report_lines.append("**❌ 问题**:")
                    for issue in item['issues']:
                        report_lines.append(f"- {issue}")

                if item.get('warnings'):
                    report_lines.append("\n**⚠️ 警告**:")
                    for warning in item['warnings']:
                        report_lines.append(f"- {warning}")

                if item.get('suggestions'):
                    report_lines.append("\n**💡 建议**:")
                    for suggestion in item['suggestions']:
                        report_lines.append(f"- {suggestion}")

                report_lines.append("")

            if len(stats['needs_review']) > 20:
                report_lines.append(f"\n*（仅显示前20个，共{len(stats['needs_review'])}个需要审核）*\n")

        # 高质量映射示例
        excellent_mappings = [r for r in results if r['quality_level'] == 'excellent'][:10]
        if excellent_mappings:
            report_lines.append("## ✅ 优秀映射示例（前10个）\n")
            report_lines.append("| 中文字段 | 英文字段 | 分组 | 类型 | 评分 |")
            report_lines.append("|---------|---------|------|------|------|")
            for r in excellent_mappings:
                report_lines.append(
                    f"| {r['cn_name']} | `{r['en_name']}` | {r['group']} | {r['dtype']} | {r['overall_score']} |"
                )
            report_lines.append("")

        # 质量分布
        report_lines.append("## 📈 质量分布\n")
        report_lines.append("```")
        report_lines.append(f"优秀 {'█' * (stats['excellent'] * 50 // max(stats['total'], 1))} {stats['excellent']}")
        report_lines.append(f"良好 {'█' * (stats['good'] * 50 // max(stats['total'], 1))} {stats['good']}")
        report_lines.append(f"一般 {'█' * (stats['fair'] * 50 // max(stats['total'], 1))} {stats['fair']}")
        report_lines.append(f"较差 {'█' * (stats['poor'] * 50 // max(stats['total'], 1))} {stats['poor']}")
        report_lines.append("```\n")

        report_content = '\n'.join(report_lines)

        # 保存到文件
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report_content, encoding='utf-8')

        return report_content


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("使用方法: python mapping_validator.py <字段映射JSON路径> [报告输出路径]")
        sys.exit(1)

    mapping_file = Path(sys.argv[1])
    report_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    # 读取映射文件
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mappings = json.load(f)

    # 验证
    validator = MappingValidator()
    validation_result = validator.batch_validate(mappings)

    # 生成报告
    report = validator.generate_report(validation_result, report_path)

    print(report)

    if report_path:
        print(f"\n✅ 报告已保存到: {report_path}")
