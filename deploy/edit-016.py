# BATCH-016 编辑脚本(挑码/预测交互调整+导航顺序)
P = "/opt/data/workspace/macaujc-predictor/web/index.html"
src = open(P, encoding="utf-8").read()
n0 = len(src)
edits = []

def rep(old, new, tag):
    global src
    n = src.count(old)
    assert n == 1, f"[{tag}] 命中{n}次(须唯一): {old[:60]}"
    src = src.replace(old, new)
    edits.append(tag)

# ── 1) ball(): 加 copyAll 选项(data-copyall 属性) ──
rep('function ball(n,{sm,lg,special,wave,copy,label}={}){const w=wave&&WAVE[wave]?WAVE[wave]:"grey";',
    'function ball(n,{sm,lg,special,wave,copy,copyAll,label}={}){const w=wave&&WAVE[wave]?WAVE[wave]:"grey";',
    "ball签名")
rep('const b=`<span class="${cls}"${copy?` data-copy="${esc(n)}" title="点击复制"`:""}>${esc(n)}</span>`;',
    'const b=`<span class="${cls}"${copy?` data-copy="${esc(n)}" title="点击复制"`:""}${copyAll?` data-copyall="1" title="点击复制全部号码"`:""}>${esc(n)}</span>`;',
    "ball属性")

# ── 2) 全局点击代理: copyall 优先拦截 ──
rep('document.addEventListener("click",e=>{',
    'document.addEventListener("click",e=>{\n  const ca=e.target.closest("[data-copyall]");\n  if(ca){const all=(PK_LAST&&PK_LAST.length?PK_LAST:(PD_LAST&&PD_LAST.items?PD_LAST.items.map(x=>x.number):[]));\n    all.length?copyText(all.join(" "),"已复制全部号码"):toast("先选筛选条件");return;}',
    "点击代理")

# ── 3) 挑码页: 结果球+说明文字 改复制全部 ──
rep('$("#pk-remaining").innerHTML=rem.map(n=>ball(n,{wave:waveClassOf(n),copy:true})).join("")',
    '$("#pk-remaining").innerHTML=rem.map(n=>ball(n,{wave:waveClassOf(n),copyAll:true})).join("")',
    "挑码球copyAll")
rep('$("#pk-count").textContent=`命中 ${r.count} 个号码 · 单击号码可复制`;',
    '$("#pk-count").textContent=`命中 ${r.count} 个号码 · 单击号码复制全部`;',
    "挑码说明")

# ── 4) 预测页: 推荐球+大球 接 copyAll ──
rep('$("#pd-combo-balls").innerHTML=items.map(it=>ball(it.number,{copy:true,wave:it.attrs?.wave})).join("");',
    '$("#pd-combo-balls").innerHTML=items.map(it=>ball(it.number,{copyAll:true,wave:it.attrs?.wave})).join("");',
    "推荐球copyAll")
rep('${ball(it.number,{lg:true,wave:it.attrs?.wave})}',
    '${ball(it.number,{lg:true,copyAll:true,wave:it.attrs?.wave})}',
    "pred大球copyAll")
rep('${items.length} 个号码（单击号码可复制）`;',
    '${items.length} 个号码（单击号码复制全部）`;',
    "预测说明")

# ── 5) 挑码页: 清空按钮放大 ──
rep('<button class="btn ghost" style="float:right;padding:4px 10px;font-size:12px" id="pk-clear">清空</button>',
    '<button class="btn ghost" style="float:right;padding:9px 18px;font-size:13.5px;font-weight:600" id="pk-clear">清空</button>',
    "清空放大")

# ── 6) 挑码页: 删智能组号整卡(grid g2 → 单卡) ──
rep("""      <div class="grid g2">
        <div class="card" id="pk-panel"></div>
        <div class="card">
          <div class="card-head"><h3>🎛️ 智能组号 <span class="tag">前6平码 + 末位特码</span></h3>
            <button class="btn ghost" id="pk-copy-set">📋 复制组号</button></div>
          <div class="controls" style="margin:0 0 10px">
            <label>推荐池</label>
            <select id="pk-pool"><option value="composite">综合分</option><option value="hot">热号</option>
              <option value="cold">冷号</option><option value="all">全池</option></select>
            <button class="btn" id="pk-gen">生成 (6+1)</button>
          </div>
          <div class="result-balls" id="pk-set"></div>
          <p class="small muted" id="pk-note"></p>
        </div>
      </div>""",
    '      <div class="card" id="pk-panel" style="margin-bottom:14px"></div>',
    "删智能组号卡")

# ── 7) 死代码清理: 清空处理器残留行+pk-gen/pk-copy-set 绑定+genPick 函数+PK_SET ──
rep('''    $("#pk-set").innerHTML="";$("#pk-note").textContent="";PK_SET=[];};
''', '    };\n', "清空处理器")
rep('''  $("#pk-gen").onclick=genPick;
  $("#pk-copy-set").onclick=()=>{PK_SET.length?copyText(PK_SET.join(" "),"已复制组号"):toast("先点击生成组号")};
''', '', "pk-gen绑定")
rep('''let PK_LAST=[];let PK_SET=[];
''', 'let PK_LAST=[];\n', "PK_SET声明")
rep('''async function genPick(){
  try{
    const r=await apiPost("/api/pick",{count:7,pool:$("#pk-pool").value,filters:JSON.parse(JSON.stringify(PK_SEL))});
    const set=(r.sets&&r.sets[0])||[];
    $("#pk-set").innerHTML=set.length?set.map((n,i)=>ball(n,{special:i===6,wave:waveClassOf(n),copy:true})).join(""):`<span class="muted small">池不足，无法组号</span>`;
    PK_SET=set.map(x=>+x);
    $("#pk-note").textContent=r.strategy_note||"";
  }catch(e){$("#pk-note").textContent="组号失败: "+e.message}
}
''', '', "genPick函数")

# ── 8) 预测页: 打分文案+模式去英文 ──
rep('<p>透明可解释打分：recency 40 + 遗漏压力 30 + 维度回补 15 + 日种子 15（当天固定）</p>',
    '<p>透明可解释打分：权重40 + 遗漏压力 30 + 维度回补 15 + 日种子 15（当天固定）</p>',
    "打分文案")
rep('<option value="composite">综合 composite</option><option value="hot">热号 hot</option>',
    '<option value="composite">综合</option><option value="hot">热号</option>', "模式去英文1")
rep('<option value="cold">冷号 cold</option><option value="omission">遗漏 omission</option>',
    '<option value="cold">冷号</option><option value="omission">遗漏</option>', "模式去英文2")

# ── 9) 导航: 统计分析挪至末位 ──
rep('''    <a data-page="overview" class="on"><span class="ico">📊</span>数据总览</a>
    <a data-page="draws"><span class="ico">📜</span>历史开奖</a>
    <a data-page="stats"><span class="ico">📈</span>统计分析</a>
    <a data-page="omit"><span class="ico">⏳</span>遗漏监控</a>
    <a data-page="predict"><span class="ico">🎯</span>预测推荐</a>
    <a data-page="picker"><span class="ico">🎛️</span>挑码筛选</a>''',
    '''    <a data-page="overview" class="on"><span class="ico">📊</span>数据总览</a>
    <a data-page="draws"><span class="ico">📜</span>历史开奖</a>
    <a data-page="omit"><span class="ico">⏳</span>遗漏监控</a>
    <a data-page="predict"><span class="ico">🎯</span>预测推荐</a>
    <a data-page="picker"><span class="ico">🎛️</span>挑码筛选</a>
    <a data-page="stats"><span class="ico">📈</span>统计分析</a>''',
    "导航顺序")

# ── 10) mock 数据死代码清理(引用已删元素) ──
rep('''  if(path.startsWith("/api/pick"))return{sets:[["07","12","18","23","29","34","40"]],strategy_note:"演示数据"};
''', '', "mockApi/pick")

open(P, "w", encoding="utf-8").write(src)
print(f"OK {len(edits)} 刀全部落盘 ({n0}→{len(src)} chars)")
for t in edits: print(" -", t)
