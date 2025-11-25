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

## 7. 测试与校验

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
