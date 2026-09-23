"""
网感名生成引擎 v2.0
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from name_wuge import get_kangxi_strokes, calc_wuge, to_simplified
from trendy_names_data import COMMON_SURNAMES, COMPOUND_SURNAMES, TRENDY_CHARS, STYLE_NAMES
import random
from typing import Optional, List, Dict, Tuple

try:
    from pypinyin import lazy_pinyin, Style
    PYPINYIN_AVAILABLE = True
except ImportError:
    PYPINYIN_AVAILABLE = False

def get_char_pool_by_style(style):
    if style not in TRENDY_CHARS:
        style = random.choice(list(TRENDY_CHARS.keys()))
    return TRENDY_CHARS[style]["chars"].split()

def check_phonetic_harmony(chars):
    if not PYPINYIN_AVAILABLE or len(chars) < 2:
        return True
    return True

def calculate_stroke_balance_score(surname, name_chars):
    strokes = [get_kangxi_strokes(c) for c in [surname] + name_chars]
    strokes = [s for s in strokes if s]
    if len(strokes) < 2:
        return 50.0
    avg = sum(strokes) / len(strokes)
    variance = sum((s - avg) ** 2 for s in strokes) / len(strokes)
    std_dev = variance ** 0.5
    if std_dev < 3:
        score = 70 + (3 - std_dev) * 5
    elif std_dev <= 8:
        score = 90 - (std_dev - 3) * 2
    else:
        score = max(50, 80 - (std_dev - 8) * 3)
    return min(100, max(0, score))

def calculate_style_match_score(chars, style):
    style_chars = set(get_char_pool_by_style(style))
    match_count = sum(1 for c in chars if c in style_chars)
    return (match_count / len(chars)) * 100 if chars else 0

def calculate_modernity_score(chars):
    if len(chars) == 2:
        base_score = 80
    elif len(chars) == 1:
        base_score = 60
    else:
        base_score = 50
    return min(100, max(0, base_score + random.randint(-10, 10)))

def calculate_trendy_score(surname, name_chars, wuge_result, style, require_wuge_ji=False):
    scores = {}
    ji_count = 0
    for grid_name, grid_info in wuge_result['wuge'].items():
        if grid_info.get('jixiong') == '吉':
            ji_count += 1
    scores["wuge"] = (ji_count / 5) * 100
    scores["phonetic"] = 90 if check_phonetic_harmony(name_chars) else 50
    scores["stroke"] = calculate_stroke_balance_score(surname, name_chars)
    scores["style"] = calculate_style_match_score(name_chars, style)
    scores["modernity"] = calculate_modernity_score(name_chars)
    if require_wuge_ji:
        weights = {"wuge": 0.30, "phonetic": 0.25, "stroke": 0.20, "style": 0.15, "modernity": 0.10}
    else:
        weights = {"wuge": 0.15, "phonetic": 0.25, "stroke": 0.20, "style": 0.25, "modernity": 0.15}
    total = sum(scores[k] * weights[k] for k in scores)
    return round(total, 1)

def recommend_styles(surname):
    classical = ["柳", "苏", "林", "谢", "沈", "欧阳", "司马", "诸葛", "慕容"]
    common = ["王", "李", "张", "刘", "陈", "杨", "黄", "赵", "吴", "周"]
    rare = ["云", "凌", "夜", "星", "月", "风", "龙"]
    if surname in classical or any(surname.startswith(c) for c in classical):
        return ["guochao", "literary", "elegant"]
    elif surname in rare:
        return ["anime", "cool", "minimal"]
    elif surname in common:
        return ["xiaohongshu", "minimal", "gentle"]
    else:
        return ["gentle", "elegant", "minimal"]

def generate_trendy_names(surname=None, style=None, gender=None, name_length=2, count=20, require_wuge_ji=False):
    results = []
    if not surname:
        all_surnames = COMMON_SURNAMES + COMPOUND_SURNAMES
        surname = random.choice(all_surnames)
    if not style:
        recommended = recommend_styles(surname)
        style = recommended[0]
    if style not in TRENDY_CHARS:
        style = "xiaohongshu"
    char_pool = get_char_pool_by_style(style)
    attempts = 0
    max_attempts = count * 50
    while len(results) < count and attempts < max_attempts:
        attempts += 1
        if name_length == 1:
            name_chars = [random.choice(char_pool)]
        else:
            name_chars = random.sample(char_pool, min(name_length, len(char_pool)))
        given_name = "".join(name_chars)
        full_name = surname + given_name
        wuge_result = calc_wuge(surname, given_name)
        if not wuge_result:
            continue
        if require_wuge_ji:
            ji_count = 0
            for grid_name, grid_info in wuge_result['wuge'].items():
                if grid_info.get('jixiong') == '吉':
                    ji_count += 1
            if ji_count < 5:
                continue
        if not check_phonetic_harmony(name_chars):
            continue
        score = calculate_trendy_score(surname, name_chars, wuge_result, style, require_wuge_ji)
        if score < 70:
            continue
        style_desc = TRENDY_CHARS[style]["description"]
        results.append((full_name, wuge_result, score, style_desc))
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:count]

def run_trendy_generate(surname=None, style=None, gender=None, name_length=2, count=20, require_wuge_ji=False):
    results = generate_trendy_names(surname=surname, style=style, gender=gender, name_length=name_length, count=count, require_wuge_ji=require_wuge_ji)
    if not results:
        return "未能生成符合条件的名字"

    lines = []
    for name, wuge_result, score, desc in results:
        wuge_info = wuge_result['wuge']
        zong_grid = wuge_info.get('总格', {})
        zong_num = zong_grid.get('number', 0)
        zong_jx = zong_grid.get('jixiong', '凶')

        # 提取每个字的笔画
        strokes_info = []
        full_name = name
        surname_len = 2 if len(full_name) > 2 and full_name[:2] in COMPOUND_SURNAMES else 1
        surname_part = full_name[:surname_len]
        given_part = full_name[surname_len:]

        for char in full_name:
            stroke = get_kangxi_strokes(char)
            strokes_info.append(f"{char}({stroke})")

        strokes_str = "+".join(strokes_info)

        lines.append(f"【{name}】风格:{desc} 笔画:{strokes_str} 评分:{int(score)} (总格:{zong_num}-{zong_jx})")

    return chr(10).join(lines)


# ============================================
# 押韵名生成器（三种押韵模式）
# ============================================

def generate_rhyming_names(
    surname=None,
    rhyme_type="yunmu",      # yunmu(韵母) / bushou(部首) / yijing(意境)
    yunmu_target=None,       # 如 "i", "u", "ang", "eng"
    bushou_target=None,      # 如 "艹", "氵", "木", "钅"
    theme=None,              # 如 "nature", "season", "flower", "water"
    name_length=2,
    count=20,
    require_zongge_ji=True   # 总格必须为吉
):
    """
    生成押韵名字（总格为吉）

    三种押韵模式：
    1. yunmu - 韵母押韵（音韵和谐）
    2. bushou - 部首统一（视觉和谐）
    3. yijing - 意境关联（主题统一）
    """
    results = []
    if not surname:
        all_surnames = COMMON_SURNAMES + COMPOUND_SURNAMES
        surname = random.choice(all_surnames)

    # 根据押韵类型构建字符池
    if rhyme_type == "yunmu" and yunmu_target and PYPINYIN_AVAILABLE:
        char_pool = _build_yunmu_pool(yunmu_target)
    elif rhyme_type == "bushou" and bushou_target:
        char_pool = _build_bushou_pool(bushou_target)
    elif rhyme_type == "yijing" and theme:
        char_pool = _build_theme_pool(theme)
    else:
        return []

    if not char_pool or len(char_pool) < name_length:
        return []

    attempts = 0
    max_attempts = count * 100

    while len(results) < count and attempts < max_attempts:
        attempts += 1

        if name_length == 1:
            name_chars = [random.choice(char_pool)]
        else:
            name_chars = random.sample(char_pool, min(name_length, len(char_pool)))

        given_name = "".join(name_chars)
        full_name = surname + given_name

        wuge_result = calc_wuge(surname, given_name)
        if not wuge_result:
            continue

        # 检查总格是否为吉
        zong_grid = wuge_result['wuge'].get('总格', {})
        if require_zongge_ji and zong_grid.get('jixiong') != '吉':
            continue

        # 计算评分（押韵名简化评分）
        score = _calculate_rhyming_score(surname, name_chars, wuge_result, rhyme_type)

        if score < 70:
            continue

        # 生成描述
        desc = _generate_rhyme_desc(rhyme_type, yunmu_target, bushou_target, theme)

        results.append((full_name, wuge_result, score, desc))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:count]


def _build_yunmu_pool(yunmu_target):
    """构建韵母相同的字符池"""
    if not PYPINYIN_AVAILABLE:
        return []

    all_chars = set()
    for style_data in TRENDY_CHARS.values():
        all_chars.update(style_data["chars"].split())

    pool = []
    for char in all_chars:
        pinyin_list = lazy_pinyin(char, style=Style.FINALS)
        if pinyin_list and pinyin_list[0] == yunmu_target:
            pool.append(char)

    return pool


def _build_bushou_pool(bushou_target):
    """构建部首相同的字符池"""
    all_chars = set()
    for style_data in TRENDY_CHARS.values():
        all_chars.update(style_data["chars"].split())

    # 预定义常见部首的字符集合
    bushou_sets = {
        "艹": "芷 茉 茜 芸 莉 兰 梅 菊 萱 蕊 薇 菡 荷 芙 蓉 菲 蓝 薰 莲 芳 萌 蔷 薇 茗 芮 荟 蕾 菱 莹 苓 苑 英 茂 荣 萝 芬 蒂 芊 茵 苏 莞 芯 蕴 荃 荠 萍 蒡 菁 茹 荔 菀 茜 芃 茹 蕙 荌",
        "氵": "江 河 海 湖 溪 泉 澜 波 涛 浪 流 汐 沁 洛 沫 涵 澈 清 润 泽 滑 柔 淡 浅 深 渊 潭 瀑 漓 洁 洋 浩 涌 泳 汉 沙 沐 泊 沁 洒 洪 津 浦 洲 滨 渝 泰 浓 涓 汀 淳 溶 滔 渺 淀 漾 沧 淑 漫 淮 滢",
        "木": "林 森 桐 梧 松 柏 杏 桃 李 梨 樱 桂 柚 柠 橙 枫 桦 梓 栎 梁 棋 杨 柳 梅 樟 榆 槐 桢 栋 梵 楠 榕 椿 槿 栀 檀 楚 枝 杭 杉 柱 棠 楹 橘 榛 棉 楷 梧 樱 榉 柯",
        "钅": "锐 锋 刃 剑 刀 银 铁 钢 锦 镜 铃 钟 铭 锡 钰 铄 钦 锌 铮 铎 锦 镭 锟 铠 锴 钊 铨 锋 钧 铭 钏 铢 铮 锤 镐 镑 链 铨 锚 铸",
        "王": "琪 瑶 琳 珺 瑾 瑜 璇 琦 琴 筝 玲 璃 玥 珞 瑕 璞 璋 璧 环 琮 圭 玄 玉 珏 珮 珩 琳 琛 琨 瑾 瑶 璇 珏 璟 瑜 璞 琅 琊",
        "纟": "绫 纯 素 绮 绚 缤 纷 纹 绣 织 绵 纱 绸 缎 维 纲 纪 约 纯 绅 绛 绮 绯 纾 缘 缨 纭 综 绦 绫 缇",
        "阝": "陈 陆 阳 阴 陵 陶 郭 郑 郝 邓 邵 邱 郁 都 邦 郎 邻 陪 陌 院 阁 阵 隆 际 陶 郁 郦 邹 邬"
    }

    if bushou_target in bushou_sets:
        pool = [c for c in bushou_sets[bushou_target].split() if c in all_chars]
    else:
        pool = []

    return pool


def _build_theme_pool(theme):
    """构建主题相关的字符池"""
    theme_pools = {
        "nature": "云 山 岚 谷 溪 泉 江 河 海 湖 波 澜 风 雨 雪 霜 露 雾 霁 晴 树 林 森 木 松 柏 竹 梅 兰 菊 荷 莲 芷 萱 薇 藤",
        "season": "春 夏 秋 冬 暖 寒 暑 凉 青 绿 红 黄 白 雪 霜 露 雨 风 花 叶 果 实 种 芽 苗 蕾 绽 落 枯 荣",
        "flower": "梅 兰 竹 菊 荷 莲 牡 丹 桃 李 杏 梨 樱 桂 茉 莉 玫 瑰 百 合 芙 蓉 芷 萱 薇 蔷 薇 茜 菲 芸 蕊",
        "water": "江 河 海 湖 溪 泉 澜 波 涛 浪 流 汐 沁 洛 沫 涵 澈 清 润 泽 滑 柔 淡 浅 深 渊 潭 瀑 漓",
        "sky": "天 空 云 星 月 日 辰 曦 晨 昏 暮 晓 夕 霞 虹 霓 雷 电 霜 雪 雾 露 风 岚 晴 朗 明 亮 光 辉"
    }

    chars = theme_pools.get(theme, "")
    return chars.split()


def _calculate_rhyming_score(surname, name_chars, wuge_result, rhyme_type):
    """押韵名评分（简化版）"""
    scores = {}

    # 五格评分（主要看总格）
    zong_grid = wuge_result['wuge'].get('总格', {})
    if zong_grid.get('jixiong') == '吉':
        scores["wuge"] = 100
    else:
        scores["wuge"] = 0

    # 笔画平衡
    scores["stroke"] = calculate_stroke_balance_score(surname, name_chars)

    # 押韵匹配度
    scores["rhyme"] = 90  # 默认高分，因为已经从押韵池中筛选

    # 音韵和谐
    scores["phonetic"] = 85 if check_phonetic_harmony(name_chars) else 60

    weights = {
        "wuge": 0.40,      # 总格权重提高
        "stroke": 0.20,
        "rhyme": 0.25,
        "phonetic": 0.15
    }

    total = sum(scores[k] * weights[k] for k in scores)
    return round(total, 1)


def _generate_rhyme_desc(rhyme_type, yunmu_target, bushou_target, theme):
    """生成押韵描述"""
    if rhyme_type == "yunmu":
        return f"韵母押韵(-{yunmu_target})"
    elif rhyme_type == "bushou":
        return f"部首统一({bushou_target})"
    elif rhyme_type == "yijing":
        theme_names = {
            "nature": "自然意境",
            "season": "四季主题",
            "flower": "花草主题",
            "water": "山水意境",
            "sky": "天象主题"
        }
        return theme_names.get(theme, "意境关联")
    return "押韵名"


def run_rhyming_generate(
    surname=None,
    rhyme_type="yunmu",
    yunmu_target=None,
    bushou_target=None,
    theme=None,
    name_length=2,
    count=20
):
    """押韵名生成的格式化输出接口"""
    results = generate_rhyming_names(
        surname=surname,
        rhyme_type=rhyme_type,
        yunmu_target=yunmu_target,
        bushou_target=bushou_target,
        theme=theme,
        name_length=name_length,
        count=count,
        require_zongge_ji=True
    )

    if not results:
        return f"未能生成符合条件的押韵名（{rhyme_type}模式）"

    lines = []
    for name, wuge_result, score, desc in results:
        wuge_info = wuge_result['wuge']
        zong_grid = wuge_info.get('总格', {})
        zong_num = zong_grid.get('number', 0)
        zong_jx = zong_grid.get('jixiong', '凶')

        strokes_info = []
        for char in name:
            stroke = get_kangxi_strokes(char)
            strokes_info.append(f"{char}({stroke})")

        strokes_str = "+".join(strokes_info)

        lines.append(f"【{name}】{desc} 笔画:{strokes_str} 评分:{int(score)} (总格:{zong_num}-{zong_jx})")

    return chr(10).join(lines)
