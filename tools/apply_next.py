from pathlib import Path
import hashlib, re, subprocess
src=Path('index.html')
raw=src.read_bytes()
actual=hashlib.sha256(raw).hexdigest()
expected='4a7cb8899bac587e88556c358ef2ff25c2b8d282e356a969a21afb191b19689f'
assert actual==expected,(actual,expected)
s=raw.decode('utf-8')

# Visible version bump.
s=s.replace('<span class="version-badge">V9-8</span>','<span class="version-badge">V9-8.1</span>')
s=s.replace('V9-8 · Firebase 실시간 수업','V9-8.1 · Firebase 실시간 수업')
s=s.replace("진행자 현황판 · ${online?'V9-8 실시간':'V8 STABLE'}","진행자 현황판 · ${online?'V9-8.1 실시간':'V8 STABLE'}")

# Live-theme controls in waiting room / facilitator.
css_anchor='@media(max-width:560px){.theme-presets{grid-template-columns:repeat(2,minmax(0,1fr))}.theme-color-grid{grid-template-columns:1fr 1fr}.theme-color-field:last-child{grid-column:1/-1}}\n'
assert css_anchor in s
css_add='''@media(max-width:560px){.theme-presets{grid-template-columns:repeat(2,minmax(0,1fr))}.theme-color-grid{grid-template-columns:1fr 1fr}.theme-color-field:last-child{grid-column:1/-1}}\n.live-theme-control{grid-column:1/-1;border:1px solid #cfe0ea;border-radius:15px;background:#f7fbfd;padding:0;margin-top:13px;overflow:hidden}.live-theme-control>summary{cursor:pointer;list-style:none;padding:13px 14px;font-size:12px;font-weight:900;color:#244f6c;display:flex;align-items:center;justify-content:space-between;gap:10px}.live-theme-control>summary::-webkit-details-marker{display:none}.live-theme-control>summary:after{content:'열기';font-size:10px;color:#6e8291;background:#eaf3f8;border-radius:999px;padding:4px 7px}.live-theme-control[open]>summary:after{content:'접기'}.live-theme-control-body{border-top:1px solid #dbe6ec;padding:13px}.live-theme-note{border:1px solid #cce3d6;background:#f1faf5;color:#35664c;border-radius:10px;padding:9px 10px;font-size:10.5px;line-height:1.5;margin-bottom:10px}.live-theme-control .setting-section{background:#fff;margin-bottom:10px}.live-theme-control .setting-section:last-child{margin-bottom:0}\n'''
s=s.replace(css_anchor,css_add,1)

helper_anchor="function studentDesignSettings(){const t=studentTheme(state.activity),cardLabels={white:'화이트',warm:'웜 화이트',glass:'소프트'},rLabels={14:'단정',24:'기본',32:'둥글게'};"
idx=s.find(helper_anchor); assert idx!=-1
line_end=s.find('\n',idx); assert line_end!=-1
helpers=r'''
let studentThemeSyncTimer=null;
function applyStudentThemeToOpenPreviews(){const style=studentThemeStyle(state.activity);document.querySelectorAll('.student-theme-preview,.theme-mini-preview').forEach(el=>el.setAttribute('style',style))}
function scheduleStudentThemeLiveSync(immediate=false){const sess=state.sessionSetup;if(!sess||sess.mode!=='firebase'||sess.status==='ended'||!initFirebase())return;const theme=clone(studentTheme(state.activity)),send=()=>fbDb.collection('sessions').doc(sess.id).update({'activity.studentTheme':theme,updatedAt:firebase.firestore.FieldValue.serverTimestamp()}).catch(e=>{console.error(e);toast(firebaseErrorMessage(e))});if(studentThemeSyncTimer){clearTimeout(studentThemeSyncTimer);studentThemeSyncTimer=null}if(immediate){send();return}studentThemeSyncTimer=setTimeout(()=>{studentThemeSyncTimer=null;send()},180)}
function persistStudentTheme(options={}){autosave();applyStudentThemeToOpenPreviews();scheduleStudentThemeLiveSync(!!options.immediate);if(options.rerender)render()}
function liveThemeControlHTML(){if(state.sessionSetup?.mode!=='firebase')return '';return `<details class="live-theme-control"><summary>학생 화면 디자인 · 실시간 반영</summary><div class="live-theme-control-body"><div class="live-theme-note"><b>수업을 다시 열 필요 없습니다.</b> 여기서 색이나 카드 모양을 바꾸면 현재 연결된 학생 화면에도 바로 반영됩니다.</div>${studentDesignSettings()}</div></details>`}
'''
s=s[:line_end+1]+helpers+s[line_end+1:]

start=s.index('function sessionSetupHTML(){'); end=s.index('function responseRequiredBlock',start)
frag=s[start:end]
needle='<div class="waiting-actions">'; assert needle in frag
frag=frag.replace(needle,"${online?liveThemeControlHTML():''}"+needle,1)
s=s[:start]+frag+s[end:]

start=s.index('function facilitatorPreviewHTML(){'); end=s.index('function render(){',start)
frag=s[start:end]
needle="${online?classResultsHTML(sess):''}</main>"; assert needle in frag
frag=frag.replace(needle,"${online?classResultsHTML(sess):''}${online?liveThemeControlHTML():''}</main>",1)
s=s[:start]+frag+s[end:]

old=""" document.querySelectorAll('[data-theme-preset]').forEach(el=>el.onclick=()=>{const key=el.dataset.themePreset,p=STUDENT_THEME_PRESETS[key];if(!p)return;state.activity.studentTheme={...studentTheme(state.activity),bg1:p.bg1,bg2:p.bg2,accent:p.accent,preset:key};autosave();render()});
 document.querySelectorAll('[data-theme-color]').forEach(el=>{const apply=()=>{const k=el.dataset.themeColor;if(!['bg1','bg2','accent'].includes(k))return;state.activity.studentTheme={...studentTheme(state.activity),[k]:el.value,preset:'custom'};autosave();render()};el.onchange=apply});
 document.querySelectorAll('[data-theme-card]').forEach(el=>el.onclick=()=>{state.activity.studentTheme={...studentTheme(state.activity),card:el.dataset.themeCard,preset:'custom'};autosave();render()});
 document.querySelectorAll('[data-theme-radius]').forEach(el=>el.onclick=()=>{state.activity.studentTheme={...studentTheme(state.activity),radius:Number(el.dataset.themeRadius)||24,preset:'custom'};autosave();render()});
 document.querySelectorAll('[data-theme-reset]').forEach(el=>el.onclick=()=>{delete state.activity.studentTheme;autosave();render()});"""
new=""" document.querySelectorAll('[data-theme-preset]').forEach(el=>el.onclick=()=>{const key=el.dataset.themePreset,p=STUDENT_THEME_PRESETS[key];if(!p)return;state.activity.studentTheme={...studentTheme(state.activity),bg1:p.bg1,bg2:p.bg2,accent:p.accent,preset:key};persistStudentTheme({immediate:true,rerender:true})});
 document.querySelectorAll('[data-theme-color]').forEach(el=>{const apply=immediate=>{const k=el.dataset.themeColor;if(!['bg1','bg2','accent'].includes(k))return;state.activity.studentTheme={...studentTheme(state.activity),[k]:el.value,preset:'custom'};persistStudentTheme({immediate:!!immediate,rerender:false})};el.oninput=()=>apply(false);el.onchange=()=>apply(true)});
 document.querySelectorAll('[data-theme-card]').forEach(el=>el.onclick=()=>{state.activity.studentTheme={...studentTheme(state.activity),card:el.dataset.themeCard,preset:'custom'};persistStudentTheme({immediate:true,rerender:true})});
 document.querySelectorAll('[data-theme-radius]').forEach(el=>el.onclick=()=>{state.activity.studentTheme={...studentTheme(state.activity),radius:Number(el.dataset.themeRadius)||24,preset:'custom'};persistStudentTheme({immediate:true,rerender:true})});
 document.querySelectorAll('[data-theme-reset]').forEach(el=>el.onclick=()=>{delete state.activity.studentTheme;persistStudentTheme({immediate:true,rerender:true})});"""
assert old in s
s=s.replace(old,new,1)

for marker in ['V9-8.1','function scheduleStudentThemeLiveSync',"'activity.studentTheme':theme",'function liveThemeControlHTML','el.oninput=()=>apply(false)',"${online?liveThemeControlHTML():''}<div class=\"waiting-actions\">", "${online?classResultsHTML(sess):''}${online?liveThemeControlHTML():''}</main>"]:
    assert marker in s, marker

src.write_text(s,encoding='utf-8')
parts=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',s,flags=re.S)
Path('/tmp/drb_v981_app.js').write_text(parts[-1],encoding='utf-8')
subprocess.run(['node','--check','/tmp/drb_v981_app.js'],check=True)
new_hash=hashlib.sha256(src.read_bytes()).hexdigest()
expected_out='7c24d763b60f3d6b07cc0fb4796e8fbb53191ffb7a3fb42527013d46f84b4f7f'
assert new_hash==expected_out,(new_hash,expected_out)
print(f'V9-8.1 applied: {src.stat().st_size} bytes, sha256={new_hash}')
