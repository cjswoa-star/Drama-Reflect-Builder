from pathlib import Path
import hashlib, re, subprocess

src=Path('index.html')
raw=src.read_bytes()
actual=hashlib.sha256(raw).hexdigest()
expected='cde7c52398b8899da0fa02a6649a839279cc18dc414665e34202f8fb830e14d2'
assert actual==expected,(actual,expected)
s=raw.decode('utf-8')

# Version bump
s=s.replace('<span class="version-badge">V9-8.4</span>','<span class="version-badge">V9-8.5</span>')
s=s.replace('V9-8.4 · Firebase 실시간 수업','V9-8.5 · Firebase 실시간 수업')
s=s.replace("진행자 현황판 · ${online?'V9-8.4 실시간':'V8 STABLE'}","진행자 현황판 · ${online?'V9-8.5 실시간':'V8 STABLE'}")

# Student join feedback UI
css=r'''

/* V9-8.5: student join reliability + visible diagnostics */
.student-join-feedback{display:none;margin-top:12px;border-radius:12px;padding:11px 12px;font-size:12px;line-height:1.5;text-align:left}.student-join-feedback.show{display:block}.student-join-feedback.info{background:#eef7fd;border:1px solid #cfe4f1;color:#345d78}.student-join-feedback.error{background:#fff4f3;border:1px solid #efcbc7;color:#8b403b}.student-join-feedback.ok{background:#f1faf5;border:1px solid #cee5d8;color:#34654c}.student-join-actions .btn[disabled]{opacity:.58;cursor:wait}
'''
assert '</style>' in s
s=s.replace('</style>',css+'\n</style>',1)

old="function firebaseErrorMessage(e){const code=e?.code||'';if(code.includes('unauthorized-domain'))return '승인된 도메인에 cjswoa-star.github.io를 추가해 주세요.';if(code.includes('popup-blocked'))return '브라우저가 Google 로그인 팝업을 차단했습니다.';if(code.includes('permission-denied'))return 'Firestore 보안 규칙에서 요청이 거부되었습니다.';if(code.includes('student-separate-browser'))return '교사로 로그인된 브라우저입니다. 학생 테스트는 다른 기기나 시크릿 창에서 열어 주세요.';return e?.message||'Firebase 연결 중 오류가 발생했습니다.'}"
new="function firebaseErrorMessage(e){const code=e?.code||'',msg=String(e?.message||'');if(code.includes('unauthorized-domain'))return '승인된 도메인에 cjswoa-star.github.io를 추가해 주세요.';if(code.includes('popup-blocked'))return '브라우저가 Google 로그인 팝업을 차단했습니다.';if(code.includes('operation-not-allowed')||code.includes('admin-restricted-operation')||msg.includes('OPERATION_NOT_ALLOWED'))return '학생 익명 로그인이 꺼져 있습니다. Firebase Authentication에서 익명(Anonymous) 로그인을 사용 설정해 주세요.';if(code.includes('network-request-failed'))return '인터넷 연결이 불안정합니다. 연결을 확인한 뒤 다시 입장해 주세요.';if(code.includes('permission-denied'))return 'Firestore 보안 규칙에서 학생 입장이 거부되었습니다. 최신 규칙이 게시되었는지 확인해 주세요.';if(code.includes('student-separate-browser'))return '교사로 로그인된 브라우저입니다. 학생 테스트는 다른 기기나 시크릿 창에서 열어 주세요.';return e?.message||'Firebase 연결 중 오류가 발생했습니다.'}"
assert old in s
s=s.replace(old,new,1)

# Remove teacher-return button from student entry screen and add persistent feedback area.
old="<div class=\"student-join-actions\"><button class=\"btn primary\" data-action=\"firebaseStudentJoin\">입장하기</button>${last?.code?`<button class=\"btn soft\" data-action=\"studentResumeRecent\">최근 수업 ${esc(last.code)} 이어가기</button>`:''}<button class=\"btn\" data-action=\"studentJoinExit\">교사용 화면으로 돌아가기</button></div>${last?.code?`<div class=\"recent-live-hint\">이 기기에서 참여했던 최근 수업이 저장되어 있습니다.</div>`:''}<div class=\"auth-help\">학생은 Firebase 익명 인증으로 접속합니다. 다른 학생의 개인 응답이나 명단 전체는 읽을 수 없도록 보안 규칙을 적용합니다.</div>"
new="<div class=\"student-join-actions\"><button class=\"btn primary\" data-action=\"firebaseStudentJoin\">입장하기</button>${last?.code?`<button class=\"btn soft\" data-action=\"studentResumeRecent\">최근 수업 ${esc(last.code)} 이어가기</button>`:''}</div><div class=\"student-join-feedback\" data-student-join-feedback aria-live=\"polite\"></div>${last?.code?`<div class=\"recent-live-hint\">이 기기에서 참여했던 최근 수업이 저장되어 있습니다.</div>`:''}<div class=\"auth-help\">학생은 별도 계정 없이 익명 인증으로 참여합니다.</div>"
assert old in s
s=s.replace(old,new,1)

# Join feedback helper
anchor="function subscribeStudentParticipant(sessionRef,uid){"
assert anchor in s
helper="""function setStudentJoinFeedback(message='',kind='info'){const el=document.querySelector('[data-student-join-feedback]');if(!el)return;if(!message){el.className='student-join-feedback';el.textContent='';return}el.className=`student-join-feedback show ${kind}`;el.textContent=message}
"""
s=s.replace(anchor,helper+anchor,1)

# Replace join flow with explicit pending state and visible errors.
start=s.index('async function joinFirebaseSession(){')
end=s.index('\nfunction oneSelected',start)
old_join=s[start:end]
new_join=r'''async function joinFirebaseSession(){
 const code=(document.querySelector('[data-student-code]')?.value||'').replace(/\D/g,'').slice(0,6),name=(document.querySelector('[data-student-name]')?.value||'').trim().slice(0,20),btn=document.querySelector('[data-action="firebaseStudentJoin"]');
 if(code.length!==6){setStudentJoinFeedback('6자리 참여 코드를 입력해 주세요.','error');return}
 if(!name){setStudentJoinFeedback('이름을 입력해 주세요.','error');return}
 if(btn?.disabled)return;
 if(btn){btn.disabled=true;btn.dataset.oldText=btn.textContent;btn.textContent='입장 확인 중…'}
 setStudentJoinFeedback('수업 연결을 확인하고 있습니다. 잠시만 기다려 주세요.','info');
 try{
   const user=await ensureAnonymousAuth();
   setStudentJoinFeedback('참여 코드를 확인하고 있습니다.','info');
   const codeSnap=await fbDb.collection('joinCodes').doc(code).get();
   if(!codeSnap.exists){setStudentJoinFeedback('참여 코드를 찾지 못했습니다. 선생님 화면의 6자리 코드를 다시 확인해 주세요.','error');return}
   const sessionId=codeSnap.data().sessionId,sessionRef=fbDb.collection('sessions').doc(sessionId),partRef=sessionRef.collection('participants').doc(user.uid);
   let sessionSnap,partSnap;
   try{[sessionSnap,partSnap]=await Promise.all([sessionRef.get(),partRef.get()])}
   catch(e){if(e?.code==='permission-denied'){setStudentJoinFeedback('이 수업에 입장할 권한이 없습니다. 선생님이 학생 입장을 열어 두었는지 확인해 주세요.','error');return}throw e}
   if(!sessionSnap.exists){setStudentJoinFeedback('수업을 찾지 못했습니다. 새 참여 코드를 받아 주세요.','error');return}
   const sd=sessionSnap.data()||{};
   if(partSnap.exists){const pd=partSnap.data()||{};await partRef.update({lastSeen:firebase.firestore.FieldValue.serverTimestamp()}).catch(()=>{});rememberStudentJoin(code,{sessionId,name:pd.name||name});setStudentJoinFeedback('기존 수업으로 다시 연결합니다.','ok');attachStudentSession(sessionRef,user,{joined:true,sessionId,name:pd.name||name,activityTitle:sd.activityTitle||'수업',sessionStatus:sd.status||'draft',currentBlock:Number.isInteger(sd.currentBlock)?sd.currentBlock:0,activity:sd.activity||null,responses:{blocks:{}},participant:pd});return}
   if(sd.status==='ended'){setStudentJoinFeedback('이미 종료된 수업입니다.','error');return}
   if(!sd.entryOpen){setStudentJoinFeedback('현재 학생 입장이 닫혀 있습니다. 선생님께 입장을 열어 달라고 해 주세요.','error');return}
   setStudentJoinFeedback('이름을 등록하고 있습니다.','info');
   await partRef.set({uid:user.uid,name,role:'student',status:'waiting',currentBlock:0,joinedAt:firebase.firestore.FieldValue.serverTimestamp(),lastSeen:firebase.firestore.FieldValue.serverTimestamp()});
   rememberStudentJoin(code,{sessionId,name});
   setStudentJoinFeedback('입장이 확인되었습니다.','ok');
   attachStudentSession(sessionRef,user,{joined:true,sessionId,name,activityTitle:sd.activityTitle||'수업',sessionStatus:sd.status||'draft',currentBlock:Number.isInteger(sd.currentBlock)?sd.currentBlock:0,activity:sd.activity||null,responses:{blocks:{}},participant:null});
 }catch(e){console.error(e);const m=firebaseErrorMessage(e);setStudentJoinFeedback(m,'error');toast(m)}
 finally{const b=document.querySelector('[data-action="firebaseStudentJoin"]');if(b){b.disabled=false;b.textContent=b.dataset.oldText||'입장하기'}}
}'''
s=s[:start]+new_join+s[end:]

# Keep obsolete action harmless if old cached DOM somehow calls it, but it is no longer rendered.
assert '교사용 화면으로 돌아가기' not in s
for marker in ['V9-8.5','student-join-feedback','setStudentJoinFeedback','입장 확인 중…','operation-not-allowed']:
    assert marker in s,marker

src.write_text(s,encoding='utf-8')
parts=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',s,flags=re.S)
Path('/tmp/drb_v985_app.js').write_text(parts[-1],encoding='utf-8')
subprocess.run(['node','--check','/tmp/drb_v985_app.js'],check=True)
print(f'V9-8.5 applied: {src.stat().st_size} bytes, sha256={hashlib.sha256(src.read_bytes()).hexdigest()}')
