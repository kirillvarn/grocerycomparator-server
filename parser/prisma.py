from requests_html import HTMLSession
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import socket

# disable warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# db
from db import *

### constants and global variables ###

# base url
URL = 'https://www.prismamarket.ee'
# instance of HTMLSession class for JS-rendered pages
session = HTMLSession()
# global products list
p_array = list()


def getURLs(url):
    url_array = list()
    content = session.get(url, verify=False)
    links = content.html.find('a.name')


    for link in links:
        url_array.append(list(link.links)[0])
    return url_array

def parseItemData(html_code):
    name = html_code.find('div', class_='name').text
    try:
        subname = html_code.find('span', class_='subname').text
        subname = ', ' + subname.split(',')[0]
    except:
        subname = ''

    price = html_code.find('span', class_='whole-number').text + "." + html_code.find('span', class_='decimal').text
    discount = True if html_code.find('div', class_="discount-price") != None else False
    return {'name': name + subname, 'price': price, 'discount': discount}

async def getProducts(session, url):
    page = 1
    while True:
        async with session.get(url = f"{URL + url}?page={page}", headers={"Connection": "close"}, ssl=False) as response:
            response_data = await response.text()
            html_data = BeautifulSoup(response_data, 'html.parser')
            items = html_data.find_all('li', class_='item')
            for item in items: 
                prod = parseItemData(item)
                if prod in p_array:
                    return False
                p_array.append(prod)

async def scrap():
    

    m_urls = list()
    for link in getURLs(URL + "/products/selection"):
        m_urls.append(getURLs(URL + link))
    link_list = [item for sublist in m_urls for item in sublist]
    semaphore = asyncio.Semaphore(200)
    async with semaphore:
        connector = aiohttp.TCPConnector(family=socket.AF_INET, force_close=True, ssl=False)
        async with aiohttp.ClientSession(connector=connector, trust_env = True) as session:
            tasks = (getProducts(session, url) for url in link_list)
            await asyncio.gather(*tasks)      

def main(method):
    try:
        asyncio.run(scrap())
    except Exception as e:
        raise e
    if (method == "naive"):
        naiveHandleDB(p_array, 'prisma')
    else:
        handleDB(p_array, 'prisma')
