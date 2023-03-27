import parser.maxima as maxima, parser.rimi as rimi, parser.selver as selver, parser.prisma as prisma
from threading import Thread

from parser.db import log_products

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

    log_products()
