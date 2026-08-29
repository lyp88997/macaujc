// BATCH-016 诊断 v2: 语法检查+运行时路径跟踪
const fs = require("fs");
const src = fs.readFileSync("/opt/data/workspace/macaujc-predictor/web/index.html", "utf-8");
const main = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1])[1];

const log = [];
global.document = {
  addEventListener: (ev, fn) => { console.log("[注册]", ev); if (ev === "click") global._click = fn; },
  querySelector: s => { console.log("[查询]", s); return s === "#copy-toast" ? { textContent:"", classList:{ add(){}, remove(){} } } : null; },
  querySelectorAll: () => [],
  createElement: () => ({ style:{}, focus(){}, select(){}, remove(){} }),
  body: { appendChild(){}, removeChild(){} },
  documentElement: { style:{ setProperty(){} }, getAttribute: () => null, setAttribute(){}, removeAttribute(){} },
  execCommand: () => true
};
global.navigator = { clipboard: { writeText: async t => { console.log("[剪贴板]", t); log.push("CLIP:" + t); } } };
global.window = global;
global.fetch = async () => { throw new Error("mock"); };

const a = main.indexOf("const $=");
const b = main.lastIndexOf("/*", main.indexOf("顶部状态"));
const tools = main.slice(a, b);
fs.writeFileSync("/tmp/tools-v7.js", tools);

const prelude = tools + `
let PK_LAST=[3, 9, 17, 22, 38, 45];
let PD_LAST=null;
`;
try {
  eval(prelude);
  console.log("[eval] OK | _click:", typeof global._click, "| ball:", typeof ball, "| copyText:", typeof copyText);
} catch(e) { console.log("[eval] 异常:", e.message); }

try {
  const span = { closest: sel => sel === "[data-copyall]" ? { dataset: { copyall: "1" } } : null };
  global._click({ target: span });
  console.log("[click] handler执行完毕无同步异常");
} catch(e) { console.log("[click] 异常:", e.message); }

setTimeout(() => {
  console.log("[log]", JSON.stringify(log));
  const ok = log[0] === "CLIP:3 9 17 22 38 45";
  console.log(ok ? "OK" : "NG");
  process.exit(ok ? 0 : 1);
}, 150);
