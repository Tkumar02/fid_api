# file: fidelity_api.py
# FastAPI + requests/BeautifulSoup (no Selenium)
# Runs smoothly on Render free tier

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SearchRequest(BaseModel):
    search_term: str

@app.post("/search")
def automate_fidelity_search(request: SearchRequest):
    search_term = request.search_term.strip()
    result = {"instrument_name": None, "buy_price": None, "sell_price": None, "url": None, "error": None}

    try:
        # Fidelity search endpoint
        url = f"https://www.fidelity.co.uk/search/?q={search_term}"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Example selectors (may need adjusting if Fidelity changes layout)
        name_elem = soup.select_one("h1.detail__name")
        if name_elem:
            result["instrument_name"] = name_elem.get_text(strip=True)

        buy_elem = soup.select_one("div.buyPrice, span.buyPrice, h3.buyPrice")
        sell_elem = soup.select_one("div.sellPrice, span.sellPrice, h3.sellPrice")

        if buy_elem and sell_elem:
            result["buy_price"] = buy_elem.get_text(strip=True)
            result["sell_price"] = sell_elem.get_text(strip=True)

        result["url"] = url

    except Exception as e:
        result["error"] = str(e)

    return result


# Optional: local run for testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fidelity_api:app", host="0.0.0.0", port=8080, log_level="info")
