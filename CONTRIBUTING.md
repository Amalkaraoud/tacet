# Contributing
Defensive, academic project. Open an issue before large changes. Keep `firmware/` free of CPython-only
syntax (no dataclasses, typing, `hmac` module): it must run on MicroPython 1.20+. Every behaviour change
needs a test in `tests/` and, if it changes a verdict, an update of `tools/run_scenarios.py` output.
Never commit real keys or PINs. Run `python -m pytest -q tests` before pushing.
