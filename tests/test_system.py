import unittest

import requests


class TestUser(unittest.TestCase):
    # register with user name that already exist
    def test_Registration(self):
        url = 'https://cureona.herokuapp.com/Registration'
        myobj = {'username': 'tal', 'password': '123', 'type': 'customer'}
        response = requests.post(url, data=myobj)
        self.assertEqual(response.json(), {'state': 'user name already exist'})


if __name__ == '__main__':
    unittest.main()
