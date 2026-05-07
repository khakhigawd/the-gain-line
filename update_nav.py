import os

print("Adding password protection to all pages...")

files = [
    'index.html',
    'prop_matrix.html',
    'epl_matrix.html',
    'tennis_matrix.html',
    'wta_matrix.html',
    'match_simulator.html',
]

auth_script = """<script>
if (!sessionStorage.getItem('layback_auth')) {
  window.location.href = 'password.html';
}
</script>"""

for filename in files:
    filepath = os.path.join('C:\\Users\\bayet\\RugbyEdge', filename)
    if not os.path.exists(filepath):
        print("Skipping " + filename + " - not found")
        continue

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Don't add twice
    if 'layback_auth' in content:
        print("Skipping " + filename + " - already protected")
        continue

    # Add auth check right after <body>
    content = content.replace('<body>', '<body>' + auth_script, 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Protected " + filename)

print("\nDone! All pages now require password.")
print("Password is: layback2026")
print("Change it in password.html if needed.")
print("Run: git add . && git commit -m 'Add password protection' && git push")