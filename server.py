from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import main
import argparse

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
    return jsonify(main.get_tables("products"), dev=is_dev)

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
    return jsonify(main.get_products("products", limit_by, offset_by, search_str=search_str, shop_str=shop_str, dev=is_dev))


@app.route("/products/<id>")
@cross_origin()
def product_data(id):
    return jsonify(main.get_product_prices("products", id, dev=is_dev))


# @app.route("/prices")
# @cross_origin()
# def prices():
#    return jsonify(main.get_prices(main.conn_naive))

if __name__ == "__main__":
    from waitress import serve

    parser = argparse.ArgumentParser()
    parser.add_argument("-dev", action='store_true')
    args = parser.parse_args()

    is_dev = args.dev

    if is_dev == True:
        host = "0.0.0.0"
        port = "8000"
        print(f"Starting development server on host {host} on port {port}")
    else:
        host = "0.0.0.0"
        port = "8080"
        print(f"Starting production server on host {host} on port {port}")
<<<<<<< Updated upstream

    serve(app, host=host, port=port, threads=16)
=======
    
    serve(app, host=host, port=port, threads=16)
>>>>>>> Stashed changes
