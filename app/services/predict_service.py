import os
import requests
import re
import json
from services.exchange_service import get_usd_to_eur_rate

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def parse_ollama_response(raw_text: str) -> str:
    """
    Concatenate streaming NDJSON responses into a single coherent string.
    """
    parts = []
    for line in raw_text.splitlines():
        print(123, line)
        if not line.strip():
            continue
        try:
            data = json.loads(line)
            if "response" in data:
                parts.append(data["response"])
        except json.JSONDecodeError:
            continue
    return "".join(parts)


def _query_ollama(prompt: str, timeout: int = 60) -> str:
    """
    Sends prompt to Ollama API (/api/generate). Returns text output.
    """
    url = f"{OLLAMA_URL}/api/generate"
    payload = {"model": OLLAMA_MODEL, "prompt": prompt}
    r = requests.post(url, json=payload, timeout=timeout)

    r.raise_for_status()

    data = r.text

    if isinstance(data, dict):
        for k in ("response", "text", "result", "completion", "output"):
            if k in data and isinstance(data[k], str):
                return data[k]
        # Some endpoints return {'generations': [{'text': '...'}]}
        if "generations" in data and isinstance(data["generations"], list) and data["generations"]:
            gen0 = data["generations"][0]
            if isinstance(gen0, dict) and "text" in gen0:
                return gen0["text"]
    return data


_FLOAT_RE = re.compile(r"[-+]?\d{1,3}(?:[,\d{3}])*(?:\.\d+)?|\d+\.\d+|\d+")


def _extract_first_number(text: str) -> float:
    if not text:
        raise ValueError("Empty response from model")

    # Try to concatenate streaming JSON chunks if present
    combined = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if "response" in obj:
                combined.append(obj["response"])
        except json.JSONDecodeError:
            # if not valid JSON, treat as plain text
            combined.append(line)

    # join fragments
    text = "".join(combined) if combined else text

    # extract the first numeric pattern
    matches = re.findall(r"[-+]?\d[\d,]*\.?\d*", text)
    if not matches:
        raise ValueError(f"No numeric value found in model response: {text}")
    num = matches[0].replace(",", "")
    return float(num)


def health() -> dict:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return {"ollama_up": r.status_code == 200}
    except Exception:
        return {"ollama_up": False}


def predict_from_dict(payload: dict) -> dict:
    """
    Send payload to Ollama model. Expect model to return a USD price number (or text containing it).
    Convert to EUR using Frankfurter rate and return both values.
    """
    # Build a clear instruction prompt for the model
    prompt_lines = [
        "You are an assistant that outputs a single JSON object with a numeric field price_usd.",
        "Do not include any explanation or extra text. Only output valid JSON.",
        "If you cannot predict, return {\"price_usd\": null}.",
        "",
        "Input features:",
        f"{payload}"
    ]
    prompt = "\n".join(prompt_lines) + \
        "\n\nReturn example: {\"price_usd\": 12345.67}"

    text = _query_ollama(prompt)
    # Try to parse JSON first
    import json
    price_usd = None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and "price_usd" in parsed:
            price_usd = parsed["price_usd"]
    except Exception:
        # not JSON; try to extract number
        try:
            price_usd = _extract_first_number(text)
        except Exception as e:
            raise RuntimeError(
                f"Could not parse price from Ollama response: {text}") from e

    if price_usd is None:
        raise RuntimeError(f"Ollama returned null price: {text}")

    try:
        rate = get_usd_to_eur_rate()
    except Exception as e:
        raise RuntimeError(
            f"Prediction succeeded but failed to convert to EUR: {e}") from e

    price_eur = round(float(price_usd) * rate, 2)
    return {"price_usd": float(price_usd), "price_eur": price_eur, "exchange_rate": rate, "raw_response": text}
