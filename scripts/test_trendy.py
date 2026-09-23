# 网感名生成器测试脚本

import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from trendy_names_generator import run_trendy_generate

print("=" * 70)
print("网感名生成器测试")
print("=" * 70)
print()

# 测试1: 小红书风 - 李姓
print("【测试1】李姓 - 小红书风")
print(run_trendy_generate(surname="李", style="xiaohongshu", count=10))
print("
" * 2)

# 测试2: 文艺风 - 随机姓氏
print("【测试2】随机姓氏 - 文艺风")
print(run_trendy_generate(surname=None, style="literary", count=10))
print("
" * 2)

# 测试3: 国潮风 - 欧阳复姓
print("【测试3】欧阳 - 国潮风")
print(run_trendy_generate(surname="欧阳", style="guochao", count=10))
print("
" * 2)

# 测试4: 五格全吉模式
print("【测试4】王姓 - 温柔风 - 五格全吉")
print(run_trendy_generate(surname="王", style="gentle", count=10, require_wuge_ji=True))
print("
" * 2)

# 测试5: 单名模式
print("【测试5】张姓 - 极简风 - 单名")
print(run_trendy_generate(surname="张", style="minimal", count=10, name_length=1))
print("
" * 2)

print("=" * 70)
print("测试完成！")
print("=" * 70)
