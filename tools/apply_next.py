from pathlib import Path
import re, subprocess

src=Path('index.html')
s=src.read_text(encoding='utf-8')
assert 'V9-8.5' in s, 'expected V9-8.5 base'

# Version bump
s=s.replace('V9-8.5','V9-8.6')

# Isolate student Firebase auth from teacher auth. This prevents a student test tab
# on the same iPad/browser from replacing the teacher's Google auth session.
old="let fbApp=null,fbAuth=null,fbDb=null,fbSessionUnsub=null,fbParticipantsUnsub=null,fbResponsesUnsub=null,studentSessionUnsub=null,studentParticipantUnsub=null,studentHeartbeatTimer=null,persistenceRequested=false;"
new="let fbApp=null,fbAuth=null,fbDb=null,studentFbApp=null,studentFbAuth=null,studentFbDb=null,fbSessionUnsub=null,fbParticipantsUnsub=null,fbResponsesUnsub=null,studentSessionUnsub=null,studentParticipantUnsub=null,studentHeartbeatTimer=null,persistenceRequested=false;"
assert old in s
s=s.replace(old,new,1)

anchor='function firebaseErrorMessage(e){'
assert anchor in s
student_init="""function initStudentFirebase(){if(studentFbApp)return true;if(!firebaseAvailable())return false;try{studentFbApp=(firebase.apps||[]).find(a=>a.name==='drb-student')||firebase.initializeApp(FIREBASE_CONFIG,'drb-student');studentFbAuth=studentFbApp.auth();studentFbDb=studentFbApp.firestore();return true}catch(e){console.error('Student Firebase init failed',e);return false}}\n"""
s=s.replace(anchor,student_init+anchor,1)

# Student auth uses the secondary app only.
start=s.index('async function ensureAnonymousAuth(){')
end=s.index('\nfunction sixDigitCode',start)
s=s[:start]+"async function ensureAnonymousAuth(){if(!initStudentFirebase())throw new Error('Firebase SDK를 불러오지 못했습니다.');if(studentFbAuth.currentUser?.isAnonymous)return studentFbAuth.currentUser;const result=await studentFbAuth.signInAnonymously();return result.user}"+s[end:]

# Student restore uses the secondary app/database.
start=s.index('async function tryRestoreStudentSession(){')
end=s.index('\nfunction studentJoinURL',start)
block=s[start:end]
block=block.replace("if(!saved||!initFirebase())return;fbAuth.onAuthStateChanged", "if(!saved||!initStudentFirebase())return;studentFbAuth.onAuthStateChanged")
block=block.replace("const ref=fbDb.collection('sessions')", "const ref=studentFbDb.collection('sessions')")
s=s[:start]+block+s[end:]

# Student join and response writes also use the secondary Firestore instance.
start=s.index('async function joinFirebaseSession(){')
end=s.index('\nfunction oneSelected',start)
block=s[start:end].replace("fbDb.collection('joinCodes')","studentFbDb.collection('joinCodes')").replace("fbDb.collection('sessions')","studentFbDb.collection('sessions')")
s=s[:start]+block+s[end:]

start=s.index('async function saveStudentResponse(){')
end=s.index('\nfunction bindLiveStudentInputs',start)
block=s[start:end].replace("fbDb.collection('sessions')","studentFbDb.collection('sessions')")
s=s[:start]+block+s[end:]

# Re-check teacher ownership immediately before class start. Old cached versions may
# already have changed the primary auth session; this recovers safely on button press.
old="async function runFirebaseSession(){const sess=state.sessionSetup;if(!sess||sess.mode!=='firebase'||sess.status!=='draft')return;if(!(sess.participants||[]).length){toast('입장한 학생이 없습니다.');return}try{await updateAllFirebaseParticipants({status:'active',currentBlock:0,lastSeen:firebase.firestore.FieldValue.serverTimestamp()});await updateFirebaseSession({status:'running',entryOpen:false,currentBlock:0,startedAt:firebase.firestore.FieldValue.serverTimestamp()})}catch(e){console.error(e);toast(firebaseErrorMessage(e))}}"
new="async function runFirebaseSession(){const sess=state.sessionSetup;if(!sess||sess.mode!=='firebase'||sess.status!=='draft')return;if(!(sess.participants||[]).length){toast('입장한 학생이 없습니다.');return}try{const teacher=await ensureTeacherAuth(),ref=fbDb.collection('sessions').doc(sess.id),snap=await ref.get();if(!snap.exists||snap.data()?.teacherUid!==teacher.uid){const e=new Error('이 수업을 만든 교사 계정과 현재 로그인 계정이 다릅니다.');e.code='teacher-session-mismatch';throw e}await updateAllFirebaseParticipants({status:'active',currentBlock:0,lastSeen:firebase.firestore.FieldValue.serverTimestamp()});await updateFirebaseSession({status:'running',entryOpen:false,currentBlock:0,startedAt:firebase.firestore.FieldValue.serverTimestamp()});toast('수업을 시작했습니다.')}catch(e){console.error(e);toast(firebaseErrorMessage(e))}}"
assert old in s
s=s.replace(old,new,1)

# Better error for teacher session mismatch.
needle="if(code.includes('student-separate-browser'))return '교사로 로그인된 브라우저입니다. 학생 테스트는 다른 기기나 시크릿 창에서 열어 주세요.';"
if needle in s:
    s=s.replace(needle,"if(code.includes('teacher-session-mismatch'))return '현재 교사 로그인 계정이 이 수업을 만든 계정과 다릅니다. 교사 계정으로 다시 로그인해 주세요.';"+needle,1)
else:
    # V9-8.5 still contains this marker; fail loudly if the function changed unexpectedly.
    assert 'function firebaseErrorMessage' in s

# Add a safe close/cancel path for Firebase waiting rooms.
insert_before='const STUDENT_LOCAL_PREFIX='
assert insert_before in s
close_fn="""async function closeSessionSetup(){const sess=state.sessionSetup;if(!sess)return;if(sess.mode==='firebase'&&sess.status==='draft'){if(!confirm('이 대기실을 닫고 현재 참여 코드를 폐기할까요?'))return;try{await ensureTeacherAuth();await fbDb.collection('sessions').doc(sess.id).update({status:'ended',entryOpen:false,cancelledAt:firebase.firestore.FieldValue.serverTimestamp(),updatedAt:firebase.firestore.FieldValue.serverTimestamp()});if(sess.code)await fbDb.collection('joinCodes').doc(sess.code).delete().catch(()=>{});clearTeacherSession()}catch(e){console.error(e);toast(firebaseErrorMessage(e));return}}else if(sess.mode==='firebase'&&sess.status==='ended'){clearTeacherSession()}if(sess.mode==='firebase')stopFirebaseListeners();state.sessionSetup=null;state.facilitatorPreview=false;state.shareBoard=false;render()}\n"""
s=s.replace(insert_before,close_fn+insert_before,1)

# Online waiting room now always has an obvious close button on iPad/mobile.
old="${online?`<div style=\"display:flex;gap:6px;align-items:center\"><span class=\"firebase-badge\">실시간</span>${networkPillHTML()}</div>`:`<button class=\"closex\" data-action=\"sessionClose\">✕ 닫기</button>`}"
new="${online?`<div style=\"display:flex;gap:6px;align-items:center\"><span class=\"firebase-badge\">실시간</span>${networkPillHTML()}<button class=\"closex\" data-action=\"sessionClose\" aria-label=\"대기실 닫기\">✕ 닫기</button></div>`:`<button class=\"closex\" data-action=\"sessionClose\">✕ 닫기</button>`}"
assert old in s
s=s.replace(old,new,1)

old="else if(a==='sessionClose'){if(state.sessionSetup?.mode==='firebase')stopFirebaseListeners();state.sessionSetup=null;state.facilitatorPreview=false;render()}"
new="else if(a==='sessionClose'){closeSessionSetup()}"
assert old in s
s=s.replace(old,new,1)

# Syntax and structural checks.
for marker in ["V9-8.6","initStudentFirebase","studentFbAuth.signInAnonymously","studentFbDb.collection('joinCodes')","closeSessionSetup","aria-label=\"대기실 닫기\"","teacher-session-mismatch"]:
    assert marker in s, marker

src.write_text(s,encoding='utf-8')
parts=re.findall(r'<script(?: [^>]*)?>(.*?)</script>',s,flags=re.S)
Path('/tmp/drb_v986_app.js').write_text(parts[-1],encoding='utf-8')
subprocess.run(['node','--check','/tmp/drb_v986_app.js'],check=True)
print(f'V9-8.6 applied: {src.stat().st_size} bytes')
