"""Read the reference document's typography instead of imposing a PDF redesign."""
import os
import struct
from pathlib import Path

from django.conf import settings
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
NS = {'w': W[1:-1]}
_SINGLE_LINE_RATIO = 1.15


def register_original_fonts():
    global _SINGLE_LINE_RATIO
    private = Path(getattr(settings, 'AIM_PDF_FONT_DIR', Path(settings.BASE_DIR).parent / 'private_fonts' / 'Arial'))
    candidates = [(private, ['arial.ttf', 'arialbd.ttf', 'ariali.ttf', 'arialbi.ttf'])]
    if os.name == 'nt':
        candidates.append((Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts', candidates[0][1]))
    # Liberation Sans is metrically compatible with Arial, used by Linux CI.
    for directory in ['/usr/share/fonts/truetype/liberation2', '/usr/share/fonts/truetype/liberation', '/usr/share/fonts/liberation-sans']:
        candidates.append((Path(directory), ['LiberationSans-Regular.ttf', 'LiberationSans-Bold.ttf',
                                            'LiberationSans-Italic.ttf', 'LiberationSans-BoldItalic.ttf']))
    names = ['AIMOriginal', 'AIMOriginalBold', 'AIMOriginalItalic', 'AIMOriginalBoldItalic']
    for directory, files in candidates:
        if all((directory / name).is_file() for name in files):
            for name, file in zip(names, files):
                pdfmetrics.registerFont(TTFont(name, str(directory / file)))
            # Word's single line uses the font's hhea metrics, not font size × 1.2.
            data = (directory / files[0]).read_bytes()
            tables = {data[12+i*16:16+i*16]: struct.unpack_from('>I', data, 20+i*16)[0]
                      for i in range(struct.unpack_from('>H', data, 4)[0])}
            ascent, descent, gap = struct.unpack_from('>hhh', data, tables[b'hhea'] + 4)
            units = struct.unpack_from('>H', data, tables[b'head'] + 18)[0]
            _SINGLE_LINE_RATIO = (ascent - descent + gap) / units
            pdfmetrics.registerFontFamily(names[0], normal=names[0], bold=names[1], italic=names[2], boldItalic=names[3])
            return
    raise FileNotFoundError('Original contract fonts must be provisioned before deployment')


def run_size(run, default=9):
    size = run.find('w:rPr/w:sz', NS)
    return float(size.get(W+'val')) / 2 if size is not None else default


def paragraph_style(paragraph, styles):
    direct = paragraph.find('w:pPr', NS)
    key = direct.find('w:pStyle', NS) if direct is not None else None
    style_id = key.get(W+'val') if key is not None else 'Normal'
    inherited = []
    visited = set()
    while style_id and style_id not in visited:
        visited.add(style_id)
        style = styles.get(style_id)
        if style is None:
            break
        inherited.append(style.find('w:pPr', NS))
        base = style.find('w:basedOn', NS)
        style_id = base.get(W+'val') if base is not None else None

    def property_value(name, attribute, default=None):
        for properties in [direct, *inherited]:
            item = properties.find('w:'+name, NS) if properties is not None else None
            if item is not None and item.get(W+attribute) is not None:
                return item.get(W+attribute)
        return default

    size = max([run_size(run) for run in paragraph.findall('.//w:r', NS)] or [9])
    line = float(property_value('spacing', 'line', 240))
    rule = property_value('spacing', 'lineRule', 'auto')
    leading = line / 20 if rule == 'exact' else max(size * _SINGLE_LINE_RATIO, line / 20) if rule == 'atLeast' else size * _SINGLE_LINE_RATIO * line / 240
    alignment = {'center': TA_CENTER, 'right': TA_RIGHT, 'both': TA_JUSTIFY,
                 'distribute': TA_JUSTIFY}.get(property_value('jc', 'val', 'left'), TA_LEFT)
    left = float(property_value('ind', 'left', 0)) / 20
    right = float(property_value('ind', 'right', 0)) / 20
    first = (float(property_value('ind', 'firstLine', 0)) - float(property_value('ind', 'hanging', 0))) / 20
    return ParagraphStyle('original', fontName='AIMOriginal', fontSize=size, leading=leading,
                          alignment=alignment, spaceBefore=float(property_value('spacing', 'before', 0)) / 20,
                          spaceAfter=float(property_value('spacing', 'after', 0)) / 20,
                          leftIndent=left, rightIndent=right, firstLineIndent=first,
                          allowWidows=0, allowOrphans=0)


def page_geometry(section):
    size = section.find('w:pgSz', NS)
    margin = section.find('w:pgMar', NS)
    return {
        'pagesize': (float(size.get(W+'w')) / 20, float(size.get(W+'h')) / 20),
        **{key+'Margin': float(margin.get(W+key)) / 20 for key in ['top', 'bottom', 'left', 'right']},
    }
