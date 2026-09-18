---
name: dashi-ppt-media-slot-avoidance
description: 用 dashi-ppt 生成 PPT 时，避开自带图片槽的页面组件——这类组件即使用户不要图，也会在成品里渲染出可见的"＋ 上传 / 拖入或点击上传"占位，导致交付失败。提供按主题实测的无媒体槽 layout 白名单、选页校验步骤、以及渲染导出环节的踩坑处理。触发词：dashi-ppt 图片占位、上传占位、拖入或点击上传、PPT 出现上传框、不要图片槽、dashi 选页。
agent_created: true
---

# dashi-ppt 图片槽避坑

## 问题

dashi-ppt 的部分页面组件**内置图片槽**。当用户明确说"不要图片"时，只靠
`layout:query` / `inspect:layout` 判断不可靠——有些组件 `mediaSlots` 显示为空，
但渲染时仍会铺出可见的图片占位（"＋ 上传" / "拖入或点击上传"），并带一个上传按钮。

**后果**：用户打开 PPT 看到一堆"上传"框，交付失败。

## 判断原则

1. **不要相信 `inspect:layout` 的 `mediaSlots` 字段就能筛干净**。必须用最终产物反查。
2. **无媒体槽不等于无占位**。已实测：`theme09_page088`（跨栏图景）、`theme09_page082`（影像纪程）、
   `theme09_page106`（专题洞察）在 `inspect:layout` 里 `mediaSlots` 是空数组，
   但渲染出的 PPTX 里有可见的上传占位。
3. **唯一的可靠判定 = 导出 PPTX 后用 python-pptx 全文扫描**。

## 交付前必做的反查

```bash
python -c "
from pptx import Presentation
p=Presentation('输出.pptx')
bad=[]
for i,s in enumerate(p.slides,1):
    txt=[sh.text_frame.text.strip() for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    for t in txt:
        for w in ['上传','拖入','请输入','据此推演','AI Capital','SoundWave','Roadmap','Key Metrics','End of Report']:
            if w in t: bad.append((i,t[:40]))
print('模板残留:', bad if bad else '无')
"
```

残留清单里有"上传/拖入"→ 该页 layout 必须换。
清单里只有"据此推演如右""各轮次""分布"→ 属于组件固定装饰文案，不在 `copyKeys` 里、改不掉；
语义中性时可接受，否则换页。

## theme09 实测 layout 黑白名单

### 无图片槽（可安全使用）

| layout | 名称 | 结构 | 备注 |
|---|---|---|---|
| `page101` | 篇章卡 | 章节号+标题+4~6 条索引 | 章节页首选 |
| `page102` | 核心要点 | 引导句 + 3~6 条（标题/描述） | 清单型 |
| `page104` | 实施路径 | 2~6 个步骤 + 结论条 | 流程型 |
| `page105` | 关键问答 | Q/A 列表 3~6 条 | 拆解"表面→真相"很好用 |
| `page029` | 核心结论 | 3 条（维度/标题/英文/描述）+ 总结 | |
| `page032` | 归纳括弧 | 3~5 条短句 + 结论块 | 概念页首选，`items[].text` 限 20 字 |
| `page034` | 轮次结构 | 6 条双指标 + 洞察 | 有"各轮次/分布"固定装饰词 |
| `page053` | 金句主张 | 5 段短句 | |
| `page054` | 批注精读 | 正文分段 + 3~4 条批注 | 叙事型 |
| `page068` | 交集视图 | 2~3 集合 + 核心区 + 旁注 | 收束/总结首选 |
| `page019` | 论点推演 | 3~5 前提 + 结论 | 有"据此推演如右"固定装饰词 |

### 带图片槽（不要用）

`page022` 典型案例、`page024` 分镜脚本、`page060` 双联对照、
`page082` 影像纪程、`page088` 跨栏图景、`page106` 专题洞察、`page052` 观点引述。

## 其他选页硬约束（theme09 实测）

- **`page103`（多维对比）**：`rows[].cells` 固定长度 5，`ratingMax` 必须是数字。
  不适合简单叙事——narration 塞进去会连环报错。
- **`page050`（关键指标）**：`stats[].spark` 是定长嵌套数组，且
  `write-safe-props` 与 `validate-goal-spec` 两套校验器对该字段口径冲突
  （一个要求 5 个点、一个限制最多 4 个）。**直接避开这个 layout**。
- **`page098`（布局路线）**：泳道 + 里程碑结构过于复杂，不适合非专业受众。
- **`items[].text` 类短槽（如 `page032`）限 20 字**，超了会被 `validate-goal-spec` 拦。
  这反而有助于把概念写短——顺势压缩即可，不要为了塞字换 layout。
- **layout 必须全局唯一**，同一页组件不能用于两个内容页。

## 环境与流程踩坑

1. **首次生成必须先 `npm install`**（在 `<skill-root>/project` 下）。
   缺 node_modules 时报 `Cannot find package 'react' imported from src/renderDeck.jsx`，
   而 `render_goal_deck.ps1` 的前置安装检测会被跳过（有 `.npmrc` 时逻辑顺序问题），
   表现是 PowerShell 执行返回 exit code 1 且**不输出任何错误**。

2. **PowerShell 工具在本机可能吞掉所有输出**（含报错）。定位问题时绕开它，
   直接用 Bash 调 `npx tsx scripts/render-goal-deck.jsx <goal> <out>`。

3. **渲染/导出会卡住不返回**。用这种形式跑，不要直接管道接 `tail`：

   ```bash
   (node scripts/export-pptx.mjs <deck/ppt> <out.pptx> > /tmp/e.log 2>&1 &)
   sleep 50; cat /tmp/e.log
   ```

4. **预览服务无法在沙箱常驻**（`start-preview-server.mjs` 起的进程随命令结束退出，
   后续 `curl`/`node` 探测都是 ECONNREFUSED）。
   **不要在这上面反复重试**——直接用 `export-pptx.mjs` 导出文件交付。
   该脚本自带临时服务，不依赖常驻预览。

5. **预览服务的工作目录要指向 `ppt/` 子目录**，不是 deck 根目录
   （否则报 `Preview index.html not found`）。

6. **`goal.json` 会被 `props:safe --write` 重写**（缩进、数组展开）。
   之后再想用 Edit 精确替换会失配——改用 python 载入 json、改对象、dump 回去。

## 标准流程

```bash
# 1. 装依赖（仅首次）
cd <skill-root>/project && npm install

# 2. 写 goal.json 到工作区 output/<deck>/goal.json

# 3. 规范化 + 校验（每一步都要看 errorCount）
node scripts/write-safe-props.mjs --goal <goal> --write
node scripts/validate-goal-spec.mjs --goal <goal>

# 4. 渲染（避开 PowerShell，用后台重定向）
(npx tsx scripts/render-goal-deck.jsx <goal> <deck/ppt/index.html> > /tmp/r.log 2>&1 &)
sleep 45; cat /tmp/r.log

# 5. 输出后校验
node scripts/validate-swiss-deck.mjs <deck/ppt/index.html>
node scripts/validate-goal-copy.mjs <goal> <deck/ppt/index.html>

# 6. 导出 PPTX
(node scripts/export-pptx.mjs <deck/ppt> <out.pptx> --title "<标题>" > /tmp/e.log 2>&1 &)
sleep 50; cat /tmp/e.log

# 7. 反查模板残留（见上文脚本）—— 这一步不能省
```

## 验收清单

- [ ] `write-safe-props` 全部页面 errorCount = 0
- [ ] `validate-goal-spec` / `validate-swiss` / `validate-goal-copy` 三项通过
- [ ] 导出 PPTX 页数与设计一致
- [ ] **python-pptx 反查：无"上传/拖入/请输入"残留**
- [ ] 无与主题无关的模板文案（AI Capital / SoundWave / 投融资 等）
- [ ] 各页文字与设计稿一致，无串页、无空页
