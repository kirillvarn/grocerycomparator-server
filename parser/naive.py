import maxima, rimi, selver, prisma, coop
from threading import Thread


def run():
    METHOD = "naive"
    th_list = []

    th_list.append(Thread(target=selver.main, args=(METHOD,)))
    th_list.append(Thread(target=rimi.main, args=(METHOD,)))
    th_list.append(Thread(target=prisma.main, args=(METHOD,)))
    th_list.append(Thread(target=maxima.main, args=(METHOD,)))
    th_list.append(Thread(target=coop.main, args=(METHOD,)))

    for i in th_list:
        i.start()

    for i in th_list:
        i.join()
