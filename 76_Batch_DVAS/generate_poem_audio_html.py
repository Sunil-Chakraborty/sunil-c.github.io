#python generate_poem_audio_html.py
#https://sunil-chakraborty.github.io/sunil-c.github.io/kobita/
#https://tinyurl.com/kobitamala
import re
import os
from pathlib import Path

# Read the poem file
with open("Poem2.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# Function to check if audio file exists
def audio_exists(audio_path):
    return os.path.exists(audio_path)

# Updated pattern to match Bengali poem structure with audio line
# Matches: "কবিতা : title \n কবি : poet \n audio:filename.mp3 \n\n poem_body"
pattern = re.compile(
    r"কবিতা\s*:\s*(.*?)\s*\nকবি\s*:\s*(.*?)\s*\naudio\s*:\s*(.*?)\s*\n\n(.*?)(?=কবিতা\s*:|$)",
    re.DOTALL
)
matches = pattern.findall(raw_text)

# Start HTML content
html = """<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8">
  <title>বাংলা কবিতা সংকলন</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <!-- PDF libraries -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>

  <style>
    body { 
      font-family: 'Noto Serif Bengali', serif; 
      margin: 0; 
      padding: 0; 
      display: flex; 
      height: 100vh; 
      overflow: hidden; 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    aside { 
      width: 30%; 
      background: rgba(255, 255, 255, 0.95); 
      padding: 2em; 
      overflow-y: auto; 
      border-right: 1px solid #ccc;
      backdrop-filter: blur(10px);
      box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }
    main { 
      width: 70%; 
      padding: 2em; 
      overflow-y: auto; 
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(5px);
    }
    h1 { 
      color: #003366; 
      margin-top: 0; 
      text-align: center;
      font-size: 1.5em;
      border-bottom: 2px solid #003366;
      padding-bottom: 0.5em;
    }
    .index a { 
      color: #0066cc; 
      text-decoration: none; 
      font-weight: 500;
    }
    .index a:hover { 
      text-decoration: underline; 
      color: #004499;
    }
    .poem { 
      margin-bottom: 4em; 
      padding: 2em;
      background: white;
      border-radius: 10px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .poem h2 {
      color: #003366;
      border-bottom: 1px solid #ddd;
      padding-bottom: 0.5em;
      margin-bottom: 0.5em;
    }
    .poet-name {
      color: #666;
      font-style: italic;
      margin-bottom: 1.5em;
      font-size: 0.9em;
    }
    .poem-content { 
      white-space: pre-line; 
      line-height: 1.8;
      color: #333;
    }
    .download-btn {
      background: linear-gradient(45deg, #0066cc, #004499);
      color: white;
      border: none;
      padding: 10px 15px;
      margin-bottom: 15px;
      cursor: pointer;
      border-radius: 5px;
      font-size: 14px;
      width: 100%;
      transition: all 0.3s ease;
    }
    .download-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .index-item {
      display: flex;
      flex-direction: column;
      margin: 1em 0;
      padding: 0.8em;
      background: rgba(0, 102, 204, 0.05);
      border-radius: 5px;
      transition: background 0.3s ease;
    }
    .index-item:hover {
      background: rgba(0, 102, 204, 0.1);
    }
    .index-item audio {
      width: 100%;
      height: 30px;
      margin-top: 0.5em;
    }
    .poem-title-link {
      font-size: 1em;
      margin-bottom: 0.3em;
    }
    .stats {
      margin-bottom: 1em;
      padding: 1em;
      background: rgba(0, 102, 204, 0.1);
      border-radius: 5px;
      text-align: center;
    }
  </style>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Bengali:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body>
  <aside>
    <h1>📚 বাংলা কবিতা সংকলন</h1>
    
    <div class="stats">
      <strong>মোট কবিতা: """ + str(len(matches)) + """</strong><br>
      <span style="font-size: 0.9em; color: #666;">🔊 অডিও সহ: """ + """<span id="audioCount"></span></span>
    </div>
    
     
    <div class="index">
"""

# Add index links with audio players (only if audio exists)
main_content = ""
audio_count = 0
for idx, (title, poet, audio_filename, body) in enumerate(matches, start=1):
    # Create anchor from title (cleaned up)
    anchor = f"poem_{title.strip().replace(' ', '_').replace(':', '_')}"
    audio_file = f"audio/{audio_filename.strip()}"  # Use the audio filename from the text
    
    # Clean up title and poet names
    title = title.strip()
    poet = poet.strip()
    
    # Check if audio file exists
    has_audio = audio_exists(audio_file)
    if has_audio:
        audio_count += 1
    
    html += f'''
      <div class="index-item">
        <div class="poem-title-link">
          <a href="#{anchor}">{title} - {poet}</a>
        </div>'''
        
    # Only add audio player if file exists
    if has_audio:
        html += f'''
        <audio controls preload="none">
          <source src="{audio_file}" type="audio/mpeg">
          আপনার ব্রাউজার অডিও সাপোর্ট করে না।
        </audio>'''
    
    html += '''
      </div>
    '''
    
    main_content += f"""
    <div class="poem" id="{anchor}">
      <h2>{title}</h2>
      <div class="poet-name">✍ কবি: {poet}</div>
      <div class="poem-content">{body.strip()}</div>
    </div>
"""

# Close aside and add main content
html += f"""    </div>
  </aside>
  <main id="poemContainer">
{main_content}
  </main>

<script>
// Update audio count
document.getElementById('audioCount').textContent = '{audio_count}';

// Smooth scrolling for internal links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
  anchor.addEventListener('click', function (e) {{
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {{
      target.scrollIntoView({{
        behavior: 'smooth',
        block: 'start'
      }});
    }}
  }});
}});
</script>

</body>
</html>
"""

# Save HTML file
output_file = Path("bengali_poems_collection.html")
output_file.write_text(html, encoding="utf-8")
print(f"✅ {output_file.name} generated successfully!")
print(f"📊 Found {len(matches)} poems in the collection")
print(f"🔊 Audio files available: {audio_count}/{len(matches)}")
print("\n📝 Extracted poems:")
for idx, (title, poet, audio_filename, body) in enumerate(matches, start=1):
    print(f"{idx}. {title.strip()} - {poet.strip()} (Audio: {audio_filename.strip()})")
    