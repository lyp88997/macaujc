"""号码属性派生引擎。

严格按 tasks/api_contract.md「属性派生规则」+ macaujc-analysis/context/picker_rules.md 实现:
- 波色  = 官方固定表 (config.WAVE_*)
- 生肖  = 槽位公式(槽位0=当年生肖, 逐年倒退; 槽位k号码=k+1,k+13,k+25,k+37, k=0含49),
          年份按开奖日查 lunar_table_1900_2100.json(start=正月初一公历日, branch=地支序0-11鼠起),
          date < start 归上一年; cycle=鼠牛虎兔龍蛇馬羊猴雞狗豬 (繁体)
- 五行  = 按公历年 t, while t<1976: t+=30; while t>2025: t-=30 → wuxing_table.json[t]
          (简化声明: 五行按公历年而非农历年, 春节前后数日可能差一档)
- 大小  = 01-24 小 / 25-49 大; 单双 = 奇/偶; 头 = 十位(0-4); 尾 = 个位(0-9);
          合数 = 十位+个位 (2-13)

对外主入口: attrs_for_number(num, open_date, calendar_year) → dict
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from . import config

ZODIAC_CYCLE = "鼠牛虎兔龍蛇馬羊猴雞狗豬"  # 地支序 0-11, 鼠起
# lunar 表 branch 字段以 馬=0 起序(实测: 2020鼠=6, 2025蛇=11, 2026馬=0, 相邻年+1 全表一致),
# 换算标准地支序(鼠=0): 地支序 = (branch + 6) % 12
BRANCH_OFFSET = 6

# 五行按公历年取表的简化声明 (api_contract.md 要求文档注明)
WUXING_NOTE = "五行按公历年(非农历年)取表, 春节前后数日可能差一档"

_LUNAR: Optional[List[dict]] = None
_WUXING: Optional[dict] = None
_LOCK = None  # 延迟初始化线程锁


def _ensure_tables() -> None:
    global _LUNAR, _WUXING, _LOCK
    if _LUNAR is not None and _WUXING is not None:
        return
    if _LOCK is None:
        import threading

        _LOCK = threading.Lock()
    with _LOCK:
        if _LUNAR is None:
            _LUNAR = config.load_lunar_table()
        if _WUXING is None:
            _WUXING = config.load_wuxing_table()


# ---------- 波色 ----------

def wave_of(num: int) -> str:
    if num in config.WAVE_RED:
        return "红"
    if num in config.WAVE_BLUE:
        return "蓝"
    return "绿"


# ---------- 生肖 ----------

def _lunar_idx(date_str: str) -> int:
    """开奖公历日 → lunar 表行号。idx = Y-1900, 若 date < 该阴历年正月初一(start) 归上一年。"""
    _ensure_tables()
    y = int(date_str[0:4])
    idx = max(0, min(y - 1900, len(_LUNAR) - 1))
    # 'YYYY-MM-DD HH:MM:SS' 与 'YYYY-MM-DD' 字典序比较安全
    if date_str < _LUNAR[idx]["start"]:
        idx = max(0, idx - 1)
    return idx


def lunar_branch_index(date_str: str) -> int:
    """公历日 → 标准地支序(0=鼠..11=猪)。"""
    _ensure_tables()
    return (int(_LUNAR[_lunar_idx(date_str)]["branch"]) + BRANCH_OFFSET) % 12


def zodiac_year_for_date(date_str: str) -> int:
    """返回 1900..2099 的阴历年序号(供缓存 key)。"""
    return 1900 + _lunar_idx(date_str)


def zodiac_of(num: int, branch: int) -> str:
    """槽位公式: zodiac(n) = cycle[(branch - (n-1)) mod 12]。

    等价于槽位0=当年生肖、槽位k号码=k+1,k+13,k+25,k+37(k=0含49)、逐年倒退。
    """
    return ZODIAC_CYCLE[(branch - (num - 1)) % 12]


def zodiac_table(branch: int) -> Dict[int, str]:
    """49 号 → 生肖 的完整映射表(给定当年地支序), picker 引擎用。"""
    t: Dict[int, str] = {}
    for k in range(12):
        z = ZODIAC_CYCLE[(branch - k) % 12]
        nums = [k + 1, k + 13, k + 25, k + 37]
        if k == 0:
            nums.append(49)
        for n in nums:
            t[n] = z
    return t


# ---------- 五行 ----------

def wuxing_norm_year(year: int) -> int:
    t = year
    while t < 1976:
        t += 30
    while t > 2025:
        t -= 30
    return t


def wuxing_of(num: int, calendar_year: int) -> str:
    _ensure_tables()
    row = _WUXING[str(wuxing_norm_year(calendar_year))]
    for element, payload in row.items():
        if num in payload["numbers"]:
            return element
    return ""  # 不应发生(表覆盖 1-49)


def wuxing_table_for_year(year: int) -> Dict[str, List[str]]:
    """picker 引擎用: 该年五行 → 零填充号码列表。"""
    _ensure_tables()
    row = _WUXING[str(wuxing_norm_year(year))]
    return {
        element: [f"{n:02d}" for n in payload["numbers"]]
        for element, payload in row.items()
    }


# ---------- 简单派生 ----------

def odd_even_of(num: int) -> str:
    return "单" if num % 2 == 1 else "双"


def big_small_of(num: int) -> str:
    return "大" if num >= 25 else "小"  # 01-24 小 / 25-49 大


def head_of(num: int) -> int:
    return num // 10  # 十位 0-4


def tail_of(num: int) -> int:
    return num % 10  # 个位 0-9


def he_sum_of(num: int) -> int:
    return (num // 10) + (num % 10)  # 2-13


def attrs_for_number(num: int, open_date: str = "", calendar_year: int = 0) -> dict:
    """单号码全属性。open_date='YYYY-MM-DD...' 用于生肖阴历年定位。

    calendar_year 优先于从 open_date 解析(五行用公历年); 均缺省时用今天。
    """
    _ensure_tables()
    if not calendar_year:
        calendar_year = int(open_date[0:4]) if open_date else datetime.now().year
    if not open_date:
        open_date = datetime.now().strftime("%Y-%m-%d")
    branch = lunar_branch_index(open_date)
    return {
        "wave": wave_of(num),
        "zodiac": zodiac_of(num, branch),
        "wuxing": wuxing_of(num, calendar_year),
        "odd_even": odd_even_of(num),
        "big_small": big_small_of(num),
        "head": head_of(num),
        "tail": tail_of(num),
        "he_sum": he_sum_of(num),
    }
