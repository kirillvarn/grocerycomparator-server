from flask import Flask, jsonify
import main

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify(main.order_products_by_name(main.conn_naive))

@app.route("/prices")
def prices():
    return jsonify(main.get_prices(main.conn_naive))

if __name__ == "__main__":
    app.run(debug=False)