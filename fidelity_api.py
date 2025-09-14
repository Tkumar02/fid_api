import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI

app = FastAPI()

@app.get("/scrape")
async def scrape():
    url=input('Please enter a url: ')
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extracting the current price
    price_elem = soup.find('h3', class_='detail_value text-grey-800 mb-8 no-wrap')
    if price_elem:
        price = price_elem.text.strip()
        print(price)
    else:
        price = "Price not found."
        print(price)

    return {"price": price}

