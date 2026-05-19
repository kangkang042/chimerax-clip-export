# ChimeraX Clip-Export

Export ChimeraX global near/far clip plane settings as a reusable command string. Works like the built-in `view matrix` command — output goes to the Log window and can be pasted back into the Command window to restore the same clip configuration.

## Installation

Download the latest `.whl` file from [Releases](https://github.com/kangkang042/chimerax-clip-export/releases), then install in ChimeraX:

```
toolshed install /path/to/chimerax_clip_export-0.1.1.whl
```

Or build from source:

```bash
python build_wheel_manual.py
```

Then install the generated wheel in `dist/` with the same `toolshed install` command.

## Usage

1. Open a structure in ChimeraX.
2. Adjust the near/far clip planes (e.g. using the Side View panel).
3. Run `clipstate` in the Command window.
4. The Log window shows a command like:

```
clip off ; clip near 0.5 far 100
```

5. Copy and paste this command back into the Command window anytime to restore the exact same clip settings.

## Why `clip off ; clip near ... far ...`?

The built-in `clip near X far Y` command moves planes *relative* to their current position when planes already exist. The `clip off` prefix ensures planes are cleared first, so the values always set absolute positions from the center of rotation.

## Requirements

- ChimeraX 1.x (tested on 1.11)
- Python 3.9+

## License

This project is for educational and personal use.
