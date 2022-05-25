import psycopg2.extensions
import psycopg2
from credentials import user_data

import time
from math import floor


# CONSTANTS

INITIAL_TABLE_NAME = "initial_table"
RETRY_LIMIT = 10

# type aliases
connection = psycopg2.extensions.connection

# SETTING UP THE CONNECTION #
def connect(retries=0, db="products"):
    try:
        CONNECTION = psycopg2.connect(dbname=db, user=user_data['username'], password=user_data['password'], host=user_data['host'], port=user_data['port'], connect_timeout=3)
        retries = 0
        return CONNECTION
    except psycopg2.OperationalError as error:
        if retries >= RETRY_LIMIT:
            raise error
        else:
            retries += 1
            time.sleep(5)
            return connect(retries=retries, db=db)
    except (Exception, psycopg2.Error) as error:
        raise error

def get_tables(dbname) -> list:
    conn = connect(db=dbname)

    query_st: str = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name ASC"
    cursor = conn.cursor()
    cursor.execute(query_st)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return [x[0].replace("'", "") for x in data]


def get_products(dbname, limit_by=64, offset_by=0, search_str='', shop_str='') -> dict:
    conn = connect(db=dbname)

    tables = get_tables(dbname)
    cursor = conn.cursor()
    search_pattern = f"%{search_str}%"
    shop_pattern = f"%{shop_str}%"

    query = 'SELECT (SELECT COUNT(*) FROM initial_products WHERE name ILIKE %s AND shop ILIKE %s), prod_id, name, price, shop, discount FROM initial_products WHERE name ILIKE %s AND shop ILIKE %s LIMIT %s OFFSET %s;'
    cursor.execute(query, (search_pattern, shop_pattern, search_pattern, shop_pattern, limit_by, int(offset_by) * int(limit_by)))
    fetched = cursor.fetchall()
    data = {f"{id}":{"id": id, "name": name, "price": price, "shop": shop, "discount": discount} for _, id, name, price, shop, discount in fetched}
    cursor.close()
    conn.close()
    try:
        pages = floor(int(fetched[0][0])/int(limit_by))
    except:
        pages = 1
    return {"pages": pages, "data": data}

def order_products_by_name(dbname) -> tuple:
    conn = connect(db=dbname)
    data = dict()

    products = get_product(dbname)
    data_keys = list(products.keys())

    for d_key in data_keys:
        for item in products[d_key]:
            if products[d_key][item]["shop"] == "selver":
                key = f"{item}, {products[d_key][item]['name']}"
            else:
                key = item

            data[key] = {'id': products[d_key][item]['id'], 'name': products[d_key][item]['name'] , 'discount': products[d_key][item]['discount'], 'shop': products[d_key][item]['shop']}


    return data_keys, data

def get_names_and_ids(data: list) -> list:
    return list(map(lambda x: x[0] if x[3] == "selver" else x[1], data))

def get_product_prices(dbname, id):
    conn = connect(db=dbname)

    tables = get_tables(dbname)
    query_l = [f'SELECT name, price FROM "\'{x}\'" WHERE prod_id={id}' for x in tables if x != "initial_products" and x != "updatedates"]
    query_l.insert(0, f'SELECT name, price FROM initial_products WHERE prod_id={id}')
    cursor = conn.cursor()
    query = ' UNION ALL '.join(query_l)

    cursor.execute(query)
    fetched = cursor.fetchall()
    data = {fetched[0][0]: [x[1] for x in fetched]}
    cursor.close()
    conn.close()
    return data

def get_prices(dbname) -> tuple:
    conn = connect(dbname)

    products = get_products(dbname)
    data_keys = list(products.keys())

    price_data = dict()

    for d_key in data_keys:
        for item in products[d_key]:
            if products[d_key][item]["shop"] == "selver":
                key = f"{item}, {products[d_key][item]['name']}"
            else:
                key = item
            try:
                price_data[key] += [products[d_key][item]['price']]
            except:
                price_data[key] = [products[d_key][item]['price']]

    return data_keys, price_data
