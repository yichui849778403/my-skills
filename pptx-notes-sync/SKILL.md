---
name: pptx-notes-sync
description: PPT 演讲者备注的批量操作，两种用途：(a) 把一份 PPT 的备注整页搬运到另一份同结构 PPT（页数、顺序一致，例如"换皮版""新配色版"）；(b) 整份删掉 PPT 的备注，用于发客户前清稿。触发词：备注复制、备注搬过去、把备注同步到另一个PPT、notes 同步、V6备注搬到V7、去掉备注、删除备注、清除备注、把ppt的备注去掉、发客户前清备注。核心结论：不要用本地 editor_sdk 的 slide_set_notes_text / slide_add_notes 做这类批量备注操作——搬运时它把整页备注写成单个段落，换行变成字面 &#13;/&#10;，PowerPoint 备注区会挤成一坨（正确做法是 python-pptx 直接复制 notesSlide 的 <a:p> 段落）；删除时它只能清空文本、留下空备注页，且保存 pptx 会重组 ppt/media/* 目录，"其它别动"的要求满足不了（正确做法是包级手术删 notesSlides 部件）。scripts/ 下有 strip_notes.py 与 verify_no_notes.py 可直接用。
agent_created: true
---

# PPT 演讲者备注跨文件搬运

## 适用场景

两份 PPT 页数一致、页序一致（同源的不同版本：换配色、换 logo、文案微调），
需要把 A 的演讲者备注原样搬到 B，且**保留段落分行**。

判断前提：先用 python-pptx 逐页比对两版的可见文本，差异应只出现在少数页（文案微调），
不存在插入/删除页。**页数或页序不一致时不要用本流程**（会串页），先与用户确认页对应关系。

## ⚠️ 关键坑：不要用 editor_sdk 写备注

`tencent-local-office-edit`（editor_sdk）的备注工具：

- `slide_add_notes` / `slide_set_notes_text` 只接受**纯文本**；
- 实测（2026-09 验证）传入含 `\r` 或 `\n` 的文本时，编辑器把换行写成
  **a:t 内部的字面字符** `&#13;` / `&#10;`，并且整页备注只有 **1 个 `<a:p>`**；
- 结果：PowerPoint 备注区不换行，讲稿挤成一坨，**不可用**；
- 与此配套的是 `slide_get_notes_text`，它读出的文本以 `\r` 作段落分隔符，
  只能用于"取到文字"，不能用来往返（读出来再写回去就丢段落）。

结论：备注的**结构化搬运**走 python-pptx，不要走 editor_sdk。

## 正确做法（XML 级复制段落）

从**目标文件的原始备份**出发（不要从 editor_sdk 保存过的文件出发，避免媒体被重组等副作用），
逐页把源文件的 `<a:p>` 段落深拷贝到目标备注文本框的 `txBody` 里：

```python
from copy import deepcopy
from pptx import Presentation
from pptx.oxml.ns import qn

src = Presentation(V6_PATH)
dst = Presentation(TARGET_BAK_PATH)          # 目标文件的原始备份
assert len(src.slides) == len(dst.slides)

for ss, ds in zip(src.slides, dst.slides):
    s_tx = ss.notes_slide.notes_text_frame._txBody
    d_tx = ds.notes_slide.notes_text_frame._txBody   # 无备注页时会自动创建（需 notesMaster 存在）
    for p in d_tx.findall(qn('a:p')):                # 清掉目标原有段落
        d_tx.remove(p)
    for p in s_tx.findall(qn('a:p')):                # 原样搬运源段落（含 run 级格式）
        d_tx.append(deepcopy(p))
    if not s_tx.findall(qn('a:p')):                  # 保底：避免出现零段落的 txBody
        d_tx.append(d_tx.makeelement(qn('a:p'), {}))

dst.save(OUT)
```

要点：

- 只复制 `<a:p>`，保留目标 `txBody` 的外壳（`bodyPr` / `lstStyle`），版式设置不串味；
- `deepcopy` 会带上 run 级字体、字号、颜色，备注格式与源文件一致；
- `ds.notes_slide` 在目标没有备注页时会自动新建，不需要先手工建页；
- 目标文件里本来就有备注页的页（哪怕空文本）直接复用，同样逻辑即可。

## 强制收尾动作

1. **先备份**目标文件为 `xxx.bak.pptx`（Python 的 `shutil.copy2` 即可），源文件不动。
2. 若目标文件当前在 editor_sdk 池里（用过 `get_pool_status` 能看到），
   **先 `close_file` 关掉实例再覆盖磁盘文件**，否则脏实例可能回写覆盖结果。
3. 输出到临时文件 → 校验通过 → 再覆盖正式文件。

## 校验清单（缺一不可）

```python
# 1) 页数、段落总数、逐页段落文本
paras = lambda f: [[p.text for p in s.notes_slide.notes_text_frame.paragraphs]
                   for s in Presentation(f).slides]
assert len(paras(src)) == len(paras(out))
assert sum(map(len, paras(src))) == sum(map(len, paras(out)))   # 段落总数必须相等
assert [i for i,(x,y) in enumerate(zip(paras(src), paras(out))) if x!=y] == []
```

2. **媒体资源零改动**：比较目标 `bak` 与最终文件的 `*/media/*` 条目数与内容 MD5，
   两者必须完全一致（证明换皮、logo 都没被动过）。
3. **PowerPoint 实测**：用 PowerPoint COM 打开最终文件，读 `Slides.Item(n).NotesPage`
   的 `TextFrame.TextRange.Paragraphs().Count`，与源文件对应页的段落数比对；
   同时 `Slide.Export(..., "PNG", 1280, 720)` 导几张图肉眼确认版式没坏。
   COM 脚本里尽量用**纯 ASCII 路径**（先把文件复制到 `%LOCALAPPDATA%\Temp\...`），
   规避 PowerShell 5.1 读含中文路径脚本时的编码问题。

## 常见陷阱

- 用 python-pptx 读备注文本时，`\n` 是段落分隔、`\x0b` 是段内软换行（`a:br`）；
  两文件"文本看起来一样"不等于结构一样，**必须比对段落数**。
- 两份 PPT 除了备注，可能还有少数页的正文文案差异（如把否定句式改掉）。
  搬完备注后**主动检查这些差异页**：备注里若提到被改掉的措辞，需要同步微调并告知用户。
- editor_sdk 保存 pptx 会把 `ppt/media/*` 重组到 `ppt/slides/media`、`ppt/slideLayouts/media` 等目录
  （PowerPoint 打开正常，但文件结构变了）。这就是本流程坚持"从原始备份出发"的原因。

---

# 用途 B：整份删除备注（发客户前清稿）

## 适用场景

"把 ppt 的备注去掉，我发给客户用的"——备注是内部讲稿，不能外发。
要求通常是**只删备注、其它一点都别动**（含版式、图片、图表、动画）。

## 做法：包级手术，别去逐页清文本

备注内容存在 `ppt/notesSlides/notesSlideN.xml`，由 `ppt/slides/_rels/slideN.xml.rels`
里的 `.../relationships/notesSlide` 关系引用。**删掉部件 + 删掉关系 + 删掉
`[Content_Types].xml` 里的 Override**，备注页就整体消失。

不要走的两条路：

- **editor_sdk**：`slide_set_notes_text` 只能写纯文本，把备注清成空串后
  **空备注页还在**（客户在 PowerPoint 里翻到备注页仍会看到空页），
  且保存时会重组 `ppt/media/*` 目录，违反"其它别动"。
- **python-pptx 往返保存**：虽然 `slide.part.drop_rel()` 能摘掉关系、
  内容类型也会自动重生成，但整包 XML 会被重新序列化，无法证明"除备注外零改动"。

正确做法（zip 级复制，未改动的条目**逐字节照搬**）：

```python
import zipfile, re
NOTES = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
zin = zipfile.ZipFile(SRC, "r")
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for info in zin.infolist():
        name = info.filename
        if name.startswith("ppt/notesSlides/"):      # 1) 丢部件（含其 rels）
            continue
        data = zin.read(name)
        if name.startswith("ppt/slides/_rels/") and name.endswith(".rels"):   # 2) 摘关系
            s = data.decode("utf-8")
            data = re.sub(r'<Relationship\b[^>]*Type="' + re.escape(NOTES) + r'"[^>]*/>',
                          "", s).encode("utf-8")
        elif name == "[Content_Types].xml":          # 3) 摘 Override
            s = data.decode("utf-8")
            data = re.sub(r'<Override\b[^>]*PartName="/ppt/notesSlides/[^"]*"[^>]*/>',
                          "", s).encode("utf-8")
        elif name == "docProps/app.xml":             # 4) Notes 计数归零
            data = re.sub(rb"<Notes>\d+</Notes>", b"<Notes>0</Notes>", data)
        zout.writestr(info, data)   # 传 info 而非裸数据，保留原压缩方式/时间戳
```

现成脚本：`scripts/strip_notes.py <源.pptx> <输出.pptx>`。

要点：

- **保留 `ppt/notesMasters/notesMaster1.xml`**（和 `presentation.xml.rels` 里对它的引用）。
  没有 notesSlide 时它不参与渲染，PowerPoint 自己的默认模板也带着它；删它反而要多改两处。
- 用 `zout.writestr(info, data)` 而不是 `writestr(name, data)`，条目顺序、压缩类型、
  时间戳都保持原样。
- 输出到**新文件**（如 `xxx_无备注.pptx`），原文件不动——客户版和讲稿版都要留着。
  输出到新文件还有个好处：不碰 editor_sdk 池里的实例，没有脏实例回写风险。
- 别在 editor_sdk 池开着同一路径时覆盖它；输出新文件则天然规避。

## 校验（缺一不可）

`scripts/verify_no_notes.py <原.pptx> <去备注后.pptx>`，逐项打印 PASS/FAIL：

1. zip 完整性；
2. 除 `notesSlides/`、`[Content_Types].xml`、`docProps/app.xml`、`ppt/slides/_rels/*` 外，
   **其余条目逐字节一致**（这是"其它别动"的唯一硬证据）；
3. 每个 slide rels 的差异恰好是"少 1 条 notesSlide 关系"，不多不少；
4. `*/media/*` 条目数与内容 MD5 一致；
5. 幻灯片数一致、正文文本框文本一致、有备注页的页数为 0。

## ⚠️ PowerPoint 侧的判读陷阱

删完打开 COM 校验会发现：**`Slides.Item(n).NotesPage` 依然存在，而且"有文本"**。
别慌——备注页是视图，由 notesMaster 派生，每页都有；剩下的文本是
**"幻灯片编号"占位符**（`PlaceholderFormat.Type == 13`），内容就是 `'1'`、`'2'`…`'N'`。

所以 COM 校验**不能**断言"有文本的备注页数 = 0"，要比的是字符总量：

```
示例（85 页，2026-09 实测）：旧 17075 字符 -> 新 161 字符
161 == len("1".."85") == 9 + 76*2，正好是编号长度，说明备注文本已彻底清空
```

判据：新文件的残留字符数与 `len("".join(str(i) for i in range(1, N+1)))` 相等，
且占位符类型全部是 13（SlideNumber）。用 PowerPoint 打开不弹修复即通过。

