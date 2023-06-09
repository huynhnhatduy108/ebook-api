from unidecode import unidecode
from crawl.tiki import tiki_crawl_list



def crawl_data(keywork= ""):
    data_crawl = []
    # try:
    if not keywork:
        return data_crawl
    keywork = unidecode(keywork)
    keywork = keywork.lower()

    tiki_data = tiki_crawl_list(keywork)
    if tiki_data:
        data_crawl +=tiki_data
    
    return data_crawl
# except:
    # return data_crawl






            




    