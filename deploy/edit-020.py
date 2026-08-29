# BATCH-020 编辑脚本(总览去序号+秒级追新+版本1.1.9+品牌+筛选放大+页脚)
import re, py_compile

P = "/opt/data/workspace/macaujc-predictor/web/index.html"
S = "/opt/data/workspace/macaujc-predictor/app/server.py"
H = "/opt/data/workspace/macaujc-predictor/app/http_api.py"
src = open(P, encoding="utf-8").read()
n0 = len(src)
edits = []

def rep(old, new, tag, text=None):
    global src
    t = src if text is None else text
    c = t.count(old)
    assert c == 1, f"[{tag}] 命中 {c} 次(须唯一): {old[:60]}"
    if text is None:
        src = src.replace(old, new)
    edits.append(tag)

# ── 1) 品牌改新澳六合(标题+头部+渐变CSS) ──
rep("<title>MACAUJC · 号码分析台</title>", "<title>新澳六合 分析预测</title>", "title")
rep('<div class="brand"><div class="logo">🎰</div>MACAUJC <small>号码分析台</small></div>',
    '<div class="brand"><div class="logo">🎰</div><span class="brand-name">新澳六合 分析预测</span></div>', "brand")
CSS_ADD = """/* B020 品牌渐变(浅变色)+筛选放大+页脚 */
.brand-name{font-size:17.5px;font-weight:800;letter-spacing:.5px;background:linear-gradient(120deg,var(--acc),var(--acc2));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
footer.site-foot{margin-top:6px;padding:14px 0 4px;text-align:center;font-size:12.5px;color:var(--dim);border-top:1px solid var(--border)}
footer.site-foot .fs-name{font-weight:700;background:linear-gradient(120deg,var(--acc),var(--acc2));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
footer.site-foot a{color:var(--acc);text-decoration:none;font-weight:600}
footer.site-foot a:hover{text-decoration:underline}
#pk-panel h3{font-size:17px;font-weight:700}
main{overflow-y:auto;padding:18px 20px 40px}"""
rep("main{overflow-y:auto;padding:18px 20px 40px}", CSS_ADD, "css-add")

# ── 2) 总览去序号 1-7 ──
for n in range(1, 8):
    rep(f'<i class="seq">{n}</i>', "", f"seq-{n}")

# ── 3) 秒级追新: 20s→1s, 去超时 ──
rep("(20s/次, 最长12分钟; 后端采集实测 1m44s~5m 入库)", "(1s/次, 直到获取数据为止; 21:32 开奖后即追)", "poll-comment")
rep("},20000);", "},1000);", "poll-1s")
TIMEOUT = """      if(Date.now()-started>12*60*1000){  /* 12分钟超时: 官网未更新, 按下一期重挂倒计时 */
        clearInterval(AUTO_POLL);AUTO_POLL=null;
        const s2=await api("/api/status");
        startCountdown(s2?.next_draw_at||new Date(Date.now()+864e5).toISOString());
      }
"""
rep(TIMEOUT, "", "poll-timeout-rm")

# ── 4) 演示数据版本 ──
rep('service:"macaujc-predictor",version:"1.0.0",', 'service:"macaujc-predictor",version:"1.1.9",', "mock-ver")

# ── 5) 筛选页放大 ──
rep("padding:5px 12px;border-radius:18px;border:1px solid var(--border);background:var(--panel2);",
    "padding:8px 18px;border-radius:20px;border:1px solid var(--border);background:var(--panel2);", "fchip-pad")
rep("font-size:12.5px;cursor:pointer;transition:all .15s;user-select:none}",
    "font-size:15px;cursor:pointer;transition:all .15s;user-select:none}", "fchip-font")
rep(".ft{font-size:12.5px;color:var(--dim);margin-bottom:7px}",
    ".ft{font-size:15px;color:var(--dim);margin-bottom:9px}", "ft-font")
rep('style="float:right;padding:9px 18px;font-size:13.5px;font-weight:600"',
    'style="float:right;padding:11px 24px;font-size:16px;font-weight:700"', "clear-btn")

# ── 6) 页脚 ──
FOOT = """</section>
      <footer class="site-foot"><span class="fs-name">新澳六合分析预测</span> · 开发者@平歌歌 · <a href="https://github.com/lyp88997/macaujc" target="_blank" rel="noopener">项目地址</a> · <a href="https://t.me/mzlpin" target="_blank" rel="noopener">TG联系</a> · <a href="https://tz.mzlp.eu.org/" target="_blank" rel="noopener">Komari服务器状态</a></footer>
  </main>"""
rep("</section>\n  </main>", FOOT, "footer")

open(P, "w", encoding="utf-8").write(src)
print(f"index.html {len(edits)} 刀全中: {', '.join(edits)}")
print(f"体积 {n0} → {len(src)} ({len(src)-n0:+d})")

# ── 7) 后端版本 1.1.9 ──
for path, old, new, tag in [
    (S, '__version__ = "1.0.0"', '__version__ = "1.1.9"', "server-ver"),
    (H, 'server_version = "macaujc-predictor/1.0.0"', 'server_version = "macaujc-predictor/1.1.9"', "api-server-ver"),
    (H, '"version": "1.0.0",', '"version": "1.1.9",', "api-status-ver"),
]:
    t = open(path, encoding="utf-8").read()
    assert t.count(old) == 1, f"[{tag}] 命中异常"
    open(path, "w", encoding="utf-8").write(t.replace(old, new))
    print(f"[{tag}] OK")
py_compile.compile(S, doraise=True); py_compile.compile(H, doraise=True)
print("py 语法 OK")

# ── 8) 自检(全文扫) ──
chk = open(P, encoding="utf-8").read()
assert chk.count('class="seq"') == 0, "seq 残留"
assert "20000" not in chk, "20s 轮询残留"
assert chk.count("site-foot") >= 2 and "brand-name" in chk and "平歌歌" in chk
assert "12*60*1000" not in chk, "超时块残留"
print("自检全绿: seq=0 / 1s轮询 / 超时已删 / 页脚+品牌在位")
