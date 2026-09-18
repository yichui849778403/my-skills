---
name: pptx-restyle-migration
description: 把一份 PPT 的布局和文字搬到另一套视觉规范里重建（跨母版迁移 / 换风格 / 去花哨）。适用于：把 AI 生成的 HTML 系 PPT（dashi-ppt 等）刨掉装饰、按用户自己的培训 PPT 母版重画；把任意来源的 PPTX 内容迁进既有系列 PPT 并接续页码。触发词：风格迁移、换母版、把布局搬过来、去掉花哨、按我的模板重做、把这几页插到我的 PPT 里。
agent_created: true
---

# PPTX 跨母版迁移

把源 PPT 的**布局结构 + 文字**保留，视觉按目标母版**逐页重画**，产出接续原系列的新 PPTX。

核心认知：这不是"套母版"（换主题不会重排结构），而是**看懂一页、重画一页**。所以能做到"原版花哨 → 结果克制"这种落差。代价是逐页手工，页数一多必须归并结构类型（见末节）。

## 流程

1. **读源**：解包源 PPTX，逐页看清区块结构（几个块、什么关系：三卡/数字/分栏/时间线/对比）和全部文字。
2. **提目标规范**：解包目标母版 PPTX，提取它的设计令牌（配色、透明度、字号层级、栅格边距、母版/版式继承关系）。
3. **重画**：按目标栅格重排每一页。**保留区块结构与文字，丢弃源的装饰**（网格线、发光、多余装饰形状、空白占位图）。
   - 先只做 1 页、导 PNG 看，**量出标题占位符真实底边和卡片视觉圆角**，再定其余页的内容起点。一次性写满几十页再校对，返工量大得多。
4. **插页**：新页插进目标 PPT 的指定位置，接续编号。
5. **校验**：导出 PNG 逐页看（PowerPoint COM），再比对 zip 部件清单确认没丢部件。

## 关键技术要点（踩过的坑）

1. **画布差异不要盲缩放**。源可能是 16×9 英寸（14630400×8229600 EMU），目标是 13.333×7.5 英寸标准 16:9。缩放系数虽接近 0.833，但**按目标自己的栅格重排更干净**。
2. **新页挂目标版式即可继承背景**，不用自己画底。背景在母版的装饰形状里（如深蓝渐变 + 胶片颗粒纹理），挂上版式自动带。
3. **标题用空占位符继承格式**：`<p:ph type="title"/>`，位置、字号全部来自母版/版式，不用手写。
4. **插入页免 python-pptx 建页的坑**（直接当 zip 操作）：
   - 新建 `ppt/slides/slideNN.xml` + 同名 `_rels`，rels 内**只留 rId1 → slideLayoutN.xml，不带 notesSlide**（带了会导致多页共用同一 notes 部件）
   - `[Content_Types].xml` 补 N 条 Override
   - `ppt/_rels/presentation.xml.rels` 追加 N 条 Relationship（rId 从现有最大值 +1 起）
   - `ppt/presentation.xml` 的 `<p:sldIdLst>` 按目标位置插 `<p:sldId>`（id 从现有最大值 +1 起，**不必与文件号对应**）
   - 重打包，`[Content_Types].xml` 放第一个
5. **校验手段**：PowerPoint COM 导幻灯片 PNG 逐页看，比文本 dump 可靠得多；再用 `zipfile` 比对 namelist（如 484 → 502，只多不少）。同时逐部件比对字节，确认"只改了 presentation.xml / presentation.xml.rels，其余原部件一字未动"。
6. **只改新建页**，源母版 PPT 的既有页面一律不动（用户明确要求时再动）。
7. **每个 run 必须包在 `<a:r>` 里 —— 这是最贵的一个坑**。辅助函数若设计成"直接把文本拼进 `<a:p>`"，会在 `<a:pPr>` 后留一段裸文本：lxml 能解析、python-pptx 能打开、zip 也完整，但 **PowerPoint 会直接报「PowerPoint could not open the file」拒绝打开**。所以：文本参数一律先过 `run()` 生成 `<a:r>`；写个 `_as_runs()` 兜底（`str` 或 list 都能吃）。**报"打不开"时先怀疑内容结构，别去查环境/进程/权限。**
8. **大卡片的圆角要显式压**。`prstGeom prst="roundRect"` 默认 `adj=16667`（短边 16.667%）——0.5 in 的行卡圆角 0.08 in 正好，但 3.4 in 高的大卡圆角会到 0.58 in，一眼假。给 `h > 1.0 in` 的卡显式加 `<a:avLst><a:gd name="adj" fmla="val N"/></a:avLst>`，`N = 目标圆角in / h * 100000`（本次统一 0.11 in），小卡保持默认不动。
9. **表格行卡的"行高 + 间距"要留缝**。行高 == 间距（gap 0）会让多行卡片连成一整块。gap 至少 0.12 in，视觉上才读得出"这是一行行的"。
10. **小标签别贴着标题占位符的底边猜**。标题占位符在 PPT 里没有显式 xfrm、从母版继承，实际底边比"32pt 一行"高（本次实测约 1.05 in）。标题下方的小标签（kicker）放 y ≥ 1.18 in 才不压字。**先出一版 PNG 量一下真实底边**，再定内容起点，比一次性算准靠谱。
11. **PowerShell 工具偶发不回传 stdout**（exit code 0 但无输出）。COM 导出这类任务改成"把过程写进日志文件，再用 Read 读回"，顺便还能留下可复查的导出记录。


## 脚本范式（XML 直构，勿用 python-pptx 建页）

```python
EMU = 914400
def E(v): return int(round(v * EMU))          # inch -> EMU，全脚本统一用 inch 思考

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def run(t, sz=1400, color='EAF1FA', b=False, alpha=None, spc=None):
    # -> <a:r>，含 srgbClr(+可选 alpha) + latin Arial / ea 微软雅黑
def para(rs, algn=None, lnspc=100000):
    # rs 必须是 run() 拼好的字符串；-> <a:p>（lnSpc + buNone）
def tb(ids, x, y, w, h, paras, anchor='t'):
    # -> <p:sp> 文本框；bodyPr lIns/tIns/rIns/bIns=0 + noAutofit + 无填充无边框
def card(ids, x, y, w, h, fill=None, prst='roundRect'):
    # -> <p:sp> 底卡；h > 1.0 in 时自动压圆角 avLst
def chips(ids, y, h, items):                   # 等宽横排小卡
    # items 元素可为纯文本或已拼好的 <a:r> 片段 —— 用 str.startswith('<a:r>') 判断后补 run()
```

**铁律：任何要显示的文字都必须先过 `run()`。** 别让 `para()` 直接吃裸字符串（见"踩过的坑"第 7 条）。
`ids` 是页内自增 id 计数器，每个 shape 取一个（spTree 的 `nvGrpSpPr` 固定占 id=1）。

每页写成一个 `pageN(num)` 函数，返回整页 XML，追加到 `PAGES = [...]`；`main()` 里先对新页做 XML 自检，再合并进 zip。

## 目标母版的实测令牌（2026年网络安全培训 V6.x 系列）

> 换系列时以当期母版为准，下面这组是 V6.x 实测值。

- 画布 13.333×7.5 in；版式 `ppt/slideLayouts/slideLayout3.xml`（名称"仅标题"）
- 母版 `slideMaster1.xml`：`矩形 6` 深蓝渐变底（`1A376F`→`122A58`→`091428`）、`矩形 8` 5% 胶片颗粒纹理
- 标题：`<p:ph type="title"/>` 空占位符，左上角，继承后 32pt 粗体。**必须显式写 `<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>`** —— 母版 `titleStyle` 用的是 `schemeClr bg1`，而 layout3 的 `clrMapOvr` 把 `bg1→dk1`，不显式指定会渲染成深色。**标题占位符实测底边 ≈ 1.05 in**
- 页码：`<p:ph type="sldNum" sz="quarter" idx="12"/>`，`rPr` 色 `EAF1FA`，`<a:fld>` 的 id 复用 `{5DD3DB80-B894-403A-B48E-6FDC1A72010E}`；缓存文本填正确页码（渲染时 PowerPoint 会重算）
- 栅格（两套坐标并存，别混）：标题占位符左边界 `0.72 in`；**卡片左边界 `MX=1.15`、卡片宽 `CW=11.02`（右边缘 12.17）**；行内文字左 `TX=1.64`（卡内左右各内缩 0.49）
- 纵向节奏：kicker `1.20` / 页首说明 `1.54` / 表格表头 `≈2.3–2.5` / 底部结语 `≈6.30`
- 卡片：`roundRect` + `FFFFFF` alpha **14902**，无边框；强调卡 `3B82F6` alpha **45000**；红卡 `EF4444` alpha 15000；小 chip `FFFFFF` alpha 25000；大卡圆角压到 0.11 in
- 文字：白 `FFFFFF` / 主 `EAF1FA` / 说明 `D8E2F0` / 弱化 `94A3B8` / 副标题 `CBD5E1`
- 强调色：蓝 `38BDF8`、青 `22D3EE`、绿 `22C55E`、黄 `FFC000`、红 `FF4D4F`、红卡底 `EF4444`
- **"表格"不是真表格**（无 `graphicFrame`）：= 一行表头文本框（11pt `94A3B8`）+ 每行一张 roundRect 卡 + 卡内若干 `anchor="ctr"` 文本框按列 x 定位。列 x 自行按内容宽度分配即可
- 字号参考：kicker 1100 / 页首说明 1700 / 表头 1100 / 卡内主文字 1500–1600 / 卡内说明 1150–1250 / 大数字 1800–2400 / 底句 1600 / 章节页大标题 3200


**风格基调：克制。** 一页 = 一个底 + 几个淡卡片 + 文字。宁可少装饰、多留白。

## 放大到几十页时的做法

逐页手写不划算（7 页 ≈ 575 行）。先归并结构类型：

1. 拿既有系列 PPT（如 V6.2 的 93 页）当样本，统计它实际用了哪几种页面结构
2. 拢成十几种（标题+三卡、标题+大数字、左右分栏、时间线/流程、对比表、案例分步、章节页、结尾页……）
3. 每种写一个画法函数，之后按页套用

从"每页写一遍"变成"每类写一遍"。

## 相关

源若是 dashi-ppt 生成的 HTML 系 deck：其导出 PPTX 为 PptxGenJS 输出（形状名 `Shape 0/1/2…`、无占位符、画布 16×9 英寸），正好适合当"布局来源"。但 dashi 的 layout 与主题强绑定、视觉写死在组件里，拿不到"纯布局"；结构语义要从它的 `goal.json`（`layout` + `props`）读，比从 pptx 反推几何可靠。
