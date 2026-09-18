# -*- coding: utf-8 -*-
"""整份删除 PPTX 的演讲者备注（包级手术，其余内容逐字节保留）。

用法:
    python strip_notes.py <源.pptx> <输出.pptx>

原理:
    备注内容存在 ppt/notesSlides/notesSlideN.xml，由 ppt/slides/_rels/slideN.xml.rels
    里的 notesSlide 关系引用。直接删部件 + 删关系 + 删 [Content_Types] 的 Override，
    比"把每页备注文本清空"更彻底（清空文本仍会留下空备注页）。

为什么不用 editor_sdk:
    tencent-local-office-edit 的备注工具只接受纯文本，会重写备注结构；
    且 editor_sdk 保存 pptx 会重组 ppt/media/* 目录，"其它别动"的要求满足不了。
"""
import os
import re
import sys
import zipfile

NOTES_SLIDE_TYPE = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
)


def strip(src, out):
    zin = zipfile.ZipFile(src, "r")
    infos = zin.infolist()
    n_parts = n_rels = n_ct = 0
    app_fixed = False

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in infos:
            name = info.filename

            # 1) 丢掉 notesSlides 部件（备注页 XML + 其自身 rels）
            if name.startswith("ppt/notesSlides/"):
                n_parts += 1
                continue

            data = zin.read(name)

            # 2) 摘掉每个 slide 的 notesSlide 关系
            if name.startswith("ppt/slides/_rels/") and name.endswith(".rels"):
                s = data.decode("utf-8")
                new = re.sub(
                    r'<Relationship\b[^>]*Type="' + re.escape(NOTES_SLIDE_TYPE) + r'"[^>]*/>',
                    "",
                    s,
                )
                if new != s:
                    n_rels += 1
                    data = new.encode("utf-8")

            # 3) 摘掉 [Content_Types].xml 里 notesSlides 的 Override
            elif name == "[Content_Types].xml":
                s = data.decode("utf-8")
                new = re.sub(
                    r'<Override\b[^>]*PartName="/ppt/notesSlides/[^"]*"[^>]*/>', "", s
                )
                n_ct = len(re.findall(r'PartName="/ppt/notesSlides/', s)) - len(
                    re.findall(r'PartName="/ppt/notesSlides/', new)
                )
                data = new.encode("utf-8")

            # 4) docProps/app.xml 的 Notes 计数归零
            elif name == "docProps/app.xml":
                s = data.decode("utf-8")
                new = re.sub(r"<Notes>\d+</Notes>", "<Notes>0</Notes>", s)
                if new != s:
                    app_fixed = True
                    data = new.encode("utf-8")

            zout.writestr(info, data)

    print("删除 notesSlides 部件: %d" % n_parts)
    print("清理 slide rels: %d" % n_rels)
    print("[Content_Types] 摘除 Override: %d" % n_ct)
    print("app.xml Notes 归零: %s" % app_fixed)
    print("输出: %s (%d bytes)" % (out, os.path.getsize(out)))
    return n_parts, n_rels, n_ct


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    strip(sys.argv[1], sys.argv[2])
