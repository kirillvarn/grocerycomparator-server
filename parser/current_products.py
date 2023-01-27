from pypika import Query, Table, Schema, functions as fn
from colorama import Fore, Style
from parser.db import connect
from datetime import datetime
import parser.maxima as maxima, parser.rimi as rimi, parser.selver as selver, parser.prisma as prisma
from threading import Thread

# from parser import *

DATE = datetime.today().strftime("%Y-%m-%d")

schema = Schema("public")
current_products = Table("products", schema=schema)

def run():
    th_list = []

    th_list.append(Thread(target=selver.current_products))
    th_list.append(Thread(target=rimi.current_products))
    th_list.append(Thread(target=prisma.current_products))
    th_list.append(Thread(target=maxima.current_products))

    for i in th_list:
        i.start()

    for i in th_list:
        i.join()

def is_empty(conn, shop: str) -> bool:
    q = (
        Query.from_(current_products)
        .select(fn.Count(current_products.product_id))
        .where(current_products.shop == shop)
        .get_sql()
    )

    cursor = conn.cursor()
    cursor.execute(q)
    amount = cursor.fetchone()[0]
    cursor.close()

    return True if amount == 0 else False


def insert_current_products(products: list, shop: str) -> None:
    print(f"{Fore.BLUE}[INFO][CURRENT] Started populating {shop}{Style.RESET_ALL}")
    conn = connect()
    cursor = conn.cursor()

    is_empty_flag = is_empty(conn, shop)

    if is_empty_flag:
        query = Query.into(current_products)
        for product in products:
            try:
                price = float(product["price"])
            except:
                price = 0

            q = query.insert(
                product["name"],
                price,
                shop,
                product["discount"],
                DATE,
                product["id"]
            ).get_sql()

            cursor.execute(q)
            conn.commit()
    else:
        query = Query.update(current_products)
        for product in products:
            try:
                price = float(product["price"])
            except:
                price = 0
            q = (
                query.set(current_products.price, price)
                .set(current_products.discount, product["discount"])
                .set(current_products.updated_at, DATE)
                .where(current_products.name == product["name"])
                .get_sql()
            )
            cursor.execute(q)
            conn.commit()

    # conn.commit()
    cursor.close()
    conn.close()
    print(f"{Fore.BLUE}[INFO][CURRENT] Done populating {shop}{Style.RESET_ALL}")
