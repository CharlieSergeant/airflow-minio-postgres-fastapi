from selenium.webdriver.common.by import By
import logging

def scrape_example(driver):
    driver.get("https://www.bing.com")
    driver.implicitly_wait(5)
    search_box = driver.find_element(By.NAME, "q")
    search_box.clear()
    search_box.send_keys("John Doe")  # enter your name in the search box
    search_box.submit()  # submit the search
    results = driver.find_elements(By.XPATH, "//*[@id='b_tween']/span")
    logging.info(str(results[0]))
    logging.info('+++ Success +++')
