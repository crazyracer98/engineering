// Pandoc template for the paper (passed as `pandoc --template paper/template.typ`).
// Not plain Typst: dollar-delimited names are Pandoc template variables, filled by
// `taxonomy.render_paper`. A4, numbered headings, repeating table headers,
// PDF metadata. Licence: CC BY-SA 4.0 (see paper/README.md).
#let horizontalrule = line(start: (25%, 0%), end: (75%, 0%))

#let accent = rgb("#1a4f8b")

// Rule and conflict-rule card: a framed block whose definition list
// (IF / THEN / BECAUSE / ...) is laid out as label and text columns.
#let rulecard(body) = block(
  width: 100%,
  inset: (x: 9pt, y: 7pt),
  stroke: 0.6pt + luma(170),
  radius: 2pt,
  fill: luma(248),
  below: 1.3em,
)[
  #set par(justify: false)
  #show terms: it => grid(
    columns: (2.7cm, 1fr),
    column-gutter: 8pt,
    row-gutter: 5pt,
    ..it.children.map(c => (
      text(weight: "bold", size: 8.5pt, fill: accent)[#c.term],
      c.description,
    )).flatten(),
  )
  #body
]

// "Applied in this taxonomy" box of the Method section.
#let appliedbox(body) = block(
  width: 100%,
  inset: 9pt,
  fill: rgb("#eef4fb"),
  stroke: (left: 2.5pt + accent),
  above: 1em,
  below: 1.2em,
)[
  #set par(justify: false)
  #body
]

// Switches the remaining headings to appendix numbering (A, A.1, ...).
#let appendix(body) = {
  counter(heading).update(0)
  set heading(numbering: "A.1", supplement: [Appendix])
  body
}

$if(highlighting-definitions)$
$highlighting-definitions$

$endif$
#set document(
  title: $pdf-title$,
  author: $pdf-author$,
  keywords: $pdf-keywords$,
  date: $pdf-date$,
)

#set page(
  paper: "a4",
  margin: (x: 2.2cm, top: 2.5cm, bottom: 2.4cm),
  numbering: "1",
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 8pt, fill: luma(110))
      $title$ #h(1fr) Edition $edition$
      #v(-0.5em)
      #line(length: 100%, stroke: 0.4pt + luma(190))
    ]
  },
)
#set text(font: "Libertinus Serif", size: 10pt, lang: "$if(lang)$$lang$$else$en$endif$"$if(region)$, region: "$region$"$endif$)
#set par(justify: true, leading: 0.62em, spacing: 0.9em)
#set heading(numbering: "1.1")
#show heading: set block(above: 1.4em, below: 0.8em)
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  set text(size: 15pt)
  it
  v(0.3em)
}
#show heading.where(level: 4): set text(size: 10.5pt)
#show raw: set text(font: "DejaVu Sans Mono", size: 0.85em)
#show link: set text(fill: accent)
#set list(indent: 0.8em, body-indent: 0.5em)
#set enum(indent: 0.8em, body-indent: 0.5em)
#show quote.where(block: true): set block(above: 0.4em, below: 1em, inset: (left: 1em))

// Tables: small text, light header rule, zebra rows; headers repeat across
// pages (Pandoc emits `table.header`) and long tables may break.
#set table(
  inset: 5pt,
  stroke: none,
  fill: (_, y) => if y > 0 and calc.odd(y) { luma(246) },
)
#show table: set text(size: 8.5pt)
#show table: set par(justify: false)
#show table: set align(left)
#show table.header: set text(weight: "bold")
#show figure: set block(breakable: true)
#show figure.where(kind: table): set figure.caption(position: $if(table-caption-position)$$table-caption-position$$else$top$endif$)
#show figure.where(kind: image): set figure.caption(position: $if(figure-caption-position)$$figure-caption-position$$else$bottom$endif$)
$if(smart)$
$else$
#set smartquote(enabled: false)
$endif$

#align(center)[
  #v(2.5cm)
  #text(size: 24pt, weight: "bold")[$title$]
$if(subtitle)$
  #v(0.4em)
  #text(size: 13pt)[$subtitle$]
$endif$
  #v(1.2em)
  #text(size: 12pt)[$for(author)$$author$$sep$, $endfor$]
  #v(0.5em)
  Edition $edition$ #sym.dot.c $date$ \
$if(license)$
  License: #link("$license-url$")[$license$]
$endif$
$if(keywords)$
  #v(1em)
  #text(size: 9pt)[*Keywords:* $for(keywords)$$keywords$$sep$; $endfor$]
$endif$
  #v(1.2cm)
]

$for(header-includes)$
$header-includes$

$endfor$
$for(include-before)$
$include-before$

$endfor$
$if(toc)$
#outline(
  title: [Contents],
  depth: $toc-depth$,
)
$endif$

$body$
$for(include-after)$

$include-after$
$endfor$
