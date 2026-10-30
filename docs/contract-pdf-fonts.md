# Original contract typography

The 2027 source documents use Arial 9 pt, line spacing 223/240 and mostly
1 pt after paragraphs. The PDF renderer reads run sizes, bold/italic/underline,
paragraph alignment, spacing, indents and page margins from the filled DOCX.
It adds no extra frame padding. Program-price highlighting remains intact.

Production uses the operator-provided Arial family in
`/home/aimtrave/private_fonts/Arial` (`arial.ttf`, `arialbd.ttf`, `ariali.ttf`,
`arialbi.ttf`). These font files are outside the public site and repository.
An alternate directory can be set with `AIM_PDF_FONT_DIR`. Windows development
can use its installed Arial family; Linux CI installs Liberation Sans as a
metrically compatible substitute. Rendering fails if neither family is present.

The renderer reserves at least 66 pt above the body and 60 pt below it for
print-safe headers and a signature band. Both parties have a signature field
on every contract and annex page, independent of the source footer. The
generated PDF is checked against every source paragraph before delivery;
verification failure stops generation without logging participant text.

The reviewed standard examples produce 8 pages for Full Arranged, 8 for Self
Arranged and 2 for the annex. Longer applicant details may affect pagination;
content is never shortened to force a page count.
