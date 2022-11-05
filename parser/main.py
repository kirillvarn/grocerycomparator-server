from threading import Thread
import naive, products, current_products
import selver, rimi, coop, maxima, prisma

from datetime import date


DAY = date.today().timetuple().tm_yday
DAY = int(DAY)

th_list = []

th_list.append(Thread(target=selver.current_products))
th_list.append(Thread(target=rimi.current_products))
th_list.append(Thread(target=prisma.current_products))
th_list.append(Thread(target=maxima.current_products))
th_list.append(Thread(target=coop.current_products))

for i in th_list:
    i.start()

for i in th_list:
    i.join()

if DAY % 3 == 0:
    naive.run()
    products.run()
