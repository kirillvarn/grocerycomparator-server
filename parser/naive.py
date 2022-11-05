import maxima, rimi, selver, prisma, coop
from threading import Thread

import psycopg2 as repo
import db

from datetime import date, datetime

def clear_db():
    conn = db.connect(db="naive_products")
    cursor = conn.cursor()

    DATE = datetime.today().strftime("%Y-%m-%d")

    q = 'DROP TABLE IF EXISTS "%s";'

    cursor.execute(q, (DATE, ))
    conn.commit()
    cursor.close()
    conn.close()

def run():
    METHOD = "naive"
    th_list = []

    clear_db()

    th_list.append(Thread(target=selver.main, args=(METHOD,)))
    th_list.append(Thread(target=rimi.main, args=(METHOD,)))
    th_list.append(Thread(target=prisma.main, args=(METHOD,)))
    th_list.append(Thread(target=maxima.main, args=(METHOD,)))
    #th_list.append(Thread(target=coop.main, args=(METHOD,)))

    for i in th_list:
        i.start()

    for i in th_list:
        i.join()
