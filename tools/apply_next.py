from pathlib import Path
import hashlib, re, subprocess
src=Path('index.html')
out=src
raw=src.read_bytes()
actual=hashlib.sha256(raw).hexdigest()
expected='860bac06b9b680c8376b2d814d34fc64d4c59b7bf7a3db83703ae711648d71b1'
assert actual==expected,(actual,expected)
s=raw.decode('utf-8')

# version
s=s.replace('V9-7','V9-8')

# CSS
css=r'''

/* V9-8: student screen customization */
.theme-presets{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:10px 0 14px}.theme-preset{border:1px solid #d6e1e8;background:#fff;border-radius:12px;padding:9px 8px;cursor:pointer;text-align:left}.theme-preset.on{border-color:#397faa;box-shadow:0 0 0 2px #d9edf9;background:#f7fcff}.theme-preset b{display:block;font-size:11px;margin-top:6px}.theme-swatch{display:block;height:31px;border-radius:8px;background:linear-gradient(135deg,var(--sw1),var(--sw2));position:relative;overflow:hidden;border:1px solid rgba(38,62,80,.09)}.theme-swatch:after{content:'';position:absolute;right:5px;bottom:5px;width:13px;height:13px;border-radius:50%;background:var(--sw-accent);border:2px solid rgba(255,255,255,.92);box-shadow:0 1px 4px rgba(0,0,0,.16)}.theme-color-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.theme-color-field{border:1px solid #dbe5eb;border-radius:11px;padding:8px;background:#fff}.theme-color-field label{display:block;font-size:10px;font-weight:850;color:#60778a;margin-bottom:6px}.theme-color-field input[type=color]{width:100%;height:38px;border:0;padding:0;background:transparent;cursor:pointer}.theme-choice-row{display:flex;gap:7px;flex-wrap:wrap}.theme-choice{border:1px solid #d8e3e9;background:#fff;border-radius:10px;padding:8px 10px;font-size:11px;font-weight:800;cursor:pointer}.theme-choice.on{border-color:#5492ba;background:#edf7fd;color:#245878}.theme-mini-preview{border-radius:15px;padding:13px;margin:12px 0;background:linear-gradient(135deg,var(--student-bg1),var(--student-bg2));border:1px solid rgba(45,73,94,.12)}.theme-mini-card{background:var(--student-card-bg);border-radius:var(--student-radius);padding:12px;box-shadow:0 7px 16px rgba(31,55,75,.09)}.theme-mini-card b{font-size:12px}.theme-mini-card button{display:block;width:100%;margin-top:10px;border:0;border-radius:9px;padding:8px;background:var(--student-accent);color:var(--student-accent-text);font-size:10px;font-weight:900}.theme-custom-badge{display:inline-flex;margin-left:5px;padding:3px 6px;border-radius:999px;background:#f1f5f7;color:#637789;font-size:9px;font-weight:900}.student-theme-preview{background:linear-gradient(180deg,var(--student-bg1),var(--student-bg2))!important}.student-theme-preview .phone{background:var(--student-card-bg)!important;border-radius:calc(var(--student-radius) + 6px)!important}.student-theme-preview .preview-btn{background:var(--student-accent)!important;color:var(--student-accent-text)!important}.student-theme-preview .progress i{background:var(--student-accent)!important}.student-theme-preview .mock-selected{outline-color:var(--student-accent)!important}.student-themed{background:linear-gradient(180deg,var(--student-bg1),var(--student-bg2))!important}.student-themed .live-student-card{background:var(--student-card-bg)!important;border-radius:var(--student-radius)!important}.student-themed .live-submit:not(.saved){background:var(--student-accent)!important;color:var(--student-accent-text)!important}.student-themed .live-option.live-selected,.student-themed .live-emotion-grid button.live-selected,.student-themed .live-chips button.live-selected{border-color:var(--student-accent)!important;box-shadow:inset 4px 0 0 var(--student-accent)!important}.student-themed .live-intensity button.live-selected{background:var(--student-accent)!important;color:var(--student-accent-text)!important}.student-themed .live-mood-dot{background:var(--student-accent)!important}.student-themed .student-state{background:rgba(255,255,255,.58)}
@media(max-width:560px){.theme-presets{grid-template-columns:repeat(2,minmax(0,1fr))}.theme-color-grid{grid-template-columns:1fr 1fr}.theme-color-field:last-child{grid-column:1/-1}}
'''
s=s.replace('</style>',css+'\n</style>',1)

# theme helpers before emotion points
anchor='const EMOTION_POINTS=['
assert anchor in s
helpers=r'''const STUDENT_THEME_DEFAULT={preset:'default',bg1:'#e6f0f7',bg2:'#f7f1e8',accent:'#143754',card:'white',radius:24};
const STUDENT_THEME_PRESETS={
 default:{label:'기본',bg1:'#e6f0f7',bg2:'#f7f1e8',accent:'#143754'},
 sky:{label:'하늘',bg1:'#dff2ff',bg2:'#f3f9ff',accent:'#246b9e'},
 mint:{label:'민트',bg1:'#def4ea',bg2:'#f4fbf7',accent:'#2f7b62'},
 lavender:{label:'라벤더',bg1:'#ece7ff',bg2:'#f8f5ff',accent:'#6557a8'},
 cream:{label:'크림',bg1:'#fff0d9',bg2:'#fffaf1',accent:'#9a602e'},
 rose:{label:'로즈',bg1:'#ffe7ed',bg2:'#fff5f7',accent:'#a5516d'}
};
function safeThemeHex(v,fallback){const s=String(v||'');return /^#[0-9a-fA-F]{6}$/.test(s)?s:fallback}
function studentTheme(activity=state.activity){const raw=activity?.studentTheme||{},d=STUDENT_THEME_DEFAULT,r=Number(raw.radius);return {preset:typeof raw.preset==='string'?raw.preset:d.preset,bg1:safeThemeHex(raw.bg1,d.bg1),bg2:safeThemeHex(raw.bg2,d.bg2),accent:safeThemeHex(raw.accent,d.accent),card:['white','warm','glass'].includes(raw.card)?raw.card:d.card,radius:[14,24,32].includes(r)?r:d.radius}}
function themeAccentText(hex){const h=safeThemeHex(hex,'#143754').slice(1),r=parseInt(h.slice(0,2),16),g=parseInt(h.slice(2,4),16),b=parseInt(h.slice(4,6),16),lum=(.299*r+.587*g+.114*b);return lum>165?'#132841':'#ffffff'}
function studentCardColor(card){return card==='warm'?'#fffdf8':card==='glass'?'rgba(255,255,255,.90)':'#ffffff'}
function studentThemeStyle(activity=state.activity){const t=studentTheme(activity);return `--student-bg1:${t.bg1};--student-bg2:${t.bg2};--student-accent:${t.accent};--student-accent-text:${themeAccentText(t.accent)};--student-card-bg:${studentCardColor(t.card)};--student-radius:${t.radius}px`}
function studentDesignSettings(){const t=studentTheme(state.activity),cardLabels={white:'화이트',warm:'웜 화이트',glass:'소프트'},rLabels={14:'단정',24:'기본',32:'둥글게'};return `<div class="setting-section"><h4>학생 화면 테마 ${t.preset==='custom'?'<span class="theme-custom-badge">직접 설정</span>':''}</h4><div class="tiny-note">이 활동의 모든 학생 화면에 함께 적용됩니다. 실제 학생 휴대폰 화면과 미리보기가 같은 설정을 사용합니다.</div><div class="theme-presets">${Object.entries(STUDENT_THEME_PRESETS).map(([key,p])=>`<button type="button" class="theme-preset ${t.preset===key?'on':''}" data-theme-preset="${key}"><span class="theme-swatch" style="--sw1:${p.bg1};--sw2:${p.bg2};--sw-accent:${p.accent}"></span><b>${p.label}</b></button>`).join('')}</div><div class="theme-color-grid"><div class="theme-color-field"><label>배경 위</label><input type="color" data-theme-color="bg1" value="${t.bg1}"></div><div class="theme-color-field"><label>배경 아래</label><input type="color" data-theme-color="bg2" value="${t.bg2}"></div><div class="theme-color-field"><label>버튼·강조</label><input type="color" data-theme-color="accent" value="${t.accent}"></div></div><div class="theme-mini-preview" style="${studentThemeStyle(state.activity)}"><div class="theme-mini-card"><b>학생 화면 예시</b><div class="tiny-note">배경과 강조색을 바로 확인하세요.</div><button type="button" tabindex="-1">응답 저장하기</button></div></div></div><div class="setting-section"><h4>카드 느낌</h4><div class="theme-choice-row">${Object.entries(cardLabels).map(([key,label])=>`<button type="button" class="theme-choice ${t.card===key?'on':''}" data-theme-card="${key}">${label}</button>`).join('')}</div><h4 style="margin-top:15px">모서리</h4><div class="theme-choice-row">${Object.entries(rLabels).map(([key,label])=>`<button type="button" class="theme-choice ${String(t.radius)===key?'on':''}" data-theme-radius="${key}">${label}</button>`).join('')}</div><div class="tiny-note" style="margin-top:10px">강조색의 글자색은 대비에 맞춰 자동으로 밝거나 어둡게 바뀝니다.</div><button class="btn" type="button" data-theme-reset style="margin-top:12px">기본 디자인으로 되돌리기</button></div>`}

'''
s=s.replace(anchor,helpers+anchor,1)

# tab and settings
old='<div class="tabbar"><button class="${state.tab===\'basic\'?\'on\':\'\'}" data-tab="basic">기본</button><button class="${state.tab===\'content\'?\'on\':\'\'}" data-tab="content">질문·내용</button><button class="${state.tab===\'advanced\'?\'on\':\'\'}" data-tab="advanced">고급</button></div>'
new='<div class="tabbar"><button class="${state.tab===\'basic\'?\'on\':\'\'}" data-tab="basic">기본</button><button class="${state.tab===\'content\'?\'on\':\'\'}" data-tab="content">질문·내용</button><button class="${state.tab===\'design\'?\'on\':\'\'}" data-tab="design">화면</button><button class="${state.tab===\'advanced\'?\'on\':\'\'}" data-tab="advanced">고급</button></div>'
assert old in s
s=s.replace(old,new,1)
old="function settings(b){if(state.tab==='advanced')return advancedSettings(b);if(state.tab==='content')return contentSettings(b);return basicSettings(b)}"
new="function settings(b){if(state.tab==='design')return studentDesignSettings();if(state.tab==='advanced')return advancedSettings(b);if(state.tab==='content')return contentSettings(b);return basicSettings(b)}"
assert old in s
s=s.replace(old,new,1)

# preview theming
old='<div class="phonewrap">${phone(b)}</div>'
new='<div class="phonewrap student-theme-preview" style="${studentThemeStyle(state.activity)}">${phone(b)}</div>'
assert old in s
s=s.replace(old,new,1)
old='<div class="flow-preview-stage">${phone(b,sub,\'flow\')}</div>'
new='<div class="flow-preview-stage student-theme-preview" style="${studentThemeStyle(state.activity)}">${phone(b,sub,\'flow\')}</div>'
assert old in s
s=s.replace(old,new,1)

# joined student theming
old="function studentJoinHTML(){const preset=(params.get('join')||'').replace(/\\D/g,'').slice(0,6),sj=state.studentJoin||{},last=readLastStudentJoin();"
new="function studentJoinHTML(){const preset=(params.get('join')||'').replace(/\\D/g,'').slice(0,6),sj=state.studentJoin||{},last=readLastStudentJoin(),themeStyle=studentThemeStyle(sj.activity);"
assert old in s
s=s.replace(old,new,1)
start=s.index('function studentJoinHTML(){')
end=s.index('function subscribeStudentParticipant',start)
frag=s[start:end]
assert frag.count('<div class="live-student-wrap">')==3,frag.count('<div class="live-student-wrap">')
frag=frag.replace('<div class="live-student-wrap">','<div class="live-student-wrap student-themed" style="${themeStyle}">')
s=s[:start]+frag+s[end:]

# bind design controls after tab binding
old=" document.querySelectorAll('[data-tab]').forEach(x=>x.onclick=()=>{state.tab=x.dataset.tab;render()});\n const t=document.getElementById('activityTitle');"
new=""" document.querySelectorAll('[data-tab]').forEach(x=>x.onclick=()=>{state.tab=x.dataset.tab;render()});
 document.querySelectorAll('[data-theme-preset]').forEach(el=>el.onclick=()=>{const key=el.dataset.themePreset,p=STUDENT_THEME_PRESETS[key];if(!p)return;state.activity.studentTheme={...studentTheme(state.activity),bg1:p.bg1,bg2:p.bg2,accent:p.accent,preset:key};autosave();render()});
 document.querySelectorAll('[data-theme-color]').forEach(el=>{const apply=()=>{const k=el.dataset.themeColor;if(!['bg1','bg2','accent'].includes(k))return;state.activity.studentTheme={...studentTheme(state.activity),[k]:el.value,preset:'custom'};autosave();render()};el.onchange=apply});
 document.querySelectorAll('[data-theme-card]').forEach(el=>el.onclick=()=>{state.activity.studentTheme={...studentTheme(state.activity),card:el.dataset.themeCard,preset:'custom'};autosave();render()});
 document.querySelectorAll('[data-theme-radius]').forEach(el=>el.onclick=()=>{state.activity.studentTheme={...studentTheme(state.activity),radius:Number(el.dataset.themeRadius)||24,preset:'custom'};autosave();render()});
 document.querySelectorAll('[data-theme-reset]').forEach(el=>el.onclick=()=>{delete state.activity.studentTheme;autosave();render()});
 const t=document.getElementById('activityTitle');"""
assert old in s
s=s.replace(old,new,1)

# structural checks
markers=['V9-8','data-tab="design"','function studentDesignSettings()','student-theme-preview','student-themed','data-theme-preset','data-theme-color','data-theme-card','data-theme-radius']
for m in markers:
    assert m in s,m
assert s.count('data-theme-preset')>=2
assert s.count('student-themed')>=4

out.write_text(s,encoding='utf-8')
parts=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',s,flags=re.S)
Path('/tmp/drb_v98_app.js').write_text(parts[-1],encoding='utf-8')
subprocess.run(['node','--check','/tmp/drb_v98_app.js'],check=True)
new_hash=hashlib.sha256(out.read_bytes()).hexdigest()
expected_out='4a7cb8899bac587e88556c358ef2ff25c2b8d282e356a969a21afb191b19689f'
if new_hash!=expected_out: raise SystemExit(f'unexpected output hash: {new_hash}')
print(f'V9-8 applied: {out.stat().st_size} bytes, sha256={new_hash}')