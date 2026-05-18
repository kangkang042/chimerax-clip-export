# src/chimerax/clip_export/__init__.py
# Bundle registration for chimerax-clip-export
from chimerax.core.toolshed import BundleInfo


class _BundleInfo(BundleInfo):
    pass


bundle_info = _BundleInfo()


def register_command(ci):
    from .cmd import clip_export
    ci.add_command("clip export", clip_export)
