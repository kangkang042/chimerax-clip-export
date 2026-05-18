# tests/test_cmd.py
import os
import sys
import types
from unittest.mock import MagicMock, PropertyMock

# Shim the chimerax namespace for testing (ChimeraX is NOT installed).
# We create chimerax as a real namespace module with __path__ pointing to
# the local source tree, so Python can descend into chimerax.clip_export.
# Only chimerax.core and children are mocked away.
if "chimerax" not in sys.modules:
    _src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))

    _mod = types.ModuleType("chimerax")
    _mod.__path__ = [os.path.join(_src, "chimerax")]
    _mod.__package__ = "chimerax"
    sys.modules["chimerax"] = _mod

    # ChimeraX core is not installed -- mock its modules
    sys.modules["chimerax.core"] = MagicMock()
    sys.modules["chimerax.core.toolshed"] = MagicMock()

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


def test_clip_export_one_sided():
    """When only one clip plane is set, output only that side."""
    session = MagicMock()
    cp = MagicMock()
    cp.clip = True
    type(cp).near = PropertyMock(return_value=0.5)
    type(cp).far = PropertyMock(return_value=None)
    session.main_view.clip_plane = cp

    clip_export(session)

    session.logger.info.assert_called_once_with("clip near 0.5")
