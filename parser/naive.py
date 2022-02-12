import maxima, rimi, selver, prisma, coop
from threading import Thread
from datetime import datetime

import psycopg2
from credentials import user_data
DATE = datetime.today().strftime("%Y-%m-%d")

# drop table if it exists
conn = psycopg2.connect(dbname=user_data['naive_dbname'], host=user_data['host'], port=user_data['port'], user=user_data['username'], password=user_data['password'])
cursor = conn.cursor()  
drop_q = 'DROP TABLE IF EXISTS "%s";'
cursor.execute(drop_q, (DATE, ))
cursor.close()
conn.close()

METHOD = "naive"
selver.main(METHOD)
prisma.main(METHOD)
maxima.main(METHOD)
coop.main(METHOD)
rimi.main(METHOD)
