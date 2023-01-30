from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
import asyncio

# db
from parser.db import handleDB, naiveHandleDB, insert_current_products


# if os.name == "nt":
#     loop = asyncio.ProactorEventLoop()
#     asyncio.set_event_loop(loop)
# else:
#     loop = asyncio.get_event_loop()

# disable warnings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# constants and variables
URL = "https://barbora.ee"
session = HTMLSession()
p_array = list()


def getProductData(html_code):
    index = html_code.attrs["data-b-item-id"]
    name = html_code.find("a.b-product-title > span")[0].text
    discount = (
        True if html_code.find("div.b-product-crossed-out-price") != [] else False
    )
    try:
        price = html_code.find("span.b-product-price-current-number")[0].text[1:]
    except:
        price = 0

    return {"id": index, "name": name, "price": price, "discount": discount}


def getURLs():
    p_data = session.get(URL, verify=False)
    links = p_data.html.find("li.b-categories-root-category > a")

    return [list(link.links)[0] for link in links]


async def getPageData(a_session, url):
    page = 1
    while True:
        p_url = f"{URL + url}?page={str(page)}"
        response_data = await a_session.get(p_url, verify=False)
        items = response_data.html.find("div.b-product--wrap.clearfix.b-product--js-hook")
        if len(items) == 0:
            break

        for item in items:
            p_array.append(getProductData(item))
        page += 1
    print(f"[OK][MAXIMA] {url}")


async def gatherData():
    asession = AsyncHTMLSession()
    tasks = (getPageData(asession, url) for url in getURLs())
    return await asyncio.gather(*tasks)


def main(method):

    asyncio.run(gatherData())
    if method == "naive":
        naiveHandleDB(p_array, "maxima")
    else:
        handleDB(p_array, "maxima")

def current_products() -> None:

    asyncio.run(gatherData())
    insert_current_products(p_array, "maxima")
