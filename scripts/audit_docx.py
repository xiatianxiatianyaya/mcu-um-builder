"""Structural checks only; does not render or verify hardware behavior."""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}


def audit(path):
    with ZipFile(path) as z: root=E.fromstring(z.read('word/document.xml'))
    errors=[]
    for cell in root.xpath('//w:tc',namespaces=NS):
        if cell.xpath('string(w:tcPr/w:vAlign/@w:val)',namespaces=NS)!='center': errors.append('Cell not vertically centered')
        for p in cell.xpath('w:p',namespaces=NS):
            if p.xpath('string(w:pPr/w:jc/@w:val)',namespaces=NS)!='center': errors.append('Cell paragraph not centered')
    for pic in root.xpath('//wp:inline',namespaces=NS):
        if not pic.xpath('wp:docPr/@descr',namespaces=NS): errors.append('Missing image alt text')
        if not pic.xpath('.//a:ln',namespaces=NS): errors.append('Missing image frame')
    bookmarks=root.xpath('//w:bookmarkStart/@w:name',namespaces=NS)
    if len(bookmarks)!=len(set(bookmarks)): errors.append('Duplicate bookmark')
    instructions=root.xpath('//w:fldSimple/@w:instr',namespaces=NS)
    for ins in instructions:
        parts=ins.split()
        if parts and parts[0]=='REF' and parts[1] not in bookmarks: errors.append('Dangling REF '+parts[1])
    text=''.join(root.xpath('//w:t/text()',namespaces=NS))
    for marker in ('Error! Reference source not found','错误!未找到引用源','错误！未找到引用源'):
        if marker in text: errors.append('Broken field result')
    return {'structural_pass':not errors,'errors':errors,'tables':len(root.xpath('//w:tbl',namespaces=NS)),'images':len(root.xpath('//wp:inline',namespaces=NS)),'visual_review_completed':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('docx'); p.add_argument('--report',required=True); a=p.parse_args()
    result=audit(a.docx); Path(a.report).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(result,ensure_ascii=False)); raise SystemExit(0 if result['structural_pass'] else 1)
