# src/cmd.py

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

    parts = []
    if cp.near is not None:
        parts.append(f"near {cp.near}")
    if cp.far is not None:
        parts.append(f"far {cp.far}")
    if parts:
        session.logger.info(f"clip {' '.join(parts)}")
    else:
        session.logger.warning("Clip plane has neither near nor far values set.")
