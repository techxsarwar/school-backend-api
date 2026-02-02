import os

adsense_code = """
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4450198813209397"
     crossorigin="anonymous"></script>
"""

files = [
    "404.html",
    "admin.html",
    "attendance.html",
    "blog.html",
    "codeimage.html",
    "cookies.html",
    "disclaimer.html",
    "encryptor.html",
    "id-generator.html",
    "index.html",
    "invoice.html",
    "login.html",
    "old_pricing.html",
    "pricing.html",
    "privacy.html",
    "qrcode.html",
    "result-generator.html",
    "screenshot.html",
    "seating.html",
    "terms.html",
    "thumbnail.html",
    "timer.html",
    "timetable.html",
    "tools.html"
]

base_dir = r"c:\Users\HP\Desktop\Sarwar_Portfolio"

for fname in files:
    path = os.path.join(base_dir, fname)
    if not os.path.exists(path):
        print(f"Skipping {fname}: File not found")
        continue
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "ca-pub-4450198813209397" in content:
        print(f"Skipping {fname}: Already has AdSense")
        continue

    # Insert after <head>
    if "<head>" in content:
        new_content = content.replace("<head>", "<head>" + adsense_code, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {fname}")
    else:
        print(f"Skipping {fname}: No <head> tag found")
