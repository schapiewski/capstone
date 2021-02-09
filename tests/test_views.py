import unittest
from capstone.views import logoutUser, dashboard, loginPage, register
from django.http import HttpRequest
from django.shortcuts import render


class TestViews(unittest.TestCase):
    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")
        pass

    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")
        self.request = HttpRequest()
        self.request.session = '34324324'
        pass

    def test_logout(self):
        print("Method: test_logout.")
        test = logoutUser(self.request)
        self.assertEqual(test, 'login')

    def test_dashboard(self):
        print("Method: test_dashboard.")
        test = dashboard(self.request)
        self.assertEqual(test, render(self.request, 'dashboard.html', {}))

    def test_loginPage(self):
        print("Method: test_loginPage.")
        test = loginPage(self.request)
        self.assertEqual(test, render(self.request, 'login.html', {}))

    def test_register(self):
        print("Method: test_register.")
        test = register(self.request)
        self.assertEqual(test, render(self.request, 'register.html', {}))


if __name__ == '__main__':
    unittest.main()