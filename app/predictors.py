"""预测/打分引擎: /api/predict 与 /api/pick 的核心。

composite 打分(总监规定, 透明可解释, 各分量归一 0..1):
  score = 40×recency加权频率(decay^age, decay=0.985, window 内) 归一
        + 30×遗漏压力 min(omission/avg, 2)/2
        + 15×维度回补(所属波色/生肖在 window 内占比低于均值程度) 归一
        + 15×日种子平滑随机(当天固定, 避免"每次刷新全变")

reasons 必须逐条对应真实计算值, 禁止编造文案。
"""

from __future__ import annotations

import hashlib
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from . import db, stats_engine, zodiac_wuxing as zw

DECAY = 0.985
W_FREQ = 40.0
W_OMIT = 30.0
W_REBOUND = 15.0
W_RANDOM = 15.0

DISCLAIMER = "统计分析仅供参考,不构成任何中奖承诺"

MODES = ("composite", "hot", "cold", "omission")
SCOPES = ("special", "normal")


# ---------- 工具 ----------

def _now_utc8() -> datetime:
    return datetime.now(timezone(timedelta(hours=8)))


def today_str() -> str:
    return _now_utc8().strftime("%Y-%m-%d")


def day_seed_num(num: int, date_str: str, scope: str) -> float:
    """日种子平滑随机: 当天固定(同一号码同一日恒定), 不同号码散布 0..1。"""
    raw = f"macaujc|{date_str}|{scope}|{num}".encode("utf-8")
    digest = hashlib.sha256(raw).digest()
    val = int.from_bytes(digest[:8], "big") / float(1 << 64)
    # 平滑: 0.25 + 0.5*v → 随机分量主导但不至于过散
    return 0.25 + 0.5 * val


# ---------- 窗口特征 ----------

def _window_features(conn, scope: str, window: int):
    """一次性计算 window 内特征: 每号出现年龄/次数, 号码级 omission/avg, 波色/生肖窗口占比。"""
    draws = db.draws_asc_limit(conn, window)
    n = len(draws)
    draws_desc = list(reversed(draws))  # 新→旧
    appear_age: Dict[int, int] = {}  # num → 最近一次出现的 age(0=最近一期)
    appear_count: Dict[int, int] = {}
    for age, d in enumerate(draws_desc):
        for num in stats_engine.draw_numbers(d, scope):
            appear_age.setdefault(num, age)
            appear_count[num] = appear_count.get(num, 0) + 1

    # 号码级遗漏(max/avg 基于全部历史, 号码域专用)
    omit_items = None
    try:
        omit_items = _number_omit_map(conn, scope)
    except Exception:
        omit_items = {}
    num_omission = {k: v["omission"] for k, v in omit_items.items()}
    num_avg = {k: v["avg"] for k, v in omit_items.items()}

    # 窗口内波色/生肖占比 (special scope 用特码, normal 用全部平码)
    draws_all = draws_desc
    total_slots = 0
    wave_count: Dict[str, int] = {}
    zodiac_count: Dict[str, int] = {}
    for d in draws_all:
        open_date = str(d["open_time"])[:10]
        year = int(open_date[:4])
        for num in stats_engine.draw_numbers(d, scope):
            total_slots += 1
            w = zw.wave_of(num)
            wave_count[w] = wave_count.get(w, 0) + 1
            z = zw.zodiac_of(num, zw.lunar_branch_index(open_date))
            zodiac_count[z] = zodiac_count.get(z, 0) + 1

    return {
        "window": n,
        "appear_age": appear_age,
        "appear_count": appear_count,
        "num_omission": num_omission,
        "num_avg": num_avg,
        "wave_rate": {k: v / total_slots for k, v in wave_count.items()} if total_slots else {},
        "zodiac_rate": {k: v / total_slots for k, v in zodiac_count.items()} if total_slots else {},
        "total_slots": total_slots,
    }


def _number_omit_map(conn, scope: str) -> Dict[str, Dict]:
    """号码维度 omit(复用 stats_engine 内部逻辑, 只取 number 维度)。"""
    draws_asc = db.draws_asc(conn)
    n_total = len(draws_asc)
    positions: Dict[int, List[int]] = {}
    for idx, d in enumerate(draws_asc):
        for num in stats_engine.draw_numbers(d, scope):
            positions.setdefault(num, []).append(idx)
    out: Dict[str, Dict] = {}
    for n in range(1, 50):
        pos = positions.get(n, [])
        if pos:
            gaps = [pos[i] - pos[i - 1] - 1 for i in range(1, len(pos))]
            out[f"{n:02d}"] = {
                "omission": n_total - 1 - pos[-1],
                "max": max(gaps) if gaps else 0,
                "avg": round(sum(gaps) / len(gaps), 2) if gaps else 0.0,
            }
        else:
            out[f"{n:02d}"] = {"omission": n_total, "max": n_total, "avg": None}
    return out


# ---------- composite 打分 ----------

def composite_scores(conn, scope: str, window: int):
    """49 号全部打分。返回 (items, debug) — items 未排序。"""
    feat = _window_features(conn, scope, window)
    n_win = feat["window"]
    if n_win == 0:
        return [], feat

    wave_rates = feat["wave_rate"]
    zodiac_rates = feat["zodiac_rate"]
    wave_mean = sum(wave_rates.values()) / len(wave_rates) if wave_rates else 0.0
    zodiac_mean = sum(zodiac_rates.values()) / len(zodiac_rates) if zodiac_rates else 0.0

    # recency 加权频率: sum(decay^age) per number → 归一(除以理论最大值 = 全部 age=0)
    decay_sum: Dict[int, float] = {}
    draws_desc = db.draws_asc_limit(conn, window)
    draws_desc.reverse()  # 新→旧
    for age, d in enumerate(draws_desc):
        for num in stats_engine.draw_numbers(d, scope):
            decay_sum[num] = decay_sum.get(num, 0.0) + (DECAY ** age)
    max_decay = sum(DECAY ** age for age in range(n_win))  # 理论上界(每期都同号, 特码 scope)
    if scope == "normal":
        max_decay *= 6.0

    today = today_str()
    items = []
    for num in range(1, 50):
        key = f"{num:02d}"

        # 1) recency 加权频率 (40 分)
        ds = decay_sum.get(num, 0.0)
        freq_norm = min(1.0, ds / max_decay) if max_decay > 0 else 0.0

        # 2) 遗漏压力 (30 分)
        om = feat["num_omission"].get(key)
        avg = feat["num_avg"].get(key)
        if om is not None and avg is not None and avg > 0:
            omit_norm = min(om / avg, 2.0) / 2.0
        elif om is not None and om > 0:
            # 从未出现过的号码没有历史间隔, 用该 scope 的理论平均间隔
            # 作为基准, 避免遗漏压力被错误压成 0。
            slots = 6 if scope == "normal" else 1
            expected_avg = max(1.0, (49.0 / slots) - 1.0)
            omit_norm = min(om / expected_avg, 2.0) / 2.0
        else:
            omit_norm = 0.0

        # 3) 维度回补 (15 分): 所属波色/生肖窗口占比低于均值程度 → 归一
        w = zw.wave_of(num)
        deficit = 0.0
        if wave_mean > 0:
            deficit += max(0.0, (wave_mean - wave_rates.get(w, 0.0)) / wave_mean)
        open_date = draws_desc[0]["open_time"][:10] if draws_desc else today
        z = zw.zodiac_of(num, zw.lunar_branch_index(open_date))
        if zodiac_mean > 0:
            deficit += max(0.0, (zodiac_mean - zodiac_rates.get(z, 0.0)) / zodiac_mean)
        rebound_norm = min(1.0, deficit / 2.0)  # 波色+生肖两维, 各自最大缺口 1.0

        # 4) 日种子平滑随机 (15 分)
        rnd = day_seed_num(num, today, scope)

        score = (
            W_FREQ * freq_norm
            + W_OMIT * omit_norm
            + W_REBOUND * rebound_norm
            + W_RANDOM * rnd
        )
        items.append({"number": key, "score": score, "feat": {
            "freq_norm": freq_norm, "ds": ds,
            "omission": om, "avg": avg, "omit_norm": omit_norm,
            "wave": w, "wave_rate": wave_rates.get(w, 0.0), "wave_mean": wave_mean,
            "zodiac": z, "zodiac_rate": zodiac_rates.get(z, 0.0), "zodiac_mean": zodiac_mean,
            "rebound_norm": rebound_norm, "rnd": rnd,
            "appear_count": feat["appear_count"].get(num, 0),
        }})
    return items, feat


# ---------- reasons 生成(逐条对应真实计算值) ----------

def _fmt(x: float) -> str:
    s = f"{x:.1f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def build_reasons(num_key: str, f: Dict, scope: str, window: int) -> List[str]:
    reasons: List[str] = []
    cnt = f["appear_count"]
    if cnt > 0:
        tag = "热" if cnt >= math.ceil(window / 49 * (6 if scope == "normal" else 1) * 1.5) else "温"
        reasons.append(f"近{window}期出现{cnt}次({tag})")
    else:
        reasons.append(f"近{window}期未出现")
    om = f["omission"]
    avg = f["avg"]
    if om is not None and avg:
        ratio = om / avg if avg else 0
        if ratio >= 0.8:
            reasons.append(f"遗漏{om}期≈平均{_fmt(avg)}的回补区")
        elif ratio >= 0.5:
            reasons.append(f"遗漏{om}期, 平均间隔{_fmt(avg)}期")
        else:
            reasons.append(f"遗漏{om}期, 低于平均间隔{_fmt(avg)}期")
    else:
        reasons.append("历史无出现记录")
    wr = f["wave_rate"]
    wm = f["wave_mean"]
    if wm > 0:
        if wr < wm * 0.9:
            reasons.append(f"{f['wave']}波近{window}期偏冷")
        elif wr > wm * 1.1:
            reasons.append(f"{f['wave']}波近{window}期偏热")
        else:
            reasons.append(f"{f['wave']}波近{window}期平稳")
    return reasons


# ---------- 入口: predict ----------

def predict(conn, mode: str, scope: str, count: int, window: int) -> Dict:
    count = max(1, min(int(count), 49))
    window = max(1, min(int(window), 5000))
    items_raw, feat = composite_scores(conn, scope, window)

    if mode == "hot":
        items_raw.sort(key=lambda x: (x["feat"]["appear_count"], x["score"]), reverse=True)
    elif mode == "cold":
        items_raw.sort(key=lambda x: (x["feat"]["appear_count"], x["score"]))
    elif mode == "omission":
        items_raw.sort(key=lambda x: (-(x["feat"]["omission"] or 0), x["score"]))
    else:  # composite
        items_raw.sort(key=lambda x: -x["score"])

    items = []
    for rank, it in enumerate(items_raw[:count], 1):
        key = it["number"]
        num = int(key)
        open_date = today_str()
        attrs = {
            "wave": zw.wave_of(num),
            "zodiac": zw.zodiac_of(num, zw.lunar_branch_index(open_date)),
            "wuxing": zw.wuxing_of(num, datetime.now().year),
            "head": zw.head_of(num),
            "tail": zw.tail_of(num),
            "he": zw.he_sum_of(num),
        }
        items.append(
            {
                "rank": rank,
                "number": key,
                "score": round(it["score"], 1),
                "attrs": attrs,
                "reasons": build_reasons(key, it["feat"], scope, feat["window"]),
            }
        )
    return {
        "mode": mode,
        "scope": scope,
        "window": feat["window"],
        "generated_at": db.datetime_utc8_str(),
        "items": items,
        "disclaimer": DISCLAIMER,
    }


# ---------- 入口: pick ----------

def pick_sets(conn, count: int, pool: str, filters: Optional[Dict], window: int) -> Dict:
    """count=7: 前 6 = 平码推荐 + 最后 1 = 特码推荐(号码不重复)。

    pool=composite|hot|cold → 对应 predict 打分取池; pool=all → 49 号全集。
    filters 同 filter.groups, 先过滤池。
    """
    from . import picker_engine

    remaining = picker_engine.apply_groups(filters or {})
    pool_upper = (pool or "composite").strip().lower()
    if pool_upper == "all":
        pool_nums = sorted(int(x) for x in remaining)
        normal_nums = pool_nums
        special_nums = pool_nums
    else:
        mode = pool_upper if pool_upper in MODES else "composite"
        allowed = set(int(x) for x in remaining)
        normal_pred = predict(conn, mode, "normal", 49, window)
        special_pred = predict(conn, mode, "special", 49, window)
        normal_nums = [int(it["number"]) for it in normal_pred["items"]
                       if int(it["number"]) in allowed]
        special_nums = [int(it["number"]) for it in special_pred["items"]
                        if int(it["number"]) in allowed]
        pool_nums = normal_nums

    # 分配: 前 count-1 个来自平码池, 第 count 个来自特码推荐(号码不重复)
    n_front = max(0, count - 1)
    if count <= 0:
        n_front = 0
    pool_nums = list(dict.fromkeys(pool_nums))  # 保序去重
    front = pool_nums[:n_front]
    # 特码推荐: 从剩余号码中取分最高者; 若池太小则从前 6 中取未占用的兜底
    rest = [x for x in special_nums if x not in front]
    special = rest[0] if rest else None
    if special is None and count > 0:
        for x in reversed(front):
            if front.count(x) == 1:
                front.remove(x)
                special = x
                break
    sets = []
    if special is not None:
        seq = [f"{x:02d}" for x in front] + [f"{special:02d}"]
        sets.append(seq)
    return {
        "sets": sets,
        "strategy_note": "前6=推荐池按分取,第7=特码推荐",
    }
