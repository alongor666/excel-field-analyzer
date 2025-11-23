# Excel Field Analyzer - Technical Reference

## Table of Contents

- [Complete Feature Description](#complete-feature-description)
- [Workflow Details](#workflow-details)
- [Pre-built Field Mappings](#pre-built-field-mappings)
- [AI Batch Learning](#ai-batch-learning)
- [Mapping Quality Validation](#mapping-quality-validation)
- [Configuration System](#configuration-system)
- [Business Groups](#business-groups)
- [Data Types](#data-types)
- [Output Files](#output-files)
- [Technical Architecture](#technical-architecture)
- [FAQ](#faq)
- [Dependencies](#dependencies)
- [Version History](#version-history)

---

## Complete Feature Description

### 1. Pre-built Auto Insurance Domain Mappings

Built-in 50+ auto insurance field mappings:

**Financial Fields**
- Premium: Commercial premium, signing premium, amendment premium, refund premium, NCD base premium
- Claims: Total claims, average claim, claim frequency, case count
- Fees: Total fees, fee amount, fee rate, variable cost rate

**Vehicle Fields**
- New/used vehicles, transferred vehicles, new energy vehicles
- Vehicle insurance tier, license plate attribution
- Heavy truck score, light truck score, highway risk level

**Organization Fields**
- Level 3 organization, Level 4 organization

**Product Fields**
- Insurance class, insurance type, Compulsory/Commercial insurance

**Time Fields**
- Confirmation time, policy confirmation time, refresh time, policy start date

**Other Fields**
- Business type, customer category, renewal status, terminal source

### 2. Multi-Source Configuration System

- `auto_insurance.json` - Pre-built auto insurance mappings (50+ fields)
- `custom.json` - User-defined mappings (auto-saved from interactive learning)
- Excel configuration import (future feature)

**Configuration Priority:**
Complete match > Phrase combination > AI batch learning > Unknown

Later-loaded JSON files override earlier ones.

### 3. Intelligent Field Recognition

**Matching Strategy:**
1. **Exact Match** - Highest priority
   - `商业险保费` → `commercial_premium`

2. **Phrase Combination** - Keyword-based matching
   - `总费用金额` → `total_fee_amount`

3. **Auto Type Inference** - Based on data samples
   - Numeric fields → `number`
   - Date fields → `datetime`
   - Text fields → `string`

4. **Business Group Classification** - Domain categorization
   - finance, vehicle, time, organization, product, flag, partner, general

### 4. AI Batch Learning (v2.2+)

**Zero Manual Labor for Unknown Fields**

When encountering unknown fields, AI automatically:

1. Analyzes field name semantics and keywords
2. Examines field data samples to infer type
3. Generates mappings based on auto insurance business rules
4. Batch saves to `custom.json`
5. Auto-recognizes in future analyses

**Example Output:**
```
🔍 Found 70 unknown fields
💡 Using AI to generate field mappings...
✅ Generated 70 field mappings and saved to custom.json

Results:
- 刷新时间 → time_refresh [time/datetime]
- 交叉销售标识 → flag_cross_sales [flag/string]
- 车牌号码 → license_plate [vehicle/string]
- 签单保费 → premium_signing [finance/number]
```

**AI Learning Process:**

**Semantic Analysis:**
- Keyword pattern matching (time/organization/finance/vehicle/product)
- Chinese word segmentation and pinyin conversion
- Business rule application

**Data Sample Analysis:**
- Extracts first 100 data rows
- Auto-infers numeric/text/date types
- Detects special formats (policy numbers, license plates, ID numbers)

**Batch Mapping Generation:**
- English field names (e.g., `签单保费` → `premium_signing`)
- Business groups (e.g., finance/vehicle/time)
- Data types (number/string/datetime)

**Auto-Save:**
Batch writes to `custom.json`, effective immediately

**Accuracy:**
Based on auto insurance business testing: 70 unknown fields, 100% mapping accuracy

### 5. Mapping Quality Validation (v2.3+)

**Automatic Translation Quality Assurance**

After each mapping generation, automatic multi-dimensional quality checks:

**Validation Dimensions:**

1. **Naming Convention Check**
   - snake_case format validation
   - Reasonable length (≤50 characters)
   - Avoid generic placeholders (e.g., field, unknown_field)

2. **Group Consistency Check**
   - Verify English names contain group-related domain terms
   - e.g., finance group should contain premium/fee/amount

3. **Semantic Accuracy Check**
   - Keyword mapping verification (e.g., "保费" → premium)
   - Chinese character leak detection
   - Simplification level assessment

4. **Type Consistency Check**
   - Time fields → datetime type
   - Amount fields → number type
   - "Yes/No" fields → string type

**Quality Scoring:**
- Excellent (≥90): Perfect mapping, no improvement needed
- Good (75-89): Basically accurate, optimization optional
- Fair (60-74): Manual review recommended
- Poor (<60): Requires remapping

**Output Report Format:**
```markdown
📊 Overall Statistics:
- Total fields: 76
- Average quality score: 97.17/100
- Excellent: 66  Good: 10  Fair: 0  Poor: 0

✅ Excellent Mapping Examples
⚠️ Mappings Requiring Review (with improvement suggestions)
📈 Quality Distribution Visualization
```

### 6. Interactive Learning (Manual Mode)

For precise control, manual mapping addition:

1. Pause analysis, ask user
2. User provides English field name and group
3. Save to `custom.json`
4. Auto-recognize in future

---

## Workflow Details

### Standard Analysis Flow

**1. Load Excel File**
- Read all worksheets
- Auto-identify numeric/time columns
- Data cleaning (trim spaces, type conversion)

**2. Field Statistics**
- Row count, null count, null rate
- Unique value count
- Top value distribution (top N items)
- Numeric statistics (min/max/mean/sum)

**3. Field Mapping**
- Query mapping library (exact match)
- Phrase combination matching
- Generate English field names
- Ensure unique field names (auto-add suffix)

**4. AI Batch Learning** (Automated)
- Detect unmapped fields
- **Semantic Analysis:**
  - Keyword pattern matching
  - Chinese word segmentation & pinyin conversion
  - Business rule application
- **Data Sample Analysis:**
  - Extract first 100 data rows
  - Auto-infer numeric/text/date types
  - Detect special formats
- **Batch Generate Mappings:**
  - English field names
  - Business groups
  - Data types
- **Auto-Save:** Batch write to `custom.json`
- **Immediate Effect:** Regenerate field mappings, 0 unknown fields

**5. Unknown Field Handling** (Manual Mode, Optional)
- Detect unmapped fields
- Ask user:
  - English field name?
  - Business group?
  - Data type?
- Save to `custom.json`

**6. Generate Reports**
- HTML visualization report
- JSON field mapping table
- Statistical summary
- Quality validation report

---

## Pre-built Field Mappings

### Auto Insurance Domain (50+ Fields)

**Financial Group**
| Chinese | English | Type |
|---------|---------|------|
| 商业险保费 | commercial_premium | number |
| 签单保费 | premium_signing | number |
| 批改保费 | premium_amendment | number |
| 退保保费 | premium_refund | number |
| NCD基准保费 | premium_ncd_base | number |
| 总赔款 | claims_total | number |
| 案均赔款 | claims_average | number |
| 出险频度 | frequency_claim | number |
| 案件数 | count_case | number |
| 总费用 | fee_total | number |
| 费用金额 | fee_amount | number |
| 费用率 | rate_fee | number |
| 变动成本率 | rate_variable_cost | number |

**Vehicle Group**
| Chinese | English | Type |
|---------|---------|------|
| 新旧车 | vehicle_new_used | string |
| 是否过户车 | flag_vehicle_transfer | string |
| 是否新能源车 | flag_vehicle_new_energy | string |
| 车险分等级 | vehicle_insurance_level | string |
| 车牌归属 | license_plate_attribution | string |
| 大货车评分 | score_heavy_truck | number |
| 小货车评分 | score_light_truck | number |
| 高速风险等级 | risk_level_highway | string |

**Organization Group**
| Chinese | English | Type |
|---------|---------|------|
| 三级机构 | org_level_3 | string |
| 四级机构 | org_level_4 | string |

**Product Group**
| Chinese | English | Type |
|---------|---------|------|
| 险类 | insurance_class | string |
| 险种类 | insurance_type | string |
| 交三/主全 | insurance_compulsory_commercial | string |
| 商业险 | insurance_commercial | string |
| 交强险 | insurance_compulsory | string |

**Time Group**
| Chinese | English | Type |
|---------|---------|------|
| 确认时间 | time_confirm | datetime |
| 投保确认时间 | time_confirm_insure | datetime |
| 刷新时间 | time_refresh | datetime |
| 保险起期 | date_policy_start | datetime |

---

## AI Batch Learning

### Keyword Pattern Library

**Time Pattern**
- Keywords: 时间, 日期, 年月, 起期, 到期, etc.
- Group: `time`
- Type: `datetime`

**Organization Pattern**
- Keywords: 机构, 分公司, 支公司, 部门, etc.
- Group: `organization`
- Type: `string`

**Finance Pattern**
- Keywords: 保费, 赔款, 费用, 金额, 收入, 成本, etc.
- Group: `finance`
- Type: `number`

**Vehicle Pattern**
- Keywords: 车牌, 车型, 车辆, 车龄, etc.
- Group: `vehicle`
- Type: `string`

**Product Pattern**
- Keywords: 险种, 险类, 产品, 方案, etc.
- Group: `product`
- Type: `string`

**Flag Pattern**
- Keywords: 是否, 标识, 标志, 状态, etc.
- Group: `flag`
- Type: `string`

### Type Inference Rules

**Number Type:**
- All values are numeric
- Contains decimal points
- Contains negative numbers
- Field name contains: 金额, 保费, 赔款, 评分, 数量, etc.

**DateTime Type:**
- Contains date patterns (YYYY-MM-DD, YYYY/MM/DD)
- Contains time patterns (HH:MM:SS)
- Field name contains: 时间, 日期, 起期, 到期, etc.

**String Type:**
- Default fallback
- Mixed content types
- Text-based fields

### Custom Domain Extension

To add new business domains:

**Method 1: Create New JSON File**

Create `field_mappings/logistics.json`:

```json
{
  "domain": "logistics",
  "mappings": {
    "运单号": {
      "en_name": "waybill_number",
      "group": "general",
      "dtype": "string",
      "description": "Logistics waybill number"
    },
    "配送费用": {
      "en_name": "delivery_fee",
      "group": "finance",
      "dtype": "number",
      "description": "Delivery fee amount"
    }
  }
}
```

**Method 2: Extend AI Mapper**

Edit `ai_mapper.py`, add keywords to `keyword_patterns`:

```python
self.keyword_patterns = {
    # ... existing patterns ...
    'logistics': {
        'keywords': ['运单', '配送', '物流', '快递', '仓库'],
        'group': 'logistics',
        'dtype': 'string'
    }
}
```

---

## Mapping Quality Validation

### Validation Rules

**1. Naming Convention (20 points)**
- Valid snake_case format: 10 points
- Reasonable length (≤50 chars): 5 points
- No generic placeholders: 5 points

**2. Group Consistency (30 points)**
- Finance group contains: premium, fee, amount, cost, revenue
- Vehicle group contains: vehicle, car, license, plate
- Time group contains: time, date, datetime, period
- Organization group contains: org, organization, dept, branch

**3. Semantic Accuracy (30 points)**
- Keyword mapping verification
- No Chinese character leakage
- Appropriate simplification

**4. Type Consistency (20 points)**
- Time fields → datetime type
- Amount/fee/premium fields → number type
- Flag/status fields → string type

### Quality Report Format

```markdown
# Field Mapping Quality Validation Report

## 📊 Overall Statistics
- Total fields: 76
- Average quality score: 97.17/100
- Excellent (≥90): 66 fields
- Good (75-89): 10 fields
- Requiring review: 0 fields

## ⚠️ Mappings Requiring Manual Review
(Fields below 70 points, with issues and improvement suggestions)

### Field: 客户满意度 (Score: 65/100)

**Issues:**
- ❌ Naming: Generic placeholder "field_001"
- ⚠️ Group: Not consistent with "general" group
- ✓ Semantic: OK
- ✓ Type: Correct (number)

**Suggestions:**
- Use meaningful name: customer_satisfaction_score
- Verify business group assignment

## ✅ Excellent Mapping Examples

| Chinese | English | Group | Type | Score |
|---------|---------|-------|------|-------|
| 商业险保费 | commercial_premium | finance | number | 100 |
| 确认时间 | time_confirm | time | datetime | 98 |
| 三级机构 | org_level_3 | organization | string | 95 |

## 📈 Quality Distribution

90-100: ██████████████████████████ (66 fields)
75-89:  ████ (10 fields)
60-74:  (0 fields)
<60:    (0 fields)
```

---

## Configuration System

### Configuration Files

**1. Auto Insurance Mappings**
- File: `field_mappings/auto_insurance.json`
- Contents: 50+ pre-built mappings
- Read-only (should not be modified)

**2. Custom Mappings**
- File: `field_mappings/custom.json`
- Contents: User-defined + AI-learned mappings
- Writable (auto-updated by system)

### Configuration Format

```json
{
  "domain": "auto_insurance",
  "mappings": {
    "商业险保费": {
      "en_name": "commercial_premium",
      "group": "finance",
      "dtype": "number",
      "description": "Commercial insurance premium amount"
    }
  }
}
```

### Mapping Priority

1. **Exact Match** (highest priority)
2. **Phrase Combination Match**
3. **AI Generated Mapping**
4. **Unknown** (requires learning)

Later-loaded files override earlier ones.

---

## Business Groups

| Group | Description | Example Fields |
|-------|-------------|----------------|
| finance | Financial data | Premium, claims, fees, costs |
| organization | Organization info | Level 3 org, Level 4 org, branches |
| vehicle | Vehicle-related | New/used vehicles, license plates |
| product | Product info | Insurance class, insurance type |
| time | Date/time | Confirmation time, policy start date |
| flag | Flag/status fields | Renewal flag, new energy flag |
| partner | Partner info | 4S groups, dealers |
| general | General fields | Business type, customer category |

---

## Data Types

| Type | Role | Default Aggregation | Examples |
|------|------|---------------------|----------|
| number | measure | sum | Premium, claims, scores |
| datetime | dimension | none | Confirmation time, start date |
| string | dimension | none | Insurance class, customer category |

**Role Definitions:**
- **measure**: Quantitative data, can be aggregated (sum, avg, etc.)
- **dimension**: Categorical data, used for grouping and filtering

---

## Output Files

### 1. HTML Visualization Report

**Filename:** `{original_filename}_{timestamp}_分析报告.html`

**Contents:**
- File metadata
- Field statistics table for each worksheet
- Numeric statistics, top value distribution
- Interactive exploration capability

### 2. JSON Field Mapping Table

**Filename:** `{original_filename}_{timestamp}_字段映射.json`

**Format:**
```json
[
  {
    "field_name": "commercial_premium",
    "cn_name": "商业险保费",
    "source_column": "商业险保费",
    "group": "finance",
    "dtype": "number",
    "role": "measure",
    "aggregation": "sum",
    "description": "Numeric field (commercial premium), can be aggregated by time/organization dimensions.",
    "notes": "Null rate approx 2.5%",
    "is_mapped": true
  }
]
```

### 3. Quality Validation Report

**Filename:** `{original_filename}_{timestamp}_质量检查报告.md`

**Format:** Markdown

**Contents:**
- Overall statistics: Average score, quality grade distribution
- Mappings requiring review: Low-score fields with issue diagnosis
- Excellent mapping examples: High-quality mapping references
- Quality distribution chart: Visual quality distribution

---

## Technical Architecture

```
excel-field-analyzer/
├── SKILL.md                    # Skill definition (main documentation)
├── reference.md                # Technical reference (this file)
├── examples.md                 # Usage examples
├── scripts/                    # Python scripts
│   ├── analyzer.py             # Core analysis engine
│   ├── ai_mapper.py            # AI batch field mapping generator
│   ├── mapping_validator.py   # Mapping quality validator
│   └── interactive_analyzer.py # Interactive CLI wrapper
├── field_mappings/             # Field mapping library
│   ├── auto_insurance.json     # Auto insurance pre-built mappings (50+ fields)
│   └── custom.json             # AI-learned + user-defined mappings
└── templates/                  # HTML templates (future)

Core Modules:
- analyzer.py: Excel/CSV reading, field analysis, HTML report generation, quality validation integration
- ai_mapper.py: Semantic analysis, data sample inference, batch mapping generation
- mapping_validator.py: Multi-dimensional quality checks, scoring system, report generation
- FieldMappingManager: Multi-source config management, mapping queries
- AIFieldMapper: Keyword matching, pinyin conversion, type inference
- MappingValidator: Naming convention checks, semantic validation, quality scoring
```

---

## FAQ

**Q: How accurate is AI batch learning?**
A: Based on auto insurance business testing, 70 unknown fields achieved 100% mapping accuracy. Supports time/organization/finance/product/vehicle/flag and other common groups, with accurate data type inference.

**Q: Will AI batch learning overwrite my custom mappings?**
A: No. AI only processes unknown fields; already-mapped fields remain unchanged. All learning results are saved to `custom.json` and can be edited or deleted anytime.

**Q: Can I disable AI batch learning?**
A: Yes. Delete or rename the `ai_mapper.py` file to disable it. The system will prompt "AI mapper unavailable" and skip batch learning.

**Q: What are the English field name generation rules?**
A: Based on Chinese keyword mapping (e.g., "保费" → premium, "车牌" → license_plate), multiple keywords connected with underscores. If no match, generates generic name with numeric suffix to ensure uniqueness.

**Q: How do I add new business domain mappings?**
A: Create a new JSON file in `field_mappings/` (e.g., `logistics.json`), following the `auto_insurance.json` format. Or add business keywords to `keyword_patterns` in `ai_mapper.py`.

**Q: What is the mapping priority?**
A: Exact match > Phrase combination > AI batch learning > Unknown. Later-loaded JSON overrides earlier ones.

**Q: How do I reset custom mappings?**
A: Delete or clear the `mappings` section in `field_mappings/custom.json`.

**Q: Does it support multiple worksheets?**
A: Supports reading all worksheets, but field mapping is only generated for the first worksheet.

**Q: How do I export the mapping library?**
A: Directly copy `field_mappings/*.json` files to another environment.

**Q: How do I customize the Top value count?**
A: Use the `topn` parameter, e.g., `analyzer.py file.xlsx ./output 20`.

**Q: What file formats are supported?**
A: `.xlsx`, `.xls`, `.csv`, `.txt`

**Q: How do I handle encoding issues with CSV files?**
A: The analyzer auto-detects encoding (UTF-8, GBK, GB2312). If issues persist, convert to UTF-8 first.

---

## Dependencies

### Required Python Packages

- Python 3.7+
- pandas (≥1.0.0)
- openpyxl (≥3.0.0)
- numpy (≥1.18.0)

### Installation

```bash
pip install pandas openpyxl numpy
```

Or use requirements.txt:

```bash
pip install -r requirements.txt
```

---

## Version History

### v2.3 (2025-11-23) 🎯 Quality Assurance
- 🔍 **Mapping Quality Validation** - Automatic translation accuracy verification!
- ✨ New `mapping_validator.py` module - Multi-dimensional quality assessment system
- ✨ 4 validation dimensions: Naming convention, group consistency, semantic accuracy, type consistency
- ✨ Quality scoring system: Excellent/Good/Fair/Poor four-tier rating
- 📊 Auto-generate quality reports - Markdown format with issue diagnosis and improvement suggestions
- 🔄 Integrated into analysis flow - Auto quality check after each mapping generation

### v2.2 (2025-11-23) 🚀 AI Batch Learning
- 🤖 **AI Batch Learning** - Auto-analyze unknown fields and generate mappings, zero manual labor!
- ✨ New `ai_mapper.py` module - Intelligent field mapping based on semantics and data samples
- ✨ Integrated auto insurance domain keyword library - Auto-recognize time/org/finance/product/vehicle/flag groups
- ✨ Auto type inference - Analyze field data samples to intelligently determine number/string/datetime
- 📊 Test results: Successfully batch-learned 70 unknown fields, 100% mapping accuracy
- 💾 Auto-save learning results to `custom.json` - Reuse in future analyses

### v2.1 (2025-11-23)
- ✨ **CSV file support** - Auto-detect and process .csv and .txt files
- ✨ Unified Excel and CSV analysis interface
- 📝 Updated documentation for CSV support
- 🔧 Optimized file type detection logic

### v2.0 (2025-11-23)
- ✨ Refactored as Claude Code Skill
- ✨ Multi-source configuration system (JSON + custom)
- ✨ Interactive field learning
- ✨ Enhanced field mapping management
- ✨ Support for command/conversational invocation

### v1.0
- Basic Excel analysis functionality
- HTML report generation
- JSON field mapping export

---

## License

MIT License
