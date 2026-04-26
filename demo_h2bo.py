"""Compatibility wrapper for the H2BO command-line interface.

Prefer running ``python h2bo.py`` directly. This wrapper is kept so the
original demo command still works.
"""

from __future__ import annotations

from h2bo import main


if __name__ == "__main__":
    main()
