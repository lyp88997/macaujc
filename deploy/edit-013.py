# BATCH-013 编辑脚本(统计/遗漏/生肖简体)
import re, tempfile, subprocess
P = "/opt/data/workspace/macaujc-predictor/web/index.html"
src = open(P, encoding="utf-8").read()
edits = []

def rep(old, new, tag):
    global src
    n = src.count(old)
    assert n == 1, f"[{tag}] 命中 {n} 次, 弃改"
    src = src.replace(old, new)
    edits.append(tag)

# 1) 全站繁->简 静态替换(zo 数组/文案)
trad = {"龍": "龙", "馬": "马", "雞": "鸡", "豬": "猪"}
cnt = {k: src.count(k) for k in trad}
src = "".join(trad.get(c, c) for c in src)
edits.append(f"繁简全局: {cnt}")

# 2) esc() 中枢运行时繁->简(API 返回值)
old_esc = "function esc(s){return String(s).replace("
assert src.count(old_esc) == 1
t2s = 'const T2S={"龍":"龙","馬":"马","雞":"鸡","豬":"猪"};'
t2s += 'const T2S_RE=/[龍馬雞豬]/g;'
t2s += 'function esc(s){return String(s).replace(T2S_RE,c=>T2S[c]).replace('
src = src.replace(old_esc, t2s)
edits.append("esc 繁简中枢")

# 3) 统计页: 数值区加宽不换行, 色条限宽
rep(".bar-val{width:92px",
    ".bar-val{width:158px;white-space:nowrap",
    "bar-val 加宽")
rep(".bar-track{flex:1;height:16px",
    ".bar-track{flex:1;max-width:460px;height:16px",
    "bar-track 限宽")

# 4) 遗漏页: 色条限宽, 数值区竖式, 号码球接波色
rep(".om-item .track{flex:1;height:10px",
    ".om-item .track{flex:1;max-width:320px;height:12px",
    "om-track 限宽")
rep(".om-item .v{width:104px",
    ".om-item .v{width:150px;display:flex;"
    "flex-direction:column;align-items:flex-end;gap:3px",
    "om-v 竖式")

old_k = 'dim==="number"?`<span class="ball sm">${esc(r.key)}</span>`:'
new_k = ('dim==="number"?`<span class="ball sm '
         '${WAVE[waveClassOf(r.key)]||"grey"}">${esc(r.key)}</span>`:')
rep(old_k, new_k, "om 号码球波色")

pat = re.compile(
    r'<div class="v num">遗\$\{r\.omission\} / 均\$\{r\.avg_omission\}'
    r' / 顶\$\{r\.max_omission\}\$\{hot\?\'<span class="badge-hot">'
    r'回补区🔥</span>\':""\}</div>')
hits = pat.findall(src)
assert len(hits) == 1, f"om-v 命中 {len(hits)}"
new_v = ('<div class="v"><div class="num">'
         '遗${r.omission} · 均${r.avg_omission} · 顶${r.max_omission}'
         '</div>${hot?\'<div class="badge-hot">回补区🔥</div>\':""}</div>')
src = pat.sub(new_v, src)
edits.append("om-v 竖式+徽标独立行")

open(P, "w", encoding="utf-8").write(src)
print("OK 全部落刀:", edits)
js = re.search(r"<script>(.*)</script>", src, re.S).group(1)
f = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                encoding="utf-8")
f.write(js)
f.close()
r = subprocess.run(["node", "--check", f.name],
                   capture_output=True, text=True)
print("JS语法:", "OK" if r.returncode == 0 else r.stderr[:400])
