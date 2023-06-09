# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

def lazada_crawl(keyword):
    # Set up the Chrome driver with headless mode
    # options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # # options.binary_location = "chromedriver"
    # driver = webdriver.Chrome(options=options)

    # # Navigate to the search results page
    # query = 'giet con chim nhai'
    # url = f'https://www.lazada.vn/catalog/?q={query}'
    # driver.get(url)

    # # Wait for the search results to load
    # wait = WebDriverWait(driver, 10)
    # wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'c16H9d')))

    # # Extract the product data using Selenium's find_element functions
    # products = driver.find_elements(By.CLASS_NAME, 'c16H9d')
    # for product in products:
    #     name = product.find_element(By.CLASS_NAME, 'c16H9d').text
    #     description = product.find_element(By.CLASS_NAME, 'c3lrWr').text
    #     price = product.find_element(By.CLASS_NAME, 'c13VH6').text
    #     image = product.find_element(By.CLASS_NAME, 'c1ZEkM').get_attribute('src')
        
    #     print(name, description, price, image)

    # # Close the web driver
    # driver.quit()
    pass