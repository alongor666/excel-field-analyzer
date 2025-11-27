# Excel 字段分析器 - 使用示例

## 1. 命令行用法

### 基础分析（非交互）

```bash
# 分析 Excel 文件
python scripts/analyzer.py <file_path> [output_dir] [topn]

# 示例
python scripts/analyzer.py data.xlsx ./output 10
python scripts/analyzer.py data.csv ./output 10
```

### 交互式分析（含字段学习）

```bash
# 交互模式（支持手动映射）
python scripts/interactive_analyzer.py <file_path> [output_dir] [topn]

# 示例
python scripts/interactive_analyzer.py ./data/new_data.xlsx ./analysis_output 20
```

**支持格式：**`.xlsx`、`.xls`、`.csv`、`.txt`

---

## 2. Python API 用法

### 基础分析

```python
from pathlib import Path
import sys
sys.path.append(str(Path.home() / '.claude/skills/excel-field-analyzer'))
from analyzer import ExcelAnalyzer

# 创建分析器实例
analyzer = ExcelAnalyzer()

# 执行分析
result = analyzer.analyze_excel(
    xlsx_path='data.xlsx',
    output_dir='./output',
    topn=10
)

# 检查结果
if result['success']:
    print(f"✅ Analysis complete!")
    print(f"HTML report: {result['html_path']}")
    print(f"JSON mapping: {result['json_path']}")
    print(f"Unknown fields: {', '.join(result['unknown_fields'])}")
else:
    print(f"❌ Error: {result['message']}")
```

---

## 3. Claude Code 集成

当用户请求 Excel 字段分析时，按以下步骤执行：

### 步骤 1：确认文件路径

```python
# 询问用户 Excel 文件路径
xlsx_path = input("Please provide Excel file path: ")
```

### 步骤 2：执行分析

```python
from pathlib import Path
import sys
sys.path.append(str(Path.home() / '.claude/skills/excel-field-analyzer'))
from analyzer import ExcelAnalyzer

analyzer = ExcelAnalyzer()
result = analyzer.analyze_excel(
    xlsx_path=xlsx_path,
    output_dir='./analysis_output',
    topn=10
)
```

### 步骤 3：处理未知字段

```python
if result['unknown_fields']:
    print(f"\n🔍 Found {len(result['unknown_fields'])} unknown fields:")
    for field in result['unknown_fields']:
        print(f"  - {field}")

    # 询问用户是否创建映射
    response = input("\n是否为这些字段创建映射？(y/n): ")
    if response.lower() == 'y':
        for cn_field in result['unknown_fields']:
            print(f"\n【字段: {cn_field}】")
            en_name = input("  英文名: ")
            group = input("  业务分组 (finance/vehicle/general 等): ")
            dtype = input("  数据类型 (number/string/datetime): ")
            description = input("  描述 (可选): ")

            analyzer.mapping_manager.add_custom_mapping(
                cn_field=cn_field,
                en_name=en_name,
                group=group,
                dtype=dtype,
                description=description or f"Custom mapping for {cn_field}"
            )
            print(f"  ✅ 映射已保存")

        # 使用新映射重新分析
        print("\n🔄 正在重新分析...")
        result = analyzer.analyze_excel(xlsx_path, './analysis_output', 10)
```

### 步骤 4：展示结果

```python
if result['success']:
    print(f"\n✅ 分析完成！")
    print(f"📊 工作表数量: {len(result['sheets'])}")
    print(f"📝 字段总数: {result['field_stats']['total_fields']}")
    print(f"✓ 已映射: {result['field_stats']['mapped_count']}")
    print(f"? 未知: {result['field_stats']['unknown_count']}")
    print(f"\n📄 HTML 报告: {result['html_path']}")
    print(f"📋 JSON 映射: {result['json_path']}")
```

---

## 4. 交互式学习流程

### 控制台交互示例

```
============================================================
🔍 发现 2 个未知字段
============================================================

1. 客户满意度
2. 代理商等级

============================================================
是否为这些字段创建映射？(y/n): y

开始字段学习...

────────────────────────────────────────────────────────────
字段：客户满意度
────────────────────────────────────────────────────────────
英文名 [建议: customer_satisfaction]: customer_satisfaction_score

业务分组选项：
  1. finance (Financial: premium, claims, fees)
  2. vehicle (Vehicle: license, model)
  3. organization (Organization: branches)
  4. product (Product: insurance types)
  5. time (Time/Date)
  6. flag (Flags: yes/no fields)
  7. partner (Partner: dealers)
  8. general (General fields)

选择分组 [1-8，默认 8]: 8

数据类型选项：
  1. number (Numeric)
  2. string (String)
  3. datetime (Date/Time)

选择类型 [1-3，默认 2]: 1

描述（可选，回车跳过）：Customer satisfaction score (1-5)

✅ 已保存：客户满意度 → customer_satisfaction_score（general, number）

[Continue with next field...]

============================================================
🔄 使用新映射重新分析...
============================================================
```

---

## 5. 配置管理

### 查看当前映射

```python
from analyzer import ExcelAnalyzer

analyzer = ExcelAnalyzer()
mappings = analyzer.mapping_manager.combined_mappings

for cn_field, mapping in mappings.items():
    print(f"{cn_field} → {mapping['en_name']}")
```

### 以编程方式添加自定义映射

```python
analyzer.mapping_manager.add_custom_mapping(
    cn_field="客户满意度",
    en_name="customer_satisfaction",
    group="general",
    dtype="number",
    description="Customer satisfaction score"
)
```

### 从 Excel 导入映射

Create `字段映射配置.xlsx`:

| 中文字段 | 英文字段名 | 分组 | 类型 | 说明 |
|---------|-----------|------|------|------|
| 客户等级 | customer_level | general | string | 客户等级 |

```python
import pandas as pd

config_df = pd.read_excel('字段映射配置.xlsx')
for _, row in config_df.iterrows():
    analyzer.mapping_manager.add_custom_mapping(
        cn_field=row['中文字段'],
        en_name=row['英文字段名'],
        group=row['分组'],
        dtype=row['类型'],
        description=row['说明']
    )
```

### 导出映射库

```bash
# 将映射文件复制到其他环境
cp -r ~/.claude/skills/excel-field-analyzer/field_mappings /path/to/backup/
```

---

## 6. 高级用法

### 批量分析多个文件

```python
import glob
from analyzer import ExcelAnalyzer

analyzer = ExcelAnalyzer()
files = glob.glob('./data/*.xlsx')

for file in files:
    print(f"正在分析 {file}...")
    result = analyzer.analyze_excel(file, './batch_output', 10)
    if result['success']:
        print(f"  ✅ {file} 完成")
    else:
        print(f"  ❌ {file} 失败: {result['message']}")
```

### 自定义输出格式

```python
result = analyzer.analyze_excel('data.xlsx', './output', topn=20)

# 访问详细统计
for sheet_name, sheet_data in result['stats'].items():
    print(f"\nSheet: {sheet_name}")
    for field, stats in sheet_data.items():
        print(f"  {field}: {stats['row_count']} rows, "
              f"{stats['null_rate']:.1%} null")
```

---

## 7. 手机号码自动填充

### 功能说明

自动检测并填充 Excel/CSV 文件中的空手机号码字段，使用中国未启用的 **100 号段**（10000000000-10099999999）。

### 基础用法

```bash
# 自动检测手机号字段并填充
python scripts/phone_number_filler.py data.xlsx

# 指定字段名
python scripts/phone_number_filler.py data.xlsx --field "联系电话"

# 预览模式（不实际修改文件）
python scripts/phone_number_filler.py data.xlsx --preview
```

### 高级选项

```bash
# 指定输出文件路径
python scripts/phone_number_filler.py data.xlsx --output filled_data.xlsx

# 处理 Excel 特定工作表
python scripts/phone_number_filler.py data.xlsx --sheet "客户信息"

# 使用自定义号段前缀（必须是1字头的3位数）
python scripts/phone_number_filler.py data.xlsx --prefix 101

# 处理 CSV 文件
python scripts/phone_number_filler.py data.csv

# 查看帮助
python scripts/phone_number_filler.py --help
```

### 使用示例

**示例1：自动检测并填充**
```bash
$ python scripts/phone_number_filler.py customer_data.xlsx

📱 使用号段: 100xxxxxxxx (中国未启用的100号段)
📂 正在读取文件: customer_data.xlsx
   格式: Excel, 行数: 1000, 列数: 15
🔍 自动检测到手机号字段: 手机号码, 联系电话

📊 字段 '手机号码' 统计:
   总行数: 1000
   空值数: 150
   空值率: 15.00%
✅ 成功填充 150 个手机号码

📊 字段 '联系电话' 统计:
   总行数: 1000
   空值数: 0
   空值率: 0.00%
✅ 字段 '联系电话' 没有空值，无需填充

💾 正在保存文件: customer_data_filled.xlsx
✅ 文件已保存: customer_data_filled.xlsx

============================================================
✅ 成功填充 150 个手机号码
📁 输出文件: customer_data_filled.xlsx
```

**示例2：预览模式**
```bash
$ python scripts/phone_number_filler.py data.xlsx --preview

📱 使用号段: 100xxxxxxxx (中国未启用的100号段)
📂 正在读取文件: data.xlsx
🔍 自动检测到手机号字段: 手机

📊 字段 '手机' 统计:
   总行数: 500
   空值数: 50
   空值率: 10.00%
🔍 预览模式: 将填充 50 个空值
   行 2: [空] → 10012345678
   行 5: [空] → 10087654321
   行 8: [空] → 10056789012
   行 12: [空] → 10098765432
   行 15: [空] → 10011223344

============================================================
✅ 预览完成，将填充 50 个手机号码
```

**示例3：指定字段名**
```bash
$ python scripts/phone_number_filler.py data.xlsx --field "客户手机"

📱 使用号段: 100xxxxxxxx (中国未启用的100号段)
📂 正在读取文件: data.xlsx
🎯 使用指定字段: 客户手机

📊 字段 '客户手机' 统计:
   总行数: 200
   空值数: 25
   空值率: 12.50%
✅ 成功填充 25 个手机号码

💾 正在保存文件: data_filled.xlsx
✅ 文件已保存: data_filled.xlsx
```

### Python API 用法

```python
from pathlib import Path
import sys
sys.path.append(str(Path.home() / '.claude/skills/excel-field-analyzer/scripts'))
from phone_number_filler import PhoneNumberFiller

# 创建填充器（使用100号段）
filler = PhoneNumberFiller(prefix='100')

# 处理文件
result = filler.process_file(
    file_path='data.xlsx',
    field='手机号码',           # 可选，不指定则自动检测
    output_path='filled.xlsx',  # 可选，默认添加_filled后缀
    preview=False               # False表示实际修改文件
)

# 检查结果
if result['success']:
    print(f"✅ {result['message']}")
    print(f"填充数量: {result['filled_count']}")
    print(f"输出文件: {result['output_path']}")
else:
    print(f"❌ {result['message']}")
```

### 字段自动检测规则

脚本会自动检测包含以下关键词的字段：
- 中文：手机、电话、联系方式、联系电话、移动电话
- 英文：phone、mobile、tel、telephone、contact

### 空值识别规则

以下值会被视为空值并填充：
- 空字符串 `""`
- pandas 的 `NaN`、`None`
- 字符串形式：`"nan"`、`"none"`、`"null"`、`"无"`、`"空"`、`"n/a"`、`"na"`

### 注意事项

1. **号段安全性**：默认使用 100 号段，这是中国从未分配给任何运营商的号段，不会与真实手机号冲突
2. **数据备份**：脚本默认创建新文件（添加 `_filled` 后缀），不会覆盖原文件
3. **预览模式**：使用 `--preview` 参数可以先查看将要填充的内容，确认无误后再实际执行
4. **批量处理**：可以使用 Python 脚本批量处理多个文件

### 批量处理示例

```python
import glob
from phone_number_filler import PhoneNumberFiller

filler = PhoneNumberFiller(prefix='100')
files = glob.glob('./data/*.xlsx')

for file in files:
    print(f"处理文件: {file}")
    result = filler.process_file(file)
    if result['success']:
        print(f"  ✅ 完成: {result['filled_count']} 个号码")
    else:
        print(f"  ❌ 失败: {result['message']}")
```

---

## 8. 测试与校验

### 快速测试

```bash
# 测试基础功能
python scripts/analyzer.py ./test_data.xlsx ./test_output 10

# 验证输出
ls -lh test_output/
cat test_output/*_字段映射.json | head -50
```

### 校验映射质量

分析完成后，查看质量报告：

```bash
# 查看质量报告
cat ./output/*_质量检查报告.md
```

报告将展示：
- 总体质量分数
- 需复审字段
- 优秀映射示例
- 质量分布可视化
