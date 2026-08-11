# SVG Token 高效模板

直接套用：把样式收进 `<style>`，把重复形状收进 `<defs>`，用 `class` 与 `<use>` 复用。视觉与逐元素内联写法**完全等价**，生成 token 减少 **40%–63%**（实测 6 节点片段 -42.7%；30 节点/40 连线量级约 -63%）。

> 本优化只改「写法」，不改「结构」。绝不能为了省 token 而删减「箭头与文字重叠防护」所需的白底衬底或间距——效果优先。

## 最小骨架（网络拓扑 / 架构图）

```xml
<svg viewBox="0 0 680 360" xmlns="http://www.w3.org/2000/svg">
  <style>
    .node{fill:#f3f0ff;stroke:#7c4dff;stroke-width:1.5}
    .nodeB{fill:#e3f2fd;stroke:#1976d2;stroke-width:1.5}
    .label{font-family:sans-serif;font-size:13px;fill:#333;text-anchor:middle}
    .sm{font-size:11px}
    .edge{stroke:#90a4ae;stroke-width:1.5;marker-end:url(#arrow)}
    .edgeG{stroke:#43a047;stroke-width:2;marker-end:url(#arrow)}
    .bg{fill:#ffffff}
    .lg{font-family:sans-serif;font-size:11px;fill:#555}
  </style>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="10" markerHeight="10" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#607d8b"/>
    </marker>
    <g id="box"><rect width="120" height="44" rx="6" class="node"/></g>
    <g id="boxB"><rect width="120" height="44" rx="6" class="nodeB"/></g>
  </defs>

  <!-- 节点：用 <use> 复用，文本用 class 居中 -->
  <use href="#box" x="40" y="60"/>
  <text class="label" x="100" y="87">Peer A</text>
  <use href="#boxB" x="240" y="60"/>
  <text class="label" x="300" y="87">NAT A</text>

  <!-- 连线：用 class，不必逐条写 style -->
  <line class="edge" x1="160" y1="82" x2="240" y2="82"/>
  <line class="edgeG" x1="40" y1="120" x2="360" y2="120"/>

  <!-- 防压字白底衬底：用 .bg 类，再叠文字 -->
  <rect class="bg" x="170" y="74" width="70" height="16"/>
  <text class="label sm" x="205" y="86">srflx</text>
</svg>
```

## 对比（同一 6 节点 / 4 连线片段）

| 写法 | 字节 | 生成 token |
|---|---|---|
| 逐元素内联 `style` | ~1738 | 高 |
| CSS 类 + `<defs>`/`<use>` | ~996 | 低（-42.7%） |

图越大收益越高：30 节点 / 40 连线量级约 **-63%**。

## 要点

- **中文标签**：`class="label"` 已含 `text-anchor:middle`，只需给 `x` 为节点中心、`y` 为文字基线。
- **多尺寸节点**：在 `<defs>` 多定义几个 `<g id>`（如 `#box`、`#boxB`、`#small`），`<use>` 时只传 `x`/`y`。
- **小号字**：定义 `.sm{font-size:11px}`，用 `class="label sm"` 叠加，避免内联 `style`。
- **颜色变量**：仍优先用 `read_me diagram` 提供的主题色值，保持主题一致；类里直接写色值即可。
- **白底衬底**：统一用 `.bg{fill:#ffffff}`，防压字时 `<rect class="bg" .../>` 复用，不重复写 `fill`。
