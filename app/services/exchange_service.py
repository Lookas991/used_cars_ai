import requests
import time
from typing import Optional

_CACHE = {"rate": None, "ts": 0.0}
TTL = 60 * 60  # 1 hour
FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"


def get_usd_to_eur_rate(force_refresh: bool = False) -> float:
    now = time.time()
    if not force_refresh and _CACHE["rate"] is not None and (now - _CACHE["ts"] < TTL):
        return _CACHE["rate"]
    try:
        r = requests.get(FRANKFURTER_URL, timeout=5)
        r.raise_for_status()
        data = r.json()
        usd = data.get("rates", {}).get("USD")
        if not usd:
            raise RuntimeError("USD rate missing in Frankfurter response")
        rate = 1.0 / float(usd)  # FRANK: 1 EUR = usd USD -> invert
        _CACHE["rate"] = rate
        _CACHE["ts"] = now
        return rate
    except Exception as e:
        if _CACHE["rate"]:
            return _CACHE["rate"]
        raise RuntimeError(f"Failed to fetch exchange rate: {e}")
