"""统计分析引擎: /api/stats 与 /api/omit 的计算核心。

- stats: window 期窗口内某维度各 key 的 count/rate/last_expect/omission,
  key 全域返回(count=0 也出现), 按 count 降序。
- omit: 各维度 omission(距上次出现期数) / max_omission / avg_omission (max/avg 基于全部历史)。

维度 key 语义(normal_* 维度的 same 逻辑: 号码取平码六个号码的全体):
  special_number = 特码号码(01-49)   normal_number = 平码号码(01-49)
  special_wave   = 特码波色(红/蓝/绿) normal_wave   = 平码波色
  ... 其余 zodiac/wuxing/odd_even/big_small/head/tail 同理。
"""

from __future__ import annotations

from typing import Dict, List, Optional

from . import config, db, zodiac_wuxing as zw

# 维度名 → 提取函数名 (属性键)
DIM_KEYS = {
    "number": "number",
    "wave": "wave",
    "zodiac": "zodiac",
    "wuxing": "wuxing",
    "odd_even": "odd_even",
    "big_small": "big_small",
    "head": "head",
    "tail": "tail",
    "he_sum": "he_sum",
}


def _norm_number(n: int) -> str:
    return f"{n:02d}"


def _full_domain(dim: str) -> List:
    """维度全域 key (count=0 也要出现)。"""
    if dim == "number":
        return [_norm_number(i) for i in range(1, 50)]
    if dim == "wave":
        return ["红", "蓝", "绿"]
    if dim == "zodiac":
        return list(zw.ZODIAC_CYCLE)  # 鼠牛虎兔龍蛇馬羊猴雞狗豬
    if dim == "wuxing":
        return ["金", "木", "水", "火", "土"]
    if dim == "odd_even":
        return ["单", "双"]
    if dim == "big_small":
        return ["大", "小"]
    if dim == "head":
        return [0, 1, 2, 3, 4]
    if dim == "tail":
        return list(range(10))
    if dim == "he_sum":
        return list(range(1, 14))  # 01-09 合数=面值(实测表), 全域 1-13
    return []


def _number_attr(num: int, dim: str, open_date: str, calendar_year: int):
    """号码 → 指定维度 key。number 维度返回零填充号码本身。"""
    if dim == "number":
        return _norm_number(num)
    if dim == "wave":
        return zw.wave_of(num)
    if dim == "zodiac":
        return zw.zodiac_of(num, zw.lunar_branch_index(open_date))
    if dim == "wuxing":
        return zw.wuxing_of(num, calendar_year)
    if dim == "odd_even":
        return zw.odd_even_of(num)
    if dim == "big_small":
        return zw.big_small_of(num)
    if dim == "head":
        return zw.head_of(num)
    if dim == "tail":
        return zw.tail_of(num)
    if dim == "he_sum":
        return zw.he_sum_of(num)
    return None


def draw_numbers(draw: Dict, scope: str) -> List[int]:
    """scope=special → [特码]; scope=normal → 六个平码(原始顺序)。"""
    if scope == "special":
        return [int(draw["special"])]
    return [int(draw[f"n{i}"]) for i in range(1, 7)]


def resolve_dim(dim_param: str) -> Optional[tuple]:
    """'special_tail' → ('special','tail'); 非法返回 None。"""
    for scope in ("special", "normal"):
        prefix = scope + "_"
        if dim_param.startswith(prefix):
            dim = dim_param[len(prefix):]
            if dim in DIM_KEYS:
                return (scope, dim)
    return None


def calc_stats(conn, scope: str, dim: str, window: int) -> Dict:
    """窗口统计。返回契约 #3 结构。"""
    draws = db.draws_asc_limit(conn, window)
    if not draws:
        return {"window": 0, "from_expect": None, "to_expect": None, "items": []}

    counts: Dict = {k: 0 for k in _full_domain(dim)}
    last_expect: Dict = {}
    for d in draws:  # 升序遍历 → 后写覆盖即最新出现期
        open_date = str(d["open_time"])[:10]
        year = int(open_date[:4])
        for num in draw_numbers(d, scope):
            key = _number_attr(num, dim, open_date, year)
            if key is None:
                continue
            counts[key] = counts.get(key, 0) + 1
            last_expect[key] = d["expect"]

    # 遗漏 = 距最近一次出现的期数(窗口末尾倒序找, 没出现过则 = 窗口长度)
    recent_desc = list(reversed(draws))  # 新→旧
    omission: Dict = {}
    for key in counts:
        om = None
        for i, d in enumerate(recent_desc):
            open_date = str(d["open_time"])[:10]
            year = int(open_date[:4])
            for num in draw_numbers(d, scope):
                if _number_attr(num, dim, open_date, year) == key:
                    om = i
                    break
            if om is not None:
                break
        if om is None:
            om = len(draws)  # 窗口内从未出现
        omission[key] = om

    items = [
        {
            "key": k,
            "count": counts[k],
            "rate": round(counts[k] / len(draws), 4) if len(draws) else 0.0,
            "last_expect": last_expect.get(k),
            "omission": omission[k],
        }
        for k in counts
    ]
    items.sort(key=lambda x: (-x["count"], str(x["key"])))
    return {
        "window": len(draws),
        "from_expect": draws[0]["expect"],
        "to_expect": draws[-1]["expect"],
        "items": items,
    }


def _history_keys_and_gaps(draws_asc: List[Dict], scope: str, dim: str) -> Dict:
    """全部历史扫描 → {key: {"last_seen_idx": int|None, "gaps": [相邻出现间隔...]}}。

    gap 定义: 两次出现之间隔的期数(不含出现当期)。
    """
    positions: Dict = {}
    for idx, d in enumerate(draws_asc):
        open_date = str(d["open_time"])[:10]
        year = int(open_date[:4])
        for num in draw_numbers(d, scope):
            key = _number_attr(num, dim, open_date, year)
            if key is None:
                continue
            positions.setdefault(key, []).append(idx)
    out: Dict = {}
    for key, pos in positions.items():
        gaps = [pos[i] - pos[i - 1] - 1 for i in range(1, len(pos))]
        out[key] = {
            "last_seen_idx": pos[-1] if pos else None,
            "gaps": gaps,
            "appearances": len(pos),
        }
    return out


def calc_omit(conn, scope: str) -> Dict:
    """遗漏分析(契约 #4)。omission=距上次出现的期数; max/avg 基于全部历史。"""
    dims = ["number", "wave", "zodiac", "tail", "head", "wuxing"]
    result: Dict[str, List[Dict]] = {}
    draws_asc = db.draws_asc(conn)
    n_total = len(draws_asc)
    for dim in dims:
        hist = _history_keys_and_gaps(draws_asc, scope, dim)
        domain = _full_domain(dim)
        items = []
        for key in domain:
            h = hist.get(key)
            if h and h["last_seen_idx"] is not None:
                omission = n_total - 1 - h["last_seen_idx"]
                gaps = h["gaps"] or [0]
                max_om = max(gaps)
                avg_om = round(sum(gaps) / len(gaps), 2) if gaps else 0.0
            else:
                # 全历史从未出现: omission=总期数, max=总期数, avg=None
                omission = n_total
                max_om = n_total
                avg_om = None
            items.append(
                {
                    "key": key,
                    "omission": omission,
                    "max_omission": max_om,
                    "avg_omission": avg_om,
                }
            )
        items.sort(key=lambda x: -x["omission"])
        result[dim] = items
    return result
