from pathlib import Path
import hashlib, re, subprocess
src=Path('index.html')
raw=src.read_bytes()
actual=hashlib.sha256(raw).hexdigest()
expected='7c24d763b60f3d6b07cc0fb4796e8fbb53191ffb7a3fb42527013d46f84b4f7f'
assert actual==expected,(actual,expected)
s=raw.decode('utf-8')

# Version
s=s.replace('<span class="version-badge">V9-8.1</span>','<span class="version-badge">V9-8.2</span>')
s=s.replace('V9-8.1 · Firebase 실시간 수업','V9-8.2 · Firebase 실시간 수업')
s=s.replace("진행자 현황판 · ${online?'V9-8.1 실시간':'V8 STABLE'}","진행자 현황판 · ${online?'V9-8.2 실시간':'V8 STABLE'}")

# CSS for font/text-color customization
css_anchor='.student-themed .student-state{background:rgba(255,255,255,.58)}\n'
assert css_anchor in s
css_add=css_anchor+r'''.student-theme-preview .screen,.theme-mini-preview .theme-mini-card{font-family:var(--student-font)!important;color:var(--student-text)!important;font-weight:var(--student-body-weight)!important}.student-theme-preview .screen h4,.theme-mini-preview .theme-mini-card b{color:var(--student-title)!important}.student-theme-preview .screen p,.student-theme-preview .preview-card,.student-theme-preview textarea{color:var(--student-text)!important}.student-themed .live-student-card{font-family:var(--student-font)!important;color:var(--student-text)!important;font-weight:var(--student-body-weight)!important}.student-themed .live-student-card h1,.student-themed .live-student-card h2,.student-themed .live-student-card h3,.student-themed .live-student-card h4,.student-themed .live-question b,.student-themed .student-state b{color:var(--student-title)!important}.student-themed .live-question,.student-themed .live-question p,.student-themed .live-question textarea,.student-themed .live-response-summary{color:var(--student-text)!important}.theme-contrast-ok{margin-top:9px;border:1px solid #cfe3d8;background:#f3faf6;color:#3b6a50;border-radius:10px;padding:8px 9px;font-size:10px;line-height:1.45}.theme-contrast-warn{margin-top:9px;border:1px solid #ead5ad;background:#fff9ec;color:#735a2d;border-radius:10px;padding:8px 9px;font-size:10px;line-height:1.45}.theme-font-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin-top:8px}.theme-font-choice{border:1px solid #d8e3e9;background:#fff;border-radius:10px;padding:10px;text-align:left;cursor:pointer}.theme-font-choice.on{border-color:#5492ba;background:#edf7fd;color:#245878}.theme-font-choice b{display:block;font-size:12px}.theme-font-choice small{display:block;color:#748695;font-size:9.5px;margin-top:3px}
'''
s=s.replace(css_anchor,css_add,1)

old="const STUDENT_THEME_DEFAULT={preset:'default',bg1:'#e6f0f7',bg2:'#f7f1e8',accent:'#143754',card:'white',radius:24};"
new="const STUDENT_THEME_DEFAULT={preset:'default',bg1:'#e6f0f7',bg2:'#f7f1e8',accent:'#143754',text:'#40586d',title:'#0b2743',font:'default',card:'white',radius:24};"
assert old in s
s=s.replace(old,new,1)

anchor='function safeThemeHex(v,fallback){'
assert anchor in s
font_helpers=r'''const STUDENT_FONT_PRESETS={
 default:{label:'기본',desc:'가장 안정적인 고딕',stack:'Pretendard,"Noto Sans KR",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",Arial,sans-serif',weight:600},
 rounded:{label:'둥근 느낌',desc:'부드러운 화면',stack:'"Arial Rounded MT Bold","Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif',weight:600},
 serif:{label:'명조 느낌',desc:'차분한 읽기',stack:'"Noto Serif KR","Nanum Myeongjo","Batang","AppleMyungjo",serif',weight:500},
 strong:{label:'또렷하게',desc:'굵고 선명한 화면',stack:'"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",Arial,sans-serif',weight:700}
};
function studentFontPreset(key){return STUDENT_FONT_PRESETS[key]||STUDENT_FONT_PRESETS.default}
function hexRgb(hex){const h=safeThemeHex(hex,'#000000').slice(1);return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]}
function relativeLuminance(hex){return hexRgb(hex).map(v=>{const c=v/255;return c<=.03928?c/12.92:Math.pow((c+.055)/1.055,2.4)}).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0)}
function contrastRatio(a,b){const x=relativeLuminance(a),y=relativeLuminance(b),hi=Math.max(x,y),lo=Math.min(x,y);return (hi+.05)/(lo+.05)}
function themeContrastState(t){const card=t.card==='warm'?'#fffdf8':'#ffffff',body=contrastRatio(t.text,card),title=contrastRatio(t.title,card);return {body,title,ok:body>=4.5&&title>=3}}
'''
s=s.replace(anchor,font_helpers+anchor,1)

old="function studentTheme(activity=state.activity){const raw=activity?.studentTheme||{},d=STUDENT_THEME_DEFAULT,r=Number(raw.radius);return {preset:typeof raw.preset==='string'?raw.preset:d.preset,bg1:safeThemeHex(raw.bg1,d.bg1),bg2:safeThemeHex(raw.bg2,d.bg2),accent:safeThemeHex(raw.accent,d.accent),card:['white','warm','glass'].includes(raw.card)?raw.card:d.card,radius:[14,24,32].includes(r)?r:d.radius}}"
new="function studentTheme(activity=state.activity){const raw=activity?.studentTheme||{},d=STUDENT_THEME_DEFAULT,r=Number(raw.radius),font=STUDENT_FONT_PRESETS[raw.font]?raw.font:d.font;return {preset:typeof raw.preset==='string'?raw.preset:d.preset,bg1:safeThemeHex(raw.bg1,d.bg1),bg2:safeThemeHex(raw.bg2,d.bg2),accent:safeThemeHex(raw.accent,d.accent),text:safeThemeHex(raw.text,d.text),title:safeThemeHex(raw.title,d.title),font,card:['white','warm','glass'].includes(raw.card)?raw.card:d.card,radius:[14,24,32].includes(r)?r:d.radius}}"
assert old in s
s=s.replace(old,new,1)

old="function studentThemeStyle(activity=state.activity){const t=studentTheme(activity);return `--student-bg1:${t.bg1};--student-bg2:${t.bg2};--student-accent:${t.accent};--student-accent-text:${themeAccentText(t.accent)};--student-card-bg:${studentCardColor(t.card)};--student-radius:${t.radius}px`}"
new="function studentThemeStyle(activity=state.activity){const t=studentTheme(activity),f=studentFontPreset(t.font);return `--student-bg1:${t.bg1};--student-bg2:${t.bg2};--student-accent:${t.accent};--student-accent-text:${themeAccentText(t.accent)};--student-card-bg:${studentCardColor(t.card)};--student-radius:${t.radius}px;--student-text:${t.text};--student-title:${t.title};--student-font:${f.stack};--student-body-weight:${f.weight}`}"
assert old in s
s=s.replace(old,new,1)

start=s.index('function studentDesignSettings(){')
end=s.find('\n',start)
assert end!=-1
new_func=r'''function studentDesignSettings(){const t=studentTheme(state.activity),cardLabels={white:'화이트',warm:'웜 화이트',glass:'소프트'},rLabels={14:'단정',24:'기본',32:'둥글게'},contrast=themeContrastState(t);return `<div class="setting-section"><h4>학생 화면 테마 ${t.preset==='custom'?'<span class="theme-custom-badge">직접 설정</span>':''}</h4><div class="tiny-note">이 활동의 모든 학생 화면에 함께 적용됩니다. 미리보기와 실제 학생 화면이 같은 설정을 사용합니다.</div><div class="theme-presets">${Object.entries(STUDENT_THEME_PRESETS).map(([key,p])=>`<button type="button" class="theme-preset ${t.preset===key?'on':''}" data-theme-preset="${key}"><span class="theme-swatch" style="--sw1:${p.bg1};--sw2:${p.bg2};--sw-accent:${p.accent}"></span><b>${p.label}</b></button>`).join('')}</div><div class="theme-color-grid"><div class="theme-color-field"><label>배경 위</label><input type="color" data-theme-color="bg1" value="${t.bg1}"></div><div class="theme-color-field"><label>배경 아래</label><input type="color" data-theme-color="bg2" value="${t.bg2}"></div><div class="theme-color-field"><label>버튼·강조</label><input type="color" data-theme-color="accent" value="${t.accent}"></div><div class="theme-color-field"><label>본문 글자</label><input type="color" data-theme-color="text" value="${t.text}"></div><div class="theme-color-field"><label>제목 글자</label><input type="color" data-theme-color="title" value="${t.title}"></div></div><div class="${contrast.ok?'theme-contrast-ok':'theme-contrast-warn'}">${contrast.ok?'✓ 글자와 카드 배경의 대비가 읽기 좋은 범위입니다.':`⚠ 글자 대비가 낮습니다. 본문 ${contrast.body.toFixed(1)}:1 · 제목 ${contrast.title.toFixed(1)}:1`}</div><div class="theme-mini-preview" style="${studentThemeStyle(state.activity)}"><div class="theme-mini-card"><b>학생 화면 예시</b><div class="tiny-note">폰트와 글자색도 바로 확인하세요.</div><button type="button" tabindex="-1">응답 저장하기</button></div></div></div><div class="setting-section"><h4>글꼴</h4><div class="tiny-note">외부 폰트 파일을 불러오지 않아 학교망과 학생 기기에서 안정적으로 동작합니다. 기기에 따라 가장 가까운 글꼴로 표시됩니다.</div><div class="theme-font-grid">${Object.entries(STUDENT_FONT_PRESETS).map(([key,p])=>`<button type="button" class="theme-font-choice ${t.font===key?'on':''}" data-theme-font="${key}"><b>${p.label}</b><small>${p.desc}</small></button>`).join('')}</div></div><div class="setting-section"><h4>카드 느낌</h4><div class="theme-choice-row">${Object.entries(cardLabels).map(([key,label])=>`<button type="button" class="theme-choice ${t.card===key?'on':''}" data-theme-card="${key}">${label}</button>`).join('')}</div><h4 style="margin-top:15px">모서리</h4><div class="theme-choice-row">${Object.entries(rLabels).map(([key,label])=>`<button type="button" class="theme-choice ${String(t.radius)===key?'on':''}" data-theme-radius="${key}">${label}</button>`).join('')}</div><div class="tiny-note" style="margin-top:10px">버튼 글자색은 강조색 밝기에 맞춰 자동으로 흰색 또는 진한색으로 바뀝니다.</div><button class="btn" type="button" data-theme-reset style="margin-top:12px">기본 디자인으로 되돌리기</button></div>`}'''
s=s[:start]+new_func+s[end:]

old="document.querySelectorAll('[data-theme-color]').forEach(el=>{const apply=immediate=>{const k=el.dataset.themeColor;if(!['bg1','bg2','accent'].includes(k))return;state.activity.studentTheme={...studentTheme(state.activity),[k]:el.value,preset:'custom'};persistStudentTheme({immediate:!!immediate,rerender:false})};el.oninput=()=>apply(false);el.onchange=()=>apply(true)});"
new="document.querySelectorAll('[data-theme-color]').forEach(el=>{const apply=immediate=>{const k=el.dataset.themeColor;if(!['bg1','bg2','accent','text','title'].includes(k))return;state.activity.studentTheme={...studentTheme(state.activity),[k]:el.value,preset:'custom'};persistStudentTheme({immediate:!!immediate,rerender:false})};el.oninput=()=>apply(false);el.onchange=()=>apply(true)});"
assert old in s
s=s.replace(old,new,1)

font_bind=" document.querySelectorAll('[data-theme-font]').forEach(el=>el.onclick=()=>{const key=el.dataset.themeFont;if(!STUDENT_FONT_PRESETS[key])return;state.activity.studentTheme={...studentTheme(state.activity),font:key,preset:'custom'};persistStudentTheme({immediate:true,rerender:true})});\n"
needle=" document.querySelectorAll('[data-theme-card]').forEach"
idx=s.index(needle)
s=s[:idx]+font_bind+s[idx:]

for marker in ['V9-8.2','STUDENT_FONT_PRESETS','data-theme-font','본문 글자','제목 글자','themeContrastState','--student-font','--student-text','--student-title',"'text','title'"]:
    assert marker in s,marker

src.write_text(s,encoding='utf-8')
parts=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',s,flags=re.S)
Path('/tmp/drb_v982_app.js').write_text(parts[-1],encoding='utf-8')
subprocess.run(['node','--check','/tmp/drb_v982_app.js'],check=True)
new_hash=hashlib.sha256(src.read_bytes()).hexdigest()
print(f'V9-8.2 applied: {src.stat().st_size} bytes, sha256={new_hash}')
