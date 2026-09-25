from pathlib import Path
import hashlib, re, subprocess

src=Path('index.html')
raw=src.read_bytes()
actual=hashlib.sha256(raw).hexdigest()
expected='f73250be0769a4a65174d7e6234856a25c5ac0ee5ed05e1ceb6f2bfb789d97e8'
assert actual==expected,(actual,expected)
s=raw.decode('utf-8')

# Version bump
s=s.replace('<span class="version-badge">V9-8.2</span>','<span class="version-badge">V9-8.3</span>')
s=s.replace('V9-8.2 · Firebase 실시간 수업','V9-8.3 · Firebase 실시간 수업')
s=s.replace("진행자 현황판 · ${online?'V9-8.2 실시간':'V8 STABLE'}","진행자 현황판 · ${online?'V9-8.3 실시간':'V8 STABLE'}")

# Mobile/touch reliability: avoid iOS hover/delay feeling and enlarge tap targets.
css=r'''

/* V9-8.3: mobile touch reliability */
button,.btn,[data-action],[data-tab],[data-start],[data-template],[data-template-jump],[data-open-activity],[data-home-class],[data-select],[data-theme-preset],[data-theme-font],[data-theme-card],[data-theme-radius],[data-theme-reset],.radio,.switch,.flow-preview-step,.overview-row{touch-action:manipulation;-webkit-tap-highlight-color:transparent}
button:active,.btn:active,[data-theme-preset]:active,[data-theme-font]:active,[data-theme-card]:active,[data-theme-radius]:active{filter:brightness(.97)}
@media(max-width:850px){button,.btn,[data-tab],[data-action],[data-theme-preset],[data-theme-font],[data-theme-card],[data-theme-radius],[data-theme-reset]{min-height:44px}.theme-preset,.theme-font-choice,.theme-choice{min-height:48px}}
@media(hover:none){.start-card:hover,.template-card:hover{transform:none}.btn:hover{border-color:var(--line)}}
'''
assert '</style>' in s
s=s.replace('</style>',css+'\n</style>',1)

# Soft refresh theme controls instead of rebuilding the whole DOM on every design button tap.
old="function applyStudentThemeToOpenPreviews(){const style=studentThemeStyle(state.activity);document.querySelectorAll('.student-theme-preview,.theme-mini-preview').forEach(el=>el.setAttribute('style',style))}\nfunction scheduleStudentThemeLiveSync"
new="""function applyStudentThemeToOpenPreviews(){const style=studentThemeStyle(state.activity);document.querySelectorAll('.student-theme-preview,.theme-mini-preview').forEach(el=>el.setAttribute('style',style))}
function refreshStudentThemeControls(){const t=studentTheme(state.activity);document.querySelectorAll('[data-theme-preset]').forEach(el=>el.classList.toggle('on',t.preset===el.dataset.themePreset));document.querySelectorAll('[data-theme-font]').forEach(el=>el.classList.toggle('on',t.font===el.dataset.themeFont));document.querySelectorAll('[data-theme-card]').forEach(el=>el.classList.toggle('on',t.card===el.dataset.themeCard));document.querySelectorAll('[data-theme-radius]').forEach(el=>el.classList.toggle('on',String(t.radius)===el.dataset.themeRadius));document.querySelectorAll('[data-theme-color]').forEach(el=>{const k=el.dataset.themeColor;if(document.activeElement!==el&&k&&t[k])el.value=t[k]});const c=themeContrastState(t);document.querySelectorAll('.theme-contrast-ok,.theme-contrast-warn').forEach(el=>{el.className=c.ok?'theme-contrast-ok':'theme-contrast-warn';el.textContent=c.ok?'✓ 글자와 카드 배경의 대비가 읽기 좋은 범위입니다.':`⚠ 글자 대비가 낮습니다. 본문 ${c.body.toFixed(1)}:1 · 제목 ${c.title.toFixed(1)}:1`})}
function scheduleStudentThemeLiveSync"""
assert old in s
s=s.replace(old,new,1)

old="function persistStudentTheme(options={}){autosave();applyStudentThemeToOpenPreviews();scheduleStudentThemeLiveSync(!!options.immediate);if(options.rerender)render()}"
new="function persistStudentTheme(options={}){autosave();applyStudentThemeToOpenPreviews();refreshStudentThemeControls();scheduleStudentThemeLiveSync(!!options.immediate);if(options.rerender)render()}"
assert old in s
s=s.replace(old,new,1)

# Theme controls no longer trigger a full render; this keeps live details open and scroll position stable.
s=s.replace("persistStudentTheme({immediate:true,rerender:true})","persistStudentTheme({immediate:true,rerender:false})")

# Verify all expected controls now use the soft path.
markers=['V9-8.3','function refreshStudentThemeControls','touch-action:manipulation','min-height:44px','persistStudentTheme({immediate:true,rerender:false})']
for m in markers:
    assert m in s,m
assert 'persistStudentTheme({immediate:true,rerender:true})' not in s

src.write_text(s,encoding='utf-8')
parts=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',s,flags=re.S)
Path('/tmp/drb_v983_app.js').write_text(parts[-1],encoding='utf-8')
subprocess.run(['node','--check','/tmp/drb_v983_app.js'],check=True)
print(f'V9-8.3 applied: {src.stat().st_size} bytes, sha256={hashlib.sha256(src.read_bytes()).hexdigest()}')
