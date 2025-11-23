#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-powered Field Mapping Generator for Auto Insurance
Based on industry-standard naming conventions and best practices
"""

import re
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd


class AIFieldMapper:
    """
    AI Field Mapping Generator with Industry-Standard Terminology

    Standards compliance:
    - NAIC insurance terminology
    - snake_case naming convention
    - Standard data types: string, number, datetime, boolean
    - No language-specific suffixes
    """

    def __init__(self):
        # Initialize mapping tables
        self._init_exact_mappings()
        self._init_keyword_patterns()
        self._init_business_groups()

    def _init_exact_mappings(self):
        """Exact match mappings for common insurance fields"""
        self.exact_mappings = {
            # Policy information
            '保单号': ('policy_number', 'policy', 'string'),
            '保险单号': ('policy_number', 'policy', 'string'),
            '批单号': ('endorsement_number', 'policy', 'string'),
            '投保单号': ('application_number', 'policy', 'string'),

            # Premium fields (金额类 - 使用标准命名，不加 _yuan)
            '保费': ('premium', 'finance', 'number'),
            '签单保费': ('written_premium', 'finance', 'number'),
            '商业险保费': ('commercial_premium', 'finance', 'number'),
            '交强险保费': ('compulsory_premium', 'finance', 'number'),
            '批改保费': ('endorsement_premium', 'finance', 'number'),
            '退保保费': ('refund_premium', 'finance', 'number'),
            '实收保费': ('earned_premium', 'finance', 'number'),
            'NCD保费': ('ncd_premium', 'finance', 'number'),
            'NCD基准保费': ('ncd_base_premium', 'finance', 'number'),

            # Claims fields
            '赔款': ('claim_amount', 'finance', 'number'),
            '总赔款': ('total_claims', 'finance', 'number'),
            '案均赔款': ('average_claim', 'finance', 'number'),
            '已决赔款': ('paid_claims', 'finance', 'number'),
            '未决赔款': ('outstanding_claims', 'finance', 'number'),
            '案件数': ('claim_count', 'finance', 'number'),
            '出险次数': ('claim_frequency', 'finance', 'number'),
            '出险频度': ('claim_frequency', 'finance', 'number'),

            # Fees and costs
            '手续费': ('commission', 'finance', 'number'),
            '佣金': ('commission', 'finance', 'number'),
            '费用': ('fee', 'finance', 'number'),
            '总费用': ('total_fee', 'finance', 'number'),
            '费用金额': ('fee_amount', 'finance', 'number'),
            '管理费': ('admin_fee', 'finance', 'number'),

            # Ratios and rates (使用 _rate 或 _ratio 后缀表示比率)
            '费用率': ('expense_ratio', 'finance', 'number'),
            '赔付率': ('loss_ratio', 'finance', 'number'),
            '综合成本率': ('combined_ratio', 'finance', 'number'),
            '变动成本率': ('variable_cost_ratio', 'finance', 'number'),
            '佣金率': ('commission_rate', 'finance', 'number'),
            '折扣率': ('discount_rate', 'finance', 'number'),
            '费率': ('rate', 'finance', 'number'),

            # Discounts and coefficients (使用 _factor 表示系数)
            'NCD系数': ('ncd_factor', 'finance', 'number'),
            '自主系数': ('autonomous_factor', 'finance', 'number'),
            '渠道系数': ('channel_factor', 'finance', 'number'),
            '折扣': ('discount', 'finance', 'number'),
            '优惠金额': ('discount_amount', 'finance', 'number'),

            # Organization fields
            '机构': ('organization', 'organization', 'string'),
            '三级机构': ('level_3_organization', 'organization', 'string'),
            '四级机构': ('level_4_organization', 'organization', 'string'),
            '五级机构': ('level_5_organization', 'organization', 'string'),
            '支公司': ('branch', 'organization', 'string'),
            '分公司': ('division', 'organization', 'string'),
            '中心支公司': ('central_branch', 'organization', 'string'),
            '营业部': ('sales_office', 'organization', 'string'),

            # Agent and channel
            '业务员': ('agent', 'organization', 'string'),
            '代理人': ('agent', 'organization', 'string'),
            '经纪人': ('broker', 'organization', 'string'),
            '渠道': ('channel', 'organization', 'string'),
            '销售渠道': ('sales_channel', 'organization', 'string'),
            '终端来源': ('terminal_source', 'organization', 'string'),

            # Vehicle information
            '车牌号': ('license_plate', 'vehicle', 'string'),
            '车牌号码': ('license_plate', 'vehicle', 'string'),
            '车架号': ('vin', 'vehicle', 'string'),
            '发动机号': ('engine_number', 'vehicle', 'string'),
            '车型': ('vehicle_model', 'vehicle', 'string'),
            '厂牌型号': ('make_model', 'vehicle', 'string'),
            '品牌': ('brand', 'vehicle', 'string'),
            '车辆种类': ('vehicle_type', 'vehicle', 'string'),
            '使用性质': ('use_nature', 'vehicle', 'string'),

            # Vehicle attributes
            '新旧车': ('vehicle_age_category', 'vehicle', 'string'),
            '车龄': ('vehicle_age', 'vehicle', 'number'),
            '座位数': ('seat_count', 'vehicle', 'number'),
            '吨位': ('tonnage', 'vehicle', 'number'),
            '排量': ('displacement', 'vehicle', 'number'),
            '功率': ('power', 'vehicle', 'number'),
            '整备质量': ('curb_weight', 'vehicle', 'number'),
            '购置价': ('purchase_price', 'vehicle', 'number'),
            '新车购置价': ('new_vehicle_price', 'vehicle', 'number'),

            # Product and coverage
            '险种': ('coverage_type', 'product', 'string'),
            '险别': ('coverage', 'product', 'string'),
            '险类': ('insurance_class', 'product', 'string'),
            '产品': ('product', 'product', 'string'),
            '产品名称': ('product_name', 'product', 'string'),
            '保额': ('coverage_amount', 'product', 'number'),
            '保险金额': ('insured_amount', 'product', 'number'),
            '限额': ('limit', 'product', 'number'),

            # Customer information
            '投保人': ('policyholder', 'customer', 'string'),
            '被保险人': ('insured', 'customer', 'string'),
            '客户名称': ('customer_name', 'customer', 'string'),
            '客户类型': ('customer_type', 'customer', 'string'),
            '证件号码': ('id_number', 'customer', 'string'),
            '证件类型': ('id_type', 'customer', 'string'),
            '联系电话': ('phone', 'customer', 'string'),
            '地址': ('address', 'customer', 'string'),

            # Time fields (统一使用 _date 或 _time)
            '保险起期': ('policy_start_date', 'time', 'datetime'),
            '保险止期': ('policy_end_date', 'time', 'datetime'),
            '生效日期': ('effective_date', 'time', 'datetime'),
            '到期日期': ('expiration_date', 'time', 'datetime'),
            '确认时间': ('confirmation_time', 'time', 'datetime'),
            '投保确认时间': ('application_confirmation_time', 'time', 'datetime'),
            '签单时间': ('issuance_time', 'time', 'datetime'),
            '批改时间': ('endorsement_time', 'time', 'datetime'),
            '退保时间': ('cancellation_time', 'time', 'datetime'),
            '出险时间': ('claim_time', 'time', 'datetime'),
            '报案时间': ('report_time', 'time', 'datetime'),
            '刷新时间': ('refresh_time', 'time', 'datetime'),

            # Boolean/Flag fields (使用 is_ 前缀或 _flag 后缀)
            '是否续保': ('is_renewal', 'flag', 'boolean'),
            '是否新能源': ('is_new_energy', 'flag', 'boolean'),
            '是否过户车': ('is_transferred', 'flag', 'boolean'),
            '是否网约车': ('is_ride_hailing', 'flag', 'boolean'),
            '是否营业': ('is_commercial', 'flag', 'boolean'),
            '续保标识': ('renewal_flag', 'flag', 'boolean'),
            '转保标识': ('conversion_flag', 'flag', 'boolean'),

            # Status fields
            '保单状态': ('policy_status', 'general', 'string'),
            '业务状态': ('business_status', 'general', 'string'),
            '承保状态': ('underwriting_status', 'general', 'string'),
            '理赔状态': ('claim_status', 'general', 'string'),

            # Score and rating
            '评分': ('score', 'general', 'number'),
            '风险评分': ('risk_score', 'general', 'number'),
            '等级': ('level', 'general', 'string'),
            '风险等级': ('risk_level', 'general', 'string'),
        }

    def _init_keyword_patterns(self):
        """Keyword patterns for fuzzy matching with priority order"""
        # Format: (pattern, priority, (group, dtype, en_term))
        # Higher priority = checked first
        self.keyword_patterns = [
            # Time-related (Priority 90 - very specific)
            (r'起期$', 90, ('time', 'datetime', 'start_date')),
            (r'止期$', 90, ('time', 'datetime', 'end_date')),
            (r'生效日', 90, ('time', 'datetime', 'effective_date')),
            (r'到期日', 90, ('time', 'datetime', 'expiration_date')),
            (r'确认时间', 85, ('time', 'datetime', 'confirmation_time')),
            (r'(投保|签单|批改|退保|报案|出险)时间', 85, ('time', 'datetime', None)),  # None = use keyword mapping
            (r'时间$', 80, ('time', 'datetime', 'time')),
            (r'日期$', 80, ('time', 'datetime', 'date')),

            # Finance - Premium (Priority 85)
            (r'保费$', 85, ('finance', 'number', 'premium')),
            (r'(签单|商业险|交强险|批改|退保|实收)保费', 85, ('finance', 'number', None)),

            # Finance - Claims (Priority 85)
            (r'赔款$', 85, ('finance', 'number', 'claim_amount')),
            (r'(总|案均|已决|未决)赔款', 85, ('finance', 'number', None)),
            (r'(出险|索赔)次数', 85, ('finance', 'number', 'claim_count')),
            (r'(出险|索赔)频度', 85, ('finance', 'number', 'claim_frequency')),

            # Finance - Fees (Priority 80)
            (r'手续费|佣金', 80, ('finance', 'number', 'commission')),
            (r'费用(金额)?$', 80, ('finance', 'number', 'fee')),
            (r'(管理|服务)费', 80, ('finance', 'number', None)),

            # Finance - Ratios (Priority 80)
            (r'(费用|赔付|综合成本|变动成本)率', 80, ('finance', 'number', None)),
            (r'比率|比例', 75, ('finance', 'number', 'ratio')),

            # Finance - Coefficients (Priority 80)
            (r'(NCD|自主|渠道)系数', 80, ('finance', 'number', None)),
            (r'折扣', 75, ('finance', 'number', 'discount')),

            # Finance - Amounts (Priority 70)
            (r'金额$', 70, ('finance', 'number', 'amount')),
            (r'价格', 70, ('finance', 'number', 'price')),

            # Organization (Priority 75)
            (r'[三四五]级机构', 75, ('organization', 'string', None)),
            (r'(支|分)公司', 75, ('organization', 'string', None)),
            (r'营业部|中心', 70, ('organization', 'string', None)),
            (r'业务员|代理人?|经纪人?', 75, ('organization', 'string', None)),
            (r'渠道', 70, ('organization', 'string', 'channel')),

            # Vehicle (Priority 75)
            (r'车牌(号码?)?', 90, ('vehicle', 'string', 'license_plate')),
            (r'车架号|VIN', 90, ('vehicle', 'string', 'vin')),
            (r'发动机号', 85, ('vehicle', 'string', 'engine_number')),
            (r'车型|厂牌型号', 75, ('vehicle', 'string', 'vehicle_model')),
            (r'品牌', 70, ('vehicle', 'string', 'brand')),
            (r'新旧车', 75, ('vehicle', 'string', 'vehicle_age_category')),
            (r'车龄', 75, ('vehicle', 'number', 'vehicle_age')),
            (r'座位数|吨位|排量|功率', 70, ('vehicle', 'number', None)),

            # Product (Priority 75)
            (r'险种|险别|险类', 80, ('product', 'string', None)),
            (r'产品(名称)?', 75, ('product', 'string', 'product')),
            (r'保额|保险金额|限额', 75, ('product', 'number', None)),

            # Customer (Priority 70)
            (r'投保人|被保险人', 80, ('customer', 'string', None)),
            (r'客户(名称|类型)?', 75, ('customer', 'string', None)),
            (r'证件(号码|类型)', 75, ('customer', 'string', None)),
            (r'联系电话|电话', 70, ('customer', 'string', 'phone')),
            (r'地址', 70, ('customer', 'string', 'address')),

            # Boolean flags (Priority 85)
            (r'^是否', 85, ('flag', 'boolean', None)),
            (r'标识$|标志$', 75, ('flag', 'boolean', 'flag')),

            # Status (Priority 70)
            (r'(保单|业务|承保|理赔)状态', 75, ('general', 'string', None)),
            (r'状态$', 65, ('general', 'string', 'status')),

            # Score and level (Priority 70)
            (r'评分$', 70, ('general', 'number', 'score')),
            (r'等级$', 70, ('general', 'string', 'level')),

            # General (Priority 50)
            (r'类型$|种类$', 60, ('general', 'string', 'type')),
            (r'编号$|号$', 60, ('general', 'string', 'number')),
            (r'名称$', 55, ('general', 'string', 'name')),
        ]

        # Sort by priority (highest first)
        self.keyword_patterns.sort(key=lambda x: x[1], reverse=True)

    def _init_business_groups(self):
        """Business group definitions"""
        self.business_groups = {
            'finance': 'Financial data (premium, claims, fees, ratios)',
            'organization': 'Organization and agent information',
            'vehicle': 'Vehicle information and attributes',
            'product': 'Insurance products and coverage',
            'customer': 'Customer and policyholder information',
            'time': 'Date and time fields',
            'flag': 'Boolean flags and indicators',
            'policy': 'Policy identifiers and numbers',
            'general': 'General fields'
        }

    def _translate_keywords(self, field_name: str) -> List[str]:
        """
        Translate Chinese keywords to English terms
        Returns list of English tokens in order
        """
        # Comprehensive keyword dictionary
        keyword_map = {
            # Numbers and identifiers
            '保单号': 'policy_number',
            '批单号': 'endorsement_number',
            '单号': 'number',
            '编号': 'code',

            # Premium
            '签单保费': 'written_premium',
            '商业险保费': 'commercial_premium',
            '交强险保费': 'compulsory_premium',
            '保费': 'premium',

            # Claims
            '赔款': 'claim',
            '案均': 'average',
            '总': 'total',
            '已决': 'paid',
            '未决': 'outstanding',
            '出险': 'claim',
            '索赔': 'claim',

            # Fees
            '手续费': 'commission',
            '佣金': 'commission',
            '费用': 'fee',
            '管理费': 'admin_fee',

            # Ratios
            '费用率': 'expense_ratio',
            '赔付率': 'loss_ratio',
            '成本率': 'cost_ratio',
            '综合': 'combined',
            '变动': 'variable',
            '率': 'ratio',
            '比率': 'ratio',
            '比例': 'ratio',

            # Coefficients
            'NCD系数': 'ncd_factor',
            '系数': 'factor',
            '折扣': 'discount',
            '优惠': 'discount',

            # Organization
            '三级机构': 'level_3_org',
            '四级机构': 'level_4_org',
            '五级机构': 'level_5_org',
            '机构': 'organization',
            '支公司': 'branch',
            '分公司': 'division',
            '营业部': 'sales_office',
            '中心': 'center',
            '业务员': 'agent',
            '代理人': 'agent',
            '代理': 'agent',
            '经纪人': 'broker',
            '经纪': 'broker',
            '渠道': 'channel',
            '销售': 'sales',
            '终端': 'terminal',
            '来源': 'source',

            # Vehicle
            '车牌': 'license_plate',
            '车架号': 'vin',
            '发动机号': 'engine_number',
            '车型': 'vehicle_model',
            '厂牌': 'make',
            '型号': 'model',
            '品牌': 'brand',
            '新旧车': 'vehicle_age_category',
            '车龄': 'vehicle_age',
            '座位数': 'seat_count',
            '吨位': 'tonnage',
            '排量': 'displacement',
            '功率': 'power',
            '整备质量': 'curb_weight',
            '购置价': 'purchase_price',
            '新车': 'new_vehicle',
            '车辆': 'vehicle',
            '车': 'vehicle',

            # Product
            '险种': 'coverage_type',
            '险别': 'coverage',
            '险类': 'insurance_class',
            '商业险': 'commercial',
            '交强险': 'compulsory',
            '产品': 'product',
            '保额': 'coverage_amount',
            '保险金额': 'insured_amount',
            '金额': 'amount',
            '限额': 'limit',

            # Customer
            '投保人': 'policyholder',
            '被保险人': 'insured',
            '客户': 'customer',
            '证件号': 'id_number',
            '证件': 'id',
            '电话': 'phone',
            '地址': 'address',

            # Time
            '保险起期': 'policy_start_date',
            '保险止期': 'policy_end_date',
            '起期': 'start_date',
            '止期': 'end_date',
            '生效日期': 'effective_date',
            '到期日期': 'expiration_date',
            '确认时间': 'confirmation_time',
            '投保时间': 'application_time',
            '签单时间': 'issuance_time',
            '批改时间': 'endorsement_time',
            '退保时间': 'cancellation_time',
            '报案时间': 'report_time',
            '刷新时间': 'refresh_time',
            '时间': 'time',
            '日期': 'date',
            '投保': 'application',
            '签单': 'issuance',
            '批改': 'endorsement',
            '退保': 'cancellation',
            '报案': 'report',
            '刷新': 'refresh',
            '确认': 'confirmation',

            # Boolean
            '是否': 'is',
            '续保': 'renewal',
            '转保': 'conversion',
            '新能源': 'new_energy',
            '过户': 'transferred',
            '网约车': 'ride_hailing',
            '营业': 'commercial',
            '标识': 'flag',
            '标志': 'flag',

            # Status
            '状态': 'status',
            '保单': 'policy',
            '业务': 'business',
            '承保': 'underwriting',
            '理赔': 'claim',

            # General
            '评分': 'score',
            '等级': 'level',
            '风险': 'risk',
            '类型': 'type',
            '种类': 'category',
            '名称': 'name',
            '次数': 'count',
            '频度': 'frequency',
            '数量': 'quantity',
            '笔数': 'count',
        }

        tokens = []
        remaining = field_name

        # Sort keys by length (longest first) for greedy matching
        sorted_keys = sorted(keyword_map.keys(), key=len, reverse=True)

        for keyword in sorted_keys:
            if keyword in remaining:
                # Found a match
                en_term = keyword_map[keyword]
                if en_term not in tokens:  # Avoid duplicates
                    tokens.append(en_term)
                remaining = remaining.replace(keyword, '', 1)

        return tokens

    def _infer_type_from_samples(self, sample_values: List[Any]) -> str:
        """Infer data type from sample values"""
        if not sample_values:
            return 'string'

        non_null = [v for v in sample_values if pd.notna(v)]
        if not non_null:
            return 'string'

        # Try to infer type
        sample_str = str(non_null[0])

        # Check for datetime patterns
        datetime_patterns = [
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # YYYY-MM-DD or YYYY/MM/DD
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # DD-MM-YYYY or MM/DD/YYYY
            r'\d{4}\d{2}\d{2}',              # YYYYMMDD
        ]
        for pattern in datetime_patterns:
            if re.search(pattern, sample_str):
                return 'datetime'

        # Check for boolean
        if len(set(str(v).strip() for v in non_null if pd.notna(v))) <= 3:
            unique_vals = set(str(v).strip().lower() for v in non_null)
            boolean_indicators = {'是', '否', 'y', 'n', 'yes', 'no', 'true', 'false', '0', '1', 't', 'f'}
            if unique_vals.issubset(boolean_indicators):
                return 'boolean'

        # Check for number
        try:
            # Try to convert to number
            numeric_count = 0
            for v in non_null[:20]:  # Check first 20 values
                v_str = str(v).strip().replace(',', '').replace('，', '')
                try:
                    float(v_str)
                    numeric_count += 1
                except:
                    pass

            if numeric_count / len(non_null[:20]) > 0.8:  # 80% are numbers
                return 'number'
        except:
            pass

        return 'string'

    def analyze_field(
        self,
        field_name: str,
        sample_values: Optional[List[Any]] = None
    ) -> Dict[str, str]:
        """
        Analyze a field and generate mapping suggestion

        Args:
            field_name: Chinese field name
            sample_values: Sample data for type inference

        Returns:
            {
                'en_name': str,      # English field name
                'group': str,        # Business group
                'dtype': str,        # Data type
                'description': str   # Description
            }
        """
        # Step 1: Check exact match first (highest priority)
        if field_name in self.exact_mappings:
            en_name, group, dtype = self.exact_mappings[field_name]
            return {
                'en_name': en_name,
                'group': group,
                'dtype': dtype,
                'description': f"{field_name} (exact match)"
            }

        # Step 2: Try keyword pattern matching
        group = 'general'
        dtype = 'string'
        en_term = None

        for pattern, priority, (grp, dt, term) in self.keyword_patterns:
            if re.search(pattern, field_name):
                group = grp
                dtype = dt
                en_term = term
                break  # Stop at first match (highest priority)

        # Step 3: Refine type based on sample data
        if sample_values and dtype != 'boolean':  # Boolean type is already very specific
            inferred_type = self._infer_type_from_samples(sample_values)
            # Only override if datetime or boolean detected
            if inferred_type in ['datetime', 'boolean']:
                dtype = inferred_type
            # For number type, be more careful
            elif inferred_type == 'number' and dtype == 'string':
                # Check if field name suggests it should be a number
                number_keywords = ['金额', '保费', '费用', '赔款', '价格', '数量', '次数', '频度',
                                   '评分', '率', '系数', '折扣', '吨位', '座位', '排量', '功率',
                                   '车龄', '笔数', '比例']
                if any(kw in field_name for kw in number_keywords):
                    dtype = 'number'

        # Step 4: Generate English field name
        if en_term and not en_term.endswith('_'):
            # Use provided term
            en_name = en_term
        else:
            # Translate keywords
            tokens = self._translate_keywords(field_name)
            if tokens:
                en_name = '_'.join(tokens)
            else:
                # Fallback: use a descriptive name
                en_name = f"field_{abs(hash(field_name)) % 10000}"

        # Step 5: Apply standard conventions
        # Ensure snake_case
        en_name = re.sub(r'[^a-z0-9_]', '_', en_name.lower())
        en_name = re.sub(r'_+', '_', en_name)  # Remove consecutive underscores
        en_name = en_name.strip('_')  # Remove leading/trailing underscores

        # Ensure reasonable length
        if len(en_name) > 50:
            # Truncate but keep meaningful parts
            parts = en_name.split('_')
            if len(parts) > 3:
                en_name = '_'.join(parts[:3])
            else:
                en_name = en_name[:50]

        return {
            'en_name': en_name,
            'group': group,
            'dtype': dtype,
            'description': f"{field_name} (auto-generated)"
        }

    def batch_analyze_fields(
        self,
        unknown_fields: List[str],
        df: Optional[pd.DataFrame] = None,
        sample_size: int = 100
    ) -> Dict[str, Dict[str, str]]:
        """
        Batch analyze unknown fields

        Args:
            unknown_fields: List of unknown field names
            df: DataFrame containing the fields (optional)
            sample_size: Number of samples to use for type inference

        Returns:
            {field_name: mapping_dict}
        """
        mappings = {}

        for field in unknown_fields:
            # Get sample values
            sample_values = None
            if df is not None and field in df.columns:
                sample_values = df[field].dropna().head(sample_size).tolist()

            # Analyze field
            mapping = self.analyze_field(field, sample_values)
            mappings[field] = mapping

        return mappings

    def format_as_json_config(self, mappings: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """
        Convert mappings to JSON configuration format

        Returns:
            Configuration dict compatible with field_mappings/*.json format
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
            'description': 'AI-generated field mappings with industry-standard naming',
            'mappings': config_mappings
        }


# Test and demonstration
if __name__ == '__main__':
    mapper = AIFieldMapper()

    # Test fields covering different categories
    test_fields = [
        # Finance
        '保单号', '签单保费', '商业险保费', '总赔款', '案均赔款',
        '手续费', '费用率', 'NCD系数', '折扣',
        # Organization
        '三级机构', '四级机构', '业务员', '销售渠道',
        # Vehicle
        '车牌号码', '车架号', '车型', '新旧车', '座位数',
        # Product
        '险种', '保额',
        # Customer
        '投保人', '被保险人', '证件号码',
        # Time
        '保险起期', '保险止期', '确认时间',
        # Boolean
        '是否续保', '是否新能源',
        # Status
        '保单状态',
        # Test unknown fields
        '客户满意度评分', '代理商等级', '风险预警标识',
    ]

    print("=" * 80)
    print("AI Field Mapping Generator - Test Results")
    print("Based on Insurance Industry Standards")
    print("=" * 80)

    results = mapper.batch_analyze_fields(test_fields)

    # Group by category
    by_group = {}
    for field, mapping in results.items():
        group = mapping['group']
        if group not in by_group:
            by_group[group] = []
        by_group[group].append((field, mapping))

    # Print results by group
    for group in sorted(by_group.keys()):
        print(f"\n{'='*80}")
        print(f"Group: {group.upper()}")
        print(f"{'='*80}")
        for field, mapping in by_group[group]:
            print(f"\n{field}:")
            print(f"  → {mapping['en_name']}")
            print(f"  Type: {mapping['dtype']}")
            print(f"  Description: {mapping['description']}")

    # Print statistics
    print(f"\n{'='*80}")
    print("Statistics")
    print(f"{'='*80}")
    print(f"Total fields analyzed: {len(results)}")

    type_counts = {}
    for mapping in results.values():
        dtype = mapping['dtype']
        type_counts[dtype] = type_counts.get(dtype, 0) + 1

    print("\nType distribution:")
    for dtype, count in sorted(type_counts.items()):
        print(f"  {dtype}: {count}")

    group_counts = {}
    for mapping in results.values():
        group = mapping['group']
        group_counts[group] = group_counts.get(group, 0) + 1

    print("\nGroup distribution:")
    for group, count in sorted(group_counts.items()):
        print(f"  {group}: {count}")
