import sys
import io

file_path = r"c:\Users\Wawaru\Desktop\StudyTrackr\backend\app\utils\seeder.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add sys.stdout at the top
header = """import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
if "sys.stdout = io.TextIOWrapper" not in content:
    content = header + "\n" + content

# Replacements
content = content.replace("✓", "[OK]")
content = content.replace("✗", "[FAIL]")
content = content.replace("⏭", "[SKIP]")
content = content.replace("╔══════════════════════════════════════╗", "========================================")
content = content.replace("╚══════════════════════════════════════╝", "========================================")
content = content.replace("║", "|")
content = content.replace("═", "=")
content = content.replace("—", "-")
content = content.replace("→", "->")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done replacing.")
