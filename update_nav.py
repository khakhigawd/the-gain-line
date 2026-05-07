import os

print("Fixing branding across all files...")

files = [
    'prop_matrix.html',
    'epl_matrix.html',
    'tennis_matrix.html',
    'wta_matrix.html',
    'match_simulator.html',
]

for filename in files:
    filepath = os.path.join('C:\\Users\\bayet\\RugbyEdge', filename)
    if not os.path.exists(filepath):
        print("Skipping " + filename + " - not found")
        continue

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Fix charset - add UTF-8 meta tag if not present
    if '<meta charset' not in content:
        content = content.replace('<head>', '<head>\n<meta charset="UTF-8">')

    # Fix logo text - remove any garbled emoji versions
    content = content.replace('ðŸ"Š LAYBACK ANALYTICS', 'LAYBACK ANALYTICS')
    content = content.replace('📊 LAYBACK ANALYTICS', 'LAYBACK ANALYTICS')
    content = content.replace('<div class="logo">LAYBACK <span>ANALYTICS</span></div>',
                             '<div class="logo">LAYBACK <span>ANALYTICS</span></div>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Fixed " + filename)

print("\nDone! Run: git add . && git commit -m 'Fix encoding in matrix files' && git push")