from pathlib import Path
import re, subprocess

p=Path('index.html')
s=p.read_text(encoding='utf-8')
assert 'V9-8.9' in s, 'expected V9-8.9 base'
patch=Path('tools/v990_hotfix.js').read_text(encoding='utf-8')
s=s.replace('V9-8.9','V9-9.0').replace('&v=989','&v=990').replace('?student=1&v=989','?student=1&v=990')
assert 'V9-9.0 patch render' not in s
s=s.replace('</body>', '<script>\n'+patch+'\n</script>\n</body>', 1)
p.write_text(s,encoding='utf-8')
parts=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',s,flags=re.S)
app='\n'.join(parts)
Path('/tmp/drb_v990_all.js').write_text(app,encoding='utf-8')
subprocess.run(['node','--check','/tmp/drb_v990_all.js'],check=True)
for marker in ['V9-9.0','selectedEmotions','data-live-mood-emotion','data-emotion-source','V9-9.0 patch render']:
    assert marker in s, marker
print(f'V9-9.0 applied: {p.stat().st_size} bytes')
