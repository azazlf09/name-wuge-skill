"""
╔══════════════════════════════════════════════════════════╗
║         smart_generate - 傻瓜入口 v1.0                    ║
║                                                          ║
║  用户一句自然语言 → 自动匹配专题字库 → 干净排版输出         ║
║                                                          ║
║  内置 9 大专题池：                                         ║
║    · trendy    - 网感/时尚/年轻/潮流                       ║
║    · noble     - 达官贵人/贵气/世家/名门                   ║
║    · royal     - 皇女公主/皇室/帝王/尊贵                   ║
║    · xian      - 仙气/仙风道骨/清雅/脱俗                   ║
║    · wushu     - 武将/古风/侠客/沙场                       ║
║    · sweet     - 甜美/初恋/JK/少女                         ║
║    · debut     - 出道/明星/艺人/网红                       ║
║    · literary  - 文艺/古典/诗意/书香                       ║
║    · digital   - 数字人/虚拟偶像（复姓池+全名四字，v3.1）    ║
║                                                          ║
║  内置规则：                                                ║
║    · 默认只保总格为吉                                      ║
║    · 未指定姓氏时随机分配                                  ║
║    · Windows 终端自动 UTF-8 输出                          ║
║    · 单双名混合，输出按评分降序                            ║
╚══════════════════════════════════════════════════════════╝
"""

import sys
import io
import os
import random
import re
from typing import Optional, List

# ─── Windows UTF-8 自动包装（分享给别人第一坑） ───
# 仅在 stdout 尚未是 UTF-8 时包装，避免外部已包装导致 I/O on closed file
if sys.platform == "win32":
    try:
        _cur = getattr(sys.stdout, "encoding", "") or ""
        if "utf" not in _cur.lower():
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        _cur_err = getattr(sys.stderr, "encoding", "") or ""
        if "utf" not in _cur_err.lower():
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from name_wuge import get_kangxi_strokes, calc_wuge, to_traditional


def _stroke_of(ch: str, strokes: dict) -> int:
    """显示层笔画：优先按繁体键查 calc 结果，fallback 按繁体查康熙"""
    t = to_traditional(ch)
    v = strokes.get(t)
    if v is None:
        v = strokes.get(ch)
    if v is None:
        v = get_kangxi_strokes(t)
    if v is None:
        v = get_kangxi_strokes(ch)
    return v


# ═══════════════════════════════════════════════
# § 1  百家姓 + 专题姓氏池
# ═══════════════════════════════════════════════

COMMON_SURNAMES = [
    "王","李","张","刘","陈","杨","黄","赵","吴","周",
    "徐","孙","马","朱","胡","郭","何","高","林","罗",
    "郑","梁","谢","宋","唐","许","韩","冯","邓","曹",
    "彭","曾","肖","田","董","袁","潘","于","蒋","蔡",
    "余","杜","叶","程","苏","魏","吕","丁","任","沈",
    "姚","卢","姜","崔","钟","谭","陆","汪","范","金",
    "石","廖","贾","夏","韦","傅","方","白","邹","孟",
    "熊","秦","邱","江","尹","薛","阎","段","雷","侯",
    "龙","史","陶","黎","贺","顾","毛","郝","龚","邵",
    "万","覃","武","钱","戴","严","欧","莫","孔","向",
]

COMPOUND_SURNAMES = [
    "欧阳","司马","上官","诸葛","皇甫","令狐","司徒","司空",
    "长孙","宇文","慕容","东方","南宫","西门","轩辕","独孤"
]

# ═══ 完整复姓池（数字人/虚拟偶像专用，v3.1）═══
# 用户指定 60 姓（已剔除"吴铭"——非复姓）+ 酌情增补 5 姓
COMPOUND_SURNAMES_FULL = [
    # 用户指定
    "欧阳","上官","司马","诸葛","东方","南宫","端木","令狐",
    "公孙","司徒","司空","轩辕","慕容","宇文","赫连","皇甫",
    "拓跋","夏侯","尉迟","公羊","澹台","申屠","仲孙","钟离",
    "长孙","微生","漆雕","乐正","宰父","谷梁","段干","百里",
    "呼延","东郭","南门","羊舌","西门","第五","即墨","达奚",
    "褚师","万俟","闻人","亓官","颛孙","壤驷","公良","公西",
    "公冶","闾丘","子车","夹谷","贯丘","公皙","南荣","东里",
    "东宫","仲长","子书","子桑",
    # 酌情增补（v3.1）
    "独孤","鲜于","淳于","公输","司寇",
    # v3.2 扩充：春秋战国世家（40 姓）
    "太史","太叔","太宰","左丘","左师","右师","中行","王孙",
    "王叔","公叔","公仲","公伯","公仪","公乘","公山","公玉",
    "公祖","公夏","子服","子家","叔孙","季孙","孟孙","臧孙",
    "司城","东门","南郭","北门","巫马","步叔","濮阳","梁丘",
    "毋丘","新垣","东野","少正","屠岸","主父","雍门","相里",
    # v3.2 扩充：汉唐魏晋世家（12 姓）
    "周生","信都","吾丘","石作","士孙","索卢","王官","章仇",
    "诸梁","祝其","仲梁","先轸",
    # v3.2 扩充：少数民族汉化复姓（13 姓）
    "尔朱","贺兰","贺拔","贺若","斛律","豆卢","乞伏","秃发",
    "沮渠","哥舒","仆固","乙弗","完颜",
]

NOBLE_SURNAMES = [
    "王","李","张","陈","杨","赵","黄","周","吴","徐",
    "孙","朱","胡","郭","何","高","罗","郑","梁","谢",
    "宋","唐","冯","于","董","萧","程","曹","袁","邓",
    "傅","沈","曾","彭","吕","苏","卢","蒋","蔡","贾",
    "丁","魏","薛","叶","阎","余","潘","杜","戴","夏"
]

ROYAL_SURNAMES = [
    "李","刘","赵","朱","姬","萧","杨","陈","王","张",
    "郭","高","柴","石","苻","慕","元","秦","冉"
]

XIAN_SURNAMES = [
    "李","叶","苏","云","洛","白","沈","萧","宋","顾",
    "楚","陆","谢","秦","唐","凌","慕","南","夏","秋",
    "华","封","任","商","冷","宁","许","林","江","柳",
    "花","杜","阮","文","游","邢","路","钟","石","简",
    "史","程","余","常","邵","岑","戚","方","梁","孟"
]

WUSHU_SURNAMES = [
    "李","赵","关","张","刘","曹","孙","周","吴","郭",
    "岳","秦","韩","杨","薛","程","徐","常","苏","马",
    "黄","许","谢","霍","陆","陈","宋","廖","陶","田",
    "邓","凌","甘","夏","沈","范","颜","石","白","文",
    "武","元","任","戚","郑","冯","邢","钟","史","高"
]


# ═══════════════════════════════════════════════
# § 2  8 大专题字库
# ═══════════════════════════════════════════════

THEMES = {
    # ── 网感·时尚·年轻 ──
    "trendy": {
        "label": "网感时尚",
        "surnames": COMMON_SURNAMES,
        "compound_ratio": 0.05,
        "pools_male": [
            list("宇泽轩昊霖睿禹奕辰宸晗屹俊珩栎屹凡瀚朗聿珅弈骁"),
            list("洲屿珂珩珅屹屿辰泽宇岑宥晞屹珩策骋"),
        ],
        "pools_female": [
            list("柠橘桃樱茉栀桉檬柚榕梨柑桐"),
            list("溪云初棠桐语予知念念宁栖迟眠沁"),
        ],
    },
    # ── 达官贵人·贵气·世家 ──
    "noble": {
        "label": "达官贵人",
        "surnames": NOBLE_SURNAMES,
        "compound_ratio": 0.15,
        "pools_male": [
            list("卿侯伯仲甫公君相宰丞辅翼佐尹牧"),
            list("琮璋珩琅璞珏琦琛瓒琰瑀璘瑄琚璟瑨璜"),
            list("宏巍恢浩博丰隆盛昌泰洪浚渤瀚鸿昶恺懿"),
            list("德礼诚毅敬恕让谦慎恪儒彦杰俊贤仁悌恭"),
            list("曜煜炜燿晖昱昭晗昕晏晋景璨烨晟晔曦"),
        ],
        "pools_female": [
            list("瑶璇琼珂珏璎珞璆瑗琬琚璐瑚琳璟琅瑄璘琀"),
            list("仪雅嫣婉娴静端肃慎惠敏慧淑懿娟姱姝妍妤"),
            list("淑贞娴慧蕴蓉蕙茜蕊菡萱薇嫒媛嫱嬛姮姬"),
            list("绫绮缨纨绡缃绯绛绣绢缎锦绦缛"),
            list("珠琚琅瑚瑄瑗璆翠翡钿钗环璎"),
        ],
    },
    # ── 皇女公主·帝王家 ──
    "royal": {
        "label": "皇女公主",
        "surnames": ROYAL_SURNAMES,
        "compound_ratio": 0.30,
        "pools_female": [
            list("瑄璇璟琪琬琰璘璨琀瑨璆璜琮璋珩瑀琚瑚琳琥"),
            list("徽懿仪肃雍穆端雅慧惠柔恭静娴嘉令"),
            list("兰蕙蘅荷莲菡萱薇蓉菊桂蕊茗蔷茜"),
            list("姬嬛嫱嫒媛娘娥妤娆嫣姮姱姝"),
            list("璨烨焕炫晖曦晔晟焱"),
        ],
        "pools_male": [
            list("玄泓昱曜煜昊晗昶弘澈渊瑧珏琮璋昭"),
            list("承祐钦宸奕勋辰麟骏禹嵩胤钦"),
        ],
    },
    # ── 仙风道骨·清雅脱俗 ──
    "xian": {
        "label": "仙风道骨",
        "surnames": XIAN_SURNAMES,
        "compound_ratio": 0.15,
        "pools_male": [
            list("云鹤松竹梅柏桐桦榆杉楠梧"),
            list("玄真朴虚元素清微冲默静逸超远悠旷朗澹泊淡宁恒恬"),
            list("琮璋珩琅璞珏琦琛瓒琰瑀璘瑄琚璟瑨"),
            list("樵渔隐归栖闲漫舒放游散"),
            list("寒孤独离归远别梦觉念忆素朴古禅悟尘"),
        ],
        "pools_female": [
            list("云雾露霜雪霓虹霞岚烟霭雯絮"),
            list("兰菊梅莲竹荷蕙芷蘅苓茵茜蓉蕊茗苹萱薇"),
            list("瑶璇琼珂珏璎珞璆瑗琬琚璐瑚琳璟"),
            list("清素真雅逸淡泊静湛漪溪汀渌泠泫澄澹娴婉"),
            list("筝琴筠箫笙韶歌语音律颂"),
        ],
    },
    # ── 古风武将·侠客 ──
    "wushu": {
        "label": "古风武将",
        "surnames": WUSHU_SURNAMES,
        "compound_ratio": 0.20,
        "pools_male": [
            list("戟钺锏铁铠戈剑锋刃刀矛"),
            list("骁骥豹彪犀鲸鹰隼罴貅"),
            list("岳嵩峻岭崟岚崖海洲峰"),
            list("烽燃烈煌璨炜曦昭曜熠"),
            list("骁勇烈猛骥骏刚毅忠义威震"),
        ],
        "pools_female": [
            list("锋刃銮珏璜璇琚珂瑶璟"),
            list("凰龙隼燕鹰翎羽翾"),
            list("荷蕙菊芷竹芸兰"),
            list("昱昭晞曙璨焱炜"),
            list("谋略策御慧惠毅"),
        ],
    },
    # ── 甜美·初恋·JK ──
    "sweet": {
        "label": "甜美初恋",
        "surnames": COMMON_SURNAMES,
        "compound_ratio": 0.05,
        "pools_female": [
            list("希依琪琦绮溪熙曦栀芷祺祈奇琴筝伶玲铃凌菱霓妮怡宜仪漪薇微"),
            list("苏舒菀雨羽语瑜俞愉予妤芋素芙菲珠竹初橘菊柚姝纾"),
            list("樱桃杏梨莓桂茉莉蕊薇荷莲兰梅菊桉栀"),
            list("糖蜜甜暖软柔萌喵咪橙檬"),
        ],
        "pools_male": [],
    },
    # ── 出道·明星·艺人感 ──
    "debut": {
        "label": "出道明星",
        "surnames": COMMON_SURNAMES,
        "compound_ratio": 0.05,
        "pools_male": [
            list("星辰曦煜昱璨烨煌炫熠晗晞晏昶"),
            list("凛冽霜影夜零空玥珞珏璃"),
            list("朗阳明亮光耀灿煌"),
            list("俊逸昊宇轩珩珅奕臻"),
        ],
        "pools_female": [
            list("星曦璇瑶琪琦璟煜烨昱曜辉旭昕晗澈"),
            list("凌凛冷冰霜雪影夜零玥珞珏璃铃玲琳霖菱绫"),
            list("晴朗阳明亮光耀灿璨煌炫焰"),
            list("雅韵婷娜婉婕媛嫣妍嫣娅"),
        ],
    },
    # ── 文艺·古典·诗意 ──
    "literary": {
        "label": "文艺古典",
        "surnames": COMMON_SURNAMES,
        "compound_ratio": 0.08,
        "pools_male": [
            list("砚墨简史册章书翰笔简牍编"),
            list("清远怀慕怀远之知谦逊温良"),
            list("竹松梅桐柏檀桂"),
            list("彦俊儒文彬彣彰"),
        ],
        "pools_female": [
            list("砚墨书简卷笺诗词赋辞韵"),
            list("兰蕙芷蘅荷菊竹梅"),
            list("清素雅逸淡湛湘漪溪"),
            list("婉宁柔慧慕思念清和"),
        ],
    },
    # ── 数字人·虚拟偶像（v3.1）──
    # 规则：姓氏 100% 取自完整复姓池，强制双名 → 全名固定四字
    "digital": {
        "label": "数字人",
        "surnames": COMPOUND_SURNAMES_FULL,
        "compound_ratio": 1.0,          # 只用复姓
        "no_single_name": True,          # 强制双名，全名四字
        "pools_male": [
            # 光曜感：数字神明 / 全息偶像
            list("曜曦珩珅昀晏旭煜晗昭晟"),
            # 冷冽感：未来战神 / 机甲气场
            list("夜凛烬离冥渊霄阆川霄"),
            # 墨白感：东方赛博 / 山水全息
            list("墨白玄素岚辰宇澈书棋琴"),
            # 珍异感：稀有辨识度
            list("琛珏琮璞璆翎鹤泠聿弈策"),
        ],
        "pools_female": [
            # 甜灵感：虚拟歌姬 / 猫系女友
            list("璃玥樱汐雪铃音梦兮萌茜"),
            # 清冷感：AI 神女 / 月系美人
            list("月霜星泠语浅宁晚棠湘蘅"),
            # 华彩感：全息舞台 / 千面偶像
            list("瑶璇琼珂璎珞绫绮绾纨黛"),
            # 珍异感：稀有辨识度
            list("珏琀翾菡菱桉栀栾虔窈妤"),
        ],
    },
}


# ═══════════════════════════════════════════════
# § 3  自然语言 → 主题码 映射
# ═══════════════════════════════════════════════

# 关键词 → 主题码
KEYWORD_MAP = [
    # (关键词列表, 主题码)
    (["网感","时尚","潮流","年轻","爆款","现代","小红书","ins"], "trendy"),
    (["贵气","达官","贵人","世家","名门","官宦","豪门","显赫","望族","朱门"], "noble"),
    (["皇","公主","帝王","皇室","皇家","帝","后","嫡","太子","王爷","郡主","格格"], "royal"),
    (["仙","道","脱俗","出尘","清雅","仙风","仙气","缥缈","云海","隐"], "xian"),
    (["武将","将军","侠","剑","刀","江湖","武","沙场","戎","军"], "wushu"),
    (["甜","可爱","初恋","少女","jk","软","萌","嗲","乖巧","甜妹"], "sweet"),
    (["出道","明星","艺人","偶像","爱豆","网红","主播","流量"], "debut"),
    (["文艺","古典","诗","书香","典雅","雅","书卷","儒","古风"], "literary"),
    (["数字人","数字偶像","虚拟人","虚拟偶像","虚拟主播","vup","vtuber","中之人"], "digital"),
]

# 性别关键词
MALE_HINT = ["男","男生","男孩","少年","男宝","公子","小子","儿子","男娃","boy","男性"]
FEMALE_HINT = ["女","女生","女孩","女宝","少女","小姐","千金","闺女","女娃","女儿","girl","女性"]


def parse_query(query: str) -> dict:
    """从自然语言里抽出：主题、性别、数量"""
    q = query.lower()

    # 主题
    theme = None
    for keywords, code in KEYWORD_MAP:
        for kw in keywords:
            if kw in q:
                theme = code
                break
        if theme:
            break
    theme = theme or "trendy"

    # 数量
    count = 20
    m = re.search(r"(\d+)\s*[个位]?", query)
    if m:
        count = min(max(int(m.group(1)), 1), 100)

    # 性别（"男女各"/"不限"类表述不锁定单性别，走 auto 混合池）
    gender = "auto"
    if any(kw in q for kw in ["男女各", "男女生", "男孩女孩", "男宝女宝", "男女宝宝",
                              "男女不限", "不限男女", "不限性别", "性别不限",
                              "男女均可", "男女都行", "男女都要", "混合"]):
        return {"theme": theme, "gender": "auto", "count": count}
    for kw in FEMALE_HINT:
        if kw in q:
            gender = "female"
            break
    if gender == "auto":
        for kw in MALE_HINT:
            if kw in q:
                gender = "male"
                break

    return {"theme": theme, "gender": gender, "count": count}


# ═══════════════════════════════════════════════
# § 4  核心生成
# ═══════════════════════════════════════════════

def _score(surname: str, given_chars: List[str]):
    """返回 (总格, 评分, 笔画dict) 或 None（总格凶）"""
    given = "".join(given_chars)
    try:
        r = calc_wuge(surname, given)
    except Exception:
        return None
    wg = r["wuge"]
    if wg["总格"]["jixiong"] != "吉":
        return None
    ji_count = sum(1 for k in ["天格","人格","地格","外格","总格"] if wg[k]["jixiong"] == "吉")
    score = 70 + ji_count * 5
    return wg["总格"]["number"], score, r["strokes"]


def _format(surname: str, given_chars: List[str], score: int, zong: int, theme_label: str, strokes: dict) -> str:
    # 整串转繁后再逐字拆，避免多音字在复姓中误转（如"秃发"的"发"应作"髮"15画而非"發"12画）
    trad_sur = to_traditional(surname)
    trad_given = to_traditional("".join(given_chars))
    parts = []
    for i, ch in enumerate(surname):
        parts.append(f"{ch}({_stroke_of(trad_sur[i], strokes)})")
    for i, ch in enumerate(given_chars):
        parts.append(f"{ch}({_stroke_of(trad_given[i], strokes)})")
    strokes_str = "+".join(parts)
    full = surname + "".join(given_chars)
    return f"【{full}】风格:{theme_label} 笔画:{strokes_str} 评分:{score} (总格:{zong}-吉)"


def generate(
    theme: str = "trendy",
    gender: str = "auto",
    count: int = 20,
    surname: Optional[str] = None,
    max_attempts: int = 20000,
) -> List[str]:
    """核心生成引擎"""
    if theme not in THEMES:
        theme = "trendy"
    conf = THEMES[theme]

    # 字库选择
    if gender == "female" and conf.get("pools_female"):
        pools = conf["pools_female"]
    elif gender == "male" and conf.get("pools_male"):
        pools = conf["pools_male"]
    else:
        pools = (conf.get("pools_male") or []) + (conf.get("pools_female") or [])
    if not pools:
        pools = [list("宇泽轩昊霖睿禹奕辰宸")]

    surnames = conf["surnames"]
    compound_ratio = conf.get("compound_ratio", 0.1)

    results = {}
    for _ in range(max_attempts):
        if len(results) >= count * 4:
            break
        # 姓氏（compound_ratio>=1.0 表示 surnames 本身就是复姓池，直接取）
        if surname:
            sur = surname
        elif compound_ratio >= 1.0:
            sur = random.choice(surnames)
        elif random.random() < compound_ratio:
            sur = random.choice(COMPOUND_SURNAMES)
        else:
            sur = random.choice(surnames)
        # 单双名（20% 单名，80% 双名；digital 主题强制双名→全名四字）
        if random.random() < 0.2 and not conf.get("no_single_name", False):
            chars = [random.choice(random.choice(pools))]
        else:
            p1 = random.choice(pools)
            p2 = random.choice(pools)
            c1 = random.choice(p1)
            c2 = random.choice(p2)
            if c1 == c2:
                continue
            chars = [c1, c2]
        if sur[-1] in chars:
            continue
        r = _score(sur, chars)
        if not r:
            continue
        zong, score, strokes = r
        line = _format(sur, chars, score, zong, conf["label"], strokes)
        key = line.split("】")[0]
        if key not in results or results[key][0] < score:
            results[key] = (score, line)

    sorted_out = sorted(results.values(), key=lambda x: -x[0])
    return [line for _, line in sorted_out[:count]]


# ═══════════════════════════════════════════════
# § 5  傻瓜入口
# ═══════════════════════════════════════════════

def smart_generate(query: str = "", surname: Optional[str] = None, count: Optional[int] = None) -> str:
    """
    傻瓜入口：一句自然语言 → 一批总格为吉的名字

    Examples:
      smart_generate("来30个贵气的男宝宝名字")
      smart_generate("50个甜美的女生名字")
      smart_generate("仙风道骨的男名20个")
      smart_generate("皇女公主的名字30个")
      smart_generate("古风武将女名60个")
      smart_generate("网感女名", count=100)
    """
    parsed = parse_query(query)
    if count is not None:
        parsed["count"] = count

    lines = generate(
        theme=parsed["theme"],
        gender=parsed["gender"],
        count=parsed["count"],
        surname=surname,
    )

    theme_label = THEMES[parsed["theme"]]["label"]
    gender_label = {"male": "男", "female": "女", "auto": "不限性别"}[parsed["gender"]]
    header = (
        f"════════════════════════════════════════════════════════════════\n"
        f"  ✦  {theme_label} · {gender_label} · {len(lines)} 个  ✦\n"
        f"════════════════════════════════════════════════════════════════"
    )
    body = "\n".join(f"{i:2d}. {line}" for i, line in enumerate(lines, 1))
    return f"{header}\n{body}"


# ═══════════════════════════════════════════════
# § 6  命令行入口
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "来20个网感的女生名字"
    print(smart_generate(query))
