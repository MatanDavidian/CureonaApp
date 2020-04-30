from flask import jsonify
from flask_restful import reqparse, Resource
from server.help_funcs import *
import datetime
from datetime import datetime

my_queue = new_db["user_queue"]

GetMyQueue_parser = reqparse.RequestParser()
GetMyQueue_parser.add_argument('username', required=True, help="username name cannot be blank!")


class GetMyQueue(Resource):

    def post(self):
        data = GetMyQueue_parser.parse_args()
        print(data)
        orders = my_queue.find_one({"username": data["username"]})["orders"]
        if not orders:
            empty = list()
            return jsonify(empty)

        future_queue = list()
        current_date = datetime.date.today()

        for order in orders:
            order_date = datetime.strptime(order[1], '%d-/%m-/%y')
            if order_date > current_date:
                future_queue.append(order)

        return jsonify(future_queue)
