from pathlib import Path
import re, subprocess

src=Path('index.html')
s=src.read_text(encoding='utf-8')
assert 'V9-8.6' in s, 'expected V9-8.6 base'
s=s.replace('V9-8.6','V9-8.7')

old="function studentJoinURL(code){return `${location.origin}${location.pathname}?join=${encodeURIComponent(code)}`}"
new="function studentJoinURL(code){return `${location.origin}${location.pathname}?join=${encodeURIComponent(code)}&v=987`}"
assert old in s
s=s.replace(old,new,1)

old="else if(a==='studentJoinHome'){location.href=location.pathname+'?student=1'}"
new="else if(a==='studentJoinHome'){location.href=location.pathname+'?student=1&v=987'}"
assert old in s
s=s.replace(old,new,1)

old="else if(a==='studentResumeRecent'){const last=readLastStudentJoin();if(last?.code)location.href=location.pathname+'?join='+encodeURIComponent(last.code)}"
new="else if(a==='studentResumeRecent'){const last=readLastStudentJoin();if(last?.code)location.href=location.pathname+'?join='+encodeURIComponent(last.code)+'&v=987'}"
assert old in s
s=s.replace(old,new,1)

for marker in ['V9-8.7','&v=987','initStudentFirebase','closeSessionSetup']:
    assert marker in s, marker

src.write_text(s,encoding='utf-8')
parts=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',s,flags=re.S)
Path('/tmp/drb_v987_app.js').write_text(parts[-1],encoding='utf-8')
subprocess.run(['node','--check','/tmp/drb_v987_app.js'],check=True)
print(f'V9-8.7 applied: {src.stat().st_size} bytes')
