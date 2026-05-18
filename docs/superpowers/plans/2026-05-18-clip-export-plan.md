# clip-export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a ChimeraX bundle that adds `clip export` command to output current near/far clip plane values as a reusable command string to the Log window.

**Architecture:** Single-bundle ChimeraX plugin with two Python modules. `__init__.py` registers the bundle and the CLI command; `cmd.py` reads clip plane values from `session.main_view.clip_plane` and writes formatted command to `session.logger.info()`.

**Tech Stack:** Python 3.9+, ChimeraX Bundle API (`chimerax.core.toolshed.BundleInfo`, `chimerax.core.commands`)

---

### Task 1: Project scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/chimerax/clip_export/__init__.py` (stub)

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=64", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "chimerax-clip-export"
version = "0.1.0"
description = "Export ChimeraX global clip plane settings as a reusable command string"
requires-python = ">=3.9"
dependencies = [
    "chimerax-core>=1.0",
]

[project.entry-points."chimerax.bundle"]
bundle = "chimerax.clip_export"

[tool.setuptools.package-dir]
"chimerax.clip_export" = "src/chimerax/clip_export"
```

- [ ] **Step 2: Create package `__init__.py` stub**

```python
# src/chimerax/clip_export/__init__.py
# Bundle registration for chimerax-clip-export
from chimerax.core.toolshed import BundleInfo


class _BundleInfo(BundleInfo):
    pass


bundle_info = _BundleInfo()
```

- [ ] **Step 3: Create empty `__init__.py` for the `chimerax` namespace package**

`src/chimerax/__init__.py` — empty file (PEP 420 namespace package marker)

- [ ] **Step 4: Verify directory structure**

Run: `ls -R src/`
```
src/
├── chimerax/
│   ├── __init__.py
│   └── clip_export/
│       └── __init__.py
```

- [ ] **Step 5: Initialize git and commit scaffolding**

```bash
git init
git add pyproject.toml src/
git commit -m "feat: scaffold chimerax-clip-export bundle project"
```

---

### Task 2: Write the `clip export` command implementation

**Files:**
- Create: `src/chimerax/clip_export/cmd.py`
- Modify: `src/chimerax/clip_export/__init__.py`

- [ ] **Step 1: Write `cmd.py` — the command function**

```python
# src/chimerax/clip_export/cmd.py

def clip_export(session):
    """Export current global clip plane settings to the Log window.

    Outputs a command string that can be pasted back into the Command
    window to restore the same clip configuration.
    """
    cp = session.main_view.clip_plane

    if cp is None:
        session.logger.warning("No clip plane attached to the main view.")
        return

    if not cp.clip:
        session.logger.info("clip disable")
        return

    session.logger.info(f"clip near {cp.near} far {cp.far}")
```

- [ ] **Step 2: Register the command in `__init__.py`**

Replace the stub with:

```python
# src/chimerax/clip_export/__init__.py
from chimerax.core.toolshed import BundleInfo


class _BundleInfo(BundleInfo):
    pass


bundle_info = _BundleInfo()


def register_command(ci):
    from .cmd import clip_export
    ci.add_command("clip export", clip_export)
```

- [ ] **Step 3: Commit**

```bash
git add src/chimerax/clip_export/cmd.py src/chimerax/clip_export/__init__.py
git commit -m "feat: implement clip export command"
```

---

### Task 3: Write unit tests

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_cmd.py`

- [ ] **Step 1: Write `tests/test_cmd.py`**

```python
# tests/test_cmd.py
from unittest.mock import MagicMock, PropertyMock
from chimerax.clip_export.cmd import clip_export


def test_clip_export_normal():
    """When clipping is active, output the near/far command string."""
    session = MagicMock()
    cp = MagicMock()
    cp.clip = True
    type(cp).near = PropertyMock(return_value=0.5)
    type(cp).far = PropertyMock(return_value=100.0)
    session.main_view.clip_plane = cp

    clip_export(session)

    session.logger.info.assert_called_once_with("clip near 0.5 far 100.0")


def test_clip_export_disabled():
    """When clipping is disabled, output 'clip disable'."""
    session = MagicMock()
    cp = MagicMock()
    cp.clip = False
    session.main_view.clip_plane = cp

    clip_export(session)

    session.logger.info.assert_called_once_with("clip disable")


def test_clip_export_no_clip_plane():
    """When no clip plane exists, log a warning."""
    session = MagicMock()
    session.main_view.clip_plane = None

    clip_export(session)

    session.logger.warning.assert_called_once()


def test_clip_export_idempotent():
    """Running clip_export twice produces the same log output."""
    session = MagicMock()
    cp = MagicMock()
    cp.clip = True
    type(cp).near = PropertyMock(return_value=0.3)
    type(cp).far = PropertyMock(return_value=200.0)
    session.main_view.clip_plane = cp

    clip_export(session)
    call1 = session.logger.info.call_args

    session.logger.info.reset_mock()

    clip_export(session)
    call2 = session.logger.info.call_args

    assert call1 == call2
    assert call1[0][0] == "clip near 0.3 far 200.0"
```

- [ ] **Step 2: Create `tests/__init__.py`** (empty file)

- [ ] **Step 3: Run tests to verify they fail (no ChimeraX)**

The tests mock everything, so they should pass without ChimeraX installed.

Run: `python -m pytest tests/ -v`
Expected: 4 PASS

If `chimerax` import fails (since ChimeraX isn't installed), adjust the test to patch the import:

```python
import sys
from unittest.mock import MagicMock, PropertyMock

# Shim the chimerax namespace for testing
if "chimerax" not in sys.modules:
    sys.modules["chimerax"] = MagicMock()
    sys.modules["chimerax.core"] = MagicMock()
    sys.modules["chimerax.core.toolshed"] = MagicMock()

from chimerax.clip_export.cmd import clip_export
```

(Given that the test mocks `session` entirely, the `chimerax` imports in `cmd.py` and `__init__.py` won't be exercised — but the import of `cmd.py` itself will trigger the `chimerax` import chain. The shim handles this.)

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: add unit tests for clip export command"
```

---

### Task 4: Install and smoke test in ChimeraX

- [ ] **Step 1: Install the bundle**

Run inside ChimeraX Command window (or install via pip):
```
devel install E:\AI\softwares\chimerax_plugin
```
or
```bash
pip install -e E:\AI\softwares\chimerax_plugin
```

- [ ] **Step 2: Manual smoke test**

In ChimeraX:
1. Open a structure: `open 1gcn`
2. Set clip: `clip near 0.3`
3. Run: `clip export`
4. Verify Log window shows: `clip near 0.3 far <default_value>`
5. Copy the output line and paste into Command window — verify clip is restored
6. Run: `clip disable` then `clip export` — verify Log shows `clip disable`
