from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import main

app = Flask(__name__)
cors = CORS(app)

app.config["CORS_HEADERS"] = "Content-Type"


@app.route("/")
@cross_origin()
def index():
    return jsonify(main.get_tables("products"))


@app.route("/products")
@cross_origin()
def products():
    limit_by = request.args.get("limit") or 64
    offset_by = request.args.get("page") or 0 # the same as a page
    return jsonify(main.get_products("products", limit_by, offset_by))


@app.route("/products/<id>")
@cross_origin()
def product_data(id):
    return jsonify(main.get_product_prices("products", id))


# @app.route("/prices")
# @cross_origin()
# def prices():
#    return jsonify(main.get_prices(main.conn_naive))

if __name__ == "__main__":
    from waitress import serve

    serve(app, host="127.0.0.1", port="8080", threads=16)
