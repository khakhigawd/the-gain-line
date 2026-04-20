import os

print("Updating navigation tabs in all files...")

files = {
    'prop_matrix.html': 'Super Rugby Pacific',
    'epl_matrix.html': 'EPL Soccer',
    'tennis_matrix.html': 'ATP Tennis',
    'wta_matrix.html': 'WTA Tennis',
}

for filename, active_tab in files.items():
    filepath = os.path.join('C:\\Users\\bayet\\RugbyEdge', filename)

    if not os.path.exists(filepath):
        print("Skipping " + filename + " - file not found")
        continue

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    nav = '<div class="nav-tabs">\n'
    for fname, label in files.items():
        if label == active_tab:
            nav += '<div class="nav-tab active" onclick="location.href=\'' + fname + '\'">' + label + '</div>\n'
        else:
            nav += '<div class="nav-tab" onclick="location.href=\'' + fname + '\'">' + label + '</div>\n'
    nav += '</div>'

    start = content.find('<div class="nav-tabs">')
    end = content.find('</div>', start) + 6

    if start == -1:
        print("Could not find nav-tabs in " + filename)
        continue

    new_content = content[:start] + nav + content[end:]

    with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
        f.write(new_content)

    print("Updated " + filename)

print("\nAll navigation tabs updated!")
print("Open any HTML file and the tabs will navigate between all four sports.")