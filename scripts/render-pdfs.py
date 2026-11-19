"""Render the actual Markdown drafts to PDF with Vietnamese font and vector flowchart."""
import html, re
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Polygon
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
styles=getSampleStyleSheet()
for name in ['Normal','BodyText','Title','Heading1','Heading2','Heading3']:
    styles[name].fontName='Arial';styles[name].leading=15;styles[name].fontSize=10
styles['Title'].fontName='Arial-Bold';styles['Title'].fontSize=20;styles['Title'].leading=25
styles['Heading1'].fontName='Arial-Bold';styles['Heading1'].fontSize=16;styles['Heading1'].leading=21
styles['Heading2'].fontName='Arial-Bold';styles['Heading2'].fontSize=13;styles['Heading2'].leading=18
styles['Heading3'].fontName='Arial-Bold';styles['Heading3'].fontSize=11
styles['Normal'].wordWrap='CJK'
styles.add(ParagraphStyle('Cell',fontName='Arial',fontSize=8,leading=11,wordWrap='CJK'))

def text(s):
    s=html.escape(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`([^`]+)`',r'\1',s)
    s=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1 (\2)',s)
    return s

def flowchart():
    d=Drawing(490,470)
    labels=['Commit SUT / nightly','Change affects API, DB, runtime?','Isolated DB + CSV; contract + smoke','Warmup + profiles on fixed runner','Enough samples and comparable baseline?','Compare p95, errors, throughput','Violation: repeat twice on clean runner','Persistent regression: alert + artifacts']
    for i,label in enumerate(labels):
        y=430-i*54
        d.add(Rect(70,y,350,35,rx=6,ry=6,fillColor=colors.HexColor('#e7eef7'),strokeColor=colors.HexColor('#426486')))
        d.add(String(245,y+13,label,textAnchor='middle',fontName='Arial',fontSize=9))
        if i<7:
            d.add(Line(245,y,245,y-19,strokeColor=colors.HexColor('#426486')))
            d.add(Polygon([241,y-14,245,y-19,249,y-14],fillColor=colors.HexColor('#426486')))
    d.add(Line(420,389,477,389));d.add(String(474,403,'No: skip;',textAnchor='end',fontName='Arial',fontSize=8));d.add(String(474,393,'keep nightly',textAnchor='end',fontName='Arial',fontSize=8))
    d.add(Line(70,227,15,227));d.add(String(16,241,'No: fix',fontName='Arial',fontSize=8));d.add(String(16,231,'conditions',fontName='Arial',fontSize=8))
    d.add(String(250,370,'Yes',fontName='Arial',fontSize=8));d.add(String(250,208,'Yes',fontName='Arial',fontSize=8))
    return d

def render(source):
    saved_style=(styles['Normal'].fontSize,styles['Normal'].leading)
    saved_cell=(styles['Cell'].fontSize,styles['Cell'].leading)
    if source.stem=='ai-audit':
        styles['Normal'].fontSize=9;styles['Normal'].leading=11.5
        styles['Cell'].fontSize=7.5;styles['Cell'].leading=9.5
    lines=source.read_text(encoding='utf-8').splitlines();story=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('```'):
            kind=line[3:];block=[];i+=1
            while i<len(lines) and not lines[i].strip().startswith('```'):block.append(lines[i]);i+=1
            if kind=='mermaid':story.append(flowchart())
            else:
                for code in block:story.append(Paragraph(text(code),styles['Cell']))
            i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+',x) for x in cells):rows.append(cells)
                i+=1
            cols=max(map(len,rows));data=[[Paragraph(text(x),styles['Cell']) for x in r]+['']*(cols-len(r)) for r in rows]
            table=Table(data,colWidths=[490/cols]*cols,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7eef7')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#c3cbd5')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([table,Spacer(1,9)]);continue
        image=re.match(r'!\[[^]]*\]\(([^)]+)\)',line)
        if image:
            path=(source.parent/image.group(1)).resolve()
            im=Image(str(path));factor=min(490/im.imageWidth,420/im.imageHeight)
            im.drawWidth=im.imageWidth*factor;im.drawHeight=im.imageHeight*factor
            story.extend([im,Spacer(1,10)]);i+=1;continue
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#'));label=line[level:].strip()
            if source.stem=='ai-audit' and label.startswith('Tiếp tục thu bằng chứng'):
                story.append(PageBreak())
            story.append(Paragraph(text(label),styles['Title' if level==1 else f'Heading{min(level,3)}']))
        else:
            paragraph=[line];i+=1
            while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```','![')):
                paragraph.append(lines[i].strip());i+=1
            story.extend([Paragraph(text(' '.join(paragraph)),styles['Normal']),Spacer(1,4 if source.stem=='ai-audit' else 8)]);continue
        i+=1
    target=OUT/(source.stem+'.pdf')
    def footer(c,doc):
        c.setFont('Arial',8);c.setFillColor(colors.HexColor('#637386'))
        c.drawString(48,25,'23120330 | HW05 M5 | Draft - pending student review')
        c.drawRightString(548,25,str(doc.page))
    SimpleDocTemplate(str(target),pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=42,bottomMargin=45,title=source.stem,author='23120330 - AI-assisted draft').build(story,onFirstPage=footer,onLaterPages=footer)
    reader=PdfReader(target)
    assert len(reader.pages)>0
    assert '23120330' in ''.join(p.extract_text() or '' for p in reader.pages)
    print(f'{target}: {len(reader.pages)} pages')
    styles['Normal'].fontSize,styles['Normal'].leading=saved_style
    styles['Cell'].fontSize,styles['Cell'].leading=saved_cell

if __name__=='__main__':
    for name in ['main-report','ai-audit','ai-critique']:render(ROOT/'docs'/f'{name}.md')
