from pathlib import Path
import re, subprocess

p=Path('index.html')
s=p.read_text(encoding='utf-8')
start_marker="<script>\n(()=>{\n  const V990='V9-9.0';"
start=s.find(start_marker)
if start<0:
    raise SystemExit('external V9-9.0 patch block not found')
end=s.find('</script>',start)
if end<0:
    raise SystemExit('external patch closing script not found')
block=s[start:end+9]
code=block[len('<script>\n'):-len('</script>')]
if not code.startswith("(()=>{\n  const V990='V9-9.0';") or not code.rstrip().endswith('})();'):
    raise SystemExit('unexpected V9-9.0 patch shape')
inner=code[len('(()=>{\n'):].rstrip()
inner=inner[:-len('})();')].rstrip()+"\n"
inner=re.sub(r"\n\s*document\.querySelectorAll\('\.version-badge'\)[\s\S]*?try\{render\(\)\}catch\(e\)\{console\.error\('V9-9\.0 patch render',e\)\}\s*$", "\n", inner)
s2=s[:start]+s[end+9:]
needle="if(state.studentMode)tryRestoreStudentSession();\nrender();\n})();\n</script>"
pos=s2.find(needle)
if pos<0:
    raise SystemExit('main app closure not found')
insert="/* V9-9.0 mood → emotion linkage: inside the main app IIFE. */\n"+inner+"\n"
s2=s2[:pos]+insert+s2[pos:]
if s2.count("const V990='V9-9.0'")!=1:
    raise SystemExit('unexpected V990 marker count')
if not (s2.find("const V990='V9-9.0'") < s2.find('if(state.studentMode)tryRestoreStudentSession();')):
    raise SystemExit('V990 patch is still outside main scope')
p.write_text(s2,encoding='utf-8')
# Syntax-check all inline JS blocks.
parts=re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',s2)
for i,js in enumerate(parts):
    if not js.strip():
        continue
    q=Path(f'/tmp/drb_inline_{i}.js')
    q.write_text(js,encoding='utf-8')
    subprocess.run(['node','--check',str(q)],check=True)
print('scope fix applied and JS syntax checks passed')
