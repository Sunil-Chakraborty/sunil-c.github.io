# file:///D:/JU/index3.html
# python generate_golpo_html_gen.py

import re
from pathlib import Path

with open("Poem3.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# Regex: poet, title, optional media
pattern = re.compile(
    r"(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}) - (.*?): ?[\"']?(.*?)[\"']?\n"
    r"(?:(audio|video|image|pdf):(.*?)\n)?"
    r"\n?(.*?)(?=\n\d{2}/\d{2}/\d{4}, \d{2}:\d{2} - |\Z)",
    re.DOTALL
)
matches = pattern.findall(raw_text)

# Start HTML
html = """<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8">
  <title>বাংলা গল্প সংকলন</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <style>
    body { font-family: 'Noto Serif Bengali', serif; margin: 0; padding: 0; display: flex; height: 100vh; overflow: hidden; }
    aside { width: 30%; background: #f4f4f4; padding: 2em; overflow-y: auto; border-right: 1px solid #ccc; }
    main { width: 70%; padding: 2em; overflow-y: auto; }
    h1 { color: #003366; margin-top: 0; }
    #searchBox { width: 100%; padding: 8px; margin: 10px 0; font-size: 1em; border: 1px solid #ccc; border-radius: 4px; }
    .index a { display: block; margin: 0.5em 0; color: #0066cc; text-decoration: none; }
    .index a:hover { text-decoration: underline; }
    #.index a.has-media { color: green; font-weight: bold; }
    .poem { margin-bottom: 4em; }
    p { white-space: pre-line; }
    .media-card {
      background: #fafafa;
      border: 1px solid #ddd;
      border-radius: 10px;
      padding: 12px;
      margin: 15px 0;
      box-shadow: 0 2px 6px rgba(0,0,0,0.1);
      text-align: center;
    }
    .media-card audio,
    .media-card video {
      width: 80%;
      outline: none;
      margin: 8px auto 0 auto;
      display: block;
    }
    .media-card img {
      max-width: 80%;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      margin: 8px auto 0 auto;
      display: block;
    }
    .media-caption {
      font-size: 0.9em;
      font-weight: bold;
      color: #444;
      margin: 0;
    }
    .audio-thumb {
      width: 100px;      /* thumbnail size */
      height: 100px;     /* fixed height to keep circle shape */
      border-radius: 50%; /* makes it round */
      object-fit: cover;  /* ensures image fills the circle without stretching */
      margin-bottom: 8px;
      display: block;
      margin-left: auto;
      margin-right: auto;
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }


  </style>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Bengali&display=swap" rel="stylesheet">
</head>
<body>
  <aside>
    <h1>📚 পারিবারিক সংকলন   </h1>
    <input type="text" id="searchBox" placeholder="🔍 খুঁজে দেখুন ..." onkeyup="filterPoems()">
    <div class="index">
"""

# Build index + main content
main_content = ""
for idx, (_, poet, title, media_type, media_file, body) in enumerate(matches, start=1):
    anchor = f"poem{idx}"

    # Has media?
    has_media = media_file and media_file.strip()
    link_class = "has-media" if has_media else ""
    
    # Choose emoji
    emoji = ""
    if has_media:
        if media_type == "audio":
            emoji = " 🎵"
        elif media_type == "video":
            emoji = " 🎥"
        elif media_type == "image":
            emoji = " 🖼️"
        elif media_type == "pdf":
            emoji = " 📄"
            
    # Aside index link
    html += f'      <a href="#{anchor}" class="{link_class}">{title}{emoji} - {poet}</a>\n'

    # Media block
    media_html = ""
    if has_media:
        parts = media_file.strip().split("|")
        file_name = parts[0].strip()
        cover_img = parts[1].strip() if len(parts) > 1 else None
        media_path = Path("media") / file_name
        cover_path = Path("media") / cover_img if cover_img else None

        if media_type == "audio":
            img_html = f'<img src="media/{cover_img}" alt="{title} cover" class="audio-thumb">' if cover_img and cover_path.exists() else ""
            if media_path.exists():
                media_html = f'''
                <div class="media-card">
                  {img_html}
                  <p class="media-caption">🎵 পাঠ</p>
                  <audio controls>
                    <source src="media/{file_name}" type="audio/mpeg">
                  </audio>
                </div>'''

        elif media_type == "video":
            if media_file.strip().startswith("http"):
                # external video (Google Drive, YouTube, etc.)
                media_html = f'''
                <div class="media-card">
                  <p class="media-caption">🎥 ভিডিও</p>
                  <iframe src="{media_file.strip()}" width="640" height="360" allow="autoplay" allowfullscreen></iframe>
                </div>'''
            else:
                poster_attr = f' poster="media/{cover_img}"' if cover_img and cover_path.exists() else ""
                if media_path.exists():
                    media_html = f'''
                    <div class="media-card">
                      <p class="media-caption">🎥 ভিডিও</p>
                      <video controls {poster_attr}>
                        <source src="media/{file_name}" type="video/mp4">
                      </video>
                    </div>'''

        elif media_type == "image":
            if media_path.exists():
                media_html = f'''
                <div class="media-card">
                  <p class="media-caption">🖼️ ছবি</p>
                  <img src="media/{file_name}" alt="{title}">
                </div>'''

        elif media_type == "pdf":
            if media_file.strip().startswith("http"):
                # external PDF (e.g., Google Drive preview link)
                media_html = f'''
                <div class="media-card">
                  <p class="media-caption">📄 পিডিএফ ফাইল</p>
                  <iframe src="{media_file.strip()}" width="100%" height="500px"></iframe>
                  <p><a href="{media_file.strip()}" target="_blank">🔗 পূর্ণ পিডিএফ দেখুন</a></p>
                </div>'''
            else:
                if media_path.exists():
                    media_html = f'''
                    <div class="media-card">
                      <p class="media-caption">📄 পিডিএফ ফাইল</p>
                      <iframe src="media/{file_name}" width="100%" height="500px"></iframe>
                      <p><a href="media/{file_name}" target="_blank">🔗 পূর্ণ পিডিএফ দেখুন</a></p>
                    </div>'''
                
    # Poem block
    main_content += f"""
    <div class="poem" id="{anchor}">
      <h2>{title}</h2>
      <p><strong><em>লেখক : {poet}</em></strong></p>
      {media_html}
      <p>{body.strip()}</p>
    </div>
"""

# Close HTML
html += f"""    </div>
  </aside>
  <main id="poemContainer">
{main_content}
  </main>

<script>
function filterPoems() {{
  let input = document.getElementById("searchBox").value.toLowerCase();
  let links = document.querySelectorAll(".index a");
  links.forEach(link => {{
    if (link.textContent.toLowerCase().includes(input)) {{
      link.style.display = "block";
    }} else {{
      link.style.display = "none";
    }}
  }});
}}
</script>

</body>
</html>
"""

Path("index9.html").write_text(html, encoding="utf-8")
print("✅ index9.html generated successfully with Google Drive video embed + local media support!")
