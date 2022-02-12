import requests as req
import asyncio
import aiohttp

# db
from db import *


# variables and contants
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36', 
}

api_url = 'https://www.selver.ee/api/catalog/vue_storefront_catalog_et/product/_search?_source_exclude=configurable_options,description,product_nutr_*,sgn,*.sgn,msrp_display_actual_price_type,*.msrp_display_actual_price_type,required_options&_source_include=documents,activity,configurable_children.attributes,configurable_children.id,configurable_children.final_price,configurable_children.color,configurable_children.original_price,configurable_children.original_price_incl_tax,configurable_children.price,configurable_children.price_incl_tax,configurable_children.size,configurable_children.sku,configurable_children.special_price,configurable_children.special_price_incl_tax,configurable_children.tier_prices,final_price,id,image,name,new,original_price_incl_tax,original_price,price,price_incl_tax,product_links,sale,special_price,special_to_date,special_from_date,special_price_incl_tax,status,tax_class_id,tier_prices,type_id,url_path,url_key,*image,*sku,*small_image,short_description,manufacturer,product_*,extension_attributes.deposit_data,stock,prices,vmo_badges&size=500'

p_array = list()

async def getAPIData(session, size):
    async with session.get(url = f"{api_url}&from={size}") as response:
            response = await response.json()
            response_data = response['hits']['hits']

            if len(response_data) == 0:
                return

            for item in response_data:
                discount = False
                if item["_source"]["prices"][0]["is_discount"] == True:
                    discount = True
                p_array.append({'id':item['_source']['stock']['item_id'], 'name': item['_source']['name'],'price':item['_source']['final_price_incl_tax'], 'discount': discount})

async def gatherData():
    async with aiohttp.ClientSession(trust_env = True) as session:
        tasks = list()

        for size in range(0, 15000, 500):
            task = asyncio.create_task(getAPIData(session, size))
            tasks.append(task)
        
        await asyncio.gather(*tasks)

def main(method):
    asyncio.run(gatherData())
    if (method == "naive"):
        naiveHandleDB(p_array, 'selver')
    else:
        handleDB(p_array, 'selver')

