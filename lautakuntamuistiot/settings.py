"""
Shared settings: where output goes and how the scripts identify themselves.

    LAUTAKUNTA_OUT      output directory (default: output/ in the repository root)
    LAUTAKUNTA_CONTACT  your e-mail or URL, appended to the User-Agent — Nominatim's
                        usage policy asks heavy users to identify themselves
    LAUTAKUNTA_GEOCODE_DELAY  seconds between Nominatim requests (default 1.1, the
                        policy's 1 request/s); the scheduled job uses 15 (4/minute)
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("LAUTAKUNTA_OUT") or os.path.join(ROOT, "output")
DATA = os.path.join(ROOT, "data")             # published data (the daily job writes it via LAUTAKUNTA_OUT=data)

_contact = os.environ.get("LAUTAKUNTA_CONTACT")
USER_AGENT = "lautakuntamuistiot/1.0" + (f" ({_contact})" if _contact else "")
GEOCODE_DELAY = float(os.environ.get("LAUTAKUNTA_GEOCODE_DELAY") or 1.1)
