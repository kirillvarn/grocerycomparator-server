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
def connect(retries=0, db="products", dev=True):
    if dev:
        user = "postgres"
        password = 'postgres'
        host = 'db'
        port = "5433"
        db = "products"
    else:
        user = user_data['username']
        password = user_data['password']
        host = user_data['host']
        port = user_data['port']
        db = user_data['port']

    try:
        CONNECTION = psycopg2.connect(dbname=db, user=user, password=password, host=host, port=port, connect_timeout=3)
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

def get_tables(dbname, dev=True) -> list:
    conn = connect(db=dbname, dev=dev)

    query_st: str = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name ASC"
    cursor = conn.cursor()
    cursor.execute(query_st)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return [x[0].replace("'", "") for x in data]

def start_parsing():
    #TODO: implement parsing functionality
    # should delete the table if it exist
    # if parsing stops halfway through with an error should return error response as well and maybe delete the table?

    return {"response": {"status": "error", "message": "Not implemented yet!"}}

def login(json):
    conn = connect()
    query_st: str = "SELECT * FROM utility.users WHERE username = %s and password = %s"
    cursor = conn.cursor()
    cursor.execute(query_st, (json['username'], json['password']))
    data = cursor.fetchone() or []
    cursor.close()
    conn.close()
    if len(data) > 0:
        response = True
    else:
        response = "Username or password is incorrect!"
    return response

def get_products(dbname, limit_by=64, offset_by=0, search_str='', shop_str='', dev=True) -> dict:
    conn = connect(db=dbname, dev=dev)

def get_products(dbname, limit_by=64, offset_by=0, search_str='', shop_str='') -> dict:
    conn = connect(db=dbname)

    tables = get_tables(dbname)
    last_table = tables[-1]
    cursor = conn.cursor()
    search_pattern = f"%{search_str}%"
    shop_pattern = f"%{shop_str}%"
    offset_by = int(offset_by)
    if offset_by > 0:
        offset_by = offset_by - 1
    query = 'SELECT (SELECT COUNT(*) FROM "%s" WHERE name ILIKE %s AND shop ILIKE %s), id, name, price, shop, discount FROM "%s" WHERE name ILIKE %s AND shop ILIKE %s LIMIT %s OFFSET %s;'
    cursor.execute(query, (last_table, search_pattern, shop_pattern, last_table, search_pattern, shop_pattern, limit_by, offset_by * int(limit_by)))
    fetched = cursor.fetchall()
    data = {f"{id if id else name}":{"id": id if id else name, "name": name, "price": price, "shop": shop, "discount": discount} for _, id, name, price, shop, discount in fetched}
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

def get_product_prices(dbname, id, is_name=False):
    conn = connect(db=dbname)

    tables = get_tables(dbname)
    if not is_name:
        query_l = [f'SELECT \'{x}\' as tablename, name, price FROM "\'{x}\'" WHERE id={id}' for x in tables]
    else:
        query_l = [f'SELECT \'{x}\' as tablename, name, price FROM "\'{x}\'" WHERE name=\'{id}\'' for x in tables]
    
    cursor = conn.cursor()
    query = ' UNION ALL '.join(query_l)

    cursor.execute(query)
    fetched = cursor.fetchall()
    data = {fetched[0][1]: {x[0]: x[2] for x in fetched}}
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
