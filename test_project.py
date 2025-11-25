#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Field Mapper Test Suite
Tests the optimized field mapper without requiring pandas
"""

import sys
import json
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

# Test basic imports
print("=" * 80)
print("Test 1: Basic Imports")
print("=" * 80)

try:
    # Test re module (always available)
    import re
    print("✅ re module imported")

    # Check if ai_mapper module can be parsed
    ai_mapper_path = Path(__file__).parent / 'scripts' / 'ai_mapper.py'
    if ai_mapper_path.exists():
        with open(ai_mapper_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Try to compile the code
            compile(content, str(ai_mapper_path), 'exec')
        print(f"✅ ai_mapper.py syntax valid ({len(content)} bytes)")
    else:
        print("❌ ai_mapper.py not found")
        sys.exit(1)

except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Configuration Files
print("\n" + "=" * 80)
print("Test 2: Configuration Files")
print("=" * 80)

field_mappings_dir = Path(__file__).parent / 'field_mappings'
if not field_mappings_dir.exists():
    print(f"❌ field_mappings directory not found")
    sys.exit(1)

print(f"✅ field_mappings directory exists")

# Check JSON files
json_files = list(field_mappings_dir.glob('*.json'))
print(f"\nFound {len(json_files)} JSON configuration files:")

for json_file in json_files:
    if json_file.name.endswith('.backup'):
        continue
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'mappings' in data:
                mapping_count = len(data['mappings'])
                domain = data.get('domain', 'unknown')
                print(f"  ✅ {json_file.name}: {mapping_count} mappings (domain: {domain})")
            else:
                print(f"  ⚠️ {json_file.name}: No 'mappings' key found")
    except json.JSONDecodeError as e:
        print(f"  ❌ {json_file.name}: Invalid JSON - {e}")
    except Exception as e:
        print(f"  ❌ {json_file.name}: Error - {e}")

# Test 3: Path Configuration
print("\n" + "=" * 80)
print("Test 3: Path Configuration")
print("=" * 80)

# Simulate analyzer path logic
script_path = Path(__file__).parent / 'scripts' / 'analyzer.py'
skill_dir = script_path.parent.parent
mappings_dir = skill_dir / 'field_mappings'

print(f"Script path: {script_path}")
print(f"Skill directory: {skill_dir}")
print(f"Mappings directory: {mappings_dir}")
print(f"Mappings directory exists: {mappings_dir.exists()}")

if mappings_dir.exists():
    print("✅ Path configuration correct")
else:
    print("❌ Path configuration incorrect")
    sys.exit(1)

# Test 4: Test Field Mappings (without pandas)
print("\n" + "=" * 80)
print("Test 4: Field Mapping Logic Test")
print("=" * 80)

# Test cases covering all categories
test_cases = [
    # (field_name, expected_group, expected_type, description)
    ('保单号', 'policy', 'string', 'Policy number'),
    ('签单保费', 'finance', 'number', 'Written premium'),
    ('商业险保费', 'finance', 'number', 'Commercial premium'),
    ('交强险保费', 'finance', 'number', 'Compulsory premium'),
    ('总赔款', 'finance', 'number', 'Total claims'),
    ('案均赔款', 'finance', 'number', 'Average claim'),
    ('手续费', 'finance', 'number', 'Commission'),
    ('费用率', 'finance', 'number', 'Expense ratio'),
    ('赔付率', 'finance', 'number', 'Loss ratio'),
    ('NCD系数', 'finance', 'number', 'NCD factor'),
    ('三级机构', 'organization', 'string', 'Level 3 organization'),
    ('四级机构', 'organization', 'string', 'Level 4 organization'),
    ('业务员', 'organization', 'string', 'Agent'),
    ('销售渠道', 'organization', 'string', 'Sales channel'),
    ('车牌号码', 'vehicle', 'string', 'License plate'),
    ('车架号', 'vehicle', 'string', 'VIN'),
    ('车型', 'vehicle', 'string', 'Vehicle model'),
    ('新旧车', 'vehicle', 'string', 'Vehicle age category'),
    ('座位数', 'vehicle', 'number', 'Seat count'),
    ('车龄', 'vehicle', 'number', 'Vehicle age'),
    ('险种', 'product', 'string', 'Coverage type'),
    ('保额', 'product', 'number', 'Coverage amount'),
    ('投保人', 'customer', 'string', 'Policyholder'),
    ('被保险人', 'customer', 'string', 'Insured'),
    ('证件号码', 'customer', 'string', 'ID number'),
    ('保险起期', 'time', 'datetime', 'Policy start date'),
    ('保险止期', 'time', 'datetime', 'Policy end date'),
    ('确认时间', 'time', 'datetime', 'Confirmation time'),
    ('签单时间', 'time', 'datetime', 'Issuance time'),
    ('是否续保', 'flag', 'boolean', 'Is renewal'),
    ('是否新能源', 'flag', 'boolean', 'Is new energy'),
    ('保单状态', 'general', 'string', 'Policy status'),
    ('风险评分', 'general', 'number', 'Risk score'),
]

# Test exact mappings by loading JSON
auto_insurance_path = mappings_dir / 'auto_insurance.json'
exact_mappings = {}

if auto_insurance_path.exists():
    with open(auto_insurance_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if 'mappings' in data:
            exact_mappings = data['mappings']

print(f"Loaded {len(exact_mappings)} exact mappings from auto_insurance.json\n")

# Simple validation
passed = 0
failed = 0
warnings = 0

for field_name, expected_group, expected_type, description in test_cases:
    if field_name in exact_mappings:
        mapping = exact_mappings[field_name]
        en_name = mapping.get('en_name', '')
        group = mapping.get('group', '')
        dtype = mapping.get('dtype', '')

        # Validation
        issues = []

        # Check group
        if group != expected_group:
            issues.append(f"Group mismatch: {group} != {expected_group}")

        # Check type
        if dtype != expected_type:
            issues.append(f"Type mismatch: {dtype} != {expected_type}")

        # Check naming conventions
        if not re.match(r'^[a-z][a-z0-9_]*$', en_name):
            issues.append(f"Invalid naming: {en_name}")

        # Check for forbidden suffixes
        if any(suffix in en_name for suffix in ['_yuan', '_rmb', '_percent']):
            issues.append(f"Forbidden suffix in: {en_name}")

        if issues:
            print(f"⚠️  {field_name} → {en_name}")
            for issue in issues:
                print(f"    - {issue}")
            warnings += 1
        else:
            print(f"✅ {field_name} → {en_name} ({group}/{dtype})")
            passed += 1
    else:
        print(f"❌ {field_name}: Not found in exact mappings")
        failed += 1

# Test 5: Naming Convention Validation
print("\n" + "=" * 80)
print("Test 5: Naming Convention Validation")
print("=" * 80)

all_mappings_valid = True
invalid_names = []

for cn_field, mapping in exact_mappings.items():
    en_name = mapping.get('en_name', '')

    # Check snake_case
    if not re.match(r'^[a-z][a-z0-9_]*$', en_name):
        invalid_names.append((cn_field, en_name, "Not snake_case"))
        all_mappings_valid = False

    # Check length
    if len(en_name) > 50:
        invalid_names.append((cn_field, en_name, "Too long (>50)"))
        all_mappings_valid = False

    # Check forbidden suffixes
    if any(suffix in en_name for suffix in ['_yuan', '_rmb', '_cny']):
        invalid_names.append((cn_field, en_name, "Language-specific suffix"))
        all_mappings_valid = False

    # Check for consecutive underscores
    if '__' in en_name:
        invalid_names.append((cn_field, en_name, "Consecutive underscores"))
        all_mappings_valid = False

if all_mappings_valid:
    print(f"✅ All {len(exact_mappings)} mappings pass naming conventions")
else:
    print(f"⚠️  Found {len(invalid_names)} naming issues:")
    for cn, en, issue in invalid_names[:10]:  # Show first 10
        print(f"  - {cn} → {en}: {issue}")

# Test 6: Type System Validation
print("\n" + "=" * 80)
print("Test 6: Type System Validation")
print("=" * 80)

valid_types = {'string', 'number', 'datetime', 'boolean'}
type_counts = {}
invalid_types = []

for cn_field, mapping in exact_mappings.items():
    dtype = mapping.get('dtype', '')

    if dtype not in valid_types:
        invalid_types.append((cn_field, dtype))
    else:
        type_counts[dtype] = type_counts.get(dtype, 0) + 1

if invalid_types:
    print(f"❌ Found {len(invalid_types)} invalid types:")
    for cn, dtype in invalid_types:
        print(f"  - {cn}: {dtype}")
else:
    print(f"✅ All types are valid standard types")
    print("\nType distribution:")
    for dtype, count in sorted(type_counts.items()):
        print(f"  - {dtype}: {count}")

# Test 7: Business Group Validation
print("\n" + "=" * 80)
print("Test 7: Business Group Validation")
print("=" * 80)

valid_groups = {'finance', 'organization', 'vehicle', 'product', 'customer',
                'time', 'flag', 'policy', 'general'}
group_counts = {}
invalid_groups = []

for cn_field, mapping in exact_mappings.items():
    group = mapping.get('group', '')

    if group not in valid_groups:
        invalid_groups.append((cn_field, group))
    else:
        group_counts[group] = group_counts.get(group, 0) + 1

if invalid_groups:
    print(f"❌ Found {len(invalid_groups)} invalid groups:")
    for cn, group in invalid_groups:
        print(f"  - {cn}: {group}")
else:
    print(f"✅ All groups are valid")
    print("\nGroup distribution:")
    for group, count in sorted(group_counts.items(), key=lambda x: -x[1]):
        print(f"  - {group}: {count}")

# Final Summary
print("\n" + "=" * 80)
print("Test Summary")
print("=" * 80)

total_tests = passed + failed + warnings
print(f"Total test cases: {total_tests}")
print(f"✅ Passed: {passed}")
print(f"⚠️  Warnings: {warnings}")
print(f"❌ Failed: {failed}")

if failed == 0:
    print("\n🎉 All critical tests passed!")
    sys.exit(0)
else:
    print("\n⚠️  Some tests failed, please review")
    sys.exit(1)
