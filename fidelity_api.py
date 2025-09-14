# file: fidelity_api.py
# FastAPI + BeautifulSoup for price scraping
# Deploy to Render as web service

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- CORS setup ---
origins = [
    "http://localhost:4200/edit-fund",  # Angular dev server
    "https://projsept-e73a6.web.app/edit-fund",  # Optional: deployed frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # can use ["*"] during testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request model ---
class ScrapeRequest(BaseModel):
    url: str

# --- API endpoint ---
@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    url = request.url
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {"price": None, "name": None, "error": f"Failed to fetch URL: {e}"}

    soup = BeautifulSoup(response.content, 'html.parser')

    # Try to extract price
    price_elem = soup.find('h3', class_='detail_value text-grey-800 mb-8 no-wrap')
    invest_name = soup.find('h1', class_="mb-8 h3 detail__name")

    if price_elem:
        price = price_elem.text.strip()
        name = invest_name.text.strip()
    else:
        price = None

    return {"price": price,"name":name, "url": url}


# # file: fidelity_api_bs4.py
# from fastapi import FastAPI
# from pydantic import BaseModel
# import requests
# from bs4 import BeautifulSoup

# app = FastAPI()

# class URLRequest(BaseModel):
#     url: str

# @app.post("/scrape")
# def scrape_fidelity(request: URLRequest):
#     url = request.url
#     result = {"price": None,"name": None, "url": url, "error": None}

#     try:
#         print(f"Fetching URL: {url}")
#         response = requests.get(url, timeout=15)
#         response.raise_for_status()  # Raise error for bad HTTP status

#         soup = BeautifulSoup(response.content, 'html.parser')
#         price_elem = soup.find('h3', class_='detail_value text-grey-800 mb-8 no-wrap')
#         invest_name = soup.find('h1', class_="mb-8 h3 detail__name")

#         if price_elem:
#             result["price"] = price_elem.text.strip()
#             result["name"] = invest_name.text.strip()
#             print(f"Price found: {result['price']}")
#         else:
#             result["error"] = "Price element not found."
#             print(result["error"])

#     except requests.RequestException as e:
#         result["error"] = f"Request failed: {str(e)}"
#         print(result["error"])
#     except Exception as e:
#         result["error"] = f"Unexpected error: {str(e)}"
#         print(result["error"])

#     return result

# # Optional: run locally
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("fidelity_api_bs4:app", host="0.0.0.0", port=8080, log_level="info")


# import requests
# from bs4 import BeautifulSoup
# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/scrape")
# async def scrape():
#     url=input('Please enter a url: ')
#     response = requests.get(url)
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Extracting the current price
#     price_elem = soup.find('h3', class_='detail_value text-grey-800 mb-8 no-wrap')
#     invest_name = soup.find('h1', class_="mb-8 h3 detail__name")

#     if price_elem:
#         price = price_elem.text.strip()
#         print(price)
#     else:
#         price = "Price not found."
#         print(price)

#     return {"price": price}

