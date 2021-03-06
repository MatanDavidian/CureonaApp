from flask import jsonify
from flask_restful import reqparse, Resource

from server.help_funcs import *
from server.mongo_connection import *
from server.apps_calendar import *
import random
import string
import datetime
import calendar
import pytz

user_queue = testDB["user_queue"]
business_info = testDB["business_info"]
login = testDB["login"]

# ----------------------------------------
timeZone = pytz.timezone('Israel')
# ----------------------------------------
GetQueue_parser = reqparse.RequestParser()
GetQueue_parser.add_argument('username', required=True, help="username name cannot be blank!")
GetQueue_parser.add_argument('BusinessName', required=True, help="business name cannot be blank!")
GetQueue_parser.add_argument('company_id', required=True, help="business name cannot be blank!")
GetQueue_parser.add_argument('Day', required=True, help="Date cannot be blank!")
GetQueue_parser.add_argument('Hour', required=True, help="Date cannot be blank!")

letters = string.ascii_lowercase


def random_string(stringLength=4):
    """Generate a random string of fixed length """
    return ''.join(random.choice(letters) for i in range(stringLength))


def calc_date(Day):
    """calc date from day """
    if Day == "sunday":
        queue_day = 6
    elif Day == "monday":
        queue_day = 0
    elif Day == "tuesday":
        queue_day = 1
    elif Day == "wednesday":
        queue_day = 2
    elif Day == "thursday":
        queue_day = 3
    elif Day == "friday":
        queue_day = 4
    else:
        queue_day = 5
    current_day = datetime.datetime.today().weekday()
    if current_day <= queue_day:
        difference = queue_day - current_day
    else:
        difference = 7 - (current_day - queue_day)

    current_date = datetime.date.today()
    schedule_date = current_date + datetime.timedelta(days=difference)

    return schedule_date.strftime('%d-%m-%Y %H:%M:%S.%f')[:10]


class GetQueue(Resource):

    def post(self):
        data = GetQueue_parser.parse_args()
        print(data)
        business = business_info.find_one({"company_id": data['company_id']})
        print(business)
        # check for legal day name
        if data['Day'] == "sunday" or data['Day'] == "monday" or data['Day'] == "tuesday" or data[
            'Day'] == "wednesday" or data['Day'] == "thursday" or data['Day'] == "friday" or data['Day'] == "saturday":
            schedule_date = calc_date(data['Day'])
        else:
            return jsonify({'state': 'failed, illegal day name'})
        # check for legal business name
        if business is None:
            return jsonify({'state': 'failed, BusinessName is not register'})
        # check if the business is open or closed
        if not business["open"]:
            return jsonify({'state': 'failed, Business is closed'})
        # check if in the given day and hor there are available queue
        print(business["queue"])
        print(business["queue"][data['Day']])
        print(business["queue"][data['Day']][data['Hour']])
        print(len(business["queue"][data['Day']][data['Hour']]))
        print(str(int(len(business["queue"][data['Day']][data['Hour']]))))
        print("num of queue to this hour: " + str(int(len(business["queue"][data['Day']][data['Hour']]))))
        print("max capacity: " + str(business["max_capacity"]))
        if len(business["queue"][data['Day']][data['Hour']]) >= int(business["max_capacity"]):
            return jsonify({'state': 'failed, sorry the queue is full'})
        queue_key = random_string(4)
        print(queue_key)
        json_doc = user_queue.find_one({"username": data['username']})
        # add queue to customer
        if json_doc:
            # check if the customer already have a queue to this day and hour to this business
            prev_orders = json_doc["orders"]
            for i in prev_orders:
                if data['BusinessName'] == i[0] and schedule_date == i[1] and data['Hour'] == i[2]:
                    return jsonify({'state': 'failed, sorry you can not get two queue to the same hour'})
            order = [data['BusinessName'], schedule_date, data['Hour'], queue_key, business["address"]]
            print(order)
            user_queue.update({'username': data['username']}, {"$push": {'orders': order}})
            business_info.update({'business_name': data['BusinessName']},
                                 {"$push": {"queue." + data['Day'] + "." + data['Hour']: queue_key}})
            return jsonify({'state': 'success', 'key': queue_key})
        # make the first queue
        # check if user exist
        json_doc = login.find_one({"username": data['username']})
        if not json_doc:
            return jsonify({'state': 'User does not exist'})
        # create the first order
        orders = [[data['BusinessName'], schedule_date, data['Hour'], queue_key]]
        # print(orders)
        userQueue = {"username": data['username'], "orders": orders}
        # print(userQueue)
        user_queue.insert_one(userQueue)
        business_info.update({'business_name': data['BusinessName']},
                             {"$push": {"queue." + data['Day'] + "." + data['Hour']: queue_key}})
        return jsonify({'state': 'success', 'key': queue_key})


AvailableQueues_parser = reqparse.RequestParser()
AvailableQueues_parser.add_argument('company_id', required=True, help="company_id name cannot be blank!")


class AvailableQueues(Resource):

    def post(self):
        def available_hours(day):
            available_queues = list()
            # print("DAY =============", day)
            for hour in list_queue[day]:
                # print(hour)

                if max_capacity - len(list_queue[day][hour]) > 0:
                    available_queues.append(hour)
            return available_queues

        def available_hours_at_day(day):
            available_queues = list()
            if isinstance(list_queue[day], str):
                available_queues = list()
            else:
                available_queues = available_hours(day)
            return available_queues

        data = AvailableQueues_parser.parse_args()
        json_doc = business_info.find_one({"company_id": data['company_id']})
        if not json_doc:
            return jsonify({'state': 'failed, company_id is not exist'})
        if not json_doc["open"]:
            return jsonify({'state': 'success', 'queue': {'sunday': [], 'monday': [], 'tuesday': [], 'wednesday': [],
                                                          'thursday': [], 'friday': [], 'saturday': []}})

        max_capacity = int(json_doc["max_capacity"])
        queue = json_doc["queue"]
        print(queue)
        list_queue = []
        list_queue.append(queue["sunday"])
        list_queue.append(queue["monday"])

        list_queue.append(queue["tuesday"])
        list_queue.append(queue["wednesday"])
        list_queue.append(queue["thursday"])
        list_queue.append(queue["friday"])
        list_queue.append(queue["saturday"])
        # for key, value in queue.items():
        #     print(key)
        #     list_queue.append(value)
        print(list_queue)
        available_queues_sunday = available_hours_at_day(0)
        print("available_queues_sunday", available_queues_sunday)
        available_queues_monday = available_hours_at_day(1)
        print("available_queues_monday", available_queues_monday)
        available_queues_tuesday = available_hours_at_day(2)
        print("available_queues_tuesday", available_queues_tuesday)
        available_queues_wednesday = available_hours_at_day(3)
        print("available_queues_wednesday", available_queues_wednesday)
        available_queues_thursday = available_hours_at_day(4)
        print("available_queues_thursday", available_queues_thursday)
        available_queues_friday = available_hours_at_day(5)
        print("available_queues_friday", available_queues_friday)
        available_queues_saturday = available_hours_at_day(6)
        print("available_queues_saturday", available_queues_saturday)

        open_and_available_queues = {'sunday': available_queues_sunday,
                                     'monday': available_queues_monday,
                                     'tuesday': available_queues_tuesday,
                                     'wednesday': available_queues_wednesday,
                                     'thursday': available_queues_thursday,
                                     'friday': available_queues_friday,
                                     'saturday': available_queues_saturday}
        print(open_and_available_queues)
        return jsonify({'state': 'success', 'queue': open_and_available_queues})


AvailableQueues_parser = reqparse.RequestParser()
AvailableQueues_parser.add_argument('company_id', required=True, help="company_id name cannot be blank!")

deleteAppointment_parser = reqparse.RequestParser()
deleteAppointment_parser.add_argument('business_name', required=True, help="business_name name cannot be blank!")
deleteAppointment_parser.add_argument('username', required=True, help="username cannot be blank!")
deleteAppointment_parser.add_argument('code', required=True, help="CODE cannot be blank!")
deleteAppointment_parser.add_argument('date', required=True, help=" DD MM YYYY")
deleteAppointment_parser.add_argument('time', required=True, help="HH:MM-HH:MM")


# this class will delete an appointment
class deleteAppointment(Resource):

    def post(self, ):
        data = deleteAppointment_parser.parse_args()
        print(data)
        date = data['date']  # in a format of DD-MM-YYYY
        day = convert_date_string_to_day(date)
        username = data['username']
        time_of_appointment = data['time']
        code = data['code']
        business_name = data['business_name']
        user_queue_record = user_queue.find_one({"username": username})
        business_name_record = business_info.find_one({"business_name": business_name})

        ret_val = {}
        if user_queue_record and business_name_record:  # if both of the records were found
            for appointment in user_queue_record['orders']:
                if code in appointment:
                    deleted_from_array = user_queue.update({'username': username},
                                                           {'$pull': {"orders": appointment}})
                    ret_val["deleted_from_user_queue"] = 'success' if deleted_from_array['nModified'] else 'fail'

            for time_range in business_name_record['queue'][day]:
                if time_of_appointment == time_range and code in business_name_record['queue'][day][time_range]:
                    deleted_from_array = business_info.update({'business_name': business_name},
                                                              {'$pull': {"queue." + day + "." + time_range: code}})
                    ret_val["deleted_from_business_queue"] = 'success' if deleted_from_array['nModified'] else 'fail'

        if not ret_val:
            ret_val['state'] = "failed"
            ret_val['msg'] = "couldn't locate the appointment!"

        else:
            if "deleted_from_business_queue" in ret_val and "deleted_from_user_queue" in ret_val:
                if ret_val["deleted_from_business_queue"] == "success" and ret_val[
                    "deleted_from_user_queue"] == "success":
                    ret_val[
                        'msg'] = 'the appointment to ' + business_name + " at " + day + " : " + time_of_appointment + \
                                 " successfully canceled "
                    ret_val['state'] = "success"
            else:
                ret_val['msg'] = "operation not fully succeeded "
                ret_val['state'] = "failed"

            ### for the next sprint use this code:
            # for interval in time_range:
            #   deleted_from_array = business_info.update({'business_name': business_name},
            #                           {'$pull': {"queue." + day + "." + time_range: code}})
            #    calculate how many iterations need to do and then

        return jsonify(ret_val)


insert_parser = reqparse.RequestParser()
insert_parser.add_argument('company_id', required=True, help="company_id name cannot be blank!")
insert_parser.add_argument('key', required=True, help="key cannot be blank!")


class LetsUserIntoBusiness(Resource):
    def post(self):
        data = insert_parser.parse_args()

        tz_NY = pytz.timezone('Israel')

        business = business_info.find_one({"company_id": data['company_id']})
        print(business)
        current_date = datetime.date.today()
        print(current_date)
        current_day = datetime.datetime.today().weekday()
        print(current_day)
        name_current_day = calendar.day_name[current_day].lower()
        print(name_current_day)
        now = datetime.datetime.now(tz_NY)

        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")[11:16]
        print(dt_string)
        print(dt_string[3:])
        print("min interval: " + str(business["minutes_intervals"]))
        if business["minutes_intervals"] == "10":
            if int(dt_string[3:]) >= 50:
                dt_string = dt_string[:3] + "50"
            elif int(dt_string[3:]) >= 40:
                dt_string = dt_string[:3] + "40"
            elif int(dt_string[3:]) >= 30:
                dt_string = dt_string[:3] + "30"
            elif int(dt_string[3:]) >= 20:
                dt_string = dt_string[:3] + "20"
            elif int(dt_string[3:]) >= 10:
                dt_string = dt_string[:3] + "10"
            else:
                dt_string = dt_string[:3] + "00"
        elif business["minutes_intervals"] == "30":
            if int(dt_string[3:]) >= 30:
                dt_string = dt_string[:3] + "30"
            else:
                dt_string = dt_string[:3] + "00"

        elif business["minutes_intervals"] == "60":
            dt_string = dt_string[:3] + "00"
        else:
            if int(dt_string[3:]) >= 45:
                dt_string = dt_string[:3] + "45"
            elif int(dt_string[3:]) >= 30:
                dt_string = dt_string[:3] + "30"
            elif int(dt_string[3:]) >= 15:
                dt_string = dt_string[:3] + "15"
            else:
                dt_string = dt_string[:3] + "00"
        print(dt_string)
        print("all queue for current_day")
        print(business["queue"][name_current_day])
        code_arr = business["queue"][name_current_day][dt_string]

        if data["key"] in code_arr:
            increase_amount_in_business(business["company_id"])
            return jsonify({'state': 'success'})
        return jsonify({'state': 'failed'})


current_amount_at_business = reqparse.RequestParser()
current_amount_at_business.add_argument('company_id', required=True, help="company_id name cannot be blank!")


class currentAmountAtBusiness(Resource):

    def post(self):
        data = current_amount_at_business.parse_args()
        business = get_business_data(data['company_id'])
        timeZone = pytz.timezone('Israel')
        current_time = get_time_and_day_for_now(
            timeZone)  # current_time is an array that built like so: current_time[0]=day name, current_time[1]=hour
        convert_time_to_str(current_time, business['minutes_intervals'], business['open_hours'][current_time[0]])
        amount = check_if_hour_exists(business, current_time)
        if 'error' in amount:
            return jsonify({'state': 'fail', "current_amount_in_business": amount})
        print(current_time)

        return jsonify({'state': 'success', "current_amount_in_business": amount,
                        'max_capacity': business['max_capacity']})


spontaneous_appointment = reqparse.RequestParser()
spontaneous_appointment.add_argument('company_id', required=True, help="company_id name cannot be blank!")
spontaneous_appointment.add_argument('cellphone', required=True, help="cellphone number cannot be blank!")


class generateCodeForSpontaneousAppointment(Resource):

    def post(self):
        data = spontaneous_appointment.parse_args()
        try:
            business = get_business_data(data['company_id'])
            validate_data(data['cellphone'])
        except Exception as err:
            return jsonify({'state': 'fail', 'reason': str(err)})

        current_time = get_time_and_day_for_now(timeZone)
        convert_time_to_str(current_time, business['minutes_intervals'], business['open_hours'][current_time[0]])
        print(business['business_name'])
        print("queue." + current_time[0] + "." + current_time[1] + data['cellphone'])
        # example: current_time[0]=day name, current_time[1]=hour
        query_result = business_info.update({'company_id': business['company_id']},
                                            {"$push": {
                                                "queue." + current_time[0] + "." + current_time[1]: data['cellphone']}})
        no_error = True if query_result['nModified'] != 0 else False
        if no_error:
            increase_amount_in_business(business['company_id'])
        return jsonify({"state": 'success' if no_error else 'fail',
                        'costumer_entered': data['cellphone'] if no_error else 'unknown error'})


get_out_parser = reqparse.RequestParser()
get_out_parser.add_argument('company_id', required=True, help="company_id name cannot be blank!")
get_out_parser.add_argument('key', required=True, help="key cannot be blank!")


class LetsUserOutBusiness(Resource):
    def post(self):
        data = get_out_parser.parse_args()
        tz_NY = pytz.timezone('Israel')
        business = business_info.find_one({"company_id": data['company_id']})
        current_date = datetime.date.today()
        print(current_date)
        current_day = datetime.datetime.today().weekday()
        print(current_day)
        name_current_day = calendar.day_name[current_day].lower()
        print(name_current_day)
        print("codes")
        code_arr = business["queue"][name_current_day]

        print(code_arr)
        flag = 0
        for time_range in business['queue'][name_current_day]:
            if data["key"] in code_arr[time_range]:
                flag = 1
            business_info.update({'company_id': data['company_id']},
                                 {'$pull': {"queue." + name_current_day + "." + time_range: data["key"]}})
        """
        for q in code_arr:
            if data["key"] in q:
                q.remove(data["key"])
                print(q)
        """
        business = business_info.find_one({"company_id": data['company_id']})
        code_arr = business["queue"][name_current_day]
        print(code_arr)
        if flag == 1:
            decrease_amount_in_business(business['company_id'])
            return jsonify({'state': 'success', 'msg': 'the code exist'})
        else:
            return jsonify({'state': 'failed', 'msg': 'the code is not exist'})


get_amount_day_hour = reqparse.RequestParser()
get_amount_day_hour.add_argument('company_id', required=True, help="company_id name cannot be blank!")
get_amount_day_hour.add_argument('day', required=True, help="day cannot be blank!")
get_amount_day_hour.add_argument('hour', required=True, help="hour cannot be blank!")


class getAmountOfCostumersForDayAndHour(Resource):

    def post(self):
        data = get_amount_day_hour.parse_args()
        business = get_business_data(data['company_id'])
        time_to_check = [data['day'], data['hour']]
        amount = check_if_hour_exists(business, time_to_check)
        return jsonify({"state": 'success' if not 'error' in amount else 'fail', 'amount': amount})


get_precise_amount = reqparse.RequestParser()
get_precise_amount.add_argument('company_id', required=True, help="company_id name cannot be blank!")


class getPreciseAmountOfCostumers(Resource):

    def post(self):
        data = get_precise_amount.parse_args()
        try:
            business = get_business_data(data['company_id'])
        except Exception as e:
            return jsonify({"state": "fail", "error": str(e)})

        return jsonify({"state": 'success', 'current_amount_in_business ': str(business['current_amount']),
                        'max_capacity': str(business['max_capacity'])})
