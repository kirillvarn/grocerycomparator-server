import requests as req
from parser.db import *
from parser.current_products import *

# disable warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# variables
URL = 'http://api.ecoop.ee/supermarket/products?language=et&page='
p_array = list()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

def parseApi():
    page = 1
    while True:
        data = req.get(URL + str(page), headers=headers, timeout=60, verify=False)
        response = data.json()["data"]

        if len(response) == 0:
            break

        for item in response:
            if item['price_sale'] != None:
                discount = True
                price = item['price_sale']
            else:
                discount = False
                price = item['price']

            p_array.append({'id': item['id'], 'name': item['name'], 'price': price, 'discount': discount})

        page += 1

def main(method):
    parseApi()
    if method == "naive":
        naiveHandleDB(p_array, 'coop')
    else:
        handleDB(p_array, 'coop')

def current_products() -> None:
    parseApi()
    insert_current_products(p_array, "coop")