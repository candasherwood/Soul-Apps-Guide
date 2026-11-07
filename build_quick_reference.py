#!/usr/bin/env python3
"""
Rebuild the standalone quick-reference sheet from the main guide.

The guide, "Installing the Soul Apps Manually.md", is the single source of truth.
Its "Quick reference" section is lifted verbatim into three derived files, so the
sheet can never drift from the guide:

    Soul Apps Quick Reference.md     source for the sheet
    Soul Apps Quick Reference.pdf    the one-page printable sheet (A4)
    Soul Apps Quick Reference.txt    the same content as plain text

Usage:
    py build_quick_reference.py            rebuild all three files
    py build_quick_reference.py --check    exit 1 if any of them is out of date
    py build_quick_reference.py --watch    rebuild whenever the guide is saved

Needs Python 3.9+ and Google Chrome. No pip packages: the markdown renderer is
built in, and the PDF is printed by Chrome's headless mode.
"""
import html
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
GUIDE = HERE / "Installing the Soul Apps Manually.md"
SHEET_MD = HERE / "Soul Apps Quick Reference.md"
SHEET_PDF = HERE / "Soul Apps Quick Reference.pdf"
SHEET_TXT = HERE / "Soul Apps Quick Reference.txt"

START_MARK = "## Quick reference"
END_MARK = "## 1. What you are installing"
FIRST_LINE = "**Python check**"
TYPE_SIZES = [12, 11.5, 11, 10.5, 10, 9.5, 9]
TEXT_WIDTH = 72

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    str(Path.home() / r"AppData\Local\Google\Chrome\Application\chrome.exe"),
]

TITLE = "# Soul Apps \u2014 Quick reference"
INTRO = (
    "Every install and start command on one page, for pinning up next to the machine.\n"
    "The full walkthrough with explanations is in *Installing the Soul Apps Manually*."
)
FOOTER = (
    "---\n\n"
    "*Soul Apps live in `D:\\SoulApps`. The full guide "
    "(`Installing the Soul Apps Manually.pdf`)\n"
    "explains each command, the order to run them in, and what to do when "
    "something fails.*"
)

PAGE_RE = re.compile(rb"/Type\s*/Page[^s]")


# --------------------------------------------------------------------------- #
# source extraction
# --------------------------------------------------------------------------- #
def extract_commands(guide_text):
    """Return the commands-only block of the guide's quick-reference section."""
    if START_MARK not in guide_text:
        raise SystemExit(f"ERROR: '{START_MARK}' not found in {GUIDE.name}")
    if END_MARK not in guide_text:
        raise SystemExit(f"ERROR: '{END_MARK}' not found in {GUIDE.name}")
    start = guide_text.index(START_MARK)
    end = guide_text.index(END_MARK, start)
    lines = guide_text[start:end].splitlines()
    for i, line in enumerate(lines):
        if line.startswith(FIRST_LINE):
            return "\n".join(lines[i:]).strip() + "\n"
    raise SystemExit(
        f"ERROR: no line starting '{FIRST_LINE}' in the quick-reference section"
    )


def build_markdown(commands):
    return f"{TITLE}\n\n{INTRO}\n\n{commands}\n{FOOTER}\n"


# --------------------------------------------------------------------------- #
# markdown -> HTML (just the constructs the sheet uses)
# --------------------------------------------------------------------------- #
def inline(text):
    out = []
    for part in re.split(r"(`[^`]+`)", text):
        if len(part) > 1 and part.startswith("`") and part.endswith("`"):
            out.append("<code>" + html.escape(part[1:-1]) + "</code>")
        else:
            esc = html.escape(part)
            esc = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc)
            esc = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", esc)
            out.append(esc)
    return "".join(out)


def render_html(md, base, target):
    bits, para, code, in_code = [], [], [], False

    def flush():
        if para:
            bits.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            if in_code:
                bits.append(
                    "<pre><code>" + html.escape("\n".join(code)) + "</code></pre>"
                )
                in_code, code = False, []
            else:
                flush()
                in_code = True
            continue
        if in_code:
            code.append(raw)
            continue
        if not line.strip():
            flush()
            continue
        if line.strip() == "---":
            flush()
            bits.append("<hr>")
            continue
        if line.startswith("# "):
            flush()
            bits.append("<h1>" + inline(line[2:]) + "</h1>")
            continue
        para.append(line.strip())
    flush()

    css = f"""
@page {{ size: A4; margin: 14mm 14mm 12mm 14mm; }}
body {{ font-family: "Segoe UI", Arial, sans-serif; font-size: {base}pt; line-height: 1.4;
        color: #1c2230; margin: 0; }}
h1 {{ font-size: {base + 11}pt; margin: 0 0 3pt 0; color: #12324f;
      border-bottom: 3px solid #1f6f8b; padding-bottom: 6pt; }}
p {{ margin: 3pt 0; }}
strong {{ color: #0f2438; }}
code {{ font-family: Consolas, "Courier New", monospace; font-size: {base - 1.2}pt;
        background: #f2f4f7; padding: 1pt 3pt; border-radius: 2pt; }}
pre {{ background: #f6f8fa; border: 1px solid #d8dee7; border-left: 3px solid #1f6f8b;
       border-radius: 3pt; padding: 4pt 7pt; margin: 3pt 0 6pt 0;
       page-break-inside: avoid; white-space: pre-wrap; word-wrap: break-word; }}
pre code {{ background: none; padding: 0; font-size: {base - 2.2}pt; line-height: 1.28; }}
hr {{ border: none; border-top: 1px solid #d8dee7; margin: 8pt 0 5pt 0; }}
em {{ color: #44505f; }}
"""
    target.write_text(
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Soul Apps Quick Reference</title><style>"
        + css
        + "</style></head><body>"
        + "".join(bits)
        + "</body></html>",
        encoding="utf-8",
    )


# --------------------------------------------------------------------------- #
# markdown -> plain text
# --------------------------------------------------------------------------- #
def plain(s):
    s = s.replace("\u2014", "-").replace("\u2013", "-").replace("*", "")
    return re.sub(r"`([^`]+)`", r"\1", s).strip()


def build_text(md):
    lines = md.splitlines()
    out = ["SOUL APPS - QUICK REFERENCE", "=" * 27]
    pending = []
    after_label = False

    def blank():
        if out and out[-1] != "":
            out.append("")

    def flush():
        nonlocal after_label
        if not pending:
            return
        text = plain(" ".join(pending))
        pending.clear()
        blank()
        out.extend(
            textwrap.wrap(
                text, width=TEXT_WIDTH, break_long_words=False,
                break_on_hyphens=False,
            )
            or [""]
        )
        after_label = False

    i = 1
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            flush()
            i += 1
            if not after_label:
                blank()
            while i < len(lines) and not lines[i].startswith("```"):
                out.append("    " + lines[i])
                i += 1
            i += 1
            after_label = False
            continue
        if line.strip() == "---":
            flush()
            after_label = False
            blank()
            out.append("-" * TEXT_WIDTH)
            i += 1
            continue
        label = re.match(r"\*\*(.+?)\*\*(.*)", line)
        if label:
            flush()
            rest = re.sub(r"`([^`]+)`", r"\1", label.group(2))
            rest = rest.replace("\u2014", "-").replace("\u2013", "-").rstrip()
            blank()
            out.append(plain(label.group(1)).upper() + rest)
            after_label = True
            i += 1
            continue
        if not line.strip() or line.startswith("# "):
            flush()
            i += 1
            continue
        pending.append(line.strip())
        i += 1
    flush()
    text = ("\r\n".join(out)).strip() + "\r\n"
    try:
        text.encode("ascii")
    except UnicodeEncodeError as exc:
        raise SystemExit(f"ERROR: non-ASCII character in the text sheet: {exc}")
    return text


# --------------------------------------------------------------------------- #
# PDF printing
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


def print_pdf(chrome, html_path, profile, base):
    if SHEET_PDF.exists():
        SHEET_PDF.unlink()
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--user-data-dir=" + str(profile),
            "--print-to-pdf=" + str(SHEET_PDF),
            html_path.as_uri(),
        ],
        check=True,
        capture_output=True,
    )
    if not SHEET_PDF.exists():
        raise SystemExit("ERROR: Chrome did not write the PDF")
    return count_pages(SHEET_PDF)


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def build():
    if not GUIDE.exists():
        raise SystemExit(f"ERROR: guide not found: {GUIDE}")
    md = build_markdown(extract_commands(GUIDE.read_text(encoding="utf-8")))
    text = build_text(md)

    md_changed = not SHEET_MD.exists() or SHEET_MD.read_text(encoding="utf-8") != md
    txt_changed = (
        not SHEET_TXT.exists() or SHEET_TXT.read_bytes() != text.encode("ascii")
    )
    if md_changed:
        SHEET_MD.write_text(md, encoding="utf-8")
    if txt_changed:
        SHEET_TXT.write_bytes(text.encode("ascii"))

    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        html_path = tmp / "sheet.html"
        profile = tmp / "chrome-profile"
        for base in TYPE_SIZES:
            render_html(md, base, html_path)
            pages = print_pdf(chrome, html_path, profile, base)
            if pages == 1:
                return md_changed, txt_changed, base, 1
            if pages is None:
                print(f"  warning: could not count pages; kept {base}pt")
                return md_changed, txt_changed, base, None
            print(f"  {base}pt overflowed to {pages} pages, trying smaller type")
    raise SystemExit("ERROR: the sheet does not fit on one page even at the smallest type")


def check():
    missing = [p.name for p in (SHEET_MD, SHEET_PDF, SHEET_TXT) if not p.exists()]
    if missing:
        print("OUT OF DATE: missing " + ", ".join(missing))
        return 1
    md = build_markdown(extract_commands(GUIDE.read_text(encoding="utf-8")))
    if SHEET_MD.read_text(encoding="utf-8") != md:
        print("OUT OF DATE: the markdown sheet differs from the guide")
        print("Run: py build_quick_reference.py")
        return 1
    if SHEET_TXT.read_bytes() != build_text(md).encode("ascii"):
        print("OUT OF DATE: the text sheet differs from the guide")
        print("Run: py build_quick_reference.py")
        return 1
    pages = count_pages(SHEET_PDF)
    if pages != 1:
        print(f"OUT OF DATE: sheet PDF has {pages} page(s), expected 1")
        return 1
    print(
        f"OK: all three files match the guide "
        f"({SHEET_PDF.stat().st_size // 1024} KB PDF, 1 page)"
    )
    return 0


def main():
    args = sys.argv[1:]
    if "--check" in args:
        return check()
    if "--watch" in args:
        print(f"watching {GUIDE.name} - press Ctrl+C to stop")
        stamp = GUIDE.stat().st_mtime
        while True:
            time.sleep(2)
            current = GUIDE.stat().st_mtime
            if current != stamp:
                stamp = current
                print(time.strftime("%H:%M:%S"), "guide changed, rebuilding...")
                try:
                    md_changed, txt_changed, base, pages = build()
                    print(
                        f"  md {'updated' if md_changed else 'unchanged'}, "
                        f"txt {'updated' if txt_changed else 'unchanged'}, "
                        f"{base}pt, {pages} page(s)"
                    )
                except SystemExit as exc:
                    print("  build failed:", exc)
        return 0

    md_changed, txt_changed, base, pages = build()
    print(f"markdown {'updated' if md_changed else 'unchanged'}: {SHEET_MD.name}")
    print(f"text     {'updated' if txt_changed else 'unchanged'}: {SHEET_TXT.name}")
    print(
        f"PDF      rebuilt at {base}pt: {SHEET_PDF.name} "
        f"({pages} page(s), {SHEET_PDF.stat().st_size // 1024} KB)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
