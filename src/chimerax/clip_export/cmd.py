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
