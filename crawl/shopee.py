import requests


def shopee_crawl(q):
    url = "https://shopee.vn/search?keyword=nha%20gia%20kim"
    response = requests.get(url)