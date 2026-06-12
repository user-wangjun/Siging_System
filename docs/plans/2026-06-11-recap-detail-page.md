# 实施计划：复盘详情页（preview.html 阶段 · 前端优先）

> **计划版本**：v1.0
> **编写日期**：2026-06-11
> **编写人**：SOLO Coder
> **关联 PRD**：[event-registration-prd.md §5.6 通知提醒 / 场景 D 活动复盘](../design/event-registration-prd.md)
> **关联决策**：用户 2026-06-11 确认「前端优先 + 占位接口」「跳页式详情」「首期不实现参与者画像」
> **作用范围**：仅 `preview.html`（单文件前端预览），零新依赖

---

## 1. 目标与边界

### 1.1 目标

把首页「已结束活动」卡片上的「查看复盘」按钮（preview.html L510、L544、L590 共 3 处）从无操作的占位锚点，改造为可点击的**复盘详情页跳转**。详情页承载四块内容：

1. **总概文字**（用户口述：自己写总结文字）
2. **录音回放**（用户口述：会上传录音文件）
3. **数据回顾**（首期只 4 个数字 + 一条进度条）
4. **资料下载**（首期 mock 2 个资料包；真实资源后端接入时再补）

### 1.2 明确不做（留给后续 PR）

- Markdown 渲染（首期仅纯文本 + 段间换行）
- 参与者画像（Top N 城市 / 职业分布）
- 现场照片墙 / 嘉宾金句
- 复盘发布后台
- Flask 路由 + 真实 `GET /api/activities/{id}/recap` 实现（约定接口形状，本 PR 不实现）

---

## 2. 信息架构

### 2.1 触发与路由

- 点击「查看复盘」→ `history.pushState({page:'recap', id}, '', '#/recap/'+id)` → 隐藏首页 `<main>` → 显示 `<section id="recap-detail-page">`。
- 浏览器「← 返回」触发 `popstate` → 自动回到首页（无需手动处理）。
- 详情页右上角「← 返回首页」按钮，等价 `history.back()`，阻止默认 a 标签跳转。

### 2.2 详情页分区（自上而下）

| 区块 | ID | 数据来源 | 失败兜底 |
| --- | --- | --- | --- |
| 头部 hero | `recap-hero` | `title` / `endedAt` / `org.name` | — |
| 总概文字 | `recap-overview` | `overview` (string[]) | 数组为空时整块隐藏 |
| 录音回放 | `recap-audio` | `audio` | `audio.url == null` 时禁用控件 + toast「录音待上传」 |
| 数据回顾 | `recap-stats` | `stats` | 4 项缺一即整块隐藏（不显示半残） |
| 资料下载 | `recap-assets` | `assets[]` | 空数组时整块隐藏 |

### 2.3 占位接口形状（前端先按此字段消费，后端照此实现）

```jsonc
// GET /api/activities/{id}/recap  （占位；preview 阶段走 mock）
{
  "activityId": "ev-2026-05-30",
  "title": "WaytoAGI 东莞周会·RAG 实战",
  "org": {
    "name": "WaytoAGI 东莞",
    "logo": "/static/images/碳基社区.png"
  },
  "endedAt": "2026-05-30T17:30:00+08:00",
  "overview": [
    "本次周会围绕 RAG 的工程落地展开，...",
    "现场分两组 demo：基于 LangChain 的轻量方案 vs 自研向量检索。",
    "下一步将整理现场 Q&A 与代码仓库链接，通过站内信推送给报名用户。"
  ],
  "audio": {
    "url": null,                            // ← null 时禁用播放
    "filename": "recap-2026-05-30.m4a",
    "durationSec": 754,
    "sizeBytes": 9011200
  },
  "stats": {
    "registered": 168,
    "attended": 142,
    "absent": 26,
    "checkinRate": 0.845
  },
  "assets": [
    { "name": "嘉宾 PPT 合集.zip", "sizeBytes": 25165824, "url": null },
    { "name": "现场照片精选.zip",  "sizeBytes": 163577856, "url": null }
  ]
}
```

约定：**`url: null` 时点击播放/下载按钮 → 弹顶部 toast「资料待上传」**；后端就绪后填上真实 `url` 即可无缝切换。

---

## 3. 关键实现要点

### 3.1 文件约束

- 全部代码塞在 `preview.html` 一个文件（项目规则：preview.html 不引入新依赖，沿用 Tailwind CDN + Alpine.js 3.x）。
- 新增 mock 数据放 `<script type="application/json" id="recap-mock">{...}</script>` 节点，避免污染 JS 逻辑。
- Alpine 顶层 `function recapPage() { return { ... } }` 与现有 `authModal()` 并列，互不影响。

### 3.2 路由切换伪代码

```js
// 伪代码：Alpine 状态机
function recapPage() {
  return {
    route: 'home',                  // 'home' | 'recap'
    currentActivity: null,
    toast: { show: false, text: '' },
    init() {
      window.addEventListener('popstate', () => this.syncFromHash());
      this.syncFromHash();
    },
    openRecap(activityId) {
      const data = this.lookupMock(activityId);
      if (!data) return;
      this.currentActivity = data;
      this.route = 'recap';
      history.pushState({page:'recap', id:activityId}, '', '#/recap/' + activityId);
      window.scrollTo(0, 0);
    },
    goHome() {
      this.route = 'home';
      history.back();
    },
    syncFromHash() {
      const m = location.hash.match(/^#\/recap\/([\w-]+)$/);
      if (m) {
        this.currentActivity = this.lookupMock(m[1]);
        this.route = this.currentActivity ? 'recap' : 'home';
      } else {
        this.route = 'home';
      }
    },
    formatSize(bytes) { /* KB / MB / GB 自适应 */ },
    formatDuration(sec) { /* mm:ss */ },
    pendingUpload() { /* 弹 toast「资料待上传」 */ },
  };
}
```

### 3.3 模板关键片段

```html
<!-- 根元素挂双 controller：auth 弹窗 + recap 路由 -->
<body x-data="authModal()" x-data="recapPage()">

<main x-show="route === 'home'">… 现有首页 …</main>

<section id="recap-detail-page" x-show="route === 'recap'" x-cloak>
  <header class="recap-hero">… 标题 + 主办方 + 返回按钮 …</header>
  <article class="recap-overview">
    <template x-for="(p, i) in currentActivity.overview" :key="i">
      <p x-text="p" class="mb-3 leading-relaxed text-ink/85"></p>
    </template>
  </article>

  <section class="recap-audio">
    <audio :src="currentActivity.audio.url" controls preload="metadata"
           :disabled="!currentActivity.audio.url"
           @click.prevent="!currentActivity.audio.url && pendingUpload()"></audio>
    <div class="text-xs text-soft" x-text="… 文件名 + 时长 + 大小 …"></div>
  </section>

  <section class="recap-stats">
    <!-- 4 张统计卡 + 1 条 CSS 进度条 -->
  </section>

  <section class="recap-assets">
    <template x-for="a in currentActivity.assets" :key="a.name">
      <div class="asset-item">
        <span x-text="a.name"></span>
        <span x-text="formatSize(a.sizeBytes)"></span>
        <button @click="a.url || pendingUpload()">下载</button>
      </div>
    </template>
  </section>
</section>
```

### 3.4 可访问性 / 键盘

- 详情页根节点加 `role="region" aria-labelledby="recap-title"`。
- 顶部「← 返回」按钮使用 `<button type="button">`，不用 `<a href="#">`，避免 a 标签触发跳页语义。
- 不引入焦点陷阱（详情页是路由切换而非弹窗），但保留 `tabindex="-1"` + 路由切到 recap 时 `this.$refs.hero.focus()` 提升屏幕阅读器体验。

---

## 4. 验证方法

预览页阶段没有 pytest，验证手段：

1. **静态浏览验证**（手工）：
   - 打开 `preview.html`，分别点 3 个「查看复盘」按钮 → 详情页正确打开对应活动数据。
   - 浏览器「← 后退」回到首页，URL 回到 `/preview.html`。
   - 详情页内点「下载资料」「播放录音」 → 弹 toast「资料待上传」。
   - ESC 不会关闭详情页（这是路由不是弹窗，符合预期）。
2. **浏览器兼容**：Chrome / Edge 最新版 + 移动端宽度（≤ 640px）下排版不破。
3. **接口契约对齐**：在 PR 描述中贴出 §2.3 的 JSON 结构，供后续 Flask 后端 PR 对照。

---

## 5. 影响范围

| 项 | 影响 |
| --- | --- |
| `preview.html` | 顶部导航 home/recap 路由 + 新增 ~150 行（hero / 4 区块 + Alpine 逻辑） + mock 数据 |
| 后端 | **无**（本 PR 不动 Python 代码） |
| 数据库 | **无** |
| 第三方 | **无** |
| 接口契约 | 新增 `GET /api/activities/{id}/recap`（仅约定形状，preview 阶段 mock） |

---

## 6. 后续 PR 候选（不在本 PR 范围）

- `feature/backend-recap-api`：实现 `GET /api/activities/{id}/recap` 真实路由 + PyMySQL 查询
- `feature/recap-markdown`：总概文字接入 Markdown 渲染
- `feature/recap-assets-upload`：复盘资料上传后台（鉴权 + 写 `static/uploads/recap/`）
- `feature/recap-photo-wall`：现场照片墙（瀑布流 + 懒加载）

---

> **本文档维护规则**：本计划落地后归档到 `docs/snapshots/2026-06-11-recap-detail-page.done.md`；后续接口字段有调整需同步更新 §2.3。
