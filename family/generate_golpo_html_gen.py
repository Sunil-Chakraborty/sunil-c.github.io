# python generate_golpo_html_gen.py
# https://tinyurl.com/paribernama

import re
from pathlib import Path

# Read raw text file
with open("Poem3.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# Regex: poet, title, optional media, optional dance
pattern = re.compile(
    r"(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}) - (.*?): ?[\"']?(.*?)[\"']?\n"
    r"(?:(audio|video|image|pdf):(.*?)\n)?"
    r"(?:(dance|painter):(.*?)\n)?"
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
    .index a.has-media { color: green; font-weight: bold; }
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
      width: 100px;
      height: 100px;
      border-radius: 50%;
      object-fit: cover;
      margin-bottom: 8px;
      display: block;
      margin-left: auto;
      margin-right: auto;
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }

    /* 🎨 Painting frame (6 images in flexbox) */
    .painting-frame {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 10px;
      margin: 20px 0;
    }
    .painting-frame img {
      width: 150px;
      height: 150px;
      object-fit: cover;
      border-radius: 10px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
      transition: transform 0.2s ease;
    }
    .painting-frame img:hover {
      transform: scale(1.05);
    }
  </style>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Bengali&display=swap" rel="stylesheet">
</head>
<body>
  <aside>
    <h1>👨‍👩‍👧‍👦 পারিবারিক কার্যক্রম</h1>
    <input type="text" id="searchBox" placeholder="🔍 খুঁজে দেখুন ..." onkeyup="filterPoems()">
    <div class="index">
"""

# Build index + main content
main_content = ""
for idx, (_, poet, title, media_type, media_file, dance_tag, dance_file, body) in enumerate(matches, start=1):
    anchor = f"poem{idx}"

    # Determine if it has media
    has_media = media_file and media_file.strip()
    link_class = "has-media" if has_media else ""

    # Add to side index
    html += f'      <a href="#{anchor}" class="{link_class}">{title} - {poet}</a>\n'

    # Build media HTML
    media_html = ""
    if has_media:
        parts = media_file.strip().split("|")
        file_name = parts[0].strip()
        cover_img = parts[1].strip() if len(parts) > 1 else None
        media_path = Path("media") / file_name
        cover_path = Path("media") / cover_img if cover_img else None

        if media_type == "audio":
            if media_file.strip().startswith("http") and "facebook.com/reel" in media_file:
                media_html = f'''
                <div class="media-card">
                  <p class="media-caption">🎵 ফেসবুক রিল</p>
                  <iframe src="https://www.facebook.com/plugins/video.php?href={media_file.strip()}&show_text=false&width=500"
                          width="500" height="680" style="border:none;overflow:hidden" scrolling="no"
                          frameborder="0" allowfullscreen="true"
                          allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>
                </div>'''
            else:
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
            # 🖼️ If "painting" keyword found, use painting-frame
            if "paintings-1" in file_name.lower():
                media_html = f'''
                <div class="painting-frame">
                  <img src="media/paint1.jpg" alt="Painting 1">
                  <img src="media/paint2.jpg" alt="Painting 2">
                  <img src="media/paint3.jpg" alt="Painting 3">
                  <img src="media/paint4.jpg" alt="Painting 4">
                  <img src="media/paint5.jpg" alt="Painting 5">
                  <img src="media/paint6.jpg" alt="Painting 6">
                  <img src="media/paint7.jpg" alt="Painting 7">
                  <img src="media/paint8.jpg" alt="Painting 8">
                  <img src="media/paint9.jpg" alt="Painting 9">
                  <img src="media/paint10.jpg" alt="Painting 10">
                  <img src="media/paint11.jpg" alt="Painting 11">
                  <img src="media/paint12.jpg" alt="Painting 12">
                </div>'''
            elif media_path.exists():
                media_html = f'''
                <div class="media-card">
                  <p class="media-caption">🖼️ ছবি</p>
                  <img src="media/{file_name}" alt="{title}">
                </div>'''

        elif media_type == "pdf":
            if media_file.strip().startswith("http"):
                media_html = f'''
                <div class="media-card">
                  <p class="media-caption">📄 পিডিএফ ফাইল</p>
                  <iframe src="{media_file.strip()}" width="100%" height="500px"></iframe>
                  <p><a href="{media_file.strip()}" target="_blank">🔗 পূর্ণ পিডিএফ দেখুন</a></p>
                </div>'''
            elif media_path.exists():
                media_html = f'''
                <div class="media-card">
                  <p class="media-caption">📄 পিডিএফ ফাইল</p>
                  <iframe src="media/{file_name}" width="100%" height="500px"></iframe>
                  <p><a href="media/{file_name}" target="_blank">🔗 পূর্ণ পিডিএফ দেখুন</a></p>
                </div>'''

    # ✅ Dynamic label
    if dance_tag == "dance":
        label_text = "নৃত্য পরিবেশনা :"
    elif dance_tag == "painter":
        label_text = "চিত্রকার  :"
    else:
        label_text = "লেখক :"

    main_content += f"""
    <div class="poem" id="{anchor}">
      <h2>{title}</h2>
      <p><strong><em>{label_text} {poet}</em></strong></p>
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
    link.style.display = link.textContent.toLowerCase().includes(input) ? "block" : "none";
  }});
}}
</script>

</body>
</html>
"""

Path("index9.html").write_text(html, encoding="utf-8")
print("✅ index9.html generated successfully with dynamic labels, 👨‍👩‍👧‍👦 heading, and 🎨 painting frame!")
