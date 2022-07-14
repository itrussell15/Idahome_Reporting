# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 22:45:21 2022

@author: Schmuck
"""

import requests
import datetime

class EnerfloWrapper:
    
    def __init__(self):
        self.BASE_URL = "https://enerflo.io/api/{}"
        self._headers = {"api-key": self._loadToken()}
        self._endpoints = {
                "GET": {
                        "all_customers": "v1/customers"
                    }
            }
        
    def _loadToken(self):
        with open("Secret.txt", "r") as f:
            data = f.readlines()[0]
        return data

    def _getURL(self, endpoint):
        return self.BASE_URL.format(endpoint)
    
    # Put get request with pages here
    def _get(self, url, params):
        r = requests.get(url, params = params, headers = self._headers)
        # Returns json if good
        if r.status_code == 200:
            return r.json()
        # Raises errors with code if bad.
        # else:
            # raise RequestError
    
    # Get customers 
    def getCustomers(self, pageSize = 500):
        
        url = self._getURL(self._endpoints["GET"]["all_customers"])

        # Get the number of data points to collect for next time.
        numLeads = requests.get(url, headers = self._headers).json()["dataCount"]
        
        # Get the number of pages we need to run through to get all the leads
        numPages = numLeads//pageSize
        # If there is the division isn't spot on, then add an extra page
        if numLeads % pageSize != 0:
            numPages += 1
        
        # TODO Start at the end of all the pages and move backwards rather than forward until we get dates that are within our date range that we want.
        for i in range(numPages, 0, -1):
            print("Requesting Page -{}-".format(i))
            params = {"pageSize": pageSize, "page": i}
            page = self._get(url, params)


if __name__ == "__main__":
    wrapper = EnerfloWrapper()
    
    wrapper.getCustomers()