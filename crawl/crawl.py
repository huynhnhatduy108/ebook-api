import requests
from unidecode import unidecode

def crawl(keywork= ""):
    data_crawl = []
    if not keywork:
        return data_crawl
    keywork = unidecode(keywork)
    keywork = keywork.lower()

    tiki_data = tiki_crawl(keywork)
    if tiki_data:
        data_crawl.append(tiki_data)
    
    return data_crawl

def tiki_crawl(q):
    tiki_domain ="https://tiki.vn/"
    tiki_search =  tiki_domain + "search?q={}".format(q)
    tiki_api = "https://tiki.vn/api/v2/products?limit={}&q={}".format(15, q)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }

    response = requests.get(tiki_api, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        books = data["data"]
        if len(books):
            best_data = {
                "domain":"TIKI",
                "price": books[0]["price"],
                "name": books[0]["name"],
                "quantity_sold": books[0]["quantity_sold"]["value"],
                "url_path": tiki_domain + books[0]["url_path"],
                "url_search": tiki_search,
            }
            return best_data 
        return None       
    return None

def shopee_crawl(q):
    pass
            

            




    