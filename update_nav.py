import os

print("Rebranding to Layback Analytics...")

files = {
    'prop_matrix.html': 'Rugby',
    'epl_matrix.html': 'EPL Soccer',
    'tennis_matrix.html': 'ATP Tennis',
    'wta_matrix.html': 'WTA Tennis',
    'match_simulator.html': 'Simulator',
    'index.html': 'Home',
}

replacements = [
    ('THE <span>GAIN</span> LINE', '📊 LAYBACK ANALYTICS'),
    ('The Gain Line', 'Layback Analytics'),
    ('THE GAIN LINE', 'LAYBACK ANALYTICS'),
    ('the-gain-line', 'laybackanalytics'),
    ('The Gain Line |', 'Layback Analytics |'),
    ('<title>The Gain Line', '<title>Layback Analytics'),
]

for filename in files.keys():
    filepath = os.path.join('C:\\Users\\bayet\\RugbyEdge', filename)
    if not os.path.exists(filepath):
        print("Skipping " + filename + " - not found")
        continue

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    for old, new in replacements:
        content = content.replace(old, new)

    with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(content)

    print("Updated " + filename)

print("\nRebrand complete!")
print("Run: git add . && git commit -m 'Rebrand to Layback Analytics' && git push")