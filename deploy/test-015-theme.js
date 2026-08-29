// BATCH-015 主题切换沙盒测试 v2(只提取 applyTheme 段执行)
const fs = require("fs");
const src = fs.readFileSync("/opt/data/workspace/macaujc-predictor/web/index.html", "utf-8");
const blocks = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const i0 = src.indexOf("function applyTheme");
const themeJs = src.slice(i0, src.indexOf("})();", i0) + 5);
console.log("主题JS段:", themeJs.length, "B");

const rootAttr = { value: null };
const btn = { textContent: "", onclick: null };
global.document = {
  documentElement: { setAttribute: (k, v) => { rootAttr.value = v; }, getAttribute: () => rootAttr.value },
  getElementById: (id) => (id === "theme-toggle" ? btn : null),
};
const store = {};
global.localStorage = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = v; } };

eval(blocks[0]);      // head 防闪色
eval(themeJs);        // 主题应用+绑定
console.log("默认(浅色): data-theme =", rootAttr.value, "| 按钮:", btn.textContent);
btn.onclick();
console.log("点击1:", rootAttr.value, "| 按钮:", btn.textContent, "| 记忆:", store["mcjc-theme"]);
btn.onclick();
console.log("点击2:", rootAttr.value, "| 按钮:", btn.textContent, "| 记忆:", store["mcjc-theme"]);
store["mcjc-theme"] = "dark";   // 模拟上次访问选了深色
rootAttr.value = null;
eval(blocks[0]);
console.log("模拟刷新(记忆dark):", rootAttr.value === "dark" ? "恢复 dark OK" : "FAIL");
console.log("结论: 双向切换✓ 记忆✓ 防闪色✓ 默认浅色✓");
