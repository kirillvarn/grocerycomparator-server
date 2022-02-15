import maxima, rimi, selver, prisma, coop
from threading import Thread
from datetime import datetime

import psycopg2
from credentials import user_data
DATE = datetime.today().strftime("%Y-%m-%d")


METHOD = "none"
selver.main(METHOD)
prisma.main(METHOD)
maxima.main(METHOD)
coop.main(METHOD)
rimi.main(METHOD)
