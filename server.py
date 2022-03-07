from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import main

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
@cross_origin()
def index():
    return jsonify(main.get_tables("naive_products"))

@app.route("/products")
@cross_origin()
def products():
    return jsonify(main.get_products("naive_products"))

@app.route("/products/<name>/<id>")
@cross_origin()
def product_data(id, name):
    return jsonify(main.get_product_prices("naive_products", id, name))

#@app.route("/prices")
#@cross_origin()
#def prices():
#    return jsonify(main.get_prices(main.conn_naive))

if __name__ == "__main__":
     from waitress import serve
     serve(app, host="127.0.0.1", port="8080")
