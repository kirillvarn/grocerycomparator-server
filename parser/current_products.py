from pypika import Query, Table, Field, Schema
from credentials import user_data
import psycopg2


conn = psycopg2.connect(
    dbname=user_data["dbname"],
    user=user_data["username"],
    password=user_data["password"],
    host=user_data["host"],
    port=user_data["port"],
)

schema = Schema("current_products")
current_products = Table("products", schema=schema)

cursor = conn.cursor()

q = Query.from_(current_products).select("*").get_sql()
print(q)

cursor.execute(q)
data = cursor.fetchall()
cursor.close()
conn.close()
