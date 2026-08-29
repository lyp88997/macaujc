# BATCH-014 编辑脚本(统计/遗漏完整词标注+统计号码球波色)
P = "/opt/data/workspace/macaujc-predictor/web/index.html"
src = open(P, encoding="utf-8").read()
edits = []

def rep(old, new, tag):
    n = src.count(old)
    assert n == 1, f"[{tag}] 命中 {n} 次(须为1)"
    return (old, new, tag)

edits.append(rep(
    ".bar-track{flex:1;max-width:460px;",
    ".bar-track{flex:1;max-width:380px;",
    "统计色条缩短"))
edits.append(rep(
    ".bar-val{width:158px;white-space:nowrap;flex:none;font-size:12px;color:var(--dim);text-align:right}",
    ".bar-val{width:222px;white-space:nowrap;flex:none;font-size:11.5px;color:var(--dim);text-align:right}",
    "统计数值区加宽"))
edits.append(rep(
    '.om-item .track{flex:1;max-width:320px;height:12px;background:rgba(255,255,255,.05);border-radius:5px;overflow:hidden}',
    '.om-main{flex:1;min-width:0;display:flex;flex-direction:column;gap:3px}\n'
    '.om-item .track{width:100%;max-width:340px;height:12px;background:rgba(255,255,255,.05);border-radius:5px;overflow:hidden}',
    "遗漏改两行结构CSS"))
edits.append(rep(
    ".om-item .v{width:150px;display:flex;flex-direction:column;align-items:flex-end;gap:3px;flex:none;text-align:right;color:var(--dim);font-size:11.5px}",
    ".om-vals{font-size:11px;color:var(--dim);line-height:1.55}",
    "遗漏标注行CSS"))
edits.append(rep(
    'else if(DIM_KIND[dim]==="num")label=`<span class="ball sm">${esc(it.key)}</span>`;',
    'else if(DIM_KIND[dim]==="num")label=`<span class="ball sm ${WAVE[waveClassOf(it.key)]||"grey"}">${esc(it.key)}</span>`;',
    "统计号码球接波色"))
edits.append(rep(
    "${it.count}次 · ${(it.rate*100).toFixed(1)}% · 遗${it.omission}",
    "出现${it.count}次 · 频率${(it.rate*100).toFixed(1)}% · 当前遗漏${it.omission}",
    "统计完整词标注"))
edits.append(rep(
    '''            <div class="track"><div class="fill" style="width:${pct.toFixed(0)}%"></div></div>
            <div class="v"><div class="num">遗${r.omission} · 均${r.avg_omission} · 顶${r.max_omission}</div>${hot?'<div class="badge-hot">回补区🔥</div>':""}</div>''',
    '''            <div class="om-main">
              <div class="track"><div class="fill" style="width:${pct.toFixed(0)}%"></div></div>
              <div class="om-vals">当前遗漏${r.omission} · 平均遗漏${r.avg_omission} · 历史最大遗漏${r.max_omission}${hot?' <span class="badge-hot">回补区🔥</span>':""}</div>
            </div>''',
    "遗漏完整词标注+两行模板"))
edits.append(rep(
    "  .ball-col{gap:4px}",
    """  /* 统计/遗漏完整词标注: 手机端色条让宽, 数值行可换行 */
  .bar-row{flex-wrap:wrap;row-gap:2px}
  .bar-track{max-width:none;min-width:56px}
  .bar-val{width:auto;font-size:10px}
  .om-vals{font-size:10px}
  .ball-col{gap:4px}""",
    "手机端适配"))

for old, new, tag in edits:
    src = src.replace(old, new, 1)
    print("OK", tag)
open(P, "w", encoding="utf-8").write(src)
print("共", len(edits), "刀全部落盘")
