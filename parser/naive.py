import maxima, rimi, selver, prisma, coop

def run():
    METHOD = "naive"
    selver.main(METHOD)
    prisma.main(METHOD)
    maxima.main(METHOD)
    coop.main(METHOD)
    rimi.main(METHOD)
