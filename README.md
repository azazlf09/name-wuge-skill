# name-wuge · 姓名五格 + 八大主题起名

**姓名五格数理测算** + **八大主题名字生成**（网感 / 贵气 / 皇室 / 仙气 / 武将 / 甜美 / 出道 / 文艺）

一句自然语言直接生成，全平台开箱即用。

**跨平台：** ✅ macOS · ✅ Linux · ✅ Windows（Python 3.8+）

---

## 30 秒上手

### 1️⃣ 安装

**macOS / Linux：**
```bash
git clone https://github.com/azazlf09/name-wuge-skill.git ~/.claude/skills/name-wuge
cd ~/.claude/skills/name-wuge && pip3 install -r requirements.txt
```

**Windows（Git Bash / PowerShell）：**
```bash
git clone https://github.com/azazlf09/name-wuge-skill.git ~/.claude/skills/name-wuge
cd ~/.claude/skills/name-wuge && pip install -r requirements.txt
```

### 2️⃣ 使用（三选一）

**A · 对 Claude / NewMax 说自然语言（最推荐）：**

```
来30个贵气的男宝宝名字
50个甜美的女生名字
仙风道骨男名20个
皇女公主的名字30个
```

AI 会自动调用 skill，输出干净格式。

**B · 命令行直接跑：**

```bash
cd scripts
python smart_generate.py "来30个贵气的男宝宝名字"
```

**C · Python API：**

```python
from scripts.smart_generate import smart_generate
print(smart_generate("来30个贵气的男宝宝名字"))
```

---

## 输出效果

每一行统一格式：

```
════════════════════════════════════════════════════════════════
  ✦  达官贵人 · 男 · 30 个  ✦
════════════════════════════════════════════════════════════════
 1. 【吕鸿宏】风格:达官贵人 笔画:吕(6)+鸿(17)+宏(7) 评分:95 (总格:31-吉)
 2. 【唐卿恕】风格:达官贵人 笔画:唐(10)+卿(11)+恕(10) 评分:95 (总格:31-吉)
 3. 【宋珏瑨】风格:达官贵人 笔画:宋(7)+珏(10)+瑨(15) 评分:95 (总格:32-吉)
 ...
```

- ✅ 全部 **总格为吉**
- ✅ 按评分降序
- ✅ 单双名混合
- ✅ 随机姓氏自动匹配主题
- ✅ Windows 中文不乱码

---

## 8 大主题

| 主题码 | 触发关键词 | 示例 |
|---|---|---|
| `trendy` | 网感 / 时尚 / 潮流 / 小红书 | 来30个网感女名 |
| `noble` | 贵气 / 达官 / 世家 / 名门 | 来30个贵气男名 |
| `royal` | 皇 / 公主 / 帝王 / 皇室 | 来30个皇女公主的名字 |
| `xian` | 仙 / 道 / 脱俗 / 清雅 | 来20个仙风道骨男名 |
| `wushu` | 武将 / 将军 / 侠 / 沙场 | 来50个古风武将男名 |
| `sweet` | 甜 / 初恋 / JK / 少女 | 来50个甜美女生名 |
| `debut` | 出道 / 明星 / 艺人 / 网红 | 来40个出道女名 |
| `literary` | 文艺 / 古典 / 诗 / 书香 | 来20个文艺古典男名 |

---

## 分享给别人怎么用

给朋友直接甩两个东西就够了：

1. **本仓库地址**：`https://github.com/azazlf09/name-wuge-skill`
2. **[傻瓜使用指令.md](./傻瓜使用指令.md)**：一句一句复制就能用

---

## 五格测算功能（原有）

```python
from scripts.name_wuge import run, run_company, calc_wuge

# 测算姓名
print(run("李", "明华"))

# 公司名总格
print(run_company("阿里巴巴"))

# 结构化返回
data = calc_wuge("李", "明华")
print(data['wuge']['总格'])  # {'number': 33, 'jixiong': '吉', ...}
```

对 AI 直接说也行：
```
测名 李明华
公司名 阿里巴巴
```

---

## 参数详解（如果需要精确控制）

```python
smart_generate(
    query="贵气的男宝宝名字",  # 自然语言，自动映射主题+性别+数量
    surname="李",              # 可选：指定姓氏（否则随机）
    count=30,                  # 可选：覆盖 query 里的数量
)
```

内部规则：
- **主题识别**：从 query 里搜关键词，未命中默认 `trendy`
- **性别识别**：男/女/男宝/女宝/JK/少女... → male/female
- **数量识别**：正则抽数字，1-100 之间
- **过滤**：只保总格为吉
- **单双名**：20% 单名 + 80% 双名

---

## 依赖

```
opencc-python-reimplemented   # 繁简转换
pypinyin                      # 音韵分析（押韵功能用）
```

无需 GPU、无需 API Key、无需网络（首次运行会自动下载 3MB 康熙字典缓存到 `~/.cache/name_skill/`）。

---

## 数据来源

- **81数理**：[cnk3x/bys](https://github.com/cnk3x/bys) (Apache-2.0)
- **康熙笔画**：[breezyreeds/kangxi-strokecount](https://github.com/breezyreeds/kangxi-strokecount) (MIT)
- **8 大主题字库**：人工精选 1500+ 字符

---

## 文件结构

```
name-wuge-skill/
├── SKILL.md                    # Claude Code Skill 元数据与触发规则
├── README.md                   # 本文件
├── 傻瓜使用指令.md              # 一句话使用卡片（给别人）
├── 使用教程.md                 # 详细教程
├── DEPENDENCIES.md
├── requirements.txt
├── LICENSE                     # MIT
└── scripts/
    ├── smart_generate.py       # ⭐ 傻瓜入口（v3.0）
    ├── name_wuge.py            # 五格核心引擎
    ├── name_generator.py       # 传统全吉生成器
    ├── trendy_names_generator.py  # 网感名生成 v2.0
    ├── trendy_names_data.py    # 8种风格字库
    └── test_trendy.py
```

---

## 更新日志

### v3.0 (2026-09-23) - 分享友好版
- ⭐ 新增 `smart_generate` 傻瓜入口，自然语言直接调用
- ⭐ 内置 8 大主题池（trendy / noble / royal / xian / wushu / sweet / debut / literary）
- ⭐ 自然语言 → 主题/性别/数量自动映射
- ⭐ Windows 终端 UTF-8 自动包装，不再乱码
- ⭐ 默认强制总格为吉，未指定姓氏自动随机
- ⭐ 命令行入口：`python smart_generate.py "自然语言"`
- 📄 新增 `傻瓜使用指令.md`，一句话使用卡片

### v2.0 (2026-08-27)
- 网感名生成器，8种现代风格
- 多维度评分（五格 + 音韵 + 笔画 + 风格 + 现代感）
- 普通模式与五格全吉模式

### v1.0
- 五格数理测算
- 传统五格全吉生成器
- 康熙字典笔画查询

---

## License

MIT
