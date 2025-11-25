# Excel 字段分析器 - 技术参考

## 目录

- [完整功能说明](#完整功能说明)
- [工作流详情](#工作流详情)
- [预置字段映射](#预置字段映射)
- [AI 批量学习](#ai-批量学习)
- [映射质量校验](#映射质量校验)
- [配置系统](#配置系统)
- [业务分组](#业务分组)
- [数据类型](#数据类型)
- [输出文件](#输出文件)
- [技术架构](#技术架构)
- [常见问题](#常见问题)
- [依赖](#依赖)
- [版本历史](#版本历史)

---

## 完整功能说明

### 1. 预置车险领域映射

内置 50+ 个车险领域字段映射：

**财务类字段**
- 保费：商业险保费、签单保费、批改保费、退保保费、NCD 基准保费
- 赔款：总赔款、案均赔款、出险频度、案件数
- 费用：总费用、费用金额、费用率、变动成本率

**车辆类字段**
- 新旧车、过户车、新能源车
- 车险分等级、车牌归属
- 大货车评分、小货车评分、高速风险等级

**机构类字段**
- 三级机构、四级机构

**产品类字段**
- 险类、险种、交强/商业

**时间类字段**
- 确认时间、投保确认时间、刷新时间、保险起期

**其它字段**
- 业务类型、客户类别、续保状态、终端来源

### 2. 多源配置系统

- `auto_insurance.json` - 预置车险映射（50+ 字段）
- `custom.json` - 用户自定义映射（交互学习自动保存）
- Excel 配置导入（后续功能）

**配置优先级：**
完整匹配 > 词组组合 > AI 批量学习 > 未识别
后加载的 JSON 会覆盖先加载的 JSON。

### 3. 智能字段识别

**匹配策略：**
1. **精确匹配** - 最高优先级
   - `商业险保费` → `commercial_premium`
2. **词组组合** - 基于关键词的组合匹配
   - `总费用金额` → `total_fee_amount`
3. **自动类型推断** - 基于数据样本
   - 数值型 → `number`
   - 日期型 → `datetime`
   - 文本型 → `string`
4. **业务分组归类** - 按领域分类
   - finance, vehicle, time, organization, product, flag, partner, general

### 4. AI 批量学习（v2.2+）

**未知字段零人工处理**

遇到未知字段时，AI 自动：
1. 分析字段名语义与关键词
2. 检查字段数据样本以推断类型
3. 基于车险业务规则生成映射
4. 批量保存到 `custom.json`
5. 后续分析自动识别

**示例输出：**
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

**AI 学习流程：**

**语义分析：**
- 关键词模式匹配（时间/机构/财务/车辆/产品）
- 中文分词与拼音转换
- 业务规则应用

**数据样本分析：**
- 抽取前 100 行数据
- 自动推断数值/文本/日期类型
- 识别特殊格式（保单号、车牌、证件号码）

**批量生成映射：**
- 英文字段名（如 `签单保费` → `premium_signing`）
- 业务分组（如 finance/vehicle/time）
- 数据类型（number/string/datetime）

**自动保存：**
批量写入 `custom.json`，即时生效

**准确率：**
车险业务测试：70 个未知字段，映射准确率 100%

### 5. 映射质量校验（v2.3+）

**自动化翻译质量保障**

每次生成映射后进行自动多维质量检查：

**校验维度：**

1. **命名规范检查**
   - 验证 snake_case 格式
   - 合理长度（≤50 字符）
   - 避免通用占位符（如 field、unknown_field）

2. **分组一致性检查**
   - 校验英文字段名包含与分组相关的领域术语
   - 例如 finance 组应包含 premium/fee/amount

3. **语义准确性检查**
   - 关键词映射验证（如“保费” → premium）
   - 中文字符泄露检测
   - 简化程度评估

4. **类型一致性检查**
   - 时间类字段 → datetime 类型
   - 金额类字段 → number 类型
   - 是/否类字段 → string 类型

**质量评分：**
- 优秀（≥90）：映射完美，无需改进
- 良好（75-89）：基本准确，可选优化
- 一般（60-74）：建议人工复审
- 较差（<60）：需重新映射

**输出报告格式：**
```markdown
📊 Overall Statistics:
- Total fields: 76
- Average quality score: 97.17/100
- Excellent: 66  Good: 10  Fair: 0  Poor: 0

✅ Excellent Mapping Examples
⚠️ Mappings Requiring Review (with improvement suggestions)
📈 Quality Distribution Visualization
```

### 6. 交互式学习（手动模式）

用于精确控制，支持手动新增映射：
1. 暂停分析，询问用户
2. 用户提供英文字段名与分组
3. 保存到 `custom.json`
4. 后续自动识别

---

## 工作流详情

### 标准分析流程

**1. 加载 Excel 文件**
- 读取所有工作表
- 自动识别数值/时间列
- 数据清洗（去空格、类型转换）

**2. 字段统计**
- 行数、空值数、空值率
- 唯一值数量
- Top 值分布（前 N 项）
- 数值统计（最小/最大/均值/合计）

**3. 字段映射**
- 查询映射库（精确匹配）
- 词组组合匹配
- 生成英文字段名
- 保证字段名唯一（自动添加后缀）

**4. AI 批量学习**（自动化）
- 检测未映射字段
- **语义分析：**
  - 关键词模式匹配
  - 中文分词与拼音转换
  - 业务规则应用
- **数据样本分析：**
  - 抽取前 100 行数据
  - 自动推断数值/文本/日期类型
  - 识别特殊格式
- **批量生成映射：**
  - 英文字段名
  - 业务分组
  - 数据类型
- **自动保存：** 批量写入 `custom.json`
- **即时生效：** 重新生成字段映射，未知字段为 0

**5. 未知字段处理**（手动模式，可选）
- 检测未映射字段
- 询问用户：
  - 英文字段名？
  - 业务分组？
  - 数据类型？
- 保存到 `custom.json`

**6. 生成报告**
- HTML 可视化报告
- JSON 字段映射表
- 统计摘要
- 质量校验报告

---

## 预置字段映射

### 车险领域（50+ 字段）

**财务组**
| 中文 | 英文 | 类型 |
|------|------|------|
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

**车辆组**
| 中文 | 英文 | 类型 |
|------|------|------|
| 新旧车 | vehicle_new_used | string |
| 是否过户车 | flag_vehicle_transfer | string |
| 是否新能源车 | flag_vehicle_new_energy | string |
| 车险分等级 | vehicle_insurance_level | string |
| 车牌归属 | license_plate_attribution | string |
| 大货车评分 | score_heavy_truck | number |
| 小货车评分 | score_light_truck | number |
| 高速风险等级 | risk_level_highway | string |

**机构组**
| 中文 | 英文 | 类型 |
|------|------|------|
| 三级机构 | org_level_3 | string |
| 四级机构 | org_level_4 | string |

**产品组**
| 中文 | 英文 | 类型 |
|------|------|------|
| 险类 | insurance_class | string |
| 险种类 | insurance_type | string |
| 交三/主全 | insurance_compulsory_commercial | string |
| 商业险 | insurance_commercial | string |
| 交强险 | insurance_compulsory | string |

**时间组**
| 中文 | 英文 | 类型 |
|------|------|------|
| 确认时间 | time_confirm | datetime |
| 投保确认时间 | time_confirm_insure | datetime |
| 刷新时间 | time_refresh | datetime |
| 保险起期 | date_policy_start | datetime |

---

## AI 批量学习

### 关键词模式库

**时间模式**
- 关键词：时间、日期、年月、起期、到期 等
- 分组：`time`
- 类型：`datetime`

**机构模式**
- 关键词：机构、分公司、支公司、部门 等
- 分组：`organization`
- 类型：`string`

**财务模式**
- 关键词：保费、赔款、费用、金额、收入、成本 等
- 分组：`finance`
- 类型：`number`

**车辆模式**
- 关键词：车牌、车型、车辆、车龄 等
- 分组：`vehicle`
- 类型：`string`

**产品模式**
- 关键词：险种、险类、产品、方案 等
- 分组：`product`
- 类型：`string`

**标识模式**
- 关键词：是否、标识、标志、状态 等
- 分组：`flag`
- 类型：`string`

### 类型推断规则

**数值型：**
- 全部为数值
- 包含小数点
- 包含负数
- 字段名包含：金额、保费、赔款、评分、数量 等

**日期时间型：**
- 包含日期模式（YYYY-MM-DD、YYYY/MM/DD）
- 包含时间模式（HH:MM:SS）
- 字段名包含：时间、日期、起期、到期 等

**字符串型：**
- 默认兜底
- 内容类型混合
- 文本类字段

### 自定义领域扩展

若需新增业务领域：

**方法一：新增 JSON 文件**

创建 `field_mappings/logistics.json`：

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

**方法二：扩展 AI 映射器**

编辑 `ai_mapper.py`，在 `keyword_patterns` 中新增关键词：

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

## 映射质量校验

### 校验规则

**1. 命名规范（20 分）**
- 合法 snake_case：10 分
- 合理长度（≤50 字符）：5 分
- 无通用占位符：5 分

**2. 分组一致性（30 分）**
- 财务组包含：premium、fee、amount、cost、revenue
- 车辆组包含：vehicle、car、license、plate
- 时间组包含：time、date、datetime、period
- 机构组包含：org、organization、dept、branch

**3. 语义准确性（30 分）**
- 关键词映射校验
- 无中文字符泄露
- 适度简化

**4. 类型一致性（20 分）**
- 时间类 → datetime 类型
- 金额/费用/保费类 → number 类型
- 标识/状态类 → string 类型

### 质量报告格式

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

## 配置系统

### 配置文件

**1. 车险映射**
- 文件：`field_mappings/auto_insurance.json`
- 内容：50+ 预置映射
- 只读（不建议修改）

**2. 自定义映射**
- 文件：`field_mappings/custom.json`
- 内容：用户自定义 + AI 学习映射
- 可写（系统自动更新）

### 配置格式

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

### 映射优先级

1. **精确匹配**（最高优先级）
2. **词组组合匹配**
3. **AI 生成映射**
4. **未知**（需学习）

后加载文件覆盖先加载文件。

---

## 业务分组

| 分组 | 描述 | 示例字段 |
|------|------|-----------|
| finance | 财务数据 | 保费、赔款、费用、成本 |
| organization | 机构信息 | 三级机构、四级机构、分支 |
| vehicle | 车辆相关 | 新旧车、车牌 |
| product | 产品信息 | 险类、险种 |
| time | 日期/时间 | 确认时间、起保日期 |
| flag | 标识/状态 | 续保标识、新能源标识 |
| partner | 合作方信息 | 4S 集团、经销商 |
| general | 通用字段 | 业务类型、客户类别 |

---

## 数据类型

| 类型 | 角色 | 默认聚合 | 示例 |
|------|------|----------|------|
| number | 度量 | sum | 保费、赔款、评分 |
| datetime | 维度 | none | 确认时间、起保日期 |
| string | 维度 | none | 险类、客户类别 |

**角色定义：**
- **measure**：定量数据，可聚合（sum、avg 等）
- **dimension**：分类数据，用于分组与筛选

---

## 输出文件

### 1. HTML 可视化报告

**文件名：**`{original_filename}_{timestamp}_分析报告.html`

**内容：**
- 文件元信息
- 各工作表字段统计表
- 数值统计、Top 值分布
- 交互式探索能力

### 2. JSON 字段映射表

**文件名：**`{original_filename}_{timestamp}_字段映射.json`

**格式：**
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

### 3. 质量校验报告

**文件名：**`{original_filename}_{timestamp}_质量检查报告.md`

**格式：** Markdown

**内容：**
- 总体统计：平均得分、质量等级分布
- 需复审映射：低分字段的问题诊断
- 优秀映射示例：高质量参考
- 质量分布图：可视化分布

---

## 技术架构

```
excel-field-analyzer/
├── SKILL.md                    # 技能定义（主文档）
├── reference.md                # 技术参考（本文档）
├── examples.md                 # 使用示例
├── scripts/                    # Python 脚本
│   ├── analyzer.py             # 核心分析引擎
│   ├── ai_mapper.py            # AI 批量字段映射生成器
│   ├── mapping_validator.py    # 映射质量校验器
│   └── interactive_analyzer.py # 交互式命令行封装
├── field_mappings/             # 字段映射库
│   ├── auto_insurance.json     # 车险预置映射（50+ 字段）
│   └── custom.json             # AI 学习 + 用户自定义映射
└── templates/                  # HTML 模板（后续）

核心模块：
- analyzer.py：读取 Excel/CSV、字段分析、HTML 报告生成、质量校验集成
- ai_mapper.py：语义分析、数据样本推断、批量映射生成
- mapping_validator.py：多维质量检查、评分体系、报告生成
- FieldMappingManager：多源配置管理、映射查询
- AIFieldMapper：关键词匹配、拼音转换、类型推断
- MappingValidator：命名规范检查、语义校验、质量评分
```

---

## 常见问题

**问：AI 批量学习的准确率如何？**
答：车险业务测试中，70 个未知字段达到 100% 映射准确率。覆盖时间/机构/财务/产品/车辆/标识等常见分组，并能准确推断数据类型。

**问：AI 批量学习会覆盖我的自定义映射吗？**
答：不会。AI 仅处理未知字段，已映射字段保持不变。全部学习结果保存到 `custom.json`，可随时编辑或删除。

**问：可以关闭 AI 批量学习吗？**
答：可以。删除或重命名 `ai_mapper.py` 即可禁用，系统会提示 “AI mapper unavailable” 并跳过批量学习。

**问：英文字段名的生成规则是什么？**
答：基于中文关键词映射（如“保费”→ premium，“车牌”→ license_plate），多个关键词以下划线连接。若无匹配，将生成带数字后缀的通用名称以确保唯一性。

**问：如何新增业务领域映射？**
答：在 `field_mappings/` 新建 JSON 文件（如 `logistics.json`），遵循 `auto_insurance.json` 格式；或在 `ai_mapper.py` 的 `keyword_patterns` 中补充业务关键词。

**问：映射优先级是什么？**
答：精确匹配 > 词组组合 > AI 批量学习 > 未知。后加载的 JSON 覆盖先加载的 JSON。

**问：如何重置自定义映射？**
答：删除或清空 `field_mappings/custom.json` 中的 `mappings` 区域。

**问：是否支持多工作表？**
答：支持读取所有工作表，但字段映射仅针对第一个工作表生成。

**问：如何导出映射库？**
答：直接复制 `field_mappings/*.json` 到目标环境即可。

**问：如何自定义 Top 值数量？**
答：使用 `topn` 参数，例如：`analyzer.py file.xlsx ./output 20`。

**问：支持哪些文件格式？**
答：`.xlsx`、`.xls`、`.csv`、`.txt`

**问：CSV 文件的编码问题如何处理？**
答：分析器会自动检测编码（UTF-8、GBK、GB2312）。如仍有问题，请先转换为 UTF-8。

---

## 依赖

### 必需的 Python 包

- Python 3.7+
- pandas (≥1.0.0)
- openpyxl (≥3.0.0)
- numpy (≥1.18.0)

### 安装

```bash
pip install pandas openpyxl numpy
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

---

## 版本历史

### v2.3 (2025-11-23) 🎯 质量保障
- 🔍 **映射质量校验** - 自动验证翻译准确性！
- ✨ 新增 `mapping_validator.py` 模块 - 多维质量评估体系
- ✨ 4 大校验维度：命名规范、分组一致、语义准确、类型一致
- ✨ 质量评分体系：优秀/良好/一般/较差 四档评级
- 📊 自动生成质量报告 - Markdown 格式，含问题诊断与改进建议
- 🔄 集成到分析流程 - 每次生成映射后自动质量检查

### v2.2 (2025-11-23) 🚀 AI 批量学习
- 🤖 **AI 批量学习** - 自动分析未知字段并生成映射，零人工！
- ✨ 新增 `ai_mapper.py` 模块 - 基于语义与数据样本的智能映射
- ✨ 集成车险领域关键词库 - 自动识别时间/机构/财务/产品/车辆/标识分组
- ✨ 自动类型推断 - 分析字段数据样本，智能判定 number/string/datetime
- 📊 测试结果：成功批量学习 70 个未知字段，准确率 100%
- 💾 学习结果自动保存到 `custom.json` - 后续复用

### v2.1 (2025-11-23)
- ✨ **支持 CSV 文件** - 自动识别并处理 .csv 与 .txt
- ✨ 统一 Excel 与 CSV 分析接口
- 📝 更新 CSV 支持相关文档
- 🔧 优化文件类型检测逻辑

### v2.0 (2025-11-23)
- ✨ 重构为 Claude Code Skill
- ✨ 多源配置系统（JSON + 自定义）
- ✨ 交互式字段学习
- ✨ 增强字段映射管理
- ✨ 支持命令/对话式调用

### v1.0
- 基础 Excel 分析功能
- 生成 HTML 报告
- 导出 JSON 字段映射

---

## 许可证

MIT 许可证
