import os
import re

# Fix App.js duplicate const
with open('frontend/src/App.js', 'r') as f:
    content = f.read()

content = re.sub(r'const\s+const\s+', 'const ', content)

with open('frontend/src/App.js', 'w') as f:
    f.write(content)

# Create favicon
os.makedirs('frontend/public', exist_ok=True)
with open('frontend/public/favicon.svg', 'w') as f:
    f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><text x="8" y="12" text-anchor="middle" font-family="monospace" font-size="12">⚡</text></svg>')

print("✅ Fixed duplicate const and created favicon")
