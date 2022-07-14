# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 22:45:21 2022

@author: Schmuck
"""

import requests
import datetime
import pandas as pd

class EnerfloWrapper:
    
    def __init__(self):
        self.BASE_URL = "https://enerflo.io/api/{}"
        self._headers = {"api-key": self._loadToken()}
        self._endpoints = {
                "GET": {
                        "all_customers": "v1/customers"
                    }
            }
        self.requestCount = 0
        
    def _loadToken(self):
        with open("Secret.txt", "r") as f:
            data = f.readlines()[0]
        return data

    def _getURL(self, endpoint):
        return self.BASE_URL.format(endpoint)
    
    # Put get request with pages here
    def _get(self, url, params = None, as_json = True):
        try:
            r = requests.get(url, params = params, headers = self._headers)
            self.requestCount += 1
            r.raise_for_status()
            
        except requests.exceptions.HTTPError as err:
            raise requests.exceptions.HTTPError(err)
        except Exception as err:
            raise err
        
        if as_json:
            return r.json()
        else:
            return r

    
    # Get customers 
    def getCustomers(self, pageSize = 400):
        
        url = self._getURL(self._endpoints["GET"]["all_customers"])

        # Get the number of data points to collect for next time.
        # numLeads = requests.get(url, headers = self._headers).json()["dataCount"]
        r = self._get(url)
        numLeads = r["dataCount"]
        # Get the number of pages we need to run through to get all the leads
        numPages = numLeads//pageSize
        # If there is the division isn't spot on, then add an extra page
        if numLeads % pageSize != 0:
            numPages += 1
        
        # print(numPages)
        # TODO Start at the end of all the pages and move backwards rather than forward until we get dates that are within our date range that we want.
        for i in range(numPages, 0, -1):
            print("Requesting Page -{}-".format(i))
            params = {"pageSize": pageSize, "page": i}
            page = self._get(url, params, as_json = False)
            remainingReqs = page.headers["X-RateLimit-Remaining"]
            print("Received Page -{}-, {} Remaining Requests".format(i, remainingReqs))
            # Info needed Name, Lead Source, Lead Status, Setter, Lead Owner, Next Appointment, Added
            pageLeads = self.extractLeadData(page.json()["data"])
            
    def extractLeadData(self, pageData):
        # df = pd.DataFrame()
        data = []
        for lead in pageData:
            leadData = {
                "name": f"""{lead["first_name"]} {lead["last_name"]}""",
                "email": lead["email"],
                "phone": lead["mobile"],
                "address": f"""{lead["address"]} {lead["city"]}, {lead["state"]} {lead["zip"]}"""
                        }
            print(leadData)
if __name__ == "__main__":
    wrapper = EnerfloWrapper()
    
    wrapper.getCustomers()