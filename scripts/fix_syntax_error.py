#!/usr/bin/env```thon3
"""
ENTROPY - Fix Syntax Error```Missing Assets```xes the duplicate const keyword and adds```ssing favicon/```o
"""

import os

def main():
    print("🔧 ```ROPY - Fixing Syntax Error & Missing Assets```    print("=" * 50)
    
    # ```Fix the duplicate const in App.js
    print("🔧 Fixing syntax```ror in App.js...")
    
    app_js_path =```rontend/src/App```"
    if os.path.exists```p_js_path):
        with open(app_js_path, '``` as f:
            content = f.read()
        
        # Fix the duplicate const keyword
        fixed_content = content```place('const const moveUncomplete```sks', 'const moveUncomplet```asks')
        
        # Also fix any```her potential```plicate const issues```      import re
        fixed_content = re.```(r'const\s+const\s+', 'const ', fixe```ontent)
        
        with open(app_js_path```w') as f:
            f.write(fixed_content)
        
        print("✅ Fixe```uplicate const keyword in App```")
    else:
        print("❌ App.js not found")
    
    # 2. Create missing favicon an```ogo files
    print("📁 Creating missing asset```les...")
    
    public_dir = "frontend/public"```  os.makedirs(public_dir, exist_ok=```e)
    
    # Create minimal favicon.ico (16x16 transparent icon)
    favicon_content```'''<svg xmlns="http://```.w3.org/2000/svg" viewBox="``` 16 16">
  <rect width="16" height="16" fill="none"/>```<text x="8" y="12" text-anchor="middle" font-family="mon```ace" font-size="12" fill="#000">⚡</text>```svg>'''
    
    with open(f"{public_dir}/favicon.svg```'w') as f:
        f.write(favicon_content)
    
    # Create minimal manifest```on
    manifest_content = '''{
  "short_name": "```ropy",
  "name": "Entropy```sk Manager",
  "icons": [
    {
      "src": "favicon.svg",
      "sizes": "any",
      "type": "image/svg+xml"
    }
  ],
  "start_url": ".",
  "display": "standalone",```"theme_color": "#000000",
  "background_color": "#ffffff"```''
    
    with open(f"{public_dir}/manifest.json", 'w') as f:
        f.write(manifest_content)
    
    # Update```dex.html to```e the correct favicon```  index_html_path = f```ublic_dir}/index.html"```  if os.path.exists```dex_html_path):
        with open(index_html_path, '``` as f:
            html_content = f.```d()
        
        # Update favicon reference```      html_content = html_content.```lace(
            '<link rel="icon"```ef="%PUBLIC_URL%/favicon.ico"```',
            '<link rel="icon" href```PUBLIC_URL%/favicon.svg```>'
        )
        
        with open(index_html_path, 'w```as f:
            f.write(html_content)
        
        print("✅ Update```avicon reference in index.html```    
    print("✅ Created favicon```g and manifest.```n")
    
    print("\n🎉 All```xes Applie```)
    print("=" * 25)
    print("✅ Fixe```Duplicate const keyword syntax```ror")
    print("✅ Fixed: Missing favicon.ico```favicon.svg")
    print("✅ Fixed: Missing manifest```on")
    print("✅ Update```index.html favicon```ference")
    
    print("\n🚀 Your```p should now work without```rors!")
    print("Restart your app```/start.sh")

if __name__ == "__```n__":
    main()
