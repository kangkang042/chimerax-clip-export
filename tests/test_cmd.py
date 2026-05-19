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
    class BundleAPI:
        api_version = 1
    _chimerax_toolshed.BundleAPI = BundleAPI
    sys.modules["chimerax.core.toolshed"] = _chimerax_toolshed

    _chimerax_commands = types.ModuleType("chimerax.core.commands")
    class CmdDesc:
        def __init__(self, **kwargs):
            self.synopsis = kwargs.get("synopsis", "")
    _chimerax_commands.CmdDesc = CmdDesc
    sys.modules["chimerax.core.commands"] = _chimerax_commands

# Load our bundle package and command module
_src = os.path.join(os.path.dirname(__file__), "..", "src")

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "chimerax.clipstate", os.path.join(_src, "__init__.py")
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["chimerax.clipstate"] = _mod
_spec.loader.exec_module(_mod)

_spec_cmd = importlib.util.spec_from_file_location(
    "chimerax.clipstate.cmd", os.path.join(_src, "cmd.py")
)
_mod_cmd = importlib.util.module_from_spec(_spec_cmd)
sys.modules["chimerax.clipstate.cmd"] = _mod_cmd
_spec_cmd.loader.exec_module(_mod_cmd)

clipstate = _mod_cmd.clipstate


class _MockPlane:
    """Simulate a ChimeraX ClipPlane (near/far)."""
    def __init__(self, name, offset_from_center):
        self.name = name
        self._offset = offset_from_center

    def offset(self, point):
        return self._offset


class _MockClipPlanes:
    """Simulate session.main_view.clip_planes."""
    def __init__(self, near_plane=None, far_plane=None):
        self._planes = [p for p in (near_plane, far_plane) if p is not None]

    def find_plane(self, name):
        for p in self._planes:
            if p.name == name:
                return p
        return None

    def planes(self):
        return self._planes


class _MockBounds:
    def center(self):
        from numpy import array
        return array((0, 0, 0))


def _make_session(near=None, far=None):
    """Build a mock session with near/far clip planes."""
    session = MagicMock()
    session.main_view.clip_planes = _MockClipPlanes(
        near_plane=_MockPlane('near', near) if near is not None else None,
        far_plane=_MockPlane('far', -far) if far is not None else None,
    )
    session.main_view.drawing_bounds.return_value = _MockBounds()
    return session


def test_clipstate_normal():
    session = _make_session(near=0.5, far=100.0)
    clipstate(session)
    session.logger.info.assert_called_once_with("clip near 0.5 far 100")
    session.logger.warning.assert_not_called()


def test_clipstate_disabled():
    session = _make_session(near=None, far=None)
    clipstate(session)
    session.logger.info.assert_called_once_with("clip off")


def test_clipstate_idempotent():
    session = _make_session(near=0.3, far=200.0)
    clipstate(session)
    call1 = session.logger.info.call_args
    session.logger.info.reset_mock()
    clipstate(session)
    call2 = session.logger.info.call_args
    assert call1 == call2
    assert call1[0][0] == "clip near 0.3 far 200"


def test_clipstate_near_only():
    session = _make_session(near=0.5, far=None)
    clipstate(session)
    session.logger.info.assert_called_once_with("clip near 0.5")


def test_clipstate_far_only():
    session = _make_session(near=None, far=800.0)
    clipstate(session)
    session.logger.info.assert_called_once_with("clip far 800")


def test_clipstate_zero_value():
    session = _make_session(near=0.0, far=50.0)
    clipstate(session)
    session.logger.info.assert_called_once_with("clip near 0 far 50")
