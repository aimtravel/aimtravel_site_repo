"""PDF layout for the reviewed paragraph-only 2027 agreements.

Text is taken from the filled DOCX, never retyped. Unsupported body structures
fail closed rather than dropping contractual content. No external service is
used: participant data stays on the hosting account.
"""
from io import BytesIO
from pathlib import Path
import re
from xml.sax.saxutils import escape
from zipfile import ZipFile

from lxml import etree
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Table, TableStyle, PageBreak, Spacer, KeepTogether
from .document_typography import register_original_fonts, paragraph_style, run_size, page_geometry

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{' + NS['w'] + '}'


def render_pdf(source, destination):
    register_original_fonts()
    with ZipFile(source) as package:
        root = etree.fromstring(package.read('word/document.xml'))
        if root.xpath('//w:tbl|//w:drawing|//w:txbxContent|//w:footnoteReference|//w:endnoteReference|//w:del', namespaces=NS):
            raise ValueError('Unsupported document structure requires a reviewed PDF layout')
        paragraphs = root.xpath('/w:document/w:body/w:p', namespaces=NS)
        style_root = etree.fromstring(package.read('word/styles.xml'))
        styles = {style.get(W+'styleId'): style for style in style_root.findall('w:style', NS)}
        sections = root.xpath('//w:sectPr', namespaces=NS)
        geometry = page_geometry(sections[-1])
        if any(page_geometry(section) != geometry for section in sections):
            raise ValueError('Different section geometry requires a reviewed PDF layout')
        # Word wraps around its floating header; reserve its occupied height here
        # so continuing paragraphs cannot collide with the logo/contact details.
        geometry['topMargin'] = max(geometry['topMargin'], 50)
        page_width, page_height = geometry['pagesize']
        column_width = (page_width - geometry['leftMargin'] - geometry['rightMargin']) / 2
        logo = package.read('word/media/image1.jpeg') if 'word/media/image1.jpeg' in package.namelist() else None
        header_text = ''
        signature_footer = False
        for name in package.namelist():
            if re.fullmatch(r'word/(header|footer)\d+\.xml', name):
                part = etree.fromstring(package.read(name))
                text = ''.join(part.xpath('//w:t/text()', namespaces=NS)).strip()
                if 'header' in name and text:
                    if header_text and header_text != text:
                        raise ValueError('Different section headers require review')
                    header_text = text
                if 'footer' in name and text:
                    signature_footer = signature_footer or 'Подпис' in text
                    if not re.fullmatch(r'[\d\s/.…]+|[\d\s]*Подпис[\s.…]+|Страница \d+ от \d+', text):
                        raise ValueError('Footer text needs explicit rendering: ' + name)
    story = []
    previous_signature_heading = False
    signature_zone = False
    signature_start = None
    for paragraph in paragraphs:
        body = paragraph_style(paragraph, styles)
        pieces = []
        plain = []
        for run in paragraph.xpath('.//w:r', namespaces=NS):
            text = ''.join(('\n' if etree.QName(n).localname in {'br', 'cr'} else
                            '\t' if etree.QName(n).localname == 'tab' else n.text or '')
                           for n in run if etree.QName(n).localname in {'t', 'br', 'cr', 'tab'})
            plain.append(text)
            text = escape(re.sub(r'[ \t]+', ' ', text)).replace('\n', '<br/>')
            bold = run.find('w:rPr/w:b', NS)
            if bold is not None and bold.get(W+'val', '1') not in {'0', 'false'}:
                text = '<b>' + text + '</b>'
            italic = run.find('w:rPr/w:i', NS)
            if italic is not None and italic.get(W+'val', '1') not in {'0', 'false'}:
                text = '<i>' + text + '</i>'
            underline = run.find('w:rPr/w:u', NS)
            if underline is not None and underline.get(W+'val', 'single') not in {'0', 'false', 'none'}:
                text = '<u>' + text + '</u>'
            color = run.find('w:rPr/w:color', NS)
            if color is not None and re.fullmatch(r'[0-9A-Fa-f]{6}', color.get(W+'val', '')):
                text = '<font color="#' + color.get(W+'val') + '">' + text + '</font>'
            pieces.append('<font size="' + str(run_size(run, body.fontSize)) + '">' + text + '</font>')
        text = ''.join(plain).strip()
        if not text:
            story.append(Spacer(1, body.leading + body.spaceBefore + body.spaceAfter))
            continue
        if '{{' in text or '}}' in text:
            raise ValueError('Unfilled document variable')
        if 'ЗА ИЗПЪЛНИТЕЛЯ:' in text and 'ВЪЗЛОЖИТЕЛ:' in text:
            if previous_signature_heading:
                continue
            previous_signature_heading = True
            signature_zone = True
            signature_start = len(story)
            table = Table([[Paragraph('<b>ЗА ИЗПЪЛНИТЕЛЯ:</b>', body), Paragraph('<b>ВЪЗЛОЖИТЕЛ:</b>', body)]], colWidths=[column_width, column_width])
            table.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('VALIGN',(0,0),(-1,-1),'TOP')]))
            story.append(table)
            continue
        previous_signature_heading = False
        if text == 'ДЕКЛАРАЦИЯ':
            if signature_start is not None:
                story[signature_start:] = [KeepTogether(story[signature_start:])]
                signature_start = None
            signature_zone = False
            story.append(PageBreak())
        raw_text = ''.join(plain)
        if (signature_zone and '\t' in raw_text) or re.search(r'\S {8,}\S', raw_text):
            rows = []
            for line in raw_text.splitlines():
                if not line.strip():
                    continue
                chunks = re.split(r'(?:\t| {8,})+', line.lstrip(' ').rstrip())
                if len(chunks) > 2:
                    raise ValueError('Signature layout has more than two columns')
                rows.append([Paragraph(escape(chunks[0].strip()), body),
                             Paragraph(escape(chunks[1].strip()), body) if len(chunks) == 2 else ''])
            table = Table(rows,colWidths=[column_width,column_width])
            table.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('VALIGN',(0,0),(-1,-1),'TOP')]))
            story.append(table)
            continue
        story.append(Paragraph(''.join(pieces).strip(), body))
    if not story:
        raise ValueError('Empty agreement')
    if signature_start is not None:
        story[signature_start:] = [KeepTogether(story[signature_start:])]

    def page_frame(canvas, doc):
        canvas.saveState()
        if logo:
            image = ImageReader(BytesIO(logo))
            width, height = image.getSize()
            draw_height = min(35, 150 * height / width)
            canvas.drawImage(image, geometry['leftMargin'], page_height - 49, width=draw_height * width / height,
                             height=draw_height, mask='auto')
        canvas.setFont('AIMOriginal', 8)
        for index, line in enumerate(re.split(r'(?=Website:|Email:|Instagram:)', header_text)):
            canvas.drawRightString(page_width-geometry['rightMargin'], page_height - 18 - index * 9.6, line)
        canvas.setFont('AIMOriginal', 8)
        if signature_footer:
            canvas.drawString(geometry['leftMargin'], 18, 'Подпис …………')
        canvas.drawRightString(page_width-geometry['rightMargin'], 18, str(doc.page))
        canvas.restoreState()

    document = BaseDocTemplate(str(destination), **geometry,
                                 title=Path(destination).stem, author='AIM Travel')
    frame = Frame(geometry['leftMargin'], geometry['bottomMargin'], column_width * 2,
                  page_height - geometry['topMargin'] - geometry['bottomMargin'],
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    document.addPageTemplates(PageTemplate(id='original', frames=[frame], onPage=page_frame))
    document.build(story)
    return Path(destination)
