# src/cmd.py

from chimerax.core.commands import CmdDesc


clipstate_desc = CmdDesc(
    synopsis="Export current clip plane settings as a command string"
)


def clipstate(session):
    """Export current global clip plane settings to the Log window.

    Outputs a command string that can be pasted back into the Command
    window to restore the same clip configuration.
    """
    planes = session.main_view.clip_planes
    near_p = planes.find_plane('near')
    far_p = planes.find_plane('far')

    if near_p is None and far_p is None:
        session.logger.info("clip off")
        return

    v = session.main_view
    b = v.drawing_bounds()
    center = b.center() if b is not None else None

    parts = []
    if near_p is not None:
        offset = near_p.offset(center) if center is not None else 0
        parts.append(f"near {offset:.5g}")
    if far_p is not None:
        offset = -far_p.offset(center) if center is not None else 0
        parts.append(f"far {offset:.5g}")

    if parts:
        session.logger.info(f"clip {' '.join(parts)}")
    else:
        session.logger.info("clip off")
