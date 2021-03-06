import unittest
import requests


class TestUserUpdateSettings(unittest.TestCase):

    def test_get_two_queue_to_same_place_at_same_time(self):
        url = 'https://curona.herokuapp.com/businessSettings'
        myobj = {'company_id': '123', 'open': 'True'}
        requests.post(url, data=myobj)
        url = 'https://curona.herokuapp.com/GetQueue'
        myobj = {"username": "c_test", 'company_id': '123', "BusinessName": "IKEA", "Day": "tuesday", "Hour": "17:30"}
        requests.post(url, data=myobj)
        response = requests.post(url, data=myobj)
        except_result = {"state": "failed, sorry you can not get two queue to the same hour"}
        self.assertEqual(response.json(), except_result)

    def test_get_queue_to_closed_business(self):
        url = 'https://curona.herokuapp.com/businessSettings'
        myobj = {'company_id': '123', 'open': 'False'}
        requests.post(url, data=myobj)
        url = 'https://curona.herokuapp.com/GetQueue'
        myobj = {"username": "c_test", 'company_id': '123', "BusinessName": "IKEA", "Day": "wednesday",
                 "Hour": "15:00"}
        response = requests.post(url, data=myobj)
        except_result = {"state": "failed, Business is closed"}
        myobj = {'company_id': '123', 'open': 'True'}
        requests.post(url, data=myobj)
        self.assertEqual(response.json(), except_result)

    def test_get_my_queue(self):
        url = 'https://curona.herokuapp.com/GetMyQueue'
        myobj = {"username": "IsNotExist"}
        response = requests.post(url, data=myobj)
        except_result = list()
        self.assertNotEqual(response, except_result)

    def test_lets_user_into_business_with_not_exist_code(self):
        url = 'https://curona.herokuapp.com/LetsUserIntoBusiness'
        myobj = {"company_id": "123", "key": "1234"}
        response = requests.post(url, data=myobj)
        except_result = {'state': 'failed'}
        self.assertNotEqual(except_result, response)

    def test_lets_user_into_business_with_not_exist_code(self):
        url = 'https://curona.herokuapp.com/deleteAppointment'
        myobj = {"business_name": "notRealBusiness", "username": "notRealUser", "code": "NotRealCode",
                 "date": "05-05-2020", "time": "22:00-23:00"}
        response = requests.post(url, data=myobj)
        except_result = {"state": "couldn't locate the appointment!"}
        self.assertNotEqual(except_result, response)

    def test_lets_user_get_out_business_with_not_exist_code(self):
        url = 'https://curona.herokuapp.com/LetsUserOutBusiness'
        myobj = {"company_id": "123", "key": "NotRealCode"}
        response = requests.post(url, data=myobj)
        except_result = {'state': 'success', 'msg': 'the code is not exist'}
        self.assertNotEqual(except_result, response)

    def test_current_amount_is_zero(self):
        url = 'https://curona.herokuapp.com/AmountForDayAndHour'
        myobj = {"company_id": "101010"}
        response = requests.post(url, data=myobj)
        except_result = {"current_amount_in_business": "0", "max_capacity": 10, "state": "success"}
        self.assertNotEqual(except_result, response)

    def test_current_amount_in_store(self):
        url = 'https://curona.herokuapp.com/PreciseAmount'
        myobj = {"company_id": "44445555"}
        response = requests.post(url, data=myobj)
        except_result = {
                      "current amount of costumers in the business ": 0,
                      "state": "success"
                    }
        self.assertNotEqual(except_result, response)


if __name__ == '__main__':
    unittest.main()
