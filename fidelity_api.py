# file: fidelity_api.py
# FastAPI + Selenium for Cloud Run
# Deploy with: gcloud run deploy fidelity-api --source . --region us-central1 --allow-unauthenticated

import time
from fastapi import FastAPI
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()

app = FastAPI()

class SearchRequest(BaseModel):
    search_term: str

@app.post("/search")
def automate_fidelity_search(request: SearchRequest):
    search_term = request.search_term
    result = {"instrument_name": None, "buy_price": None, "sell_price": None, "url": None, "error": None}

    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        # Automatically install ChromeDriver matching your Chrome version
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        url = "https://www.fidelity.co.uk/search/?host=www.fidelity.co.uk"
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        # Step 0: Switch into iframe
        frame_selector = (By.ID, "answers-frame")
        wait.until(EC.frame_to_be_available_and_switch_to_it(frame_selector))

        # Step 1: Search box
        search_box_selector = (By.ID, "yxt-SearchBar-input--SearchBar")
        search_box = wait.until(EC.presence_of_element_located(search_box_selector))
        search_box.clear()
        search_box.send_keys(search_term)
        time.sleep(1)
        search_box.send_keys(Keys.RETURN)

        # Step 2: Click first result
        first_result_selector = (By.CSS_SELECTOR, "a.HitchhikerDocumentStandard-titleLink")
        first_result_link = wait.until(EC.element_to_be_clickable(first_result_selector))
        driver.execute_script("arguments[0].click();", first_result_link)
        driver.switch_to.default_content()

        # Step 3: Extract instrument name
        name_selector = (By.CSS_SELECTOR, "h1.detail__name")
        name_elem = wait.until(EC.presence_of_element_located(name_selector))
        result["instrument_name"] = name_elem.text.strip()

        # Step 4: Extract prices
        try:
            buy_selector = (By.CSS_SELECTOR, "div.buyPrice, span.buyPrice, h3.buyPrice")
            sell_selector = (By.CSS_SELECTOR, "div.sellPrice, span.sellPrice, h3.sellPrice")
            result["buy_price"] = wait.until(EC.presence_of_element_located(buy_selector)).text.strip()
            result["sell_price"] = wait.until(EC.presence_of_element_located(sell_selector)).text.strip()
        except TimeoutException:
            try:
                sell_xpath = '//div[normalize-space(text())="Sell"]/following-sibling::h3[contains(@class,"detail_value")]'
                buy_xpath = '//div[normalize-space(text())="Buy"]/following-sibling::h3[contains(@class,"detail_value")]'
                result["buy_price"] = wait.until(EC.presence_of_element_located((By.XPATH, buy_xpath))).text.strip()
                result["sell_price"] = wait.until(EC.presence_of_element_located((By.XPATH, sell_xpath))).text.strip()
            except TimeoutException:
                fund_xpath = '//div[contains(text(),"Last buy/sell price")]/following-sibling::h3[contains(@class,"detail_value")]'
                fund_elem = wait.until(EC.presence_of_element_located((By.XPATH, fund_xpath)))
                result["buy_price"] = fund_elem.text.strip()
                result["sell_price"] = fund_elem.text.strip()

        result["url"] = driver.current_url

    except Exception as e:
        result["error"] = str(e)
    finally:
        if driver:
            driver.quit()

    return result


# Optional: local run for testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fidelity_api:app", host="0.0.0.0", port=8080, log_level="info")
