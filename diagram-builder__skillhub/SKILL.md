---
name: diagram-builder
description: "专业架构图与流程图绘制 skill。绘制系统架构图、微服务架构、网络拓扑图、业务流程图、数据流图、时序图、状态机、ER图等。支持 show_widget 内联 SVG 渲染与 Mermaid 代码块两种方式。触发关键词：架构图、流程图、时序图、状态机、拓扑图、ER图、数据流图、draw、diagram、flowchart、architecture。"
agent_created: true
---

# diagram-builder — 架构图与流程图绘制 Skill

## 概述

本 skill 提供两种图表绘制方式：

1. **内联可视化（推荐）**：调用 `read_me` + `show_widget` 工具，在对话中直接渲染精美 SVG/HTML 图表。
2. **Mermaid 代码块**：在 Markdown 中输出 Mermaid 语法，适合需要嵌入文档的场景。

---

## 方式一：内联 SVG/HTML（show_widget，推荐）

### 触发时机

凡用户明确要求"绘制"、"画出"、"可视化"某类图表，或对话内容用图表呈现比文字更清晰时，优先使用此方式。

### 操作步骤

1. **先调用 `read_me` 加载设计模块**：纯静态 SVG 架构/流程图只传 `["diagram"]`（获取 CSS 变量、颜色、排版规则）；**仅当图表含 HTML 交互控件（按钮、滑块、动态切换）时才追加 `"interactive"`**。避免为静态图加载多余模块，减少上下文 token 消耗。
2. **再调用 `show_widget`**，传入原始 SVG 或 HTML 片段。
3. SVG 必须以 `<svg>` 标签开头，viewBox 格式为 `0 0 680 <height>`，宽度固定 680px。
4. 禁止包含 `<!DOCTYPE>`、`<html>`、`<head>`、`<body>` 标签。

### 图表类型与示例

参考 `references/diagram-types.md`，其中包含以下图表类型的 SVG 骨架与最佳实践：

- 系统架构图（分层盒子 + 箭头）
- 微服务 / 云原生架构图（服务网格、API Gateway、数据库集群）
- 网络拓扑图（节点 + 连线）
- 业务流程图（泳道图、决策菱形）
- 数据流图（数据源 → 处理 → 存储 → 输出）
- 时序图（角色 + 时序线 + 消息箭头）
- 状态机图（圆角矩形状态 + 转换箭头）
- ER 图（实体矩形 + 关系线）

### SVG 设计规范

- **颜色**：加载 `read_me diagram` 后按其 CSS 变量定义使用，保持整体一致性。
- **字体**：系统默认无衬线字体，中文内容使用 `font-family="sans-serif"`。
- **间距**：组件间距不少于 16px，文字与边框间距不少于 8px。
- **箭头**：使用 SVG `<marker>` 定义 arrowhead，保持风格统一。
- **箭头与文字重叠防护（关键！）**：参见 `references/arrow-text-clearance-guide.md`。箭头尖端 10px 禁区内禁止放文字；地址/序号标注放进节点框内或两列留白 gap，箭头在节点边框前停 ≥12px；凡文字可能与连线共区，先画 `fill="#ffffff"` 矩形衬底再画文字。
- **分组**：用 `<g>` 元素对同类节点分组，复杂图表使用 `<rect>` 作为容器背景框。
- **图例**：复杂图表右下角添加图例说明颜色/形状含义。

### Token 高效 SVG 写法（关键！）

出图应优先用 **CSS 类 + `<defs>`/`<use>` 复用**，而非逐元素重复内联 `style`。同等视觉效果下，生成 token 可减少 **40%–63%**（实测 6 节点片段 -42.7%；30 节点/40 连线量级约 -63%）。规则：

- **样式集中到 `<style>`**：把 `fill`/`stroke`/`font` 等抽成类（如 `.node`、`.edge`、`.label`、`.bg`），元素用 `class="..."` 引用，杜绝每个 `<rect>`/`<text>` 重复写 `style="..."`。
- **形状用 `<defs><g id="node">` 定义一次，`<use href="#node" x= y=>` 多次实例化**：同尺寸节点只定义一次。
- **白底衬底也用类**：防压字的 `fill="#ffffff"` 矩形统一用 `.bg{fill:#fff}`，避免逐条重复。
- **坐标精简**：同列节点用统一 `x`、文本用 `text-anchor` 居中，减少坐标拼写。

参考 `references/svg-efficient-template.md` 获取可直接套用的最小模板（含 `<style>` 类集 + `<defs>` 节点/连线/白底定义）。

### 箭头 Marker 规范（关键！）

参考 `references/svg-marker-guide.md` 获取完整箭头定义规范。核心要点：

- **方向规则**：marker 的路径必须朝右（+x 方向），三角形尖端在 x 最大值处。`orient="auto"` 会自动沿线的方向旋转，所以朝右的路径在竖线上会自然旋转为朝下。
- **尺寸规则**：`markerWidth` 和 `markerHeight` 必须 **≥ viewBox 宽高**，否则视口裁切会导致箭头只剩一半或方向错乱。
- **refX/refY**：`refX` 放到路径尖端 x 坐标、`refY` 放 y 中心，确保尖端精确对齐线尾。
- **图例中的箭头**：图例行内的水平箭头线同样使用向下 marker，`orient="auto"` 会自动适配水平方向。

### 箭头与文字重叠防护（关键！）

参考 `references/arrow-text-clearance-guide.md` 获取完整规则。核心要点：

- **箭头尖端禁区**：marker 落点周围 10px 半径内禁止放任何文字，否则箭头会盖住字。
- **标注进留白/节点内**：地址、序号等注释放进两列 gap 或节点框内，箭头在节点边框前停止（留 ≥12px 间隙），不压字。
- **白底衬底**：凡文字可能与连线共区，先画 `fill="#ffffff"` 矩形衬底再画文字，彻底防压字。
- **线与线/线与字净空**：文字与连线 ≥6px，同区两线 ≥20px。

### 分层架构图布局规范

参考 `references/architecture-layout-guide.md` 获取完整分层布局指南。核心要点：

- **层级分组框**：每层用 `stroke-dasharray` 虚线圆角矩形包裹所有同层组件（标题条 + 子组件），左上角标注层号。
- **层间箭头间距**：至少 40px，箭头上端距上层框底 8px、下端距下层框顶 8px，确保箭头完整可见。
- **viewBox 高度**：先计算所有内容底部坐标 + 图例高度 + 16px 余量，再四舍五入取整。宁大勿小，避免末尾元素被裁切。
- **图例位置**：固定在最底部独立区域，与最下层内容保持 ≥16px 间距，横排紧凑布局。

---

## 方式二：Mermaid 代码块

当用户需要在文档中嵌入图表，或明确要求 Mermaid 语法时使用。

### Mermaid 常用图表类型

```
flowchart TD        # 自上而下流程图
flowchart LR        # 从左到右流程图
sequenceDiagram     # 时序图
stateDiagram-v2     # 状态机
erDiagram           # ER 图
classDiagram        # 类图
gantt               # 甘特图
graph               # 通用图
```

参考 `references/mermaid-cheatsheet.md` 获取完整语法速查与示例模板。

---

## 常见问题（FAQ）

绘制前、中、后拿不准时，**先查 `references/faq.md`**，覆盖四类高频问题：
- **能力范围**：饼/柱/折线（→chart 模块）、思维导图、3D/地图、PNG 直出、反向工程等越界请求的替代方案。
- **格式与输出**：内联图 vs Mermaid 代码块怎么选、关键字易错点、复杂图拆分。
- **渲染异常**：箭头裁切/反向、文字被压、中文乱码、图被裁掉的自查与修复。
- **请求越界怎么办**：不在支持范围或格式不清时，主动告知「不支持+原因+替代」并停下等确认，**不硬画**。

> 另：`references/diagram-types.md` 开头有「**反模式速查清单**」，逐条列出会出问题的做法与正确替代，绘制前后对照可避坑。

---

## 异常处理与主动提示（能力边界）

> 本 skill 在「异常不主动提示」上体验偏弱：**若请求了不支持的图表类型、或格式/范围不清，必须第一时间主动告知用户，而不是硬画一个错的图让用户自己排查。** 完整矩阵、前置澄清话术与出错标准话术见 `references/capability-and-exceptions.md`，绘制前务必过一遍。

核心规则：

1. **能力边界先确认**：动手前先对照支持矩阵（架构/流程/时序/状态机/ER/类图/甘特/通用图 ✅；饼柱折线等统计图、思维导图、3D/地图、PNG 直出、反向工程 ❌）。落在 ❌ 区时，**第一句就说明「不支持 + 原因 + 替代方案」并停下等确认**，绝不硬套 SVG 强行画。
2. **前置澄清三问**：输出形态（内联图 / Mermaid 代码块 / SVG 源码文件）、图表类型、范围粒度——任一项不清就用 ≤3 选项提问确认，不猜。
3. **渲染前自检**：发送 show_widget 前逐条核对 viewBox=680、无 DOCTYPE/html 标签、marker 尺寸 ≥ 视口、箭头禁区无字、中文 `sans-serif`；任一不过先改再发。
4. **出错主动交代**：任何异常按「现象 → 原因 → 建议/修复」三段式回复，由 agent 定位并修复或给替代，**用户不需要自己排查**。

---

## 绘图原则

1. **先理解，再绘制**：完整理解用户意图后再动手，必要时确认组件和关系。
2. **边界前置、异常主动**：绘制前确认类型在支持范围内、格式/范围已澄清；一旦越界或出错，主动、明确告知用户（哪里错 + 原因 + 修复/替代），绝不静默失败。
2. **分层清晰**：架构图按"前端 → 后端 → 数据层 → 基础设施"等层次布局，避免交叉。
3. **信息密度适中**：单张图不超过 20 个节点；复杂系统拆成多张图分步展示。
4. **中文友好**：节点标签支持中文，保证编码和字体兼容。
5. **复杂图分多个 show_widget**：一个 show_widget 表示一个聚焦视角，多图配合文字解释形成完整叙述。

---

## 快速参考

| 用户意图 | 推荐方式 | 参考文件 |
|---------|---------|---------|
| 系统/微服务架构图 | show_widget SVG | references/diagram-types.md |
| 业务流程 / 泳道图 | show_widget SVG 或 Mermaid flowchart | references/diagram-types.md |
| 时序图 | show_widget SVG 或 Mermaid sequenceDiagram | references/mermaid-cheatsheet.md |
| 状态机 | show_widget SVG 或 Mermaid stateDiagram-v2 | references/mermaid-cheatsheet.md |
| ER 图 | show_widget SVG 或 Mermaid erDiagram | references/mermaid-cheatsheet.md |
| 嵌入 Markdown 文档 | Mermaid 代码块 | references/mermaid-cheatsheet.md |
| 类型不在支持范围（饼/柱/思维导/3D/地图/PNG直出等） | **先主动告知不支持 + 原因 + 替代方案，等确认** | references/capability-and-exceptions.md |
| 格式 / 范围 / 输出形态不清 | **前置澄清三问后再画** | references/capability-and-exceptions.md |
| 拿不准 / 出错 / 请求越界 | **先查 FAQ，按反模式与越界路径处理** | references/faq.md · references/diagram-types.md（反模式清单） |
