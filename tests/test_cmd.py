# tests/test_cmd.py
import os
import sys
import types
from unittest.mock import MagicMock

# Shim the chimerax namespace for testing (ChimeraX is NOT installed)
if "chimerax" not in sys.modules:
    _chimerax = types.ModuleType("chimerax")
    _chimerax.__path__ = []
    sys.modules["chimerax"] = _chimerax

    _chimerax_core = types.ModuleType("chimerax.core")
    sys.modules["chimerax.core"] = _chimerax_core

    _chimerax_toolshed = types.ModuleType("chimerax.core.toolshed")
    class BundleInfo:
        pass
    _chimerax_toolshed.BundleInfo = BundleInfo
    sys.modules["chimerax.core.toolshed"] = _chimerax_toolshed

# Load our bundle package and command module
_src = os.path.join(os.path.dirname(__file__), "..", "src")

# Load chimerax.clip_export from src/__init__.py
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "chimerax.clip_export", os.path.join(_src, "__init__.py")
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["chimerax.clip_export"] = _mod
_spec.loader.exec_module(_mod)

# Load chimerax.clip_export.cmd from src/cmd.py
_spec_cmd = importlib.util.spec_from_file_location(
    "chimerax.clip_export.cmd", os.path.join(_src, "cmd.py")
)
_mod_cmd = importlib.util.module_from_spec(_spec_cmd)
sys.modules["chimerax.clip_export.cmd"] = _mod_cmd
_spec_cmd.loader.exec_module(_mod_cmd)

clip_export = _mod_cmd.clip_export


def _make_session(clip=True, near=0.5, far=100.0):
    """Build a mock session with a clip plane."""
    session = MagicMock()
    cp = MagicMock()
    cp.clip = clip
    cp.near = near
    cp.far = far
    session.main_view.clip_plane = cp
    return session


def test_clip_export_normal():
    session = _make_session(near=0.5, far=100.0)
    clip_export(session)
    session.logger.info.assert_called_once_with("clip near 0.5 far 100.0")
    session.logger.warning.assert_not_called()


def test_clip_export_disabled():
    session = _make_session(clip=False)
    clip_export(session)
    session.logger.info.assert_called_once_with("clip disable")
    session.logger.warning.assert_not_called()


def test_clip_export_no_clip_plane():
    session = _make_session()
    session.main_view.clip_plane = None
    clip_export(session)
    session.logger.warning.assert_called_once_with(
        "No clip plane attached to the main view."
    )


def test_clip_export_idempotent():
    session = _make_session(near=0.3, far=200.0)
    clip_export(session)
    call1 = session.logger.info.call_args
    session.logger.info.reset_mock()
    clip_export(session)
    call2 = session.logger.info.call_args
    assert call1 == call2
    assert call1[0][0] == "clip near 0.3 far 200.0"


def test_clip_export_one_sided():
    session = _make_session(near=0.5, far=None)
    clip_export(session)
    session.logger.info.assert_called_once_with("clip near 0.5")
    session.logger.warning.assert_not_called()


def test_clip_export_far_only():
    session = _make_session(near=None, far=800.0)
    clip_export(session)
    session.logger.info.assert_called_once_with("clip far 800.0")
    session.logger.warning.assert_not_called()


def test_clip_export_both_none():
    session = _make_session(near=None, far=None)
    clip_export(session)
    session.logger.info.assert_not_called()
    session.logger.warning.assert_called_once_with(
        "Clip plane has neither near nor far values set."
    )


def test_clip_export_zero_value():
    session = _make_session(near=0.0, far=50.0)
    clip_export(session)
    session.logger.info.assert_called_once_with("clip near 0.0 far 50.0")
    session.logger.warning.assert_not_called()
