# BATCH-022 编辑脚本(预测页复制bug按页取数+手机控件2行)
P = "/opt/data/workspace/macaujc-predictor/web/index.html"
src = open(P, encoding="utf-8").read()
n0 = len(src)
edits = []

def rep(old, new, tag):
    global src
    c = src.count(old)
    assert c == 1, f"[{tag}] count={c}"
    src = src.replace(old, new)
    edits.append(tag)

# 1) 行1开: ctl-row 包住 模式+范围
rep('      <div class="controls">\n        <label>模式</label>',
    '      <div class="controls">\n        <div class="ctl-row"><label>模式</label>', "行1开")

# 2) 行1闭+行2开: scope select 后关行1, 数量前开行2
rep('<option value="normal">平码(含特)</option></select>\n        <label>数量</label>',
    '<option value="normal">平码(含特)</option></select></div>\n        <div class="ctl-row"><label>数量</label>', "行1闭行2开")

# 3) 行2闭: 生成推荐按钮后
rep('<button class="btn" id="pd-go">生成推荐</button>\n      </div>',
    '<button class="btn" id="pd-go">生成推荐</button></div>\n      </div>', "行2闭")

# 4) 桌面CSS: ctl-row 透明化(不破坏原单行)
rep('.controls label{font-size:12.5px;color:var(--dim)}',
    '.controls label{font-size:12.5px;color:var(--dim)}\n.ctl-row{display:contents}', "桌面CSS")

# 5) 手机CSS: 520档两行(新块插在</style>前)
rep('</style>',
    '@media (max-width:520px){#page-predict .controls{flex-direction:column;align-items:stretch}'
    '.ctl-row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}'
    '#page-predict .ctl-row .btn{flex:1;justify-content:center}}\n</style>', "手机CSS")

# 6) 复制bug: 按页面取数(预测页=PD_LAST预测结果, 挑码页=PK_LAST)
old_js = ('if(ca){const all=(PK_LAST&&PK_LAST.length?PK_LAST:(PD_LAST&&PD_LAST.items?'
          'PD_LAST.items.map(x=>x.number):[]));\n    all.length?copyText(all.join(" "),'
          '"已复制全部号码"):toast("先选筛选条件");return;}')
new_js = ('if(ca){const page=(ca.closest(".page")||{}).id||"";\n'
          '    const pk=PK_LAST&&PK_LAST.length?PK_LAST:[];\n'
          '    const pd=PD_LAST&&PD_LAST.items?PD_LAST.items.map(x=>x.number):[];\n'
          '    const all=page==="page-predict"?(pd.length?pd:pk):(pk.length?pk:pd);\n'
          '    all.length?copyText(all.join(" "),"已复制全部号码"):'
          'toast(page==="page-predict"?"先生成推荐":"先选筛选条件");return;}')
rep(old_js, new_js, "复制按页取数")

open(P, "w", encoding="utf-8").write(src)
print(f"OK {len(edits)}刀全中: {edits}; 字节 {n0}->{len(src)}")
