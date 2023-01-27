import naive, products

from datetime import date, datetime
import db

DAY = date.today().timetuple().tm_yday
DAY = int(DAY)

th_list = []
#th_list.append(Thread(target=selver.current_products))
#th_list.append(Thread(target=rimi.current_products))
#th_list.append(Thread(target=prisma.current_products))
#th_list.append(Thread(target=maxima.current_products))
#th_list.append(Thread(target=coop.current_products))
#
#for i in th_list:
#    i.start()
#
#for i in th_list:
#    i.join()

def clear_db():
    conn = db.connect()
    cursor = conn.cursor()

    DATE = datetime.today().strftime("%Y-%m-%d")
    q = 'DROP TABLE IF EXISTS "%s";'
    q_2 = 'DELETE FROM public.updatedates WHERE u_name = %s'

    cursor.execute(q, (DATE, ))
    cursor.execute(q_2, (DATE, ))
    conn.commit()
    cursor.close()
    conn.close()

clear_db()
naive.run()
products.run()
