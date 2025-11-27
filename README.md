# Excel 字段分析器

智能分析 Excel 与 CSV 文件，自动生成中英文字段映射、统计报告与 HTML 可视化。

## 🎯 核心功能

### 1. 字段分析与映射 (`analyzer.py`)
- **字段统计分析**：空值率、唯一值、数据分布
- **AI 字段映射**：内置 50+ 车险领域字段，自动生成英文映射
- **映射质量校验**：4 个维度自动评分（命名、分组、语义、类型）
- **HTML 可视化报告**：交互式数据探索

### 2. 手机号码填充 (`phone_filler.py`) 🆕
- **智能填充空手机号**：自动识别并填充缺失的手机号码字段
- **安全测试号段**：使用中国未启用的号段（100、102-109）
- **零冲突风险**：生成的号码不会与真实号码冲突
- **灵活配置**：支持预览模式、自定义号段、手动指定字段

## 🚀 快速开始

### 安装依赖

```bash
pip install pandas openpyxl numpy anthropic
```

### 字段分析

```bash
# 分析 Excel/CSV 文件
python scripts/analyzer.py data.xlsx output_dir 10

# 支持格式：.xlsx, .xls, .csv, .txt
```

**输出**：
- HTML 分析报告
- JSON 字段映射表
- Markdown 质量检查报告

### 手机号码填充

```bash
# 自动填充空的手机号码（使用 100 号段）
python scripts/phone_filler.py data.xlsx

# 预览模式（不修改文件）
python scripts/phone_filler.py data.xlsx --dry-run

# 使用其他号段
python scripts/phone_filler.py data.xlsx --prefix 102 -o output.xlsx
```

## 📚 详细文档

- **[SKILL.md](SKILL.md)** - Claude Code Skill 使用说明
- **[reference.md](reference.md)** - 完整技术文档、配置细节、API 参考
- **[examples.md](examples.md)** - 代码示例、使用场景、集成指南
- **[AI_MAPPER_IMPROVEMENTS.md](AI_MAPPER_IMPROVEMENTS.md)** - AI 映射器改进说明
- **[docs/phone_filler_usage.md](docs/phone_filler_usage.md)** - 手机号码填充工具使用指南 🆕

## 💡 核心特性

### AI 批量学习

零人工干预，自动为未知字段生成映射：

```
🔍 发现 70 个未知字段
💡 使用AI自动生成字段映射...
✅ 已生成 70 个字段映射并保存到 custom.json

示例：
- 刷新时间 → time_refresh [time/datetime]
- 交叉销售标识 → flag_cross_sales [flag/string]
- 签单保费 → premium_signing [finance/number]
```

### 映射质量校验

自动检查映射质量，4 个维度评分：

- ✅ **命名规范**：snake_case、字符合法性
- ✅ **分组一致性**：finance、organization、vehicle 等
- ✅ **语义准确性**：中英文对应关系
- ✅ **类型准确性**：number、string、datetime、boolean

**质量等级**：
- 优秀（≥95 分）
- 良好（80-94 分）
- 一般（65-79 分）
- 较差（<65 分）

### 预置映射库

**车险领域** (`auto_insurance.json`)：50+ 字段
- 财务：保费、赔款、费用、费率
- 机构：三级机构、四级机构、业务员
- 车辆：车牌号、车架号、车型
- 产品：险种、险类、保额
- 时间：确认时间、起保日期

**自定义** (`custom.json`)：自动学习并保存

### 业务分组

| 分组 | 描述 | 示例 |
|------|------|------|
| finance | 财务数据 | 保费、赔款、费用 |
| organization | 机构信息 | 三级机构、四级机构 |
| vehicle | 车辆相关 | 车牌、车型 |
| product | 产品信息 | 险类、险种 |
| time | 时间字段 | 确认时间、起保日期 |
| flag | 状态标识 | 续保标识、新能源标识 |
| partner | 合作方信息 | 4S 集团、经销商 |
| general | 通用字段 | 业务类型、客户类别 |

## 🛠️ 工具说明

### 1. analyzer.py - 字段分析引擎

**功能**：
- 读取 Excel/CSV 文件
- 统计字段信息（空值率、唯一值、分布）
- 自动生成中英文映射
- 质量检查与评分
- 生成 HTML 报告

**用法**：
```bash
python scripts/analyzer.py <文件路径> [输出目录] [topn]
```

### 2. phone_filler.py - 手机号码填充工具 🆕

**功能**：
- 自动识别手机号码字段
- 为空值生成测试号码
- 使用安全的未启用号段（100-109）
- 支持预览和批量处理

**用法**：
```bash
# 基本用法
python scripts/phone_filler.py data.xlsx

# 预览模式
python scripts/phone_filler.py data.xlsx --dry-run

# 指定输出文件
python scripts/phone_filler.py data.xlsx -o output.xlsx

# 使用其他号段（102、103、104 等）
python scripts/phone_filler.py data.xlsx --prefix 102

# 手动指定字段
python scripts/phone_filler.py data.xlsx --columns 手机号 联系电话
```

**号段说明**：
- `100` - 默认，最明显的测试号段（推荐）
- `102-109` - 其他未启用号段

**示例输出**：
```
📱 手机号码填充工具
   使用号段: 100XXXXXXXX

✅ 列 '手机号': 填充 5 个空值
✅ 列 '联系电话': 填充 3 个空值

📊 处理总结
   总行数: 100
   总填充数: 8
```

### 3. ai_mapper.py - AI 映射生成器

**功能**：
- 基于车险行业标准的字段映射
- 支持精确匹配和关键词匹配
- 自动推断数据类型和业务分组

**Python API**：
```python
from scripts.ai_mapper import AIFieldMapper

mapper = AIFieldMapper()
results = mapper.batch_analyze_fields(['商业险保费', '三级机构'])

# 输出：
# {
#   '商业险保费': {
#     'en_name': 'commercial_premium',
#     'group': 'finance',
#     'dtype': 'number'
#   },
#   '三级机构': {
#     'en_name': 'level_3_organization',
#     'group': 'organization',
#     'dtype': 'string'
#   }
# }
```

### 4. mapping_validator.py - 映射质量验证器

**功能**：
- 验证字段映射质量
- 4 个维度评分
- 生成详细的质量报告

**Python API**：
```python
from scripts.mapping_validator import MappingValidator

validator = MappingValidator()
result = validator.validate_mapping({
    'cn_name': '商业险保费',
    'field_name': 'commercial_premium',
    'group': 'finance',
    'dtype': 'number'
})

print(f"质量评分: {result['overall_score']}/100")
print(f"质量等级: {result['quality_level']}")
```

## 📊 使用场景

### 场景 1: 数据分析准备

```bash
# 分析业务数据，生成字段字典
python scripts/analyzer.py sales_data.xlsx ./analysis
```

### 场景 2: 数据清洗

```bash
# 填充缺失的手机号码
python scripts/phone_filler.py customer_data.csv -o cleaned_data.csv
```

### 场景 3: 数据迁移

```bash
# 生成字段映射表用于数据迁移
python scripts/analyzer.py old_system_data.xlsx ./migration
```

### 场景 4: 测试数据生成

```bash
# 为测试数据生成虚拟手机号
python scripts/phone_filler.py test_users.xlsx --prefix 100
```

## 🔧 配置

### 环境变量

```bash
# AI 映射功能需要 Anthropic API 密钥
export ANTHROPIC_API_KEY="your-api-key"
```

### 自定义映射

编辑 `field_mappings/custom.json` 添加自定义映射：

```json
{
  "domain": "custom",
  "mappings": {
    "自定义字段": {
      "en_name": "custom_field",
      "group": "general",
      "dtype": "string",
      "description": "自定义字段说明"
    }
  }
}
```

## 📈 版本历史

### v2.4 (2025-11-27) - 手机号码填充工具 🆕
- ✨ 新增手机号码自动填充工具
- 🔐 使用安全的未启用号段（100、102-109）
- 🎯 智能识别手机号码字段
- 🔍 支持预览模式
- 📝 完整的使用文档

### v2.3 (2025-11-23) - 质量保障
- 🔍 映射质量校验体系
- 4 个校验维度与质量评分
- 自动生成质量报告

### v2.2 (2025-11-23) - AI 批量学习
- 🤖 AI 驱动的自动字段映射
- 语义分析 + 数据样本推断
- 测试数据集准确率 100%

### v2.1 (2025-11-23)
- ✨ 支持 CSV 文件
- 统一 Excel 与 CSV 接口

### v2.0 (2025-11-23)
- ✨ Claude Code Skill 架构
- 多源配置系统
- 交互式字段学习

## 📖 示例

### 示例 1: 完整流程

```bash
# 1. 分析文件
python scripts/analyzer.py insurance_data.xlsx ./output

# 2. 填充缺失手机号
python scripts/phone_filler.py insurance_data.xlsx --prefix 100

# 3. 查看结果
# - output/insurance_data_xxx_分析报告.html
# - output/insurance_data_xxx_字段映射.json
# - output/insurance_data_xxx_质量检查报告.md
```

### 示例 2: Python 集成

```python
from scripts.analyzer import FieldMappingManager, FieldAnalyzer
from scripts.phone_filler import PhoneFiller
import pandas as pd

# 读取数据
df = pd.read_excel('data.xlsx', dtype=str)

# 填充手机号
filler = PhoneFiller(prefix='100')
df, count = filler.fill_empty_phones(df, '手机号')
print(f"填充了 {count} 个手机号")

# 保存
df.to_excel('data_filled.xlsx', index=False)

# 分析字段
analyzer = FieldAnalyzer(skill_dir='.')
results = analyzer.analyze_file('data_filled.xlsx')
```

## ⚠️ 注意事项

### 手机号码填充工具

1. **仅用于测试**：生成的号码不是真实号码，不要用于生产环境
2. **数据备份**：建议使用 `-o` 参数保存到新文件
3. **号段安全**：100-109 号段在中国移动网络中未启用

### AI 映射功能

1. **API 密钥**：需要配置 `ANTHROPIC_API_KEY` 环境变量
2. **网络连接**：需要访问 Anthropic API
3. **数据隐私**：注意不要上传敏感数据

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📮 联系

如有问题或建议，请提交 Issue。
