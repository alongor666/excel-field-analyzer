# Excel Field Analyzer - Usage Examples

## 1. Command Line Usage

### Basic Analysis (Non-Interactive)

```bash
# Analyze Excel file
python scripts/analyzer.py <file_path> [output_dir] [topn]

# Examples
python scripts/analyzer.py data.xlsx ./output 10
python scripts/analyzer.py data.csv ./output 10
```

### Interactive Analysis (with Field Learning)

```bash
# Interactive mode with manual mapping
python scripts/interactive_analyzer.py <file_path> [output_dir] [topn]

# Example
python scripts/interactive_analyzer.py ./data/new_data.xlsx ./analysis_output 20
```

**Supported Formats:** `.xlsx`, `.xls`, `.csv`, `.txt`

---

## 2. Python API Usage

### Basic Analysis

```python
from pathlib import Path
import sys
sys.path.append(str(Path.home() / '.claude/skills/excel-field-analyzer'))
from analyzer import ExcelAnalyzer

# Create analyzer instance
analyzer = ExcelAnalyzer()

# Run analysis
result = analyzer.analyze_excel(
    xlsx_path='data.xlsx',
    output_dir='./output',
    topn=10
)

# Check results
if result['success']:
    print(f"✅ Analysis complete!")
    print(f"HTML report: {result['html_path']}")
    print(f"JSON mapping: {result['json_path']}")
    print(f"Unknown fields: {', '.join(result['unknown_fields'])}")
else:
    print(f"❌ Error: {result['message']}")
```

---

## 3. Claude Code Integration

When users request Excel field analysis, execute these steps:

### Step 1: Confirm File Path

```python
# Ask user for Excel file path
xlsx_path = input("Please provide Excel file path: ")
```

### Step 2: Run Analysis

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

### Step 3: Handle Unknown Fields

```python
if result['unknown_fields']:
    print(f"\n🔍 Found {len(result['unknown_fields'])} unknown fields:")
    for field in result['unknown_fields']:
        print(f"  - {field}")

    # Ask user if they want to create mappings
    response = input("\nCreate mappings for these fields? (y/n): ")
    if response.lower() == 'y':
        for cn_field in result['unknown_fields']:
            print(f"\n【Field: {cn_field}】")
            en_name = input("  English name: ")
            group = input("  Business group (finance/vehicle/general, etc.): ")
            dtype = input("  Data type (number/string/datetime): ")
            description = input("  Description (optional): ")

            analyzer.mapping_manager.add_custom_mapping(
                cn_field=cn_field,
                en_name=en_name,
                group=group,
                dtype=dtype,
                description=description or f"Custom mapping for {cn_field}"
            )
            print(f"  ✅ Mapping saved")

        # Re-analyze with new mappings
        print("\n🔄 Re-analyzing...")
        result = analyzer.analyze_excel(xlsx_path, './analysis_output', 10)
```

### Step 4: Display Results

```python
if result['success']:
    print(f"\n✅ Analysis complete!")
    print(f"📊 Sheets: {len(result['sheets'])}")
    print(f"📝 Total fields: {result['field_stats']['total_fields']}")
    print(f"✓ Mapped: {result['field_stats']['mapped_count']}")
    print(f"? Unknown: {result['field_stats']['unknown_count']}")
    print(f"\n📄 HTML report: {result['html_path']}")
    print(f"📋 JSON mapping: {result['json_path']}")
```

---

## 4. Interactive Learning Flow

### Console Interaction Example

```
============================================================
🔍 Found 2 unknown fields
============================================================

1. 客户满意度
2. 代理商等级

============================================================
Create mappings for these fields? (y/n): y

Starting field learning...

────────────────────────────────────────────────────────────
Field: 客户满意度
────────────────────────────────────────────────────────────
English name [suggestion: customer_satisfaction]: customer_satisfaction_score

Business group options:
  1. finance (Financial: premium, claims, fees)
  2. vehicle (Vehicle: license, model)
  3. organization (Organization: branches)
  4. product (Product: insurance types)
  5. time (Time/Date)
  6. flag (Flags: yes/no fields)
  7. partner (Partner: dealers)
  8. general (General fields)

Select group [1-8, default 8]: 8

Data type options:
  1. number (Numeric)
  2. string (String)
  3. datetime (Date/Time)

Select type [1-3, default 2]: 1

Description (optional, press Enter to skip): Customer satisfaction score (1-5)

✅ Saved: 客户满意度 → customer_satisfaction_score (general, number)

[Continue with next field...]

============================================================
🔄 Re-analyzing with new mappings...
============================================================
```

---

## 5. Configuration Management

### View Current Mappings

```python
from analyzer import ExcelAnalyzer

analyzer = ExcelAnalyzer()
mappings = analyzer.mapping_manager.combined_mappings

for cn_field, mapping in mappings.items():
    print(f"{cn_field} → {mapping['en_name']}")
```

### Add Custom Mapping Programmatically

```python
analyzer.mapping_manager.add_custom_mapping(
    cn_field="客户满意度",
    en_name="customer_satisfaction",
    group="general",
    dtype="number",
    description="Customer satisfaction score"
)
```

### Import Mappings from Excel

Create `字段映射配置.xlsx`:

| 中文字段 | 英文字段名 | 分组 | 类型 | 说明 |
|---------|-----------|------|------|------|
| 客户等级 | customer_level | general | string | Customer tier |

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

### Export Mapping Library

```bash
# Copy mapping files to another environment
cp -r ~/.claude/skills/excel-field-analyzer/field_mappings /path/to/backup/
```

---

## 6. Advanced Usage

### Analyzing Multiple Files

```python
import glob
from analyzer import ExcelAnalyzer

analyzer = ExcelAnalyzer()
files = glob.glob('./data/*.xlsx')

for file in files:
    print(f"Analyzing {file}...")
    result = analyzer.analyze_excel(file, './batch_output', 10)
    if result['success']:
        print(f"  ✅ {file} complete")
    else:
        print(f"  ❌ {file} failed: {result['message']}")
```

### Custom Output Format

```python
result = analyzer.analyze_excel('data.xlsx', './output', topn=20)

# Access detailed statistics
for sheet_name, sheet_data in result['stats'].items():
    print(f"\nSheet: {sheet_name}")
    for field, stats in sheet_data.items():
        print(f"  {field}: {stats['row_count']} rows, "
              f"{stats['null_rate']:.1%} null")
```

---

## 7. Testing and Validation

### Quick Test

```bash
# Test basic functionality
python scripts/analyzer.py ./test_data.xlsx ./test_output 10

# Verify output
ls -lh test_output/
cat test_output/*_字段映射.json | head -50
```

### Verify Mapping Quality

After analysis, check the quality report:

```bash
# View quality report
cat ./output/*_质量检查报告.md
```

The report will show:
- Overall quality score
- Fields requiring review
- Excellent mapping examples
- Quality distribution visualization
