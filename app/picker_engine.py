"""挑码助手引擎: /api/filter 的规则交集计算。

规则与 macaujc 挑码助手一致 (picker_rules.md):
- 生肖/家野/五行 随年份(用「今天」的公历日查阴历年; 五行按公历年+30 折返)
- 波色/单双/大小/头/尾 固定表
- 单选组 big_small/odd_even: 服务端强制单选语义, 传多值时按覆盖处理(取全部值集合,
  等价于不做该组过滤——契约注明"交集为空的语义按覆盖处理")
- 其余为多选组: 组内 children 求并集
- 结果 = 各已选组 ruleActiveItem 的交集, 去重后按数值升序
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set

from . import zodiac_wuxing as zw

ALL_NUMBERS = list(range(1, 50))

# 生肖组随年槽位: 槽位0=当年生肖, 槽位k号码=k+1,k+13,k+25,k+37 (k=0 含 49), 逐年倒退
FAMILY = ("牛", "馬", "羊", "雞", "狗", "豬")  # 家禽
WILD = ("兔", "虎", "鼠", "猴", "蛇", "龍")    # 野獸

WAVE_GROUPS = {"红": "红", "蓝": "蓝", "绿": "绿"}  # 兼容简繁常见写法


def _today() -> str:
    return datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")


def _norm_num(n) -> Optional[int]:
    try:
        v = int(str(n).strip().lstrip("0") or "0")
    except (TypeError, ValueError):
        return None
    return v if 1 <= v <= 49 else None


def _pad(nums) -> List[str]:
    out = set()
    for n in nums:
        if isinstance(n, int):
            out.add(f"{n:02d}")
        else:
            s = str(n).strip()
            out.add(s if len(s) == 2 else f"{int(s):02d}")
    return sorted(out)


def _num_key_set(values) -> Set[int]:
    """输入值(两位串或 int) → int 集合。"""
    out: Set[int] = set()
    for v in values or []:
        n = _norm_num(v)
        if n is not None:
            out.add(n)
    return out


def zodiac_numbers(today: Optional[str] = None) -> Dict[str, Set[int]]:
    """当年生肖 → 号码集合 (随年份槽位公式)。"""
    d = today or _today()
    branch = zw.lunar_branch_index(d)
    table = zw.zodiac_table(branch)
    out: Dict[str, Set[int]] = {}
    for n, z in table.items():
        out.setdefault(z, set()).add(n)
    return out


def wuxing_numbers(year: Optional[int] = None) -> Dict[str, Set[int]]:
    """该年五行 → 号码集合。"""
    y = year or datetime.now(timezone(timedelta(hours=8))).year
    table = zw.wuxing_table_for_year(y)
    return {element: set(nums) for element, nums in table.items()}


# 波色常量 (config 中为 set of int) — 置于模块顶部使用之前
from .config import WAVE_RED as config_RED  # noqa: E402
from .config import WAVE_BLUE as config_BLUE  # noqa: E402
from .config import WAVE_GREEN as config_GREEN  # noqa: E402


def group_numbers(group: str, values: List, ctx: Dict) -> Set[int]:
    """单个筛选组 → 号码 int 集合(组内并集)。未知组返回 None 由调用方忽略。"""
    if group in ("zodiac", "生肖"):
        zmap = ctx["zodiac"]
        out: Set[int] = set()
        for v in values:
            v = str(v).strip()
            # 兼容简体输入: 鼠牛虎兔龙蛇马羊猴鸡狗猪
            v = v.translate(str.maketrans("龙蛇马羊猴鸡狗猪兔", "龍蛇馬羊猴雞狗豬兔"))
            if v in zmap:
                out |= zmap[v]
        return out
    if group in ("six_conflict", "六冲", "六沖"):
        # 六沖(挑码助手 6 鈕): 馬鼠冲、牛羊冲、猴虎冲、兔雞冲、龍狗冲、豬蛇冲
        # 生肖環上相隔 6 位; 选一生肖 = 其本身 + 对冲生肖 的号码并集
        zmap = ctx["zodiac"]
        conflict = {"馬": "鼠", "牛": "羊", "猴": "虎", "兔": "雞", "龍": "狗", "豬": "蛇"}
        conflict.update({v: k for k, v in conflict.items()})
        out = set()
        for v in values:
            v = str(v).strip().translate(str.maketrans("龙蛇马羊猴鸡狗猪兔", "龍蛇馬羊猴雞狗豬兔"))
            if v in conflict:
                out |= zmap.get(v, set()) | zmap.get(conflict[v], set())
        return out
    if group in ("wave", "wave_color", "波色"):
        out = set()
        for v in values:
            v = str(v).strip()
            if v in WAVE_GROUPS:
                w = WAVE_GROUPS[v]
                nums = {"红": config_RED, "蓝": config_BLUE, "绿": config_GREEN}[w]
                out |= nums
        return out
    if group in ("big_small", "大小"):
        out = set()
        for v in values:
            v = str(v).strip()
            if v in ("大", "大数"):
                out |= {n for n in ALL_NUMBERS if n >= 25}
            elif v in ("小", "小数"):
                out |= {n for n in ALL_NUMBERS if n <= 24}
        return out
    if group in ("odd_even", "单双"):
        out = set()
        for v in values:
            v = str(v).strip()
            if v in ("单", "单数", "奇"):
                out |= {n for n in ALL_NUMBERS if n % 2 == 1}
            elif v in ("双", "双数", "偶"):
                out |= {n for n in ALL_NUMBERS if n % 2 == 0}
        return out
    if group in ("tail", "尾", " tails".strip()):
        out = set()
        for v in values:
            try:
                t = int(str(v).strip())
            except (TypeError, ValueError):
                continue
            if 0 <= t <= 9:
                out |= {n for n in ALL_NUMBERS if n % 10 == t}
        return out
    if group in ("head", "头"):
        out = set()
        for v in values:
            try:
                h = int(str(v).strip())
            except (TypeError, ValueError):
                continue
            if 0 <= h <= 4:
                out |= {n for n in ALL_NUMBERS if n // 10 == h}
        return out
    if group in ("wuxing", "五行"):
        wmap = ctx["wuxing"]
        out = set()
        for v in values:
            v = str(v).strip()
            if v in wmap:
                out |= wmap[v]
        return out
    if group in ("family_wild", "家野"):
        zmap = ctx["zodiac"]
        out = set()
        for v in values:
            v = str(v).strip()
            if v in ("家", "家禽", "家畜"):
                for z in FAMILY:
                    out |= zmap.get(z, set())
            elif v in ("野", "野兽"):
                for z in WILD:
                    out |= zmap.get(z, set())
        return out
    if group in ("he_sum", "合数", "合数单双", "合数大小"):
        out = set()
        for v in values:
            s = str(v).strip()
            if s in ("单", "合单"):
                out |= {n for n in ALL_NUMBERS if zw.he_sum_of(n) % 2 == 1}
            elif s in ("双", "合双"):
                out |= {n for n in ALL_NUMBERS if zw.he_sum_of(n) % 2 == 0}
            elif s in ("大", "合大"):
                out |= {n for n in ALL_NUMBERS if zw.he_sum_of(n) >= 7}
            elif s in ("小", "合小"):
                out |= {n for n in ALL_NUMBERS if zw.he_sum_of(n) <= 6}
            else:
                try:
                    hv = int(s)
                except (TypeError, ValueError):
                    continue
                if 2 <= hv <= 13:
                    out |= {n for n in ALL_NUMBERS if zw.he_sum_of(n) == hv}
        return out
    return set()  # 未知组: 空集合(不参与过滤由 apply_groups 决定)


def apply_groups(groups: Optional[Dict]) -> List[str]:
    """契约 #6: 各组并集 → 组间交集, 升序两位字符串。

    单选组 big_small/odd_even: 传多值按覆盖处理(组仍生效, 值取其全部声明的并集)。
    未选任何有效组 → 全部 49 号。
    """
    ctx = {
        "zodiac": zodiac_numbers(),
        "wuxing": wuxing_numbers(),
    }
    result: Optional[Set[int]] = None
    if isinstance(groups, dict):
        for gname, values in groups.items():
            if not isinstance(values, (list, tuple)):
                values = [values]
            nums = group_numbers(str(gname), list(values), ctx)
            if not nums:
                continue  # 空/未知组不参与(契约: 空选组不参与, 全 49 号)
            result = nums if result is None else (result & nums)
    if result is None:
        result = set(ALL_NUMBERS)
    return _pad(sorted(result))


def union_view(groups: Optional[Dict]) -> Dict[str, List[str]]:
    """契约 #6 的 union 字段: 每组各自展开的号码并集(升序)。"""
    ctx = {
        "zodiac": zodiac_numbers(),
        "wuxing": wuxing_numbers(),
    }
    out: Dict[str, List[str]] = {}
    if isinstance(groups, dict):
        for gname, values in groups.items():
            if not isinstance(values, (list, tuple)):
                values = [values]
            nums = group_numbers(str(gname), list(values), ctx)
            out[str(gname)] = _pad(sorted(nums))
    return out
