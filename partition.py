import psycopg2, os, time
from main import *

from psycopg2 import sql, extras
from progress.bar import Bar

def connect(retries=0, db="products"):
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    host = os.getenv("PGHOST")
    port = os.getenv("PGPORT")

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
        if retries >= 30:
            raise error
        else:
            retries += 1
            time.sleep(5)
            return connect(retries=retries, db=db)
    except (Exception, psycopg2.Error) as error:
        raise error


def leading_zero(month: int) -> str:
    s_month = str(month)
    if len(s_month) == 1:
        return f"0{s_month}"
    return s_month

tables = get_tables("naive_products")

conn = connect(db="naive_products")
cursor = conn.cursor()
try:
    bar = Bar("Processing", max = len(tables))
    for table in tables:
        # getting the data
        # query_get = sql.SQL("select *, {} from {}").format(sql.Placeholder(), sql.Identifier(f"'{table}'"))
        # cursor.execute(query_get, (table, ))
        # data = cursor.fetchall()

        # inserting the data
        query_insert = sql.SQL("insert into products (id, name, price, shop, discount, inserted_at) select id, name, price, shop, discount, {} as inserted_at from {}").format(sql.Placeholder(), sql.Identifier(f"'{table}'"))
        cursor.execute(query_insert, (table,))
    
        bar.next()
    bar.finish()
    conn.commit()
    cursor.close()
    print(f"inserted {table}")
except psycopg2.DatabaseError as error:
    print(error)
finally:
    if conn is not None:
        conn.close()








# months
# months = [table.split("-")[1] for table in tables]
# months = set(months)
# partitions = [(f"2022-{month}-1", f"2022-{leading_zero(int(month) + 1)}-1") for month in months]


# conn = connect(db="naive_products")
# cursor = conn.cursor()
# try:
#     for partition in partitions:
#         date = partition[0].split("-")
#         month = f"{date[0]}{date[1]}"
#         from_month = partition[0]
#         to_month = partition[1]

#         # query = "create table %s partition of products for values from (%s) to (%s)"
#         query = sql.SQL('create table {} partition of products for values from ({}) to ({})').format(sql.Identifier(f"products_{month}"), sql.Placeholder(), sql.Placeholder())
#         cursor.execute(query, (from_month, to_month))

#     conn.commit()
#     cursor.close()
# except psycopg2.DatabaseError as error:
#     print(error)
# finally:
#     if conn is not None:
#         conn.close()