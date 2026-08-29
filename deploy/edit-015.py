# BATCH-015 编辑脚本(CSS变量双主题+玻璃增强+主题切换默认浅色)
P = "/opt/data/workspace/macaujc-predictor/web/index.html"
src = open(P, encoding="utf-8").read()
n0 = len(src)
edits = []

def rep(old, new, tag):
    global src
    c = src.count(old)
    assert c == 1, "EXPECT 1 got %d for %s" % (c, tag)
    src = src.replace(old, new)
    edits.append(tag)

# 1) 变量块重构: :root=浅色默认(玻璃白), 新增语义变量; dark=现版深色原值
rep("""  --bg0:#070a14;--bg1:#0d1226;--panel:rgba(255,255,255,.045);--panel2:rgba(255,255,255,.07);
  --border:rgba(255,255,255,.09);--acc:#6d7cff;--acc2:#a45cff;--txt:#e8ecf8;--dim:#8a93b2;
  --red:#ff4d5e;--blue:#3d8bff;--green:#2fd57b;--gold:#ffc94d;--ok:#2fd57b;--warn:#ffb14d;
  --glow:0 0 18px rgba(109,124,255,.28);
}""",
"""  --bg0:#f3f5fb;--bg1:#e8edf8;--panel:rgba(255,255,255,.58);--panel2:rgba(255,255,255,.78);
  --border:rgba(15,23,42,.10);--acc:#6d7cff;--acc2:#a45cff;--txt:#232941;--dim:#5f6a8a;
  --red:#dc2637;--blue:#2563eb;--green:#059669;--gold:#d97706;--ok:#059669;--warn:#d97706;
  --glow:0 4px 16px rgba(109,124,255,.18);
  --bg-rad1:rgba(109,124,255,.10);--bg-rad2:rgba(164,92,255,.08);
  --glass-hd:rgba(255,255,255,.72);--glass-nav:rgba(255,255,255,.55);
  --sbar:rgba(15,23,42,.16);--row-line:rgba(15,23,42,.06);--row-hover:rgba(15,23,42,.045);
  --input-bg:#ffffff;--track-bg:rgba(15,23,42,.08);--card-shadow:0 4px 24px rgba(15,23,42,.08);
  --card-inset:rgba(255,255,255,.85);--grey-a:#cbd5e1;--grey-b:#94a3b8;--zlabel-c:#64748b;
  --toast-bg:rgba(255,255,255,.96);--toast-bd:rgba(109,124,255,.45);--toast-c:#232941;
  --kpi-a:#313a5e;--kpi-b:#5a67e8;--cd-c:#232941;--cd-shadow:0 0 18px rgba(109,124,255,.25);
  --ovsub-c:#3d4668;--nav-on-bg-a:rgba(109,124,255,.14);--nav-on-bg-b:rgba(164,92,255,.10);
  --nav-on-bd:rgba(109,124,255,.35);--nav-on-c:#4338ca;--fchip-on-bg:linear-gradient(135deg,var(--acc),var(--acc2));
  --banner-bg:rgba(255,177,77,.16);--banner-bd:rgba(217,119,6,.45);--banner-c:#92400e;
  --hot-c:#b45309;--hot-bd:rgba(217,119,6,.5);
  --soft-warn-bg:rgba(255,177,77,.14);--soft-warn-bd:rgba(217,119,6,.4);
}
html[data-theme=dark]{
  --bg0:#070a14;--bg1:#0d1226;--panel:rgba(255,255,255,.045);--panel2:rgba(255,255,255,.07);
  --border:rgba(255,255,255,.09);--txt:#e8ecf8;--dim:#8a93b2;
  --red:#ff4d5e;--blue:#3d8bff;--green:#2fd57b;--gold:#ffc94d;--ok:#2fd57b;--warn:#ffb14d;
  --glow:0 0 18px rgba(109,124,255,.28);
  --bg-rad1:rgba(109,124,255,.14);--bg-rad2:rgba(164,92,255,.10);
  --glass-hd:rgba(10,14,30,.75);--glass-nav:rgba(10,14,30,.5);
  --sbar:rgba(255,255,255,.14);--row-line:rgba(255,255,255,.05);--row-hover:rgba(255,255,255,.03);
  --input-bg:#141a30;--track-bg:rgba(255,255,255,.05);--card-shadow:0 4px 24px rgba(0,0,0,.25);
  --card-inset:rgba(255,255,255,.06);--grey-a:#3a415c;--grey-b:#232941;--zlabel-c:#aab4de;
  --toast-bg:rgba(20,26,48,.95);--toast-bd:rgba(109,124,255,.5);--toast-c:#fff;
  --kpi-a:#fff;--kpi-b:#9fb0ff;--cd-c:#fff;--cd-shadow:0 0 18px rgba(109,124,255,.55);
  --ovsub-c:#c6cdf1;--nav-on-bg-a:rgba(109,124,255,.22);--nav-on-bg-b:rgba(164,92,255,.16);
  --nav-on-bd:rgba(109,124,255,.35);--nav-on-c:#fff;
  --fchip-on-bg:linear-gradient(120deg,rgba(109,124,255,.35),rgba(164,92,255,.28));
  --banner-bg:rgba(255,177,77,.1);--banner-bd:rgba(255,177,77,.4);--banner-c:#ffd9a0;
  --hot-c:#ffd280;--hot-bd:rgba(255,177,77,.45);
  --soft-warn-bg:rgba(255,177,77,.05);--soft-warn-bd:rgba(255,177,77,.35);
}""", "root变量块+dark覆盖块")

# 2) body 径向光斑走变量
rep("radial-gradient(1200px 600px at 80% -10%,rgba(109,124,255,.14),transparent 60%),",
    "radial-gradient(1200px 600px at 80% -10%,var(--bg-rad1),transparent 60%),", "body光斑1")
rep("radial-gradient(900px 500px at -10% 110%,rgba(164,92,255,.10),transparent 60%),",
    "radial-gradient(900px 500px at -10% 110%,var(--bg-rad2),transparent 60%),", "body光斑2")

# 3) 滚动条
rep("::-webkit-scrollbar-thumb{background:rgba(255,255,255,.14);border-radius:4px}",
    "::-webkit-scrollbar-thumb{background:var(--sbar);border-radius:4px}", "滚动条")

# 4) 头部玻璃增强
rep("background:rgba(10,14,30,.75);backdrop-filter:blur(12px);position:relative;z-index:20}",
    "background:var(--glass-hd);backdrop-filter:blur(16px) saturate(1.5);-webkit-backdrop-filter:blur(16px) saturate(1.5);position:relative;z-index:20}", "头部玻璃")

# 5) 导航玻璃
rep("nav{border-right:1px solid var(--border);padding:14px 10px;background:rgba(10,14,30,.5);",
    "nav{border-right:1px solid var(--border);padding:14px 10px;background:var(--glass-nav);backdrop-filter:blur(12px) saturate(1.4);-webkit-backdrop-filter:blur(12px) saturate(1.4);", "导航玻璃")

# 6) 导航选中态
rep("nav a.on{color:#fff;background:linear-gradient(120deg,rgba(109,124,255,.22),rgba(164,92,255,.16));\n  border-color:rgba(109,124,255,.35);box-shadow:var(--glow)}",
    "nav a.on{color:var(--nav-on-c);background:linear-gradient(120deg,var(--nav-on-bg-a),var(--nav-on-bg-b));\n  border-color:var(--nav-on-bd);box-shadow:var(--glow)}", "导航选中态")

# 7) 卡片玻璃增强+顶高光
rep("padding:16px;backdrop-filter:blur(10px);box-shadow:0 4px 24px rgba(0,0,0,.25)}",
    "padding:16px;backdrop-filter:blur(14px) saturate(1.4);-webkit-backdrop-filter:blur(14px) saturate(1.4);box-shadow:var(--card-shadow),inset 0 1px 0 var(--card-inset)}", "卡片玻璃")

# 8) 表格行
rep("td{padding:8px 10px;border-bottom:1px solid rgba(255,255,255,.05);white-space:nowrap}",
    "td{padding:8px 10px;border-bottom:1px solid var(--row-line);white-space:nowrap}", "td行线")
rep("tr:hover td{background:rgba(255,255,255,.03)}",
    "tr:hover td{background:var(--row-hover)}", "行悬停")

# 9) 色条轨道(统计+遗漏)
rep("height:16px;background:rgba(255,255,255,.05);border-radius:8px;overflow:hidden}",
    "height:16px;background:var(--track-bg);border-radius:8px;overflow:hidden}", "统计轨道")
rep("height:12px;background:rgba(255,255,255,.05);border-radius:5px;overflow:hidden}",
    "height:12px;background:var(--track-bg);border-radius:5px;overflow:hidden}", "遗漏轨道")

# 10) 灰球/生肖字
rep(".ball.grey{background:linear-gradient(145deg,#3a415c,#232941)}",
    ".ball.grey{background:linear-gradient(145deg,var(--grey-a),var(--grey-b))}", "灰球")
rep(".zlabel{font-size:12.5px;font-weight:700;color:#aab4de;line-height:1.2}",
    ".zlabel{font-size:12.5px;font-weight:700;color:var(--zlabel-c);line-height:1.2}", "生肖字色")

# 11) toast
rep("background:rgba(20,26,48,.95);border:1px solid rgba(109,124,255,.5);color:#fff;",
    "background:var(--toast-bg);border:1px solid var(--toast-bd);color:var(--toast-c);", "toast")
rep(".copy-ico:hover{color:#fff;background:rgba(109,124,255,.25)}",
    ".copy-ico:hover{color:var(--toast-c);background:rgba(109,124,255,.25)}", "toast图标")

# 12) KPI 渐变字/倒计时
rep("background:linear-gradient(90deg,#fff,#9fb0ff);",
    "background:linear-gradient(90deg,var(--kpi-a),var(--kpi-b));", "KPI渐变字")
rep("  text-shadow:0 0 18px rgba(109,124,255,.55);letter-spacing:1px}",
    "  text-shadow:var(--cd-shadow);letter-spacing:1px}", "倒计时辉光")
rep(".countdown{font-size:30px;font-weight:700;font-variant-numeric:tabular-nums;color:#fff;",
    ".countdown{font-size:30px;font-weight:700;font-variant-numeric:tabular-nums;color:var(--cd-c);", "倒计时字色")

# 13) 总览副标题/时间
rep(".ov-sub{font-size:15px;font-weight:700;color:#c6cdf1}",
    ".ov-sub{font-size:15px;font-weight:700;color:var(--ovsub-c)}", "总览副题")
rep(".ov-time{font-size:12.5px;color:#8b95bd;margin-top:3px}",
    ".ov-time{font-size:12.5px;color:var(--dim);margin-top:3px}", "总览时间")

# 14) 横幅/🔥徽标/免责
rep(".banner{display:none;background:rgba(255,177,77,.1);border:1px solid rgba(255,177,77,.4);color:#ffd9a0;",
    ".banner{display:none;background:var(--banner-bg);border:1px solid var(--banner-bd);color:var(--banner-c);", "横幅")
rep(".badge-hot{font-size:10px;color:#ffd280;border:1px solid rgba(255,177,77,.45);",
    ".badge-hot{font-size:10px;color:var(--hot-c);border:1px solid var(--hot-bd);", "🔥徽标")
rep("border:1px dashed rgba(255,177,77,.35);\n  border-radius:10px;padding:10px 12px;background:rgba(255,177,77,.05)}",
    "border:1px dashed var(--soft-warn-bd);\n  border-radius:10px;padding:10px 12px;background:var(--soft-warn-bg)}", "免责条")

# 15) 输入框/挑码选中
rep("select,input[type=number]{background:#141a30;",
    "select,input[type=number]{background:var(--input-bg);", "输入框")
rep(".fchip.on{background:linear-gradient(120deg,rgba(109,124,255,.35),rgba(164,92,255,.28));\n  border-color:var(--acc);color:#fff;box-shadow:0 0 10px rgba(109,124,255,.35)}",
    ".fchip.on{background:var(--fchip-on-bg);\n  border-color:var(--acc);color:#fff;box-shadow:var(--glow)}", "挑码选中")

# 16) 主题按钮 CSS(状态栏内)
rep(".dot.warn{background:var(--warn);box-shadow:0 0 8px var(--warn)}",
    ".dot.warn{background:var(--warn);box-shadow:0 0 8px var(--warn)}\n.theme-btn{width:38px;padding:7px 0;font-size:15px;line-height:1;flex:none}", "主题按钮CSS")

# 17) 头部按钮 HTML
rep('    <div class="statusbar">\n      <span><span class="dot" id="svc-dot"></span><span id="svc-text">连接中…</span></span>',
    '    <div class="statusbar">\n      <button class="btn ghost theme-btn" id="theme-toggle" title="切换深色/浅色">🌙</button>\n      <span><span class="dot" id="svc-dot"></span><span id="svc-text">连接中…</span></span>', "主题按钮HTML")

# 18) head 防闪色内联脚本
rep("</style>\n</head>",
    '</style>\n<script>try{if(localStorage.getItem("mcjc-theme")==="dark")document.documentElement.setAttribute("data-theme","dark")}catch(e){}</script>\n</head>', "head防闪色")

# 19) 主题 JS(应用/切换/记忆)
rep("/* 倒计时归零→智能轮询新开奖(20s/次, 最长12分钟; 后端采集实测 1m44s~5m 入库) */",
    """/* 双主题: 默认浅色, 可切换深色, localStorage 记忆(head 内联脚本防首屏闪色) */
function applyTheme(t){document.documentElement.setAttribute("data-theme",t);
  var b=document.getElementById("theme-toggle");if(b)b.textContent=(t==="dark"?"\\u2600\\ufe0f":"\\ud83c\\udf19");
  try{localStorage.setItem("mcjc-theme",t)}catch(e){}}
(function(){var t="light";try{t=localStorage.getItem("mcjc-theme")||"light"}catch(e){}
  applyTheme(t);
  var b=document.getElementById("theme-toggle");
  if(b)b.onclick=function(){applyTheme(document.documentElement.getAttribute("data-theme")==="dark"?"light":"dark")};})();

/* 倒计时归零→智能轮询新开奖(20s/次, 最长12分钟; 后端采集实测 1m44s~5m 入库) */""", "主题JS")

open(P, "w", encoding="utf-8").write(src)
print("OK", len(edits), "刀全部落盘:", " | ".join(edits))
print("size", n0, "->", len(src))
