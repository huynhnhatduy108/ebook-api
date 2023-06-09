
import requests
from config.constant import TIKI_API, TIKI_DOMAIN

def tiki_crawl_list(q, quantity =5):
    tiki_search =  TIKI_DOMAIN + "search?q={}".format(q)
    tiki_api = TIKI_API + "products?limit={}&q={}".format(15, q)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    response = requests.get(tiki_api, headers=headers)
    if response.status_code == 200:
        data = response.json()
        books = data["data"]
        if len(books):
            list_products = []
            for book in books:
                if len(list_products) < quantity:
                    quantity_sold = book.get("quantity_sold")
                    if quantity_sold is not None:
                        if isinstance(quantity_sold, dict):
                            quantity_sold = quantity_sold.get("value")
                        else:
                            quantity_sold = int(quantity_sold)
                    else:
                        quantity_sold = 0
                    list_products.append({
                        "domain": "TIKI",
                        "price": book["price"],
                        "name": book["name"],
                        "quantity_sold": quantity_sold,
                        "url_path": TIKI_DOMAIN + book["url_path"],
                        "url_search": tiki_search,
                    })
                else:
                    break
            return list_products
    return None


