"""Highlight the agreed program amount without changing contractual text."""
from copy import deepcopy
import re

from docx.shared import RGBColor
from docx.text.run import Run


def highlight_program_price(document, amount):
    pattern = re.compile(rf"(?<!\d){re.escape(str(amount))}(?!\d)")
    count = 0
    for paragraph in document.paragraphs:
        matches = [(m.start(), m.end()) for m in pattern.finditer(paragraph.text)]
        count += len(matches)
        offset = 0
        for run in list(paragraph.runs):
            value = run.text
            end = offset + len(value)
            boundaries = sorted({0, len(value), *[
                max(0, min(len(value), point-offset))
                for start, stop in matches if start < end and stop > offset
                for point in (start, stop)
            ]})
            if any(start < end and stop > offset for start, stop in matches):
                for left, right in zip(boundaries, boundaries[1:]):
                    if left == right:
                        continue
                    clone = deepcopy(run._r)
                    piece = Run(clone, paragraph)
                    piece.text = value[left:right]
                    if any(start <= offset+left < stop for start, stop in matches):
                        piece.font.color.rgb = RGBColor.from_string("C00000")
                    run._r.addprevious(clone)
                run._r.getparent().remove(run._r)
            offset = end
    if not count:
        raise ValueError("Agreed program price missing from agreement")
