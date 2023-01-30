import psycopg2.extensions
import psycopg2
import os

import time
from math import floor

# CONSTANTS

INITIAL_TABLE_NAME = os.getenv("INITIAL_TABLE_NAME") or "initial_products"
RETRY_LIMIT = 10
DEV = os.environ.get("FLASK_ENV") == "development"

# type aliases
connection = psycopg2.extensions.connection

# SETTING UP THE CONNECTION #
def connect(retries=0, db="products"):
    if not DEV:
        user = os.getenv("PGUSER")
        password = os.getenv("PGPASSWORD")
        host = os.getenv("PGHOST")
        port = os.getenv("PGPORT")
    else:
        user = "postgres"
        password = "postgres"
        host = "localhost"
        port = "5432"
        db = "product_dev"

    try:
        CONNECTION = psycopg2.connect(
            dbname=db,
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=3,
        )
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

    query_st: str = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name != %s AND table_name != %s AND table_name != %s AND table_name not ilike %s ORDER BY table_name ASC"
    cursor = conn.cursor()
    cursor.execute(query_st, ("stats", "current_products", "products", "%products%"))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return [x[0].replace("'", "") for x in data]


def start_parsing():
    # TODO: implement parsing functionality
    # should delete the table if it exist
    # if parsing stops halfway through with an error should return error response as well and maybe delete the table?

    return {"response": {"status": "error", "message": "Not implemented yet!"}}


def login(json):
    conn = connect()
    query_st: str = "SELECT * FROM utility.users WHERE username = %s and password = %s"
    cursor = conn.cursor()
    cursor.execute(query_st, (json["username"], json["password"]))
    data = cursor.fetchone() or []
    cursor.close()
    conn.close()
    if len(data) > 0:
        response = True
    else:
        response = "Username or password is incorrect!"
    return response


def get_products(dbname, limit_by=64, offset_by=0, search_str="", shop_str="") -> dict:
    conn = connect(db=dbname)

    cursor = conn.cursor()
    search_pattern = f"%{search_str}%"
    shop_pattern = f"%{shop_str}%"
    offset_by = int(offset_by)
    if offset_by > 0:
        offset_by = offset_by - 1

    query_s = "select * from current_products where name ilike %s and shop ilike %s limit %s offset %s"
    cursor.execute(
        query_s, (search_pattern, shop_pattern, limit_by, offset_by * int(limit_by))
    )

    fetched = cursor.fetchall()
    data = {
        id: {
            "id": id,
            "name": name,
            "price": price,
            "shop": shop,
            "discount": discount,
            "inserted_at": inserted_at,
        }
        for id, name, price, shop, discount, inserted_at in fetched
    }
    cursor.close()
    conn.close()
    try:
        pages = floor(int(fetched[0][0]) / int(limit_by))
    except:
        pages = 1
    return {"pages": pages, "data": data}


def order_products_by_name(dbname) -> tuple:
    conn = connect(db=dbname)
    data = dict()

    products = get_products(dbname)
    data_keys = list(products.keys())

    for d_key in data_keys:
        for item in products[d_key]:
            if products[d_key][item]["shop"] == "selver":
                key = f"{item}, {products[d_key][item]['name']}"
            else:
                key = item

            data[key] = {
                "id": products[d_key][item]["id"],
                "name": products[d_key][item]["name"],
                "discount": products[d_key][item]["discount"],
                "shop": products[d_key][item]["shop"],
            }

    return data_keys, data


def get_names_and_ids(data: list) -> list:
    return list(map(lambda x: x[0] if x[3] == "selver" else x[1], data))


def get_product_prices(id):
    conn = connect(db="naive_products")
    cursor = conn.cursor()

    data_q = "select * from products where name = %s or id = %s"
    cursor.execute(data_q)
    fetched = cursor.fetchall()

    first = fetched[0]
    price_data = {{"price": item[2], "inserted_at": item[5]} for item in fetched}

    data = {
        "id": first[0],
        "name": first[1],
        "shop": first[3],
        "price_data": price_data,
    }

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
                price_data[key] += [products[d_key][item]["price"]]
            except:
                price_data[key] = [products[d_key][item]["price"]]

    return data_keys, price_data


def get_compared(dbname, products, shops) -> list:
    conn = connect(db=dbname)
    cursor = conn.cursor()
    tables = get_tables(dbname)
    latest_table = tables[-1]

    query = [
        '(select min(price), min(name), bool_or(discount), shop from "%s" where name ilike %s and price != 0 and shop in %s group by shop)'
    ] * len(products)

    if len(shops) == 1 and shops[0] == "":
        shops = ("prisma", "rimi", "coop", "maxima", "selver")

    if len(products) > 1:
        w_prod = [f"%{item}%" for item in products]
        parameters = ((latest_table, item, shops) for item in w_prod)
        parameters = tuple(element for tupl in parameters for element in tupl)
        product_query = " union ".join(query) + ";"
        cursor.execute(product_query, parameters)

    elif len(products) == 1:
        w_prod = [f"%{products[0]}%"]
        cursor.execute(query[0], (latest_table, *w_prod, shops))

    # if len(shops) > 1:
    #     query_l = f"SELECT name, price, shop, discount FROM \"%s\" WHERE ({product_query}) AND shop IN %s AND price != 0;"
    #     cursor.execute(query_l, (latest_table, *w_prod, shops))
    # elif len(shops) == 1 and shops[0] == '':
    #     query_l = f"SELECT name, price, shop, discount FROM \"%s\" WHERE {product_query} AND price != 0;"
    #     cursor.execute(query_l, (str(latest_table), *w_prod))
    # else:
    #     query_l = f"SELECT name, price, shop, discount FROM \"%s\" WHERE ({product_query}) AND shop = %s AND price != 0;"
    #     cursor.execute(query_l, (str(latest_table), *w_prod, shops[0]))

    fetched = cursor.fetchall()
    data = [
        {"name": x[1], "price": x[0], "shop": x[3], "discount": x[2]} for x in fetched
    ]

    cursor.close()
    conn.close()
    return data
