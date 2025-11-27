# 手机号码自动填充工具使用指南

## 概述

`phone_filler.py` 是一个智能的手机号码填充工具，可以自动识别 Excel/CSV 文件中的手机号码字段，并为空值生成虚拟的测试手机号码。

## 核心特性

### ✅ 安全的测试号段
- 使用中国**未启用**的号段（100、102-109）
- 不会与真实手机号码冲突
- 格式：`10XXXXXXXXX`（11位数字）
- 默认使用 **100** 号段（最明显的测试标识）

### ✅ 智能识别
- 自动检测手机号码字段（手机、电话、联系方式等）
- 验证字段是否包含真实的手机号码数据
- 支持中英文字段名

### ✅ 灵活配置
- 可选择不同的号段前缀（100-109）
- 支持预览模式（不修改文件）
- 可手动指定字段名
- 自动去重，确保不生成重复号码

## 快速开始

### 基本用法

```bash
# 自动检测并填充（覆盖原文件）
python scripts/phone_filler.py data.xlsx

# 保存到新文件
python scripts/phone_filler.py data.xlsx -o output.xlsx
```

### 预览模式

在实际修改文件之前，先预览将要进行的操作：

```bash
python scripts/phone_filler.py data.csv --dry-run
```

输出示例：
```
📱 手机号码填充工具
   使用号段: 100XXXXXXXX
   输入文件: data.csv
   模式: 预览（不修改文件）

✅ 列 '手机号': 填充 5 个空值
✅ 列 '联系电话': 填充 3 个空值

============================================================
📊 处理总结
   文件: data.csv
   总行数: 100
   处理列数: 2
   总填充数: 8

💡 这是预览模式。使用 --dry-run=false 实际修改文件
```

## 高级用法

### 1. 使用不同的号段

```bash
# 使用 102 号段
python scripts/phone_filler.py data.xlsx --prefix 102

# 使用 105 号段
python scripts/phone_filler.py data.xlsx --prefix 105
```

**可用号段列表**：
- `100` - 默认，最明显的测试号段 ⭐推荐
- `102` - 未分配
- `103` - 未分配
- `104` - 未分配
- `105` - 未分配
- `107` - 未分配
- `108` - 未分配
- `109` - 未分配

### 2. 手动指定字段

```bash
# 只处理指定的字段
python scripts/phone_filler.py data.xlsx --columns 手机号 联系电话 --no-auto-detect
```

### 3. 处理 CSV 文件

```bash
# CSV 文件处理方式相同
python scripts/phone_filler.py contacts.csv -o contacts_filled.csv
```

## Python API 使用

也可以在 Python 代码中使用：

```python
from scripts.phone_filler import PhoneFiller
import pandas as pd

# 创建填充器
filler = PhoneFiller(prefix='100')

# 读取文件
df = pd.read_csv('data.csv', dtype=str)

# 检测手机号码列
phone_columns = filler.detect_phone_columns(df)
print(f"检测到手机号码列: {phone_columns}")

# 填充指定列
df, filled_count = filler.fill_empty_phones(df, '手机号')
print(f"填充了 {filled_count} 个空值")

# 保存
df.to_csv('output.csv', index=False)
```

### 批量处理

```python
from scripts.phone_filler import PhoneFiller

filler = PhoneFiller(prefix='100')

# 处理多个文件
files = ['data1.xlsx', 'data2.csv', 'data3.xlsx']

for file in files:
    result = filler.process_file(
        input_path=file,
        auto_detect=True,
        dry_run=False
    )
    print(f"✅ {file}: 填充了 {result['total_filled']} 个空值")
```

## 工作原理

### 1. 字段识别
脚本会自动识别包含以下关键词的字段：
- 中文：手机、电话、联系电话、联系方式
- 英文：mobile, phone, tel, contact

### 2. 数据验证
对识别到的字段进行验证：
- 检查非空值是否符合手机号码格式（11位，1开头）
- 至少50%的样本符合格式才会处理

### 3. 空值检测
识别以下情况为空值：
- `NaN` / `None`
- 空字符串 `''`
- 字符串 `'nan'` / `'NaN'`

### 4. 号码生成
- 格式：`{前缀}{8位随机数字}`
- 示例：`10012345678`
- 自动去重，确保唯一性

## 使用场景

### 1. 测试环境数据脱敏

```bash
# 原始数据包含真实手机号
# 姓名,手机号,邮箱
# 张三,13800138000,zhang@example.com
# 李四,,li@example.com

# 填充后
python scripts/phone_filler.py test_data.csv

# 结果
# 姓名,手机号,邮箱
# 张三,13800138000,zhang@example.com
# 李四,10012345678,li@example.com
```

### 2. 批量数据清洗

```bash
# 处理导入的数据，填充缺失的手机号
python scripts/phone_filler.py import_data.xlsx -o cleaned_data.xlsx
```

### 3. 数据库导入准备

```python
# 填充后导入数据库，避免 NOT NULL 约束错误
from scripts.phone_filler import PhoneFiller

filler = PhoneFiller(prefix='100')
result = filler.process_file('user_data.csv', dry_run=False)

# 然后导入数据库
import_to_database('user_data.csv')
```

## 注意事项

### ⚠️ 重要提醒

1. **不要用于生产环境**
   - 生成的号码仅用于测试
   - 100 开头的号码在中国移动网络中未启用

2. **数据备份**
   - 使用 `-o` 参数保存到新文件更安全
   - 或先使用 `--dry-run` 预览

3. **数据类型**
   - 为了正确处理手机号码，文件会以字符串格式读取
   - 这可能影响其他数字列的处理

4. **文件格式**
   - 支持：`.xlsx`, `.xls`, `.csv`, `.txt`
   - Excel 文件需要 openpyxl 库

## 常见问题

### Q: 为什么选择 100 号段？

A: 100 是电信客服特服号，但 11 位的 `100XXXXXXXX` 格式在移动通信中从未启用，非常安全且易于识别。

### Q: 生成的号码会重复吗？

A: 不会。脚本内部维护了已生成号码的集合，确保每个号码唯一。

### Q: 可以保留原有的非空号码吗？

A: 可以。脚本只填充空值，不会修改已有的手机号码。

### Q: 如何只预览不修改？

A: 使用 `--dry-run` 参数：
```bash
python scripts/phone_filler.py data.xlsx --dry-run
```

### Q: 支持哪些文件格式？

A: 支持 Excel (`.xlsx`, `.xls`) 和 CSV (`.csv`, `.txt`) 格式。

### Q: 如何手动指定要处理的列？

A: 使用 `--columns` 和 `--no-auto-detect`：
```bash
python scripts/phone_filler.py data.xlsx --columns 手机号 --no-auto-detect
```

## 命令行选项参考

```
usage: phone_filler.py [-h] [-o OUTPUT] [--prefix PREFIX]
                       [--columns COLUMNS [COLUMNS ...]]
                       [--dry-run] [--no-auto-detect]
                       input

参数:
  input                 输入文件路径（支持 .xlsx, .xls, .csv）
  -o, --output         输出文件路径（默认覆盖原文件）
  --prefix             号段前缀（默认: 100）
  --columns            手动指定手机号码列名（默认自动检测）
  --dry-run            预览模式，不实际修改文件
  --no-auto-detect     禁用自动检测，必须手动指定列名
```

## 示例

### 示例 1: 基本使用
```bash
python scripts/phone_filler.py data.xlsx
```

### 示例 2: 预览模式
```bash
python scripts/phone_filler.py data.xlsx --dry-run
```

### 示例 3: 指定输出文件
```bash
python scripts/phone_filler.py data.xlsx -o filled_data.xlsx
```

### 示例 4: 使用其他号段
```bash
python scripts/phone_filler.py data.xlsx --prefix 102
```

### 示例 5: 手动指定列
```bash
python scripts/phone_filler.py data.xlsx --columns 手机号 联系电话
```

### 示例 6: 组合使用
```bash
python scripts/phone_filler.py data.csv --prefix 105 -o output.csv --dry-run
```

## 技术细节

### 号码格式
- 总长度：11 位
- 格式：`{前缀(3位)}{随机数(8位)}`
- 示例：`10012345678`, `10298765432`

### 验证规则
- 正则表达式：`^1\d{10}$`
- 必须以 1 开头
- 总共 11 位数字

### 性能
- 小文件（< 1000 行）：秒级处理
- 中等文件（1000-10000 行）：通常 < 5 秒
- 大文件（> 10000 行）：取决于空值数量

## 更新日志

### v1.0 (2025-11-27)
- ✨ 首次发布
- ✅ 支持自动检测手机号码字段
- ✅ 支持 Excel 和 CSV 格式
- ✅ 提供 9 个安全的测试号段（100, 102-109）
- ✅ 预览模式
- ✅ 手动指定字段
- ✅ Python API 支持

## 许可证

MIT License
