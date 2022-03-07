import psycopg2.extensions
import psycopg2
from credentials import user_data

import time


# CONSTANTS

INITIAL_TABLE_NAME = "initial_table"
RETRY_LIMIT = 10

# type aliases
connection = psycopg2.extensions.connection

# SETTING UP THE CONNECTION #
def connect(retries=0, db="products"):
    try:
        CONNECTION = psycopg2.connect(dbname=db, user=user_data['username'], password=user_data['password'], host=user_data['host'], port=user_data['port'])
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


def get_products(dbname) -> dict:
    conn = connect(db=dbname)

    tables = get_tables(dbname)
    select_q: str = 'SELECT * FROM "%s"'
    cursor = conn.cursor()

    query_l = [f'SELECT id, name, shop FROM "\'{x}\'"' for x in tables]
    query = ' UNION '.join(query_l)
    cursor.execute(query)
    data = {(f"{id}, {name}" if shop == "selver" else f"{id}"):{"id": id, "name": name, "shop": shop} for id, name, shop in cursor.fetchall()}
    cursor.close()
    conn.close()
    return data

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

def get_product_prices(dbname, id, name):
    conn = connect(db=dbname)

    tables = get_tables(dbname)
    query_l = [f'SELECT price FROM "\'{x}\'" WHERE "\'{x}\'".name like \'%{name}%\' and id={id}' for x in tables]
    cursor = conn.cursor()
    query = ' UNION ALL '.join(query_l)

    cursor.execute(query)
    data = {name: [x[0] for x in cursor.fetchall()]}
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
