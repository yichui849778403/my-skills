---
name: pptx-image-stamp
description: 给演示文稿（pptx）的指定页面加 logo、水印、角标等图片元素，并做像素级验证。包含 python-pptx 改 pptx 的踩坑与安全做法、PowerPoint COM 导出校验流程。触发词：PPT 加 logo、给 PPT 加水印、ppt 插入图片、页码角标、往 PPT 某几页加图。
agent_created: true
---

# 给 PPT 指定页面加图片元素（logo / 水印 / 角标）

## 一、绝对红线

### 1. 永远不要在原文件上改
先复制一份副本再动手，文件名带后缀（如 `_含logo.pptx`）。交付前用字节数+修改时间证明原文件未被动过。

### 2. 最终文件必须从原文件一次性重建
**python-pptx 反复「打开→改→保存」同一个 pptx 会损坏包结构。** 实测表现：多出未在 `[Content_Types].xml` 正确声明的 `notesSlide1.xml`、媒体部件扩展名错位（image11.png / image11.svg 互换），PowerPoint 直接报 **"PowerPoint could not open the file"**（`Presentations.Open` 抛异常）。

正确做法：所有修改攒成一次脚本，从原始文件读入 → 一次性全部应用 → 保存一次。**绝不**用「先加上去，再删掉，再改回来」的试错方式在同一文件上迭代。

如果已经迭代坏了，别修，直接从原文件重建。

### 3. 不要动占位符的坐标去「试」
给占位符写 `left/top/width/height` 会注入显式 `<p:spPr>`，破坏「继承版式」状态，渲染会偏移 1–2px。原版如果没有 spPr，就别去碰它。

若确实动了要还原：整段删除 `<p:spPr>` 而不是把值写回去。

```python
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
sp=sh._element.find('p:spPr',ns)
if sp is not None: sh._element.remove(sp)   # 恢复为继承版式
```

**python-pptx 坑**：单独设 `sh.left` 或 `sh.width` 时，若本来没有 xfrm，python-pptx 会新建一个并把 `cy` 写成 0，形状高度变 0 直接看不见。**left/top/width/height 必须四个一起显式赋值。**

---

## 二、动手前的版面勘察

1. `Presentation(path)` 读尺寸与页数；16:9 通常是 `12192000 x 6858000` EMU（13.333×7.5 英寸，1 英寸 = 914400 EMU）。
2. 逐页 dump 形状：名称、类型、`left/top/width/height`、文本。找出每页的空位。
3. **重点找顶格左对齐的标题** —— 这是左上角放 logo 的最大冲突源。居中标题的页面左上角通常是空的；`仅标题`版式的内容页标题往往顶格在 `L0.72 T0`，logo 放左上会直接压住。
4. 检查 logo PNG 的透明留白：算非透明像素包围盒。若有留白，先裁掉，否则实际视觉尺寸比设定的框小。

```python
import numpy as np
from PIL import Image
a=np.array(Image.open(png).convert('RGBA'))[:,:,3]
ys,xs=np.where(a>10)
print(xs.min(),xs.max(),ys.min(),ys.max())   # 与画布同尺寸则无留白
```

5. 查背景色，确认 logo 配色对比度：
```python
from PIL import Image; import numpy as np
print(np.array(Image.open(render).convert('RGB'))[y,x])   # 采目标区域几个点
```
白字版 logo 配深色/彩色底，黑字版配浅底。logo 里若有与底色接近的色块（色距 <60），说明那条会糊掉，需判断其余部分能否撑住识别度。

---

## 三、摆放与写入

统一位置、统一尺寸，跨页才整齐。比例务必按原图宽高比换算，别拉伸。

```python
from pptx import Presentation
from pptx.util import Emu
EMU=914400
def I(v): return Emu(int(round(v*EMU)))      # 英寸 -> EMU

W_IN=2.6                                      # 宽 2.6 英寸
H_IN=W_IN*580/993                             # 按原图 993:580 比例
LEFT=12192000-I(W_IN)-I(0.5)                  # 右边距 0.5 英寸
TOP=I(0.25)

p=Presentation('输出.pptx')
for n in [1,3,11]:
    pic=p.slides[n-1].shapes.add_picture('logo.png',I(0.5),TOP,I(W_IN),I(H_IN))
    pic.name='某某logo'                        # 命名便于后续按名查找/删除
p.save('输出.pptx')
```

- 图片加在形状栈顶，会盖住原有内容 —— 所以位置必须先确认是空的。
- 按名字过滤判断哪些页有图：`if sh.name=='某某logo'`。**别用 `sh.shape_type==13`**，那会把原有照片全捞进来。
- 删形状：`sh._element.getparent().remove(sh._element)`。

---

## 四、验证（必做，别靠肉眼）

### 1. PowerPoint COM 导出页面图
```powershell
$pp=New-Object -ComObject PowerPoint.Application
$pres=$pp.Presentations.Open($path,$true,$false,$false)   # 第2参 $true = 只读打开
$pres.Slides.Item($n).Export("$out\s$n.png","PNG",1333,750)
$pres.Close(); $pp.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp) | Out-Null
```
- **只读打开**（`$true`），别让幻灯片被改动。
- 打开失败会抛 "PowerPoint could not open the file" —— 这就是文件被写坏的信号。

### 2. 逐像素比对
从**原文件**导一份底图，从**改后文件**导一份，相减看变化区域。改动的页应只在预期矩形内变化；**没被点名的页必须逐像素完全一致**，否则说明 python-pptx 重存时动了别的东西。

### 3. 检查 logo 有没有压住内容
在底图上取 logo 矩形，数里面的白色文字像素。>50 就是压住了。

### 4. 确认整包图片没错配
python-pptx 重存会重排媒体部件名，需确认每页引用的图片字节没变：

```python
import zipfile,hashlib,re
from lxml import etree
R='http://schemas.openxmlformats.org/package/2006/relationships'
IMG='http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'
def slide_imgs(f):
    z=zipfile.ZipFile(f); out={}
    for n in z.namelist():
        m=re.match(r'ppt/slides/slide(\d+)\.xml$',n)
        if not m: continue
        i=int(m.group(1)); rp='ppt/slides/_rels/slide%d.xml.rels'%i; hs=[]
        if rp in z.namelist():
            for rel in etree.fromstring(z.read(rp)).iter('{%s}Relationship'%R):
                if rel.get('Type')==IMG:
                    hs.append(hashlib.md5(z.read('ppt/'+rel.get('Target').replace('../',''))).hexdigest()[:12])
        out[i]=sorted(hs)
    return out
```
逐页哈希应完全一致；差异只应出现在你真正改过的那几页。

---

## 五、本机环境注意事项（Windows / WorkBuddy 沙箱）

- **PowerShell 工具的 stdout 捕获不到**，只有 exit code 可靠。要拿结果就写进文件再用 Read 读。写 `$log` 时用 `Set-Content -Encoding UTF8`。
- **COM 调用失败可能返回 exit 0 却不产出文件。** 每次导完必须列目录确认文件真的生成了（看时间戳/大小），不能只看退出码。
- 卡住时先查残留进程与锁文件：`tasklist | grep -i powerpnt`、目录里有没有 `~$xxx.pptx`。有锁文件说明用户正开着，先别动。
- 临时预览目录用完即删，只留一张汇总效果图给用户看。
