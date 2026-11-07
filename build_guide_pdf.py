#!/usr/bin/env python3
"""
Print the master guide to PDF.

"Installing the Soul Apps Manually.md" is the master copy of the guide. This
turns it into styled HTML and prints that with headless Chrome, so no pandoc,
Word or LaTeX install is needed. Every section marked {: .newpage } starts on a
fresh page, and the quick-reference section, marked {: .newpage .sheet }, is set
smaller so that it keeps to its single page.

Usage:
    py build_guide_pdf.py           rebuild Installing the Soul Apps Manually.pdf
    py build_guide_pdf.py --check   exit 1 if the PDF is older than the markdown
    py build_guide_pdf.py --open    rebuild it, then open it

Needs Python 3.9+ and a local Google Chrome. No pip packages.
"""
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GUIDE_MD = HERE / "Installing the Soul Apps Manually.md"
GUIDE_PDF = HERE / "Installing the Soul Apps Manually.pdf"

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    str(Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe"),
]

PAGE_RE = re.compile(rb"/Type\s*/Page[^s]")
HEADING_RE = re.compile(r"^(#{1,3})\s+(.*?)\s*(?:\{:\s*([^}]*)\})?\s*$")
ITEM_RE = re.compile(r"^\s*(?:[*-]|\d+\.)\s+")
RULE_RE = re.compile(r"^-{3,}$")
TABLE_SEP_RE = re.compile(r"^\|[\s:|-]+\|$")


# --------------------------------------------------------------------------- #
# markdown -> HTML, for the constructs the guide uses
# --------------------------------------------------------------------------- #
def esc(text):
    return html.escape(text, quote=False)


def inline(text):
    """Bold, italics and `code`, with code spans protected from the rest."""
    parts = []
    for part in re.split(r"(`[^`]+`)", text):
        if len(part) > 1 and part.startswith("`") and part.endswith("`"):
            parts.append("<code>" + esc(part[1:-1]) + "</code>")
        else:
            parts.append(esc(part))
    joined = "".join(parts)
    joined = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", joined)
    joined = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", joined)
    return joined


def is_block_start(line):
    stripped = line.strip()
    return (
        stripped.startswith(("#", ">", "|", "```"))
        or RULE_RE.match(stripped) is not None
    )


def split_table_row(line):
    row = line.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [cell.strip() for cell in row.split("|")]


def render_table(lines, i):
    head = split_table_row(lines[i])
    aligns = []
    for cell in split_table_row(lines[i + 1]):
        left, right = cell.startswith(":"), cell.endswith(":")
        if left and right:
            aligns.append("center")
        elif right:
            aligns.append("right")
        elif left:
            aligns.append("left")
        else:
            aligns.append("")
    i += 2
    body = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        body.append(split_table_row(lines[i]))
        i += 1

    def cell(tag, text, index):
        style = aligns[index] if index < len(aligns) else ""
        attr = ' style="text-align:%s"' % style if style else ""
        return "<%s%s>%s</%s>" % (tag, attr, inline(text), tag)

    out = ["<table><thead><tr>"]
    out.extend(cell("th", text, n) for n, text in enumerate(head))
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        out.extend(cell("td", text, n) for n, text in enumerate(row))
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out), i


def render_list(lines, i):
    ordered = bool(re.match(r"^\s*\d+\.\s+", lines[i]))
    items = []
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            look = i
            while look < len(lines) and not lines[look].strip():
                look += 1
            if look < len(lines) and ITEM_RE.match(lines[look]):
                i = look
                continue
            break
        if not ITEM_RE.match(line):
            break
        text = ITEM_RE.sub("", line)
        i += 1
        while (
            i < len(lines)
            and lines[i].strip()
            and not ITEM_RE.match(lines[i])
            and not is_block_start(lines[i])
        ):
            text += " " + lines[i].strip()
            i += 1
        items.append("<li>" + inline(text) + "</li>")
    tag = "ol" if ordered else "ul"
    return "<%s>%s</%s>" % (tag, "".join(items), tag), i


def render(markdown_text):
    lines = markdown_text.replace("\r\n", "\n").split("\n")
    bits = []
    para = []
    i = 0

    def flush():
        if para:
            bits.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            flush()
            lang = stripped[3:].strip()
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            cls = ' class="language-%s"' % esc(lang) if lang else ""
            bits.append("<pre><code%s>%s</code></pre>" % (cls, esc("\n".join(code))))
            continue

        if not stripped:
            flush()
            i += 1
            continue

        heading = HEADING_RE.match(line)
        if heading:
            flush()
            level = len(heading.group(1))
            classes = (heading.group(3) or "").replace(".", " ").split()
            cls = ' class="%s"' % " ".join(classes) if classes else ""
            bits.append(
                "<h%d%s>%s</h%d>"
                % (level, cls, inline(heading.group(2)), level)
            )
            i += 1
            continue

        if RULE_RE.match(stripped):
            flush()
            bits.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            bits.append("<blockquote><p>" + inline(" ".join(quote)) + "</p></blockquote>")
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and TABLE_SEP_RE.match(lines[i + 1].strip()):
            flush()
            table, i = render_table(lines, i)
            bits.append(table)
            continue

        if ITEM_RE.match(line):
            flush()
            rendered, i = render_list(lines, i)
            bits.append(rendered)
            continue

        para.append(stripped)
        i += 1

    flush()
    return wrap_sheet_page("".join(bits))


def wrap_sheet_page(body):
    """Put the quick-reference section in its own small-type wrapper."""
    start = body.find('<h2 class="newpage sheet">')
    if start == -1:
        start = body.find('<h2 class="sheet newpage">')
    if start == -1:
        return body
    end = body.find("<h2", start + 4)
    if end == -1:
        end = len(body)
    return body[:start] + '<div class="sheetpage">' + body[start:end] + "</div>" + body[end:]


CSS = """
@page { size: A4; margin: 17mm 16mm 18mm 16mm;
        @bottom-left { content: "Installing the Soul Apps Manually";
                       font-family: "Segoe UI", Arial, sans-serif;
                       font-size: 8pt; color: #6b7280; }
        @bottom-right { content: "Page " counter(page) " of " counter(pages);
                        font-family: "Segoe UI", Arial, sans-serif;
                        font-size: 8pt; color: #6b7280; } }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt;
       line-height: 1.45; color: #1c2230; margin: 0;
       orphans: 3; widows: 3; }
h1 { font-size: 23pt; color: #12324f; margin: 0 0 10pt 0;
     border-bottom: 3px solid #1f6f8b; padding-bottom: 8pt; }
h2 { font-size: 15.5pt; color: #12324f; margin: 16pt 0 6pt 0;
     padding-bottom: 3pt; border-bottom: 1px solid #d8dee7;
     break-after: avoid; page-break-after: avoid; }
h3 { font-size: 11.5pt; color: #1f6f8b; margin: 12pt 0 4pt 0;
     break-after: avoid; page-break-after: avoid; }
p { margin: 5pt 0; }
ul, ol { margin: 5pt 0; padding-left: 16pt; }
li { margin: 2pt 0; }
code { font-family: Consolas, "Courier New", monospace; font-size: 9.4pt;
       background: #f2f4f7; padding: 0 3pt; border-radius: 2pt; }
pre { background: #f6f8fa; border: 1px solid #d8dee7; border-left: 3px solid #1f6f8b;
      border-radius: 3pt; padding: 6pt 8pt; margin: 5pt 0 8pt 0;
      break-inside: avoid; page-break-inside: avoid;
      white-space: pre-wrap; word-wrap: break-word; }
pre code { background: none; padding: 0; font-size: 8.8pt; line-height: 1.32; }
/* keep the sentence that introduces a block on the same page as the block */
p:has(+ pre), p:has(+ table), p:has(+ ul), p:has(+ ol)
    { break-after: avoid; page-break-after: avoid; }
blockquote { margin: 7pt 0; padding: 5pt 10pt; border-left: 3px solid #b45309;
             background: #fdf7ee; break-inside: avoid; page-break-inside: avoid; }
blockquote p { margin: 0; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0 9pt 0;
        font-size: 9.2pt; break-inside: avoid; page-break-inside: avoid; }
th, td { border: 1px solid #d8dee7; padding: 3pt 5pt; text-align: left;
         vertical-align: top; }
th { background: #eef2f6; color: #12324f; font-weight: 600; }
td code, th code { font-size: 8.6pt; }
hr { border: none; border-top: 1px solid #dfe4ea; margin: 10pt 0; }
h2.newpage { break-before: page; page-break-before: always; margin-top: 0; }
.sheetpage { font-size: 8.6pt; line-height: 1.3; }
.sheetpage h2 { font-size: 11.5pt; margin: 0 0 5pt 0; padding-bottom: 2pt; }
.sheetpage p { margin: 2.5pt 0; }
.sheetpage code { font-size: 7.9pt; }
.sheetpage pre { padding: 3pt 6pt; margin: 2pt 0 4pt 0; }
.sheetpage pre code { font-size: 7.4pt; line-height: 1.24; }
"""


# --------------------------------------------------------------------------- #
# printing
# --------------------------------------------------------------------------- #
def find_chrome():
    for path in CHROME_PATHS:
        if Path(path).exists():
            return path
    raise SystemExit(
        "ERROR: Google Chrome not found; install it or add its path to CHROME_PATHS"
    )


def count_pages(pdf):
    try:
        from pypdf import PdfReader  # optional, only used when installed

        return len(PdfReader(str(pdf)).pages)
    except Exception:
        pass
    return len(PAGE_RE.findall(pdf.read_bytes())) or None


def build():
    if not GUIDE_MD.exists():
        raise SystemExit("ERROR: guide not found: %s" % GUIDE_MD)
    body = render(GUIDE_MD.read_text(encoding="utf-8"))
    page = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Installing the Soul Apps Manually</title>"
        "<style>" + CSS + "</style></head><body>" + body + "</body></html>"
    )

    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        html_path = tmp / "guide.html"
        html_path.write_text(page, encoding="utf-8")
        if GUIDE_PDF.exists():
            GUIDE_PDF.unlink()
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-pdf-header-footer",
                "--user-data-dir=" + str(tmp / "chrome-profile"),
                "--print-to-pdf=" + str(GUIDE_PDF),
                html_path.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    if not GUIDE_PDF.exists():
        raise SystemExit("ERROR: Chrome did not write the PDF")
    return count_pages(GUIDE_PDF)


def check():
    if not GUIDE_PDF.exists():
        print("OUT OF DATE: missing " + GUIDE_PDF.name)
        return 1
    if GUIDE_PDF.stat().st_mtime < GUIDE_MD.stat().st_mtime:
        print("OUT OF DATE: the guide PDF is older than the markdown")
        print("Run: py build_guide_pdf.py")
        return 1
    print("OK: %s is up to date" % GUIDE_PDF.name)
    return 0


def main():
    args = sys.argv[1:]
    if "--check" in args:
        return check()
    pages = build()
    print(
        "guide PDF rebuilt: %s (%s page(s), %d KB)"
        % (GUIDE_PDF.name, pages, GUIDE_PDF.stat().st_size // 1024)
    )
    if "--open" in args:
        subprocess.Popen(["cmd", "/c", "start", "", str(GUIDE_PDF)], shell=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
