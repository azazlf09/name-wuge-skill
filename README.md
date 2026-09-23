# name-wuge - 五格数理 + 网感名生成器

完整的姓名五格数理测算与网感名生成工具。

**跨平台支持：** ✅ macOS · ✅ Linux · ✅ Windows（Python 3.8+）

## 功能模块

### 1. 五格数理测算
传统姓名学五格（天格/人格/地格/外格/总格）数理分析，基于康熙字典笔画。

### 2. 网感名生成器（v2.0）
8种风格的现代网感名字生成，结合五格数理、音韵优化、笔画平衡的多维度评分系统。

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

必需依赖：
- `opencc-python-reimplemented` - 繁简体转换
- `pypinyin` - 音韵分析

### 安装到 Claude Code Skill 目录

**macOS / Linux：**
```bash
git clone https://github.com/azazlf09/name-wuge-skill.git ~/.claude/skills/name-wuge
cd ~/.claude/skills/name-wuge && pip3 install -r requirements.txt
```

**Windows（Git Bash）：**
```bash
git clone https://github.com/azazlf09/name-wuge-skill.git ~/.claude/skills/name-wuge
cd ~/.claude/skills/name-wuge && pip install -r requirements.txt
```

### 缓存路径（跨平台自动）

完整康熙字典（~3MB）首次运行自动下载，缓存位置：

| 系统 | 缓存目录 |
|------|---------|
| macOS | `~/.cache/name_skill/kangxi_full.json` |
| Linux | `~/.cache/name_skill/kangxi_full.json` |
| Windows | `C:\Users\<用户>\.cache\name_skill\kangxi_full.json` |

也可通过环境变量 `SKILL_CACHE_DIR` 自定义。

### 测试验证

```bash
# 完整测试套件
cd scripts && python test_trendy.py

# 快速验证
python -c "from scripts.trendy_names_generator import run_trendy_generate; print(run_trendy_generate(surname='李', style='xiaohongshu', count=5))"
```

## 网感名生成器使用

### Python API

```python
from scripts.trendy_names_generator import run_trendy_generate

# 基础用法 - 小红书风格
print(run_trendy_generate(surname='李', style='xiaohongshu', count=10))

# 五格全吉模式
print(run_trendy_generate(surname='王', style='gentle', count=10, require_wuge_ji=True))

# 单名模式
print(run_trendy_generate(surname='张', style='minimal', name_length=1, count=10))

# 复姓支持
print(run_trendy_generate(surname='欧阳', style='guochao', count=10))
```

### 8种风格

| 风格代码 | 描述 | 适合姓氏 |
|---------|------|---------|
| `xiaohongshu` | 轻盈甜美，少女感十足 | 王、李、张等常见姓 |
| `literary` | 诗意古典，文艺优雅 | 柳、苏、林、谢 |
| `anime` | 动漫二次元，元气活力 | 云、凌、夜、星 |
| `guochao` | 传统底蕴，新中式 | 欧阳、司马、诸葛 |
| `minimal` | 简约高级，现代感 | 各类姓氏 |
| `cool` | 个性街头，潮酷时尚 | 龙、虎、云 |
| `gentle` | 治愈柔软，温暖温柔 | 各类姓氏 |
| `elegant` | 知性精英，高级气质 | 各类姓氏 |

### 评分维度

- **五格数理** (15-30%): 天格、人格、地格、外格、总格吉凶
- **音韵和谐** (25%): 韵母声母组合协调性
- **笔画平衡** (20%): 康熙笔画标准差控制
- **风格匹配** (15-25%): 字符与风格库的契合度
- **现代感** (10-15%): 双名优于单名的时代偏好

### 两种模式

**普通模式** (默认)：
- 总格为吉即可
- 其他四格随机搭配
- 音韵优先，名字更好听

**五格全吉模式** (`require_wuge_ji=True`)：
- 天格、人格、地格、外格、总格全部为吉
- 生成难度高，部分姓氏+风格组合可能无结果
- 评分权重向五格倾斜（30%）

## 五格测算使用

```python
from scripts.name_wuge import calc_wuge, run, run_company

# 测算姓名
result = calc_wuge('李', '明华')
print(result)

# 格式化输出
print(run('李', '明华'))

# 公司名总格测算
print(run_company('阿里巴巴'))
```

## 文件结构

```
name-wuge/
├── SKILL.md                    # Skill 元数据与触发规则
├── README.md                   # 本文件
├── DEPENDENCIES.md             # 依赖说明
├── requirements.txt            # pip 依赖清单
├── 使用教程.md                 # 详细教程
└── scripts/
    ├── name_wuge.py            # 五格数理核心引擎
    ├── name_generator.py       # 传统五格全吉生成器
    ├── trendy_names_generator.py  # 网感名生成引擎 v2.0
    ├── trendy_names_data.py    # 8种风格字库 + 百家姓数据
    └── test_trendy.py          # 测试套件
```

## 数据来源

- **81数理**: cnk3x/bys (Apache-2.0)
- **康熙笔画**: breezyreeds/kangxi-strokecount (MIT)
- **风格字库**: 人工精选 1000+ 字符，8 个主题维度

## 已知限制

1. **五格全吉模式成功率**
   - 某些姓氏+风格组合因数理限制无法生成全吉名字
   - 推荐先尝试普通模式，确认有结果后再开启全吉模式

2. **字库覆盖**
   - 常用字 3500+ 覆盖完整
   - 生僻字需触发完整康熙字典下载（自动）

3. **音韵过滤**
   - 依赖 pypinyin 库
   - 未安装时跳过音韵检查但不影响生成

## 更新日志

### v2.0 (2026-08-27)
- 新增网感名生成器，8种现代风格
- 多维度评分系统（五格+音韵+笔画+风格+现代感）
- 修复 cool 风格字库的英文字符污染问题
- 支持普通模式与五格全吉模式切换
- 完整测试覆盖所有风格

### v1.0
- 五格数理测算
- 传统五格全吉生成器
- 康熙字典笔画查询
