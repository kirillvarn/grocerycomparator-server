from datetime import datetime
import psycopg2
import time
from credentials import user_data
# exception handling
from psycopg2 import errors
UniqueViolation = errors.lookup('23505')


DATE = datetime.today().strftime("%Y-%m-%d")
RETRY_LIMIT = 50


def connect(retries=0, db='products'):
    try:
        print(f"Connecting to {db}")
        CONNECTION = psycopg2.connect(dbname=db, user=user_data['username'],
                                      password=user_data['password'], host=user_data['host'], port=user_data['port'])
        print(f"Done connecting to {db}")
        retries = 0
        return CONNECTION
    except psycopg2.OperationalError as error:
        if retries >= RETRY_LIMIT:
            raise error
        else:
            retries += 1
            print(f"[WARNING] {error} \n, Reconnecting to {db} {retries}")
            time.sleep(5)
            return connect(retries, db)
    except (Exception, psycopg2.Error) as error:
        raise error


def updateDates(shop_name):
    conn = connect(0)
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()

    try:
        query_s = "insert into updatedates values (%s, %s)"
        cursor.execute(query_s, (DATE, shop_name))
        conn.close()
    except Exception as e:
        conn.close()
        pass

    conn.commit()
    cursor.close()


def getSchemaCount():
    conn = connect(0)
    conn.set_client_encoding('UTF8')

    cursor = conn.cursor()
    query_s = 'SELECT * FROM "%s";'
    try:
        cursor.execute(query_s, (DATE,))
        cursor.close()
        conn.close()
        return True
    except:
        cursor.close()
        conn.close()
        return False


def getPopulatedDates():
    conn = connect(0)
    conn.set_client_encoding('UTF8')
    query_d = 'select u_name, shop_name from updatedates where u_name != %s'
    cursor = conn.cursor()
    cursor.execute(query_d, (DATE, ))
    data = cursor.fetchall()
    conn.close()
    return data


def getLastId(conn):
    cursor = conn.cursor()
    query_s = 'SELECT count(prod_id) FROM "initial_products"'
    cursor.execute(query_s)
    return cursor.fetchone()[0]


def createInitialTable():
    conn = connect(0)
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()

    query_s = 'CREATE TABLE IF NOT EXISTS initial_products (prod_id serial PRIMARY KEY, name varchar(255), price FLOAT, shop varchar(16), discount BOOLEAN);'
    try:
        cursor.execute(query_s)
    except Exception as e:
        print(e)

    conn.commit()
    cursor.close()
    conn.close()


def createTable():
    conn = connect(0)
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()

    query_s = 'CREATE TABLE IF NOT EXISTS "%s" (prod_id INTEGER, name varchar(255), price FLOAT, shop varchar(16), discount BOOLEAN);'
    cursor.execute(query_s, (DATE,))
    conn.commit()
    cursor.close()
    conn.close()


def populate(products, shop, is_initial):
    conn = connect(0)
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()

    for product in products:
        query_s = 'insert into "%s" values (%s, %s, %s, %s, %s)'
        query_initial = "insert into initial_products values (DEFAULT, %s, %s, %s, %s)"
        try:
            price = float(product["price"])
        except:
            price = 0

        try:
            if is_initial:
                cursor.execute(
                    query_initial, (product["name"], price, shop, product['discount']))
            else:
                cursor.execute(
                    query_s, (DATE, product["prod_id"], product["name"], price, shop, product['discount']))

            conn.commit()
        except Exception as e:
            raise e

    # adding current date to the DB
    conn.commit()
    cursor.close()
    conn.close()


def compareProducts(products, dates, shop):
    conn = connect(0)
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()

    changed_products = list()
    new_products = list()

    # iterating through each date, starting from the most recent one
    # (datetime, shopname) tuple format
    for date in dates[::-1]:
        flag_first = date[0] == "2022-02-03"
        try:
            if (flag_first):
                query_s = 'SELECT prod_id, name FROM initial_products WHERE shop=%s'
                cursor.execute(query_s, (shop,))
            else:
                query_s = 'SELECT prod_id, name FROM "%s" WHERE shop=%s'
                cursor.execute(query_s, (date[0], shop))
        except Exception as e:
            print(e)

        # getting a tuple (id, name)
        cache_names = [name[1] for name in cursor.fetchall()]
        # iterating through each product to see, whether price has changed
        for product in products:
            if (product['name'] in cache_names):
                try:
                    if not (flag_first):
                        query_p = 'SELECT prod_id, price FROM "%s" WHERE name=%s AND shop=%s'
                        cursor.execute(
                            query_p, (date[0], product['name'], shop))
                    else:
                        query_p = 'SELECT prod_id, price FROM initial_products WHERE name=%s AND shop=%s'
                        cursor.execute(query_p, (product['name'], shop))
                except Exception as e:
                    print(e)
                price_cache = cursor.fetchone()

                if product in changed_products:
                    # checking if already added a product
                    continue
                try:
                    if (float(product['price']) > price_cache[1] or float(product['price']) < price_cache[1]):
                        changed_products.append(
                            {'prod_id': price_cache[0], 'name': product['name'], 'price': product['price'], 'discount': product['discount']})
                except:
                    changed_products.append(
                        {'prod_id': price_cache[0], 'name': product['name'], 'price': 0, 'discount': product['discount']})

                # removing a product from a list to add leftovers to the DB
                products.remove(product)

    # actually adding leftovers
    new_products += products
    i_delta = 0

    for product in new_products:
        index = getLastId(conn)
        changed_products.append(
            {'prod_id': index + i_delta, 'name': product['name'], 'price': 0, 'discount': product['discount']})
        products.remove(product)

        i_delta += 1

    cursor.close()
    conn.close()
    print(f"done parsing {shop}")
    return changed_products


def handleDB(products, shop):
    dates = getPopulatedDates()

    if len([item for item in dates if shop in item and DATE not in item]) == 0:
        try:
            createInitialTable()
            updateDates(shop)
        except:
            pass
        populate(products, shop, True)
    else:
        commit_products = compareProducts(products, dates, shop)
        if len(commit_products) != 0:
            try:
                createTable()
                updateDates(shop)
            except Exception as e:
                raise e
            populate(commit_products, shop, False)


def naiveHandleDB(products, shop):
    conn = connect(0, 'naive_products')
    conn.set_client_encoding('UTF8')
    cursor = conn.cursor()

    query_s = 'CREATE TABLE IF NOT EXISTS "%s" (id integer, name varchar(255), price FLOAT, shop varchar(16), discount BOOLEAN);'

    cursor.execute(query_s, (DATE,))
    conn.commit()
    cursor.close()

    cursor = conn.cursor()

    for product in products:
        if shop == 'selver':
            query_s = 'insert into "%s" values (%s, %s, %s, %s, %s)'

            try:
                price = float(product["price"])
            except:
                price = 0
            try:
                cursor.execute(
                    query_s, (DATE, product["id"], product["name"], price, shop, product['discount']))
            except psycopg2.errors.UniqueViolation as uv:
                pass
            except Exception as e:
                raise e
        else:
            query_s = 'insert into "%s" values (null, %s, %s, %s, %s)'

            try:
                price = float(product["price"])
            except:
                price = 0
            try:
                cursor.execute(
                    query_s, (DATE, product["name"], price, shop, product['discount']))
            except Exception as e:
                raise e

        conn.commit()

    cursor.close()
    print(f"done parsing {shop}")
    # adding current date to the DB
    conn.commit()

    conn.close()
