import psycopg2, os, time
from main import *


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


tables = get_tables("naive_products")
print(tables)