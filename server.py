from flask import Flask, jsonify
import main

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify(main.order_products_by_name(main.conn_naive))

@app.route("/prices")
def prices():
    return jsonify(main.get_prices(main.conn_naive))

@app.route("/prices/<date>")
def date(date):
    return jsonify(main.get_date_data(main.conn_naive, date))

if __name__ == "__main__":
    app.run(debug=False)