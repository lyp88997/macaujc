// BATCH-016 交互沙盒 v8: defineProperty 覆写 navigator(Node26 只读getter)
const fs = require("fs");
const src = fs.readFileSync("/opt/data/workspace/macaujc-predictor/web/index.html", "utf-8");
const main = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1])[1];

const log = [];
global.document = {
  addEventListener: (ev, fn) => { if (ev === "click") global._click = fn; },
  querySelector: s => s === "#copy-toast" ? { textContent:"", classList:{ add(){}, remove(){} } } : null,
  querySelectorAll: () => [],
  createElement: () => ({ style:{}, focus(){}, select(){}, remove(){} }),
  body: { appendChild(){}, removeChild(){} },
  documentElement: { style:{ setProperty(){} }, getAttribute: () => null, setAttribute(){}, removeAttribute(){} },
  execCommand: () => true
};
Object.defineProperty(global, "navigator", {
  value: { clipboard: { writeText: async t => log.push("CLIP:" + t) } },
  configurable: true, writable: true
});
global.window = global;
global.fetch = async () => { throw new Error("mock"); };

const a = main.indexOf("const $=");
const b = main.lastIndexOf("/*", main.indexOf("顶部状态"));
const tools = main.slice(a, b);
const prelude = tools + `
let PK_LAST=[3, 9, 17, 22, 38, 45];
let PD_LAST=null;
`;
eval(prelude);
const span = { closest: sel => sel === "[data-copyall]" ? { dataset: { copyall: "1" } } : null };
global._click({ target: span });

setTimeout(() => {
  const ok = log[0] === "CLIP:3 9 17 22 38 45";
  console.log("单击球 →", ok ? "OK 复制全部(3 9 17 22 38 45)" : "NG " + (log[0] || "无输出"));
  process.exit(ok ? 0 : 1);
}, 100);
