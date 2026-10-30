"""Deterministic SVG and PNG technical figures from shared geometry."""
import json
import html
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def font_path():
    for p in ['C:/Windows/Fonts/msyh.ttc', 'C:/Windows/Fonts/simsun.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']:
        if Path(p).exists():
            return p
    raise ValueError('Chinese font unavailable; configure font_path() for this system')


def render(diagram, stem):
    w, h = diagram['width'], diagram['height']
    if not (40 <= w <= 3000 and 40 <= h <= 3000):
        raise ValueError('Invalid figure dimensions')
    scale = 3
    im = Image.new('RGB', (int(w * scale), int(h * scale)), 'white')
    d = ImageDraw.Draw(im)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">', '<rect x="1" y="1" width="{}" height="{}" fill="white" stroke="black"/>'.format(w-2,h-2)]
    d.rectangle((3,3,(w-1)*3,(h-1)*3),outline='black',width=3)
    for i in diagram['items']:
        t = i['type']
        if t == 'rect':
            x,y,rw,rh = [i[k] for k in ('x','y','w','h')]
            d.rectangle((x*3,y*3,(x+rw)*3,(y+rh)*3),outline='black',width=3)
            svg.append(f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" fill="none" stroke="black"/>')
        elif t == 'line':
            x,y,x2,y2 = [i[k] for k in ('x1','y1','x2','y2')]
            d.line((x*3,y*3,x2*3,y2*3),fill='black',width=3)
            svg.append(f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="black"/>')
            if i.get('arrow'):
                import math
                a=math.atan2(y2-y,x2-x)
                pts=[(x2,y2)]+[(x2-8*math.cos(a+v),y2-8*math.sin(a+v)) for v in (-.45,.45)]
                d.polygon([(a*3,b*3) for a,b in pts], fill='black')
                svg.append('<polygon points="'+ ' '.join(f'{a},{b}' for a,b in pts)+'"/>')
        elif t == 'text':
            x,y=i['x'],i['y']; size=i.get('size',14)
            for j,line in enumerate(i['text'].split('\n')):
                yy=y+j*size*1.4
                d.text((x*3,yy*3),line,font=ImageFont.truetype(font_path(),int(size*3)),anchor='mm',fill='black')
                svg.append(f'<text x="{x}" y="{yy}" text-anchor="middle" dominant-baseline="central" font-family="Microsoft YaHei,Noto Sans CJK SC,sans-serif" font-size="{size}">{html.escape(line)}</text>')
        else:
            raise ValueError(f'Unsupported figure primitive: {t}')
    stem=Path(stem); stem.parent.mkdir(parents=True,exist_ok=True)
    im.save(stem.with_suffix('.png'),dpi=(300,300))
    stem.with_suffix('.svg').write_text('\n'.join(svg+['</svg>']),encoding='utf-8')


def register_figure(reg, stem):
    items=[]; size=reg['size']; rows=(size+15)//16
    for row in range(rows):
        for col in range(16):
            bit=size-1-row*16-col
            if bit<0: continue
            x=20+col*35; y=35+row*85
            items += [dict(type='rect',x=x,y=y,w=35,h=32),dict(type='text',x=x+17.5,y=y+16,text=str(bit),size=11)]
        names=[]
        for f in reg.get('fields',[]):
            if (size-1-f['lsb'])//16==row:
                names.append(f"{f['name']} [{f['lsb']+f['width']-1}:{f['lsb']}]")
        items.append(dict(type='text',x=300,y=85+row*85,text='; '.join(names),size=12))
    render(dict(width=600,height=rows*85+25,items=items),stem)
