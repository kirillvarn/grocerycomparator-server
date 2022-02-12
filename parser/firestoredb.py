import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

from datetime import datetime
    
DATE = datetime.today().strftime("%Y-%m-%d")

def updateDates(shop_name):
    pass

def populate(products, shop):
    for product in products:
        try:
            name = product['name'].replace('/', ' ')
        except:
            name = product['name']

        data = {
            'price': product['price'],
            'shop': shop,
            'discount' : product['discount']
        }
        db.collection(DATE).document(name).set(data)

def compareProducts(products, dates, shop):
    pass

def handleDB(products, shop):
    populate(products, shop)