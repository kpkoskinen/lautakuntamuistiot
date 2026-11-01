"""
Shared settings: where output goes and how the scripts identify themselves.

    LAUTAKUNTA_OUT      output directory (default: ./output next to the scripts)
    LAUTAKUNTA_CONTACT  your e-mail or URL, appended to the User-Agent — Nominatim's
                        usage policy asks heavy users to identify themselves
"""
import os

OUT = os.environ.get("LAUTAKUNTA_OUT") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "output")

_contact = os.environ.get("LAUTAKUNTA_CONTACT")
USER_AGENT = "lautakuntamuistiot/1.0" + (f" ({_contact})" if _contact else "")
