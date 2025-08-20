# file:///D:/JU/index.html
# python generate_poem_html_adhir.py
import re
from pathlib import Path
from weasyprint import HTML

# ---------- Paths ----------
ROOT = Path(".")
AUDIO_DIR = ROOT / "audio"
AUDIO_DIR.mkdir(exist_ok=True)
TXT_PATH = ROOT / "Poem5.txt"
HTML_PATH = ROOT / "index5.html"
PDF_PATH = ROOT / "poems.pdf"

# ---------- Read Poems ----------
raw_text = TXT_PATH.read_text(encoding="utf-8")

pattern = re.compile(
    r"(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}) - \+91 79809 33948:\s*[\"']?(.*?)[\"']?\s*\n"
    r"(?:audio:(.*?)\n)?"
    r"\n?(.*?)(?=\n\d{2}/\d{2}/\d{4}, \d{2}:\d{2} - |\Z)",
    re.DOTALL
)
matches = pattern.findall(raw_text)

# ---------- Build HTML for browser ----------
html = """<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8">
  <title>বাংলা কবিতা সংকলন</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: 'Noto Serif Bengali', serif; margin: 0; padding: 0; display: flex; height: 100vh; overflow: hidden; }
    aside { width: 40%; background: #f4f4f4; padding: 2em; overflow-y: auto; border-right: 1px solid #ccc; }
    main { width: 60%; padding: 2em; overflow-y: auto; }
    h1 { color: #003366; margin-top: 0; }
    .index a { display: block; margin: 0.5em 0; color: #0066cc; text-decoration: none; }
    .index a:hover { text-decoration: underline; }
    .poem { margin-bottom: 4em; }
    p { white-space: pre-line; }
    audio { margin-top: 10px; display: block; }
    #searchBox { width: 100%; padding: 8px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
    .download-link { display: inline-block; margin: 1em 0; padding: 8px 12px; background: #0066cc; color: white; text-decoration: none; border-radius: 4px; }
    .download-link:hover { background: #004c99; }
    h2 { color: #222; margin-bottom: 0.3em; }
  </style>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Bengali&display=swap" rel="stylesheet">
</head>
<body>
  <aside>
    <h1>📚 বাংলা কবিতা সংকলন</h1>
    <p><strong>✍ কবি : অধীর মন্ডল (+91 79809 33948)</strong></p>

    <!-- 🔍 Search Box -->
    <input type="text" id="searchBox" placeholder="🔍 কবিতা খুঁজুন..." onkeyup="filterPoems()">

    <!-- 📄 Download PDF -->
    <a href="poems.pdf" class="download-link" download>📥 Download PDF</a>

    <div class="index">
"""

main_content = ""
index_links = ""   # for HTML sidebar
pdf_index = ""     # for PDF index
AUDIO_EXTS = [".mp3", ".aac", ".m4a"]

for idx, (_, title, audio_file, body) in enumerate(matches, start=1):
    title = (title or "").strip()
    body = (body or "").strip()
    anchor = f"poem{idx}"

    # Resolve audio
    numbered_name = f"poem{idx}.mp3"
    safe_title = title.replace(" ", "_")
    explicit = (audio_file or "").strip().replace(" ", "_") if audio_file else None
    candidates = []
    if explicit:
        candidates.append(explicit)
    candidates.append(numbered_name)
    candidates.extend([safe_title + ext for ext in AUDIO_EXTS])

    found_audio = None
    for cand in candidates:
        if (AUDIO_DIR / cand).exists():
            found_audio = cand
            break

    audio_html = ""
    title_display = title
    if found_audio:
        audio_html = f'<audio controls><source src="audio/{found_audio}" type="audio/mpeg"></audio>'
        title_display += " 🎵"

    # HTML aside index
    index_links += f'      <a href="#{anchor}" class="poem-link">{title_display}</a>\n'

    # HTML main content
    main_content += f"""
    <div class="poem" id="{anchor}">
      <h2 id="pdf-{anchor}">{idx}. {title}</h2>
      {audio_html}
      <p>{body}</p>
    </div>
"""

    # PDF index page (with target-counter for page number)
    pdf_index += f'<p>{idx}. {title} ...... <span class="page-num" target="#pdf-{anchor}" target-counter(page)></span></p>\n'

# Finish HTML for browser
html += index_links
html += f"""    </div>
  </aside>
  <main id="poemContainer">
{main_content}
  </main>

<script>
function filterPoems() {{
  const query = document.getElementById("searchBox").value.toLowerCase();
  const links = document.querySelectorAll(".index .poem-link");
  links.forEach(link => {{
    const text = link.textContent.toLowerCase();
    link.style.display = text.includes(query) ? "block" : "none";
  }});
}}
</script>

</body>
</html>
"""
HTML_PATH.write_text(html, encoding="utf-8")

# ---------- Build PDF ----------
pdf_html = f"""
<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: 'Noto Serif Bengali', serif; margin: 2em; }}
  h1 {{ text-align: center; color: #003366; }}
  h2 {{ margin-top: 1.5em; color: #222; }}
  p {{ white-space: pre-line; line-height: 1.6; }}
  .index p {{ margin: 0.3em 0; }}
  .page-num::before {{ content: "পৃষ্ঠা " target-counter(attr(target), page); }}
</style>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Bengali&display=swap" rel="stylesheet">
</head>
<body>

<h1>📚 বাংলা কবিতা সংকলন</h1>
<p style="text-align:center"><strong>✍ কবি : অধীর মন্ডল (+91 79809 33948)</strong></p>

<div class="index">
  <h2>সূচীপত্র</h2>
  {pdf_index}
</div>

<div style="page-break-after: always;"></div>

<div class="poems">
{main_content}
</div>

</body>
</html>
"""

HTML(string=pdf_html).write_pdf(str(PDF_PATH))

print("✅ index5.html and poems.pdf generated successfully (WeasyPrint with index + page numbers).")

