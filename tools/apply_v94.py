from pathlib import Path
import base64
import gzip
import hashlib

parts = []
for p in sorted(Path("tools/v94_payload").glob("chunk_*.txt")):
    parts.append(p.read_text().strip())

raw = base64.b64decode("".join(parts))
data = gzip.decompress(raw)

expected = "928c05ff80ae78fed81a1fe3a01cc3d71bd072e8c1f56d7e34852c82ccc83c49"
actual = hashlib.sha256(data).hexdigest()
if actual != expected:
    raise SystemExit(f"checksum mismatch: {actual}")

Path("index.html").write_bytes(data)
print(f"index.html written: {len(data)} bytes, sha256={actual}")
