from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import main
from credentials import api_key

app = Flask(__name__)
cors = CORS(app)

app.config["CORS_HEADERS"] = "Content-Type"


@app.route("/")
@cross_origin()
def main_page():
    return "<h1>Hello!</h1>"

@app.route("/dates")
@cross_origin()
def index():
    return jsonify(main.get_tables("products"))


@app.route("/parse", methods=['POST'])
@cross_origin()
def start_parsing():
    auth = request.headers['Authentication']
    if auth == api_key:
        response = main.start_parsing()
    else:
        response = {"response": {"status": "error", "message": "You have no access to this!"}}

    return jsonify(response)


@app.route("/user", methods=['POST'])
@cross_origin()
def user():
    json = request.get_json()
    can_login = main.login(json)
    if can_login == True:
        response = {"response": {"status": "ok"}}
    else:
        response = {"response": {"status": "error", "message": can_login}}
    return jsonify(response)

@app.route("/products")
@cross_origin()
def products():
    limit_by = request.args.get("limit") or 64
    offset_by = request.args.get("page") or 0 # the same as a page
    search_str = request.args.get("s") or ""
    shop_str = request.args.get("shop") or ""
    return jsonify(main.get_products("products", limit_by, offset_by, search_str=search_str, shop_str=shop_str))


@app.route("/products/<id>")
@cross_origin()
def product_data(id):
    return jsonify(main.get_product_prices("products", id))


# @app.route("/prices")
# @cross_origin()
# def prices():
#    return jsonify(main.get_prices(main.conn_naive))

if __name__ == "__main__":
    #from waitress import serve
    app.run()
    #serve(app, host="0.0.0.0", port="8080", threads=32, url_scheme='https')
