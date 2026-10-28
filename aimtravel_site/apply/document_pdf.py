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

from django.conf import settings
from lxml import etree
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{' + NS['w'] + '}'


def render_pdf(source, destination):
    fonts = Path(settings.BASE_DIR) / 'static/fonts/Sofia-sans/static'
    pdfmetrics.registerFont(TTFont('AIMDocument', str(fonts / 'SofiaSans-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('AIMDocumentBold', str(fonts / 'SofiaSans-Bold.ttf')))
    pdfmetrics.registerFontFamily('AIMDocument', normal='AIMDocument', bold='AIMDocumentBold',
                                  italic='AIMDocument', boldItalic='AIMDocumentBold')
    with ZipFile(source) as package:
        root = etree.fromstring(package.read('word/document.xml'))
        if root.xpath('//w:tbl|//w:drawing|//w:txbxContent|//w:footnoteReference|//w:endnoteReference|//w:del', namespaces=NS):
            raise ValueError('Unsupported document structure requires a reviewed PDF layout')
        paragraphs = root.xpath('/w:document/w:body/w:p', namespaces=NS)
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
    body = ParagraphStyle('body', fontName='AIMDocument', fontSize=10.5, leading=13,
                          alignment=TA_JUSTIFY, spaceAfter=5, splitLongWords=True)
    heading = ParagraphStyle('heading', parent=body, fontName='AIMDocumentBold',
                             alignment=TA_LEFT, spaceBefore=10, spaceAfter=7, keepWithNext=True)
    title = ParagraphStyle('title', parent=heading, fontSize=15, leading=18, alignment=TA_CENTER)
    story = []
    previous_signature_heading = False
    signature_zone = False
    for paragraph in paragraphs:
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
            color = run.find('w:rPr/w:color', NS)
            if color is not None and re.fullmatch(r'[0-9A-Fa-f]{6}', color.get(W+'val', '')):
                text = '<font color="#' + color.get(W+'val') + '">' + text + '</font>'
            pieces.append(text)
        text = ''.join(plain).strip()
        if not text:
            continue
        if '{{' in text or '}}' in text:
            raise ValueError('Unfilled document variable')
        if 'ЗА ИЗПЪЛНИТЕЛЯ:' in text and 'ВЪЗЛОЖИТЕЛ:' in text:
            if previous_signature_heading:
                continue
            previous_signature_heading = True
            signature_zone = True
            table = Table([[Paragraph('ЗА ИЗПЪЛНИТЕЛЯ:', heading), Paragraph('ВЪЗЛОЖИТЕЛ:', heading)]], colWidths=[255, 255])
            table.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('VALIGN',(0,0),(-1,-1),'TOP')]))
            story.append(table)
            continue
        previous_signature_heading = False
        if text == 'ДЕКЛАРАЦИЯ':
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
            table = Table(rows,colWidths=[255,255])
            table.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('VALIGN',(0,0),(-1,-1),'TOP')]))
            story.append(table)
            continue
        style = title if (text.startswith(('Договор №', 'Договор от')) or text == 'АНЕКС №1') else heading if (text.isupper() and len(text) < 100) else body
        story.append(Paragraph(''.join(pieces).strip(), style))
    if not story:
        raise ValueError('Empty agreement')

    def page_frame(canvas, doc):
        canvas.saveState()
        if logo:
            image = ImageReader(BytesIO(logo))
            width, height = image.getSize()
            draw_height = min(35, 150 * height / width)
            canvas.drawImage(image, 42, 793, width=draw_height * width / height,
                             height=draw_height, mask='auto')
        canvas.setFont('AIMDocument', 8)
        for index, line in enumerate(re.split(r'(?=Website:|Email:|Instagram:)', header_text)):
            canvas.drawRightString(553, 824 - index * 10, line)
        canvas.setFont('AIMDocument', 9)
        if signature_footer:
            canvas.drawString(42, 25, 'Подпис …………')
        canvas.drawRightString(553, 25, str(doc.page))
        canvas.restoreState()

    document = SimpleDocTemplate(str(destination), pagesize=(595.28, 841.89),
                                 rightMargin=42, leftMargin=42, topMargin=65, bottomMargin=44,
                                 title=Path(destination).stem, author='AIM Travel')
    document.build(story, onFirstPage=page_frame, onLaterPages=page_frame)
    return Path(destination)
