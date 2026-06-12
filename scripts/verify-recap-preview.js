// 验证脚本：抽离 preview.html 中的两个 script 块做语法校验 + 静态断言
// 1) recapPage JS 块能 Function 解析
// 2) mock JSON 3 个活动 schema 完整
// 3) 3 个「查看复盘」元素必须是 <button @click="openRecap(...)">（曾因 Edit 静默失败导致残留 <a>）
// 4) init() 中包含 DOMContentLoaded 兜底（防止 mock 节点位置调整时找不到数据）
const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, '..', 'preview.html'), 'utf8');

let failed = 0;
const check = (cond, label) => {
  if (cond) {
    console.log('  ✓', label);
  } else {
    console.log('  ✗', label);
    failed++;
  }
};

console.log('1. JS 语法');
const fnStart = html.indexOf('function recapPage');
const scriptStart = html.lastIndexOf('<script>', fnStart);
const scriptEnd = html.indexOf('</script>', fnStart);
const jsBody = html.slice(scriptStart + '<script>'.length, scriptEnd);
try {
  new Function(jsBody);
  check(true, 'recapPage 块能被 Function 解析');
} catch (e) {
  check(false, 'recapPage 块语法错：' + e.message);
}

console.log('\n2. mock JSON schema');
const jsonMatch = html.match(/<script type="application\/json" id="recap-mock">([\s\S]*?)<\/script>/);
if (!jsonMatch) {
  check(false, '找不到 #recap-mock 节点');
} else {
  try {
    const data = JSON.parse(jsonMatch[1]);
    const ids = Object.keys(data);
    check(ids.length === 3, '活动数量 = 3（实际 ' + ids.length + '）');
    for (const id of ids) {
      const a = data[id];
      const required = ['activityId', 'title', 'org', 'endedAt', 'overview', 'audio', 'stats', 'assets'];
      const missing = required.filter(k => !(k in a));
      check(missing.length === 0, `${id} 字段完整（缺失 ${missing.join(',')}）`);
      check(a.activityId === id, `${id} activityId 自洽`);
    }
  } catch (e) {
    check(false, 'mock JSON 解析失败：' + e.message);
  }
}

console.log('\n3. 3 个「查看复盘」必须全部是 <button @click="openRecap(...)">');
// 用更宽松的匹配扫整篇 <button ...>查看复盘</button> 与 <a ...>查看复盘</a>
// 关键：button 标签的 ">" 必须显式出现在 "查看复盘" 之前，否则会跨标签误匹配
const buttonMatches = html.match(/<button[^>]*>查看复盘<\/button>/g) || [];
const anchorMatches = html.match(/<a[^>]*>查看复盘<\/a>/g) || [];
check(buttonMatches.length === 3, `<button> 查看复盘数量 = 3（实际 ${buttonMatches.length}）`);
check(anchorMatches.length === 0, `<a> 查看复盘残留 = 0（实际 ${anchorMatches.length}）`);
// 确认 3 个 button 各自绑了不同 id
const expectedIds = ['ev-2026-05-17', 'ev-2026-06-14', 'ev-2026-06-28'];
for (const id of expectedIds) {
  const re = new RegExp(`@click="openRecap\\('${id}'\\)"`);
  check(re.test(html), `按钮绑定了 ${id}`);
}

console.log('\n4. init() 兜底');
check(
  /init\(\)\s*\{[\s\S]*?DOMContentLoaded[\s\S]*?loadMockData/.test(html),
  'init() 中存在 DOMContentLoaded → loadMockData 兜底',
);

console.log('\n' + (failed === 0 ? 'ALL_OK' : `FAILED ${failed} 项`));
process.exit(failed === 0 ? 0 : 1);
