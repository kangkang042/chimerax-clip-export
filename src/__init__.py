# src/__init__.py
# Bundle registration for chimerax-clip-export
from chimerax.core.toolshed import BundleAPI


class _ClipExportAPI(BundleAPI):

    api_version = 1

    @staticmethod
    def register_command(bi, ci, logger):
        func_attr = ci.name.replace(' ', '_')
        desc_attr = func_attr + "_desc"
        from . import cmd
        func = getattr(cmd, func_attr)
        desc = getattr(cmd, desc_attr)
        from chimerax.core.commands import register
        register(ci.name, desc, func)


bundle_api = _ClipExportAPI()
