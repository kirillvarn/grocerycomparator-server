import maxima, rimi, selver, prisma, coop
from threading import Thread

def run():
    METHOD = "none"
    # selver.main(METHOD)
    # prisma.main(METHOD)
    # maxima.main(METHOD)
    # coop.main(METHOD)
    # rimi.main(METHOD)

    th_list = []

    th_list.append(Thread(target=selver.main, args=(METHOD,)))
    th_list.append(Thread(target=rimi.main, args=(METHOD,)))
    th_list.append(Thread(target=prisma.main, args=(METHOD,)))
    th_list.append(Thread(target=maxima.main, args=(METHOD,)))
    #th_list.append(Thread(target=coop.main, args=(METHOD,)))

    for i in th_list:
        i.start()

    for i in th_list:
        i.join()
