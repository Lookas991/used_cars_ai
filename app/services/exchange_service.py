import requests

FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"


def get_usd_to_eur_rate() -> float:
    try:
        response = requests.get(FRANKFURTER_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        usd_rate = data["rates"].get("USD")
        if not usd_rate:
            raise RuntimeError("USD rate missing in Frankfurter response.")
        # Base is EUR, so 1 EUR = usd_rate USD. We need 1 USD = ? EUR
        return 1 / usd_rate
    except Exception as e:
        raise RuntimeError(f"Failed to fetch exchange rate: {e}")
