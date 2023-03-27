from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from apscheduler.schedulers.background import BackgroundScheduler
import current_products
import main

def parse_products():
    print("Hello parser!")
    # current_products.run()

sched = BackgroundScheduler(daemon=True)
sched.add_job(parse_products,'interval', minutes=1)
sched.start()

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
    try:
        print("get_tables.start")
        data = jsonify(main.get_tables("naive_products"))
        print("get_tables.ok")
        return data
    except Exception as e:
        print("get_tables.error", e)


@app.route("/user", methods=["POST"])
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
    offset_by = request.args.get("page") or 0  # the same as a page
    search_str = request.args.get("s") or ""
    shop_str = request.args.get("shop") or ""
    return jsonify(
        main.get_products(
            "naive_products",
            limit_by,
            offset_by,
            search_str=search_str,
            shop_str=shop_str,
        )
    )


@app.route("/products/<id>")
@cross_origin()
def product_data(id):
    return jsonify(main.get_product_prices(id))


@app.route("/compare")
@cross_origin()
def compare_product():
    product_string = request.args.get("products")
    shop_string = request.args.get("shops", "")

    products = product_string.split(",")
    shops = tuple(shop_string.split(","))

    return jsonify(main.get_compared("naive_products", products, shops))


# CRON JOBS
# @crontab.job(hour="2", minute="0")
# def populate_daily():
#     try:
#         print("crontab.start")
#         current_products.run()
#     except Exception as e:
#         print("crontab.error", e)


# @crontab.job(minute="0", hour="0", day="*", month="*", day_of_week="1")
# def populate_weekly():
#     try:
#         print("crontab.start")
#         naive_parser.run()
#     except Exception as e:
#         print("crontab.error", e)

# @crontab.job(minute="*", hour="*", day="*", month="*", day_of_week="*")
# def test_cron():
#     print("Cron")
