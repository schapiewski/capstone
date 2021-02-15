import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase, LiveServerTestCase
from capstone.views import logoutUser, dashboard, loginPage, register, show_stock_graph
from django.urls import reverse
from django.http import HttpRequest
import time

# TO RUN TESTS: Go to local path (indicated by: ..)  ../capstone/capstoneproj/capstone
# then run cmd in terminal: manage.py test tests
# All future tests must have naming scheme of: "test_[INSERT-TEST-NAME]" for test to be recognized and ran
class TestViews(StaticLiveServerTestCase):

    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")
        self.request = HttpRequest()
        self.request.session = '34324324'
        self.browser = webdriver.Chrome('tests/chromedriver.exe')
        pass

    def test_error_handling(self):
        print("Method: test_error_handling - Error Handling of Stock Information")
        # Take live server url 'http://127.0.0.1:8000/' and
        # add show_graph to test 'http://127.0.0.1:8000/show_graph/' page
        current_url = self.live_server_url + reverse('show_graph')
        self.browser.get(current_url)
        # Give time for browser to open up
        time.sleep(2)
        # Find field input for searching a stock
        inputElement = self.browser.find_element_by_id("stock-search")
        # Simulate 'this wont work' search for stock
        inputElement.send_keys('This wont work')
        # Find search stock button
        stock_search_btn = self.browser.find_element_by_id("stock-search-btn")
        # Simulate search stock button click
        stock_search_btn.click()
        # Give time for api call to be received
        time.sleep(5)
        # Find alert for error
        alert = self.browser.find_element_by_id("errorMessage")
        # Test alert against the expected error message
        self.assertEqual(
            alert.text,
            'Error: Oops! Looks like you entered an incorrect stock. hint: Ticker symbols are between 3-5 characters long!'
        )

    def test_api_call(self):
        print("Method: test_api_call - Testing API Call to get Stock Information")
        # Take live server url 'http://127.0.0.1:8000/' and
        # add show_graph to test 'http://127.0.0.1:8000/show_graph/' page
        current_url = self.live_server_url + reverse('show_graph')
        self.browser.get(current_url)
        # Give time for browser to open up
        time.sleep(2)
        # Find field input for searching a stock
        inputElement = self.browser.find_element_by_id("stock-search")
        # Simulate 'PLTR' search for stock
        inputElement.send_keys('PLTR')
        # Find search stock button
        stock_search_btn = self.browser.find_element_by_id("stock-search-btn")
        # Simulate search stock button click
        stock_search_btn.click()
        # Give time for api call to be received
        time.sleep(5)
        # Make sure api call was received correctly
        title = self.browser.find_element_by_class_name("display-2")
        # Checks title to match the expected title
        self.assertEqual(
            title.text,
            'Palantir Technologies Inc'
        )