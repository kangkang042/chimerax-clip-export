# tests/test_cmd.py
import os
import sys
import types
from unittest.mock import MagicMock

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

    sys.modules["chimerax.core"] = MagicMock()
    sys.modules["chimerax.core.toolshed"] = MagicMock()

from chimerax.clip_export.cmd import clip_export


def _make_session(clip=True, near=0.5, far=100.0):
    """Build a mock session with a clip plane.

    Pass clip_plane=None for the no-clip-plane case.
    """
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
