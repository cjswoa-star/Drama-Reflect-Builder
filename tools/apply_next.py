from pathlib import Path
parts=[]
for i in range(3):
    parts.append(Path(f'tools/v991_apply_chunk_{i}.txt').read_text(encoding='utf-8'))
code=''.join(parts)
exec(compile(code,'v991_apply.py','exec'))
