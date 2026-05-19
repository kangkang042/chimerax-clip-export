"""Build a working wheel manually, bypassing setuptools 80.9.0 bug in ChimeraX env."""
import zipfile
import os
import hashlib
import base64

DIST_DIR = r"E:\AI\softwares\chimerax_plugin\dist"
SRC_DIR = r"E:\AI\softwares\chimerax_plugin\src"
NAME = "chimerax_clip_export"
VERSION = "0.1.1"
MODULE_PATH = "chimerax/clip_export"

wheel_name = f"{NAME}-{VERSION}.whl"
wheel_path = os.path.join(DIST_DIR, wheel_name)

os.makedirs(DIST_DIR, exist_ok=True)

# Read source files
with open(os.path.join(SRC_DIR, "__init__.py"), "rb") as f:
    init_py = f.read()
with open(os.path.join(SRC_DIR, "cmd.py"), "rb") as f:
    cmd_py = f.read()

files = {
    f"{MODULE_PATH}/__init__.py": init_py,
    f"{MODULE_PATH}/cmd.py": cmd_py,
}

dist_info = f"{NAME}-{VERSION}.dist-info"

# METADATA — must match ChimeraX toolshed parser expectations:
#   - Framework :: ChimeraX is required
#   - Session versions are integers (major version only), not floats
#   - Exactly 7 fields in Bundle classifier separated by " ::"
metadata = f"""Metadata-Version: 2.4
Name: ChimeraX-Clip-Export
Version: {VERSION}
Summary: Export global clip plane settings as a reusable command string
Requires-Python: >=3.9
Requires-Dist: ChimeraX-Core>=1.0
Classifier: Framework :: ChimeraX
Classifier: Programming Language :: Python :: 3
Classifier: ChimeraX :: Bundle :: General :: 1,1 :: chimerax.clip_export ::  ::
Classifier: ChimeraX :: Command :: clipstate :: General :: Export current clip plane settings to Log
"""

files[f"{dist_info}/METADATA"] = metadata.encode("utf-8")

# WHEEL
wheel_info = """Wheel-Version: 1.0
Generator: manual
Root-Is-Purelib: true
Tag: py3-none-any
"""
files[f"{dist_info}/WHEEL"] = wheel_info.encode("utf-8")

# entry_points.txt
entry_points = """[chimerax.bundle]
bundle = chimerax.clip_export
"""
files[f"{dist_info}/entry_points.txt"] = entry_points.encode("utf-8")

# RECORD
record_lines = []
for fpath, content in sorted(files.items()):
    sha256 = base64.urlsafe_b64encode(
        hashlib.sha256(content).digest()
    ).rstrip(b"=").decode("ascii")
    size = len(content)
    record_lines.append(f"{fpath},sha256={sha256},{size}")

record_lines.append(f"{dist_info}/RECORD,,")
files[f"{dist_info}/RECORD"] = "\n".join(record_lines).encode("utf-8")

# Write wheel
with zipfile.ZipFile(wheel_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for fpath, content in sorted(files.items()):
        zf.writestr(fpath, content)

print(f"Wheel built: {wheel_path}")

# Verify
with zipfile.ZipFile(wheel_path, "r") as zf:
    print("Contents:")
    for name in zf.namelist():
        print(f"  {name} ({zf.getinfo(name).file_size} bytes)")

print("Done!")
