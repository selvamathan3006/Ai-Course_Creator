import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

OUTPUT_FILE = "font_all_test.pdf"

# 1️⃣ Test DejaVuSans (local TTF)
dejavu_path = r"C:\Users\ssmat\Downloads\ai_course_creator - Copy\ai_course_creator\DejaVuSans.ttf"
dejavu_available = os.path.exists(dejavu_path)
if dejavu_available:
    pdfmetrics.registerFont(TTFont("DejaVuSans", dejavu_path))

# 2️⃣ Built-in PDF fonts (no TTF needed)
builtin_fonts = ["Helvetica", "Times-Roman", "Courier"]

# 3️⃣ Built-in CID fonts for CJK
cjk_fonts = {
    "STSong-Light": "Simplified Chinese (你好)",
    "MSung-Light": "Traditional Chinese (您好)",
    "HeiseiMin-W3": "Japanese (こんにちは)",
    "HYSMyeongJo-Medium": "Korean (안녕하세요)"
}

for f in cjk_fonts:
    pdfmetrics.registerFont(UnicodeCIDFont(f))

# --- Generate PDF ---
c = canvas.Canvas(OUTPUT_FILE)

y = 800
c.setFont("Helvetica", 14)
c.drawString(100, y, "Font Test Report")
y -= 40

# Test DejaVuSans
if dejavu_available:
    c.setFont("DejaVuSans", 12)
    c.drawString(100, y, "DejaVuSans: Hello World! 12345 → 你好, こんにちは, 안녕하세요")
    y -= 40
else:
    c.setFont("Helvetica", 12)
    c.drawString(100, y, "⚠️ DejaVuSans.ttf NOT FOUND at expected path.")
    y -= 40

# Test built-in fonts
for f in builtin_fonts:
    c.setFont(f, 12)
    c.drawString(100, y, f"{f}: The quick brown fox jumps over the lazy dog. 1234567890")
    y -= 40

# Test CJK fonts
for f, sample in cjk_fonts.items():
    c.setFont(f, 12)
    c.drawString(100, y, f"{f}: {sample}")
    y -= 40

c.save()
print(f"✅ Generated {OUTPUT_FILE}. Open it to check all font outputs.")
