from pathlib import Path
import hashlib, re, subprocess

src=Path('index.html')
raw=src.read_bytes()
actual=hashlib.sha256(raw).hexdigest()
expected='99466367286e94f6bbe9bc1dfe8da9b54bc6ca284bb4bb749dc84dc87c95f832'
assert actual==expected,(actual,expected)
s=raw.decode('utf-8')

# Version bump
s=s.replace('<span class="version-badge">V9-8.3</span>','<span class="version-badge">V9-8.4</span>')
s=s.replace('V9-8.3 · Firebase 실시간 수업','V9-8.4 · Firebase 실시간 수업')
s=s.replace("진행자 현황판 · ${online?'V9-8.3 실시간':'V8 STABLE'}","진행자 현황판 · ${online?'V9-8.4 실시간':'V8 STABLE'}")

# Student inner-screen pastel surfaces + text palettes.
css=r'''

/* V9-8.4: student inner pastel surfaces + text palettes */
.inner-pastel-grid,.text-palette-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin-top:10px}.inner-pastel-choice,.text-palette-choice{border:1px solid #d8e3e9;background:#fff;border-radius:11px;padding:8px 7px;cursor:pointer;text-align:center;min-width:0}.inner-pastel-choice.on,.text-palette-choice.on{border-color:#4e91bc;box-shadow:inset 0 0 0 1px #4e91bc;background:#f5fbff}.inner-pastel-choice b,.text-palette-choice b{display:block;font-size:10.5px;margin-top:5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.inner-pastel-swatch{height:27px;border-radius:8px;border:1px solid rgba(31,55,75,.10);background:linear-gradient(90deg,var(--is1) 0 33.33%,var(--is2) 33.33% 66.66%,var(--is3) 66.66%)}.text-palette-swatch{height:27px;border-radius:8px;border:1px solid #e0e7ec;background:var(--ts-bg);display:flex;align-items:center;justify-content:center;gap:4px}.text-palette-swatch i{display:block;width:7px;height:17px;border-radius:999px;background:var(--ts-title)}.text-palette-swatch i:nth-child(2){height:13px;background:var(--ts-text)}.text-palette-swatch i:nth-child(3){height:9px;background:var(--ts-muted)}.theme-mini-question{margin:10px 0 8px;padding:9px 10px;border-radius:10px;background:var(--student-panel);color:var(--student-text);font-size:10.5px;border:1px solid rgba(60,80,95,.10)}
.student-theme-preview .screen{background:var(--student-surface)!important}.student-theme-preview .preview-card{background:var(--student-panel)!important}.student-theme-preview .choice,.student-theme-preview .emotion-pills span,.student-theme-preview .scale span,.student-theme-preview .starter-preview span,.student-theme-preview textarea{background:var(--student-option)!important;color:var(--student-text)!important}.student-theme-preview .screen .eyebrow,.student-theme-preview .example-note,.student-theme-preview .mock-state{color:var(--student-muted)!important}.theme-mini-preview .theme-mini-card{background:var(--student-surface)!important}.theme-mini-preview .tiny-note{color:var(--student-muted)!important}
.student-themed .live-question,.student-themed .student-state,.student-themed .live-response-summary,.student-themed .live-wait{background:var(--student-panel)!important}.student-themed .live-option,.student-themed .live-emotion-grid button,.student-themed .live-chips button,.student-themed .live-intensity button,.student-themed .live-question textarea,.student-themed .starter-preview span{background:var(--student-option)!important;color:var(--student-text)!important}.student-themed .live-stage-top small,.student-themed .live-saved-note,.student-themed .student-state span,.student-themed .live-mood-hint{color:var(--student-muted)!important}.student-themed .live-option.live-selected,.student-themed .live-emotion-grid button.live-selected,.student-themed .live-chips button.live-selected{background:color-mix(in srgb,var(--student-accent) 12%,var(--student-option))!important}.student-themed .live-intensity button.live-selected{background:var(--student-accent)!important;color:var(--student-accent-text)!important}
[data-inner-preset],[data-text-preset]{touch-action:manipulation;-webkit-tap-highlight-color:transparent}
@media(max-width:850px){[data-inner-preset],[data-text-preset]{min-height:48px}}
@media(max-width:520px){.inner-pastel-grid,.text-palette-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''
assert '</style>' in s
s=s.replace('</style>',css+'\n</style>',1)

old="const STUDENT_THEME_DEFAULT={preset:'default',bg1:'#e6f0f7',bg2:'#f7f1e8',accent:'#143754',text:'#40586d',title:'#0b2743',font:'default',card:'white',radius:24};"
new="const STUDENT_THEME_DEFAULT={preset:'default',insidePreset:'clean',textPreset:'navy',bg1:'#e6f0f7',bg2:'#f7f1e8',accent:'#143754',surface:'#fffdf9',panel:'#fffaf3',option:'#ffffff',text:'#40586d',title:'#0b2743',muted:'#718493',font:'default',card:'white',radius:24};"
assert old in s
s=s.replace(old,new,1)

font_anchor='const STUDENT_FONT_PRESETS={'
assert font_anchor in s
palette_defs=r'''const STUDENT_INNER_PRESETS={
 clean:{label:'화이트',surface:'#fffdf9',panel:'#fffaf3',option:'#ffffff'},
 mint:{label:'민트',surface:'#f4fbf7',panel:'#e7f5ed',option:'#fafffc'},
 sky:{label:'하늘',surface:'#f4f9ff',panel:'#e6f2fc',option:'#fbfdff'},
 lavender:{label:'라벤더',surface:'#f9f6ff',panel:'#eee8fb',option:'#fdfbff'},
 peach:{label:'피치',surface:'#fff7f2',panel:'#ffe9dc',option:'#fffbf8'},
 lemon:{label:'레몬',surface:'#fffdf3',panel:'#fff2c9',option:'#fffef9'},
 rose:{label:'로즈',surface:'#fff6f8',panel:'#ffe5ec',option:'#fffbfc'},
 sage:{label:'세이지',surface:'#f7faf4',panel:'#e7efdf',option:'#fcfdfb'}
};
const STUDENT_TEXT_PRESETS={
 navy:{label:'네이비',title:'#0b2743',text:'#40586d',muted:'#718493'},
 charcoal:{label:'차콜',title:'#25262b',text:'#4a4a50',muted:'#787980'},
 brown:{label:'브라운',title:'#4c352b',text:'#6b5547',muted:'#8b766a'},
 forest:{label:'포레스트',title:'#234b3c',text:'#476558',muted:'#73887e'},
 plum:{label:'플럼',title:'#4b3553',text:'#66536d',muted:'#88788d'},
 slate:{label:'슬레이트',title:'#263746',text:'#52616f',muted:'#7b8792'}
};
'''
s=s.replace(font_anchor,palette_defs+font_anchor,1)

old="function themeContrastState(t){const card=t.card==='warm'?'#fffdf8':'#ffffff',body=contrastRatio(t.text,card),title=contrastRatio(t.title,card);return {body,title,ok:body>=4.5&&title>=3}}"
new="function themeContrastState(t){const bgs=[t.surface,t.panel,t.option],body=Math.min(...bgs.map(bg=>contrastRatio(t.text,bg))),title=Math.min(...bgs.map(bg=>contrastRatio(t.title,bg))),muted=Math.min(...bgs.map(bg=>contrastRatio(t.muted,bg)));return {body,title,muted,ok:body>=4.5&&title>=3&&muted>=3}}"
assert old in s
s=s.replace(old,new,1)

old="function studentTheme(activity=state.activity){const raw=activity?.studentTheme||{},d=STUDENT_THEME_DEFAULT,r=Number(raw.radius),font=STUDENT_FONT_PRESETS[raw.font]?raw.font:d.font;return {preset:typeof raw.preset==='string'?raw.preset:d.preset,bg1:safeThemeHex(raw.bg1,d.bg1),bg2:safeThemeHex(raw.bg2,d.bg2),accent:safeThemeHex(raw.accent,d.accent),text:safeThemeHex(raw.text,d.text),title:safeThemeHex(raw.title,d.title),font,card:['white','warm','glass'].includes(raw.card)?raw.card:d.card,radius:[14,24,32].includes(r)?r:d.radius}}"
new="function studentTheme(activity=state.activity){const raw=activity?.studentTheme||{},d=STUDENT_THEME_DEFAULT,r=Number(raw.radius),font=STUDENT_FONT_PRESETS[raw.font]?raw.font:d.font,insidePreset=STUDENT_INNER_PRESETS[raw.insidePreset]?raw.insidePreset:(raw.insidePreset==='custom'?'custom':d.insidePreset),textPreset=STUDENT_TEXT_PRESETS[raw.textPreset]?raw.textPreset:(raw.textPreset==='custom'?'custom':d.textPreset);return {preset:typeof raw.preset==='string'?raw.preset:d.preset,insidePreset,textPreset,bg1:safeThemeHex(raw.bg1,d.bg1),bg2:safeThemeHex(raw.bg2,d.bg2),accent:safeThemeHex(raw.accent,d.accent),surface:safeThemeHex(raw.surface,d.surface),panel:safeThemeHex(raw.panel,d.panel),option:safeThemeHex(raw.option,d.option),text:safeThemeHex(raw.text,d.text),title:safeThemeHex(raw.title,d.title),muted:safeThemeHex(raw.muted,d.muted),font,card:['white','warm','glass'].includes(raw.card)?raw.card:d.card,radius:[14,24,32].includes(r)?r:d.radius}}"
assert old in s
s=s.replace(old,new,1)

old="function studentThemeStyle(activity=state.activity){const t=studentTheme(activity),f=studentFontPreset(t.font);return `--student-bg1:${t.bg1};--student-bg2:${t.bg2};--student-accent:${t.accent};--student-accent-text:${themeAccentText(t.accent)};--student-card-bg:${studentCardColor(t.card)};--student-radius:${t.radius}px;--student-text:${t.text};--student-title:${t.title};--student-font:${f.stack};--student-body-weight:${f.weight}`}"
new="function studentThemeStyle(activity=state.activity){const t=studentTheme(activity),f=studentFontPreset(t.font);return `--student-bg1:${t.bg1};--student-bg2:${t.bg2};--student-accent:${t.accent};--student-accent-text:${themeAccentText(t.accent)};--student-card-bg:${studentCardColor(t.card)};--student-radius:${t.radius}px;--student-surface:${t.surface};--student-panel:${t.panel};--student-option:${t.option};--student-text:${t.text};--student-title:${t.title};--student-muted:${t.muted};--student-font:${f.stack};--student-body-weight:${f.weight}`}"
assert old in s
s=s.replace(old,new,1)

# Replace design settings function with separated exterior / inner / text controls.
start=s.index('function studentDesignSettings(){')
end=s.find('\n',start)
assert end!=-1
new_func=r'''function studentDesignSettings(){const t=studentTheme(state.activity),cardLabels={white:'화이트',warm:'웜 화이트',glass:'소프트'},rLabels={14:'단정',24:'기본',32:'둥글게'},contrast=themeContrastState(t);return `<div class="setting-section"><h4>바깥 배경 ${t.preset==='custom'?'<span class="theme-custom-badge">직접 설정</span>':''}</h4><div class="tiny-note">학생 휴대폰 바깥 배경과 주요 버튼 색입니다.</div><div class="theme-presets">${Object.entries(STUDENT_THEME_PRESETS).map(([key,p])=>`<button type="button" class="theme-preset ${t.preset===key?'on':''}" data-theme-preset="${key}"><span class="theme-swatch" style="--sw1:${p.bg1};--sw2:${p.bg2};--sw-accent:${p.accent}"></span><b>${p.label}</b></button>`).join('')}</div><div class="theme-color-grid"><div class="theme-color-field"><label>배경 위</label><input type="color" data-theme-color="bg1" value="${t.bg1}"></div><div class="theme-color-field"><label>배경 아래</label><input type="color" data-theme-color="bg2" value="${t.bg2}"></div><div class="theme-color-field"><label>버튼·강조</label><input type="color" data-theme-color="accent" value="${t.accent}"></div></div></div><div class="setting-section"><h4>휴대폰 안쪽 파스텔 ${t.insidePreset==='custom'?'<span class="theme-custom-badge">직접 설정</span>':''}</h4><div class="tiny-note">질문 카드와 선택지까지 함께 바뀝니다. 수업 중에도 학생 화면에 바로 반영됩니다.</div><div class="inner-pastel-grid">${Object.entries(STUDENT_INNER_PRESETS).map(([key,p])=>`<button type="button" class="inner-pastel-choice ${t.insidePreset===key?'on':''}" data-inner-preset="${key}"><span class="inner-pastel-swatch" style="--is1:${p.surface};--is2:${p.panel};--is3:${p.option}"></span><b>${p.label}</b></button>`).join('')}</div><div class="theme-color-grid"><div class="theme-color-field"><label>화면 바탕</label><input type="color" data-theme-color="surface" value="${t.surface}"></div><div class="theme-color-field"><label>질문 박스</label><input type="color" data-theme-color="panel" value="${t.panel}"></div><div class="theme-color-field"><label>선택지·입력</label><input type="color" data-theme-color="option" value="${t.option}"></div></div></div><div class="setting-section"><h4>글자 색 ${t.textPreset==='custom'?'<span class="theme-custom-badge">직접 설정</span>':''}</h4><div class="text-palette-grid">${Object.entries(STUDENT_TEXT_PRESETS).map(([key,p])=>`<button type="button" class="text-palette-choice ${t.textPreset===key?'on':''}" data-text-preset="${key}"><span class="text-palette-swatch" style="--ts-bg:${t.surface};--ts-title:${p.title};--ts-text:${p.text};--ts-muted:${p.muted}"><i></i><i></i><i></i></span><b>${p.label}</b></button>`).join('')}</div><div class="theme-color-grid"><div class="theme-color-field"><label>제목 글자</label><input type="color" data-theme-color="title" value="${t.title}"></div><div class="theme-color-field"><label>본문 글자</label><input type="color" data-theme-color="text" value="${t.text}"></div><div class="theme-color-field"><label>보조 글자</label><input type="color" data-theme-color="muted" value="${t.muted}"></div></div><div class="${contrast.ok?'theme-contrast-ok':'theme-contrast-warn'}">${contrast.ok?'✓ 현재 안쪽 색과 글자색의 대비가 읽기 좋은 범위입니다.':`⚠ 글자 대비를 확인해 주세요. 본문 ${contrast.body.toFixed(1)}:1 · 제목 ${contrast.title.toFixed(1)}:1 · 보조 ${contrast.muted.toFixed(1)}:1`}</div><div class="theme-mini-preview" style="${studentThemeStyle(state.activity)}"><div class="theme-mini-card"><b>학생 화면 예시</b><div class="tiny-note">보조 설명은 이런 색으로 보입니다.</div><div class="theme-mini-question">오늘 장면에서 가장 기억에 남은 순간은?</div><button type="button" tabindex="-1">응답 저장하기</button></div></div></div><div class="setting-section"><h4>글꼴</h4><div class="tiny-note">외부 폰트 파일을 불러오지 않아 학교망과 학생 기기에서 안정적으로 동작합니다. 기기에 따라 가장 가까운 글꼴로 표시됩니다.</div><div class="theme-font-grid">${Object.entries(STUDENT_FONT_PRESETS).map(([key,p])=>`<button type="button" class="theme-font-choice ${t.font===key?'on':''}" data-theme-font="${key}"><b>${p.label}</b><small>${p.desc}</small></button>`).join('')}</div></div><div class="setting-section"><h4>카드 느낌</h4><div class="theme-choice-row">${Object.entries(cardLabels).map(([key,label])=>`<button type="button" class="theme-choice ${t.card===key?'on':''}" data-theme-card="${key}">${label}</button>`).join('')}</div><h4 style="margin-top:15px">모서리</h4><div class="theme-choice-row">${Object.entries(rLabels).map(([key,label])=>`<button type="button" class="theme-choice ${String(t.radius)===key?'on':''}" data-theme-radius="${key}">${label}</button>`).join('')}</div><div class="tiny-note" style="margin-top:10px">버튼 글자색은 강조색 밝기에 맞춰 자동으로 흰색 또는 진한색으로 바뀝니다.</div><button class="btn" type="button" data-theme-reset style="margin-top:12px">기본 디자인으로 되돌리기</button></div>`}'''
s=s[:start]+new_func+s[end:]

# Refresh controls without full DOM redraw.
start=s.index('function refreshStudentThemeControls(){')
end=s.find('\n',start)
assert end!=-1
new_refresh=r'''function refreshStudentThemeControls(){const t=studentTheme(state.activity);document.querySelectorAll('[data-theme-preset]').forEach(el=>el.classList.toggle('on',t.preset===el.dataset.themePreset));document.querySelectorAll('[data-inner-preset]').forEach(el=>el.classList.toggle('on',t.insidePreset===el.dataset.innerPreset));document.querySelectorAll('[data-text-preset]').forEach(el=>el.classList.toggle('on',t.textPreset===el.dataset.textPreset));document.querySelectorAll('[data-theme-font]').forEach(el=>el.classList.toggle('on',t.font===el.dataset.themeFont));document.querySelectorAll('[data-theme-card]').forEach(el=>el.classList.toggle('on',t.card===el.dataset.themeCard));document.querySelectorAll('[data-theme-radius]').forEach(el=>el.classList.toggle('on',String(t.radius)===el.dataset.themeRadius));document.querySelectorAll('[data-theme-color]').forEach(el=>{const k=el.dataset.themeColor;if(document.activeElement!==el&&k&&t[k])el.value=t[k]});const c=themeContrastState(t);document.querySelectorAll('.theme-contrast-ok,.theme-contrast-warn').forEach(el=>{el.className=c.ok?'theme-contrast-ok':'theme-contrast-warn';el.textContent=c.ok?'✓ 현재 안쪽 색과 글자색의 대비가 읽기 좋은 범위입니다.':`⚠ 글자 대비를 확인해 주세요. 본문 ${c.body.toFixed(1)}:1 · 제목 ${c.title.toFixed(1)}:1 · 보조 ${c.muted.toFixed(1)}:1`})}'''
s=s[:start]+new_refresh+s[end:]

# Manual color updates know which palette became custom.
old="document.querySelectorAll('[data-theme-color]').forEach(el=>{const apply=immediate=>{const k=el.dataset.themeColor;if(!['bg1','bg2','accent','text','title'].includes(k))return;state.activity.studentTheme={...studentTheme(state.activity),[k]:el.value,preset:'custom'};persistStudentTheme({immediate:!!immediate,rerender:false})};el.oninput=()=>apply(false);el.onchange=()=>apply(true)});"
new="document.querySelectorAll('[data-theme-color]').forEach(el=>{const apply=immediate=>{const k=el.dataset.themeColor;if(!['bg1','bg2','accent','surface','panel','option','text','title','muted'].includes(k))return;const cur=studentTheme(state.activity),next={...cur,[k]:el.value};if(['surface','panel','option'].includes(k))next.insidePreset='custom';else if(['text','title','muted'].includes(k))next.textPreset='custom';else next.preset='custom';state.activity.studentTheme=next;persistStudentTheme({immediate:!!immediate,rerender:false})};el.oninput=()=>apply(false);el.onchange=()=>apply(true)});"
assert old in s
s=s.replace(old,new,1)

# Add one-tap inner and text palette handlers.
anchor=" document.querySelectorAll('[data-theme-font]').forEach"
assert anchor in s
extra=r''' document.querySelectorAll('[data-inner-preset]').forEach(el=>el.onclick=()=>{const key=el.dataset.innerPreset,p=STUDENT_INNER_PRESETS[key];if(!p)return;state.activity.studentTheme={...studentTheme(state.activity),surface:p.surface,panel:p.panel,option:p.option,insidePreset:key};persistStudentTheme({immediate:true,rerender:false})});
 document.querySelectorAll('[data-text-preset]').forEach(el=>el.onclick=()=>{const key=el.dataset.textPreset,p=STUDENT_TEXT_PRESETS[key];if(!p)return;state.activity.studentTheme={...studentTheme(state.activity),title:p.title,text:p.text,muted:p.muted,textPreset:key};persistStudentTheme({immediate:true,rerender:false})});
'''
s=s.replace(anchor,extra+anchor,1)

# Required markers and syntax check.
markers=['V9-8.4','STUDENT_INNER_PRESETS','STUDENT_TEXT_PRESETS','data-inner-preset','data-text-preset','--student-surface','--student-panel','--student-option','--student-muted','보조 글자','피치','레몬','세이지']
for m in markers: assert m in s,m
src.write_text(s,encoding='utf-8')
parts=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',s,flags=re.S)
Path('/tmp/drb_v984_app.js').write_text(parts[-1],encoding='utf-8')
subprocess.run(['node','--check','/tmp/drb_v984_app.js'],check=True)
print(f'V9-8.4 applied: {src.stat().st_size} bytes, sha256={hashlib.sha256(src.read_bytes()).hexdigest()}')
