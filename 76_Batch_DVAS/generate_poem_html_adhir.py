# file:///D:/JU/index.html
# python generate_poem_html_adhir.py
import re
from pathlib import Path

# Paths
audio_dir = Path("audio")
image_dir = Path("image")
audio_dir.mkdir(exist_ok=True)
image_dir.mkdir(exist_ok=True)

# Read poems
with open("Poem.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# Regex: optional audio + optional image
pattern = re.compile(
    r"(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}) - .*?: ?[\"']?(.*?)[\"']?\n"
    r"(?:(?:audio):(.*?)\n)?"
    r"(?:(?:image):(.*?)\n)?"
    r"\n?(.*?)(?=\n\d{2}/\d{2}/\d{4}, \d{2}:\d{2} - |\Z)",
    re.DOTALL
)
matches = pattern.findall(raw_text)

# Start HTML
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
    audio { margin-top: 10px; display: block; max-width: 100%; }
    img { 
      margin: 10px 0;       /* space above/below */
      display: block; 
      max-width: 50%;       /* reduce size to 50% */
      height: auto; 
      float: left;          /* left-align image */
      margin-right: 15px;   /* add gap between image and text */
    }
    #searchBox { width: 100%; padding: 8px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
  </style>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Bengali&display=swap" rel="stylesheet">
</head>
<body>
  <aside>
    <h1>📚 বাংলা কবিতা সংকলন</h1>
    <p><strong>✍ কবি : অধীর মন্ডল (+91 79809 33948)</strong></p>
    <input type="text" id="searchBox" placeholder="🔍 কবিতা খুঁজুন..." onkeyup="filterPoems()">
    <div class="index">
"""

# Build content
main_content = ""
AUDIO_EXTS = [".mp3", ".aac", ".m4a"]

for idx, (_, title, audio_file, image_file, body) in enumerate(matches, start=1):
    anchor = f"poem{idx}"
    title_display = title

    # ==== AUDIO handling ====
    audio_html = ""
    numbered_name = f"poem{idx}.mp3"
    safe_title = title.strip().replace(" ", "_")

    title_candidates = [safe_title + ext for ext in AUDIO_EXTS]
    explicit = audio_file.strip().replace(" ", "_") if audio_file else None

    candidates = []
    if explicit:
        candidates.append(explicit)
    candidates.append(numbered_name)
    candidates.extend(title_candidates)

    found_audio = None
    for cand in candidates:
        if (audio_dir / cand).exists():
            found_audio = cand
            break
    if found_audio:
        audio_html = f'<audio controls><source src="audio/{found_audio}" type="audio/mpeg"></audio>'
        title_display += " 🎵"

    # ==== IMAGE handling ====
    image_html = ""
    if image_file and (image_dir / image_file.strip()).exists():
        image_html = f'<img src="image/{image_file.strip()}" alt="{title} illustration">'

    # ==== INDEX ====
    html += f'      <a href="#{anchor}" class="poem-link">{title_display}</a>\n'

    # ==== MAIN CONTENT ====
    main_content += f"""
    <div class="poem" id="{anchor}">
      <h2>{title}</h2>
      {image_html}
      {audio_html}
      <p>{body.strip()}</p>
    </div>
"""

# Finish HTML
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

# Save
Path("index.html").write_text(html, encoding="utf-8")
print("✅ index.html generated with audio + image support!")
