Used Cars — Full Ollama prediction backend

Overview:

- FastAPI app sends prompts to local Ollama container for price prediction.
- Kaggle fetcher downloads datasets into `notebooks/data/` and a cleaner copies to `ollama_data` blobs for Ollama to consume.
- Frankfurter API used for USD→EUR conversion.
- Postgres stores logs: dataset fetches and prediction requests.

Run:

1. Put `kaggle.json` in ~/.kaggle (Kaggle API).
2. Adjust `.env` or environment variables.
3. Pull or ensure Ollama model present:
   docker compose up -d ollama
   docker exec -it ollama ollama pull <model-ref>
4. Start stack:
   docker compose up -d --build
5. Check FastAPI docs: http://localhost:8000/docs

Notes:

- This repo uses Ollama as the inference engine (no local sklearn inference).
- Kaggle downloader runs via API endpoint or background scheduler inside FastAPI.
