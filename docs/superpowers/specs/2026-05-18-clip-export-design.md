# Design: `clip export` Command Plugin

## Purpose

A ChimeraX bundle that adds a `clip export` CLI command. When invoked, it reads the current global near/far clip plane values and outputs a formatted command string to the Log window. The user can later paste this string into the Command window to restore the clip settings — the same workflow as `view matrix`.

## Architecture

```
chimerax_clip_export/
├── pyproject.toml              # Bundle metadata + dependencies
├── src/
│   └── chimerax/
│       └── clip_export/
│           ├── __init__.py     # Bundle registration + command binding
│           └── cmd.py          # Command implementation (clip_export)
```

Single bundle, one or two modules, no UI panel. Pure command-line integration.

## Command Specification

### `clip export`

Reads `session.main_view.clip_plane.near` and `session.main_view.clip_plane.far`, formats the result, and writes it to `session.logger.info()`.

**Normal output (clipping enabled):**
```
clip near 0.5 far 100.0
```

**When clipping is disabled (`clip disable`):**
```
clip disable
```

**When no clip_plane exists (edge case):**
No message or a warning logged.

## API Access

The global clip plane is accessed via the main graphics view's clip_plane attribute:
- `session.main_view.clip_plane.near` — float, the near clip distance
- `session.main_view.clip_plane.far` — float, the far clip distance
- `session.main_view.clip_plane` can be `None` if no clip plane is attached

## Bundle Registration

Standard ChimeraX bundle pattern:
- Inherit from `chimerax.core.toolshed.bundle_info.BundleInfo`
- Register CLI command via the bundle's `run_provider` or class decorator
- Use `@cli.command` decorator from `chimerax.core.commands.cli`

## Output

`session.logger.info(formatted_command)` — this places the text in the Log tool window, matching the `view matrix` behavior.

## Testing

- Load a structure, set `clip near 0.3`, run `clip export`, verify Log shows `clip near 0.3 far <default>`
- Run `clip disable`, then `clip export`, verify Log shows `clip disable`
- Paste exported output into Command line, verify clip values are restored
- Verify the command is idempotent (running it, exporting, and running again produces the same output)
