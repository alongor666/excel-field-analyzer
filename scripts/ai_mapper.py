#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI驱动的批量字段映射生成器
自动分析未知字段并生成英文映射建议
"""

import re
from typing import List, Dict, Any
import pandas as pd


class AIFieldMapper:
    """AI字段映射生成器"""

    def __init__(self):
        # 车险业务领域关键词映射
        self.keyword_patterns = {
            # 时间相关
            r'时间|日期': ('time', 'datetime'),
            r'起期|止期|生效|到期': ('time', 'datetime'),

            # 机构相关
            r'机构|支公司|中心|分公司|营业部': ('organization', 'string'),
            r'业务员|代理|经纪': ('organization', 'string'),

            # 财务相关
            r'保费|费用|金额|赔款|NCD|折扣': ('finance', 'number'),
            r'手续费|佣金|税|价格': ('finance', 'number'),

            # 产品相关
            r'险种|险别|险类|产品': ('product', 'string'),
            r'保额|保障|限额': ('product', 'number'),

            # 车辆相关
            r'车牌|车架|发动机|车型|厂牌': ('vehicle', 'string'),
            r'吨位|座位|排量|功率': ('vehicle', 'number'),

            # 标识相关
            r'^是否': ('flag', 'string'),
            r'标识|标志|类型': ('flag', 'string'),

            # 客户相关
            r'客户|被保险人|投保人|姓名': ('general', 'string'),
            r'证件|身份': ('general', 'string'),

            # 保单相关
            r'保单号|批单号|单号': ('general', 'string'),
            r'续保|转保|新保': ('flag', 'string'),
        }

    def pinyin_convert(self, chinese: str) -> str:
        """
        中文转拼音的简化版本（基于常见模式）
        实际使用时可以集成pypinyin库获得更好效果
        """
        # 简化版：提取关键词并转换
        mappings = {
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
            '批单': 'endorsement',
            '业务员': 'agent',
            '是否': 'is',
            '新旧车': 'new_old_car',
            '续保': 'renewal',
            '转保': 'transfer',
            '标识': 'flag',
            '类型': 'type',
            '金额': 'amount',
            '折扣': 'discount',
            '系数': 'coefficient',
            '起期': 'start_date',
            '确认': 'confirm',
            '投保': 'insure',
            '被保险人': 'insured',
            '投保人': 'applicant',
            '证件号': 'id_number',
            '年龄': 'age',
            '性别': 'gender',
            '车型': 'vehicle_model',
            '车架号': 'vin',
            '发动机号': 'engine_number',
            '代理': 'agent',
            '经纪': 'broker',
            '签单': 'signing',
            '批改': 'endorsement',
            '保额': 'insured_amount',
            '手续费': 'commission',
            '比例': 'ratio',
            '含税': 'tax_included',
            '优待': 'discount',
            '增值税': 'vat',
            '座位数': 'seats',
            '吨位': 'tonnage',
            '排量': 'displacement',
            '整备质量': 'curb_weight',
            '购置价': 'purchase_price',
            '使用年限': 'service_years',
            '笔数': 'count',
            '数量': 'quantity',
            '来源': 'source',
            '性质': 'nature',
            '归属': 'attribution',
            '分组': 'group',
            '分段': 'segment',
            '等级': 'level',
            '评分': 'score',
            '风险': 'risk',
            '高速': 'highway',
            '货车': 'truck',
            '种类': 'category',
            '交叉': 'cross',
            '销售': 'sales',
            '过户': 'transfer_ownership',
            '新能源': 'new_energy',
            '网约车': 'online_hailing',
            '异地': 'non_local',
            '营业': 'business',
            '企业': 'enterprise',
            '集团': 'group',
            '刷新': 'refresh',
        }

        # 尝试匹配关键词
        tokens = []
        remaining = chinese

        # 按长度降序排列，优先匹配长词
        sorted_keys = sorted(mappings.keys(), key=len, reverse=True)

        for key in sorted_keys:
            if key in remaining:
                tokens.append(mappings[key])
                remaining = remaining.replace(key, '', 1)

        # ⚠️ 不再添加'field'占位符！
        # 如果完全无法识别，使用拼音首字母或返回空（由上层处理）
        if not tokens:
            # 最后的兜底：返回一个基本标识（但避免使用'field'）
            return 'unmapped'

        return '_'.join(tokens)

    def analyze_field(self, field_name: str, sample_values: List[Any] = None) -> Dict[str, str]:
        """
        分析单个字段，生成映射建议（专业标准）

        Args:
            field_name: 中文字段名
            sample_values: 字段的示例数据

        Returns:
            {'en_name': str, 'group': str, 'dtype': str, 'description': str}
        """
        # 1. 检测分组和基础类型（基于关键词）
        group = 'general'
        dtype = 'string'

        for pattern, (grp, dt) in self.keyword_patterns.items():
            if re.search(pattern, field_name):
                group = grp
                dtype = dt
                break

        # 2. 🆕 专业类型检测（优先级更高）
        # ⚠️ 保单号/批单号/证件号必须是 string
        if any(keyword in field_name for keyword in ['保单号', '批单号', '证件号', '单号', '编号']):
            dtype = 'string'

        # ⚠️ 时间/日期/起期必须是 datetime
        if any(keyword in field_name for keyword in ['时间', '日期', '起期', '止期', '生效', '到期']):
            dtype = 'datetime'

        # ⚠️ "是否"字段设置为 enum
        if field_name.startswith('是否'):
            dtype = 'enum'
            group = 'flag'

        # 3. 样本数据辅助推断（但不能覆盖专业规则）
        if sample_values and dtype not in ['datetime', 'enum']:
            non_null_values = [v for v in sample_values if pd.notna(v) and str(v).strip()]
            if non_null_values:
                try:
                    sample_str = str(non_null_values[0])
                    # 只有在没有明确规则时才尝试推断数值
                    if dtype == 'string' and sample_str.replace('.', '').replace('-', '').replace(',', '').isdigit():
                        # 如果不是单号类，可以设为number
                        if '号' not in field_name and '编号' not in field_name:
                            dtype = 'number'
                except:
                    pass

        # 4. 生成英文字段名
        base_en_name = self.pinyin_convert(field_name)

        # 5. 🆕 添加专业后缀（单位/格式标注）
        en_name = base_en_name

        # ⚠️ 金额字段添加 _yuan 后缀
        if any(keyword in field_name for keyword in ['保费', '费用', '金额', '价格', '赔款', '手续费', '税', '购置价']):
            if dtype == 'number' and not en_name.endswith('_yuan'):
                en_name = en_name + '_yuan'

        # ⚠️ 比例字段添加 _percent 后缀
        if '比例' in field_name and dtype == 'number':
            if not en_name.endswith(('_percent', '_ratio')):
                en_name = en_name + '_percent'

        # ⚠️ 系数/折扣字段添加 _coefficient 后缀
        if any(keyword in field_name for keyword in ['系数', '折扣']) and dtype == 'number':
            if not en_name.endswith('_coefficient'):
                en_name = en_name + '_coefficient'

        # 6. 生成描述
        description = f"{field_name} [组:{group}, 类型:{dtype}]"

        return {
            'en_name': en_name,
            'group': group,
            'dtype': dtype,
            'description': description
        }

    def batch_analyze_fields(
        self,
        unknown_fields: List[str],
        df: pd.DataFrame = None,
        sample_size: int = 100
    ) -> Dict[str, Dict[str, str]]:
        """
        批量分析未知字段

        Args:
            unknown_fields: 未知字段列表
            df: 包含这些字段的DataFrame（可选）
            sample_size: 采样数量

        Returns:
            {field_name: mapping_dict}
        """
        mappings = {}

        for field in unknown_fields:
            # 获取样本数据
            sample_values = None
            if df is not None and field in df.columns:
                sample_values = df[field].dropna().head(sample_size).tolist()

            # 分析字段
            mapping = self.analyze_field(field, sample_values)
            mappings[field] = mapping

        return mappings

    def format_as_json_config(self, mappings: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """
        将映射转换为JSON配置格式

        Returns:
            符合field_mappings/*.json格式的配置
        """
        config_mappings = {}

        for cn_field, mapping in mappings.items():
            config_mappings[cn_field] = {
                'en_name': mapping['en_name'],
                'group': mapping['group'],
                'dtype': mapping['dtype'],
                'description': mapping['description']
            }

        return {
            'domain': 'auto_learned',
            'description': 'AI自动学习生成的字段映射',
            'version': '1.0',
            'mappings': config_mappings,
            'learn_history': []
        }


if __name__ == '__main__':
    # 测试
    mapper = AIFieldMapper()

    test_fields = [
        '保单号',
        '车牌号码',
        '签单保费',
        '是否续保',
        '投保确认时间',
        '三级机构',
        '商业险保费'
    ]

    results = mapper.batch_analyze_fields(test_fields)

    print("AI字段映射生成测试:")
    print("=" * 60)
    for field, mapping in results.items():
        print(f"\n{field}:")
        print(f"  英文名: {mapping['en_name']}")
        print(f"  分组: {mapping['group']}")
        print(f"  类型: {mapping['dtype']}")
        print(f"  描述: {mapping['description']}")
