---
name: excel-field-analyzer
description: "分析Excel/CSV字段结构，AI自动生成中英文映射，验证翻译质量，输出统计报告。用于电子表格分析、数据字典创建、字段映射场景。"
allowed-tools: Read, Bash, Write, Glob, Grep
---

# Excel/CSV Field Analyzer

## Overview

Intelligent analysis of Excel and CSV files with automatic generation of bilingual field mappings, statistical reports, and HTML visualizations.

**Key Capabilities:**
- Field statistics analysis (null rates, unique values, distribution)
- AI-powered field mapping (50+ pre-built auto insurance fields)
- Automatic mapping quality validation
- HTML visualization reports

## Quick Start

### Conversational Invocation (Recommended)

Simply chat with Claude:
```
"Help me analyze this Excel file's fields"
"Analyze ./data/insurance_data.xlsx field mappings"
```

### Command Line

```bash
# Basic analysis
python scripts/analyzer.py <file_path> [output_dir] [topn]

# Example
python scripts/analyzer.py data.xlsx ./output 10

# Supported formats: .xlsx, .xls, .csv, .txt
```

## Core Features

### 1. Pre-built Mapping Library
- **Auto Insurance Domain**: 50+ built-in field mappings
- **Coverage**: Finance, Vehicle, Organization, Product, Time fields
- **Examples**:
  - `商业险保费` → `commercial_premium` (finance/number)
  - `三级机构` → `org_level_3` (organization/string)
  - `确认时间` → `time_confirm` (time/datetime)

### 2. AI Batch Learning
- **Zero Manual Labor**: Automatically generates mappings for unknown fields
- **Intelligent Analysis**: Semantic analysis + data sample inference
- **Auto-Save**: Results saved to `custom.json` for future use
- **High Accuracy**: 100% accuracy on 70-field test dataset

**Example:**
```
🔍 Found 70 unknown fields
💡 Using AI to generate mappings...
✅ Generated 70 mappings and saved to custom.json

- 刷新时间 → time_refresh [time/datetime]
- 交叉销售标识 → flag_cross_sales [flag/string]
- 签单保费 → premium_signing [finance/number]
```

### 3. Quality Validation
- **Automatic Checks**: 4 validation dimensions (naming, grouping, semantics, type)
- **Quality Scoring**: Excellent (≥90) / Good (75-89) / Fair (60-74) / Poor (<60)
- **Detailed Reports**: Markdown format with improvement suggestions

### 4. Interactive Learning
- **Manual Mode**: Optional precise control for field mappings
- **Guided Process**: Step-by-step field name, group, and type selection
- **Persistent Storage**: All learned mappings saved to `custom.json`

## Output Files

### 1. HTML Visualization Report
- File metadata and generation time
- Complete statistics table for each worksheet
- Numeric statistics, top value distribution
- Interactive exploration

### 2. JSON Field Mapping Table
```json
{
  "field_name": "commercial_premium",
  "cn_name": "商业险保费",
  "group": "finance",
  "dtype": "number",
  "role": "measure",
  "aggregation": "sum",
  "is_mapped": true
}
```

### 3. Quality Validation Report (Markdown)
- Overall quality statistics
- Fields requiring review with suggestions
- Excellent mapping examples
- Quality distribution visualization

## Business Groups

| Group | Description | Examples |
|-------|-------------|----------|
| finance | Financial data | Premium, claims, fees |
| organization | Organization info | Level 3 org, Level 4 org |
| vehicle | Vehicle-related | License plates, vehicle type |
| product | Product info | Insurance class, insurance type |
| time | Date/time fields | Confirmation time, start date |
| flag | Status flags | Renewal flag, new energy flag |
| partner | Partner info | 4S groups, dealers |
| general | General fields | Business type, customer category |

## Documentation

- **reference.md** - Complete technical documentation, configuration details, API reference
- **examples.md** - Code examples, usage scenarios, integration guides

## Version History

### v2.3 (2025-11-23) - Quality Assurance
- 🔍 Mapping quality validation system
- 4 validation dimensions with quality scoring
- Automatic quality report generation

### v2.2 (2025-11-23) - AI Batch Learning
- 🤖 AI-powered automatic field mapping
- Semantic analysis + data sample inference
- 100% accuracy on test dataset

### v2.1 (2025-11-23)
- ✨ CSV file support
- Unified Excel and CSV interface

### v2.0 (2025-11-23)
- ✨ Claude Code Skill architecture
- Multi-source configuration system
- Interactive field learning

## Dependencies

```bash
pip install pandas openpyxl numpy
```

## License

MIT License
