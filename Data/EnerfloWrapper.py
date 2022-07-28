# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 22:45:21 2022

@author: Schmuck
"""

import sys

import requests, json
import datetime
import pandas as pd
import logging
from types import SimpleNamespace

from global_functions import resource_path, resource_base

class EnerfloWrapper:
    
    def __init__(self, perPageRequest = 200):
        self.BASE_URL = "https://enerflo.io/api/{}"
        self._headers = {"api-key": self._loadToken()}
        self._endpoints = {
                "GET": {
                        "all_customers": "v1/customers",
                        "installs": "v3/installs"
                    }
            }
        self.requestCount = 0
        self.perPage = perPageRequest
        
    def _loadToken(self):
        with open(resource_path("Data/Secret.txt"), "r") as f:
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
            logging.error(err)
            raise requests.exceptions.HTTPError(err)
        except Exception as err:
            logging.error(err)
            raise err
        
        if as_json:
            return r.json()
        else:
            return r

    # TODO Migrate this data collection to a generic function that gathers page data
    def getCustomers(self, previous_weeks = 6):
        
        self._gatherAllPageData(self._endpoints["GET"]["all_customers"],
                                self.Lead,
                                previous_weeks)
        
        # url = self._getURL(self._endpoints["GET"]["all_customers"])

        # # Get the number of data points to collect for next time.
        # r = self._get(url)
        
        # date_cutoff = datetime.date.today() - datetime.timedelta(weeks = previous_weeks, days = 1)
        # numLeads = r["dataCount"]
        # # Get the number of pages we need to run through to get all the leads
        # numPages = numLeads//pageSize
        # # If the division isn't spot on, then add an extra page
        # if numLeads % pageSize != 0:
        #     numPages += 1
        # logging.info("{} pages available at {} leads per page".format(numPages, pageSize))
        
        # df = pd.DataFrame()
        # print("Requesting Data from Enerflo")
        # for i in range(numPages, 0, -1):
        #     # print("Requesting Page -{}-".format(i))
        #     params = {"pageSize": pageSize, "page": i}
        #     page = self._get(url, params, as_json = False)
        #     remainingReqs = page.headers["X-RateLimit-Remaining"]
        #     # print("Received Page -{}-, {} Remaining Requests".format(i, remainingReqs))
        #     pageLeads = self._extractLeadData(page.json()["data"])
        #     df = pd.concat([df, pageLeads])
        #     if df["created"].min().to_pydatetime().date() < date_cutoff:
        #         break
        # logging.info("{} requests made".format(self.requestCount))
        # logging.info("{} requests remaining after complete".format(remainingReqs))
        # df.set_index("custID", inplace = True)
 
        # return df.sort_values(by = "created", ascending = False)
            
    
    def getInstalls(self):
        return self._gatherAllPageData(self._endpoints["GET"]["installs"],
                                       self.Install,
                                       1)
    
    def _gatherAllPageData(self, url, extractionObject, previous_weeks):
        this_url = self._getURL(url)
        r = self._get(this_url)
        date_cutoff = datetime.date.today() - datetime.timedelta(weeks = previous_weeks, days = 1)
        
        # Different queries have seen different key name. This will be the first key value in the response.
        r_keys = list(r.keys())
        numLeads = r[r_keys[0]]
        numPages = numLeads//self.perPage
        
        # Adds another page if there is any leftover data in the last page
        if numLeads % self.perPage != 0:
            numPages += 1
        logging.info("{pages} pages available on {query} query @ {perPage} pages per lead".format(pages = numPages, query = url, perPage = self.perPage))
        
        df = pd.DataFrame()
        for i in range(numPages, 0, -1):
            print("Requesting page {}".format(i))
            params = {"pageSize": self.perPage, "page": i}
            page = self._get(this_url, params, as_json = False)
            rRemaining = page.headers["X-RateLimit-Remaining"]
            data = page.json()[r_keys[1]]
            pageLeads = self._extractData(data, extractionObject)
            print(pageLeads)            
            df = pd.concat([df, pageLeads])

# %% Extraction Functions
    def _extractData(self, pageData, object_type):
        data = []
        for lead in pageData:
            thisData = object_type(lead)
            data.append(vars(thisData))
        df = pd.DataFrame.from_records(data)
        return df

    class Extraction:
        def __init__(self, data):
            self.data = data
        
        def checkKey(self, key):
            if self.data[key]:
                return self.data[key]
            else:
                return None
        
        def checkSubkey(self, key, subset):
            if self.data[subset]:
                subset = self.data[subset]
                print(subset)
                if subset[key]:
                    return subset[key]
                else:
                    return None
            else:
                return None

    class Lead(Extraction):
        
        def __init__(self, leadData):
            super().__init__(leadData)
            
            self.custID = self.checkKey("id")
            self.name = self.checkKey("fullName")
            self.email = self.checkKey("email")
            self.lead_source = self.checkKey("lead_source")
            self.lead_status = self.checkKey("status_name")
            self.notes = self.checkKey("customer_notes")
            self.created = datetime.datetime.fromisoformat(self.checkKey("created"))
            self.portal = self.checkKey("customer_portal_url")
            self.latLong = (self.checkKey("lat"), self.checkKey("lng"))
            
            self.address = f"""{leadData["address"]} {leadData["city"]}, {leadData["state"]} {leadData["zip"]}"""
            self.owner = "{} {}".format(leadData["owner"]["first_name"], leadData["owner"]["last_name"]) \
                if "owner" in leadData.keys() else None                
            self.setter = "{} {}".format(leadData["setter"]["first_name"], leadData["setter"]["last_name"]) \
                if "setter" in leadData.keys() else None     

            self.nexApptDate = None
            self.nextApptDetail = None
            
            # TODO Fix this to grab appointment ID
            if self.checkKey("futureAppointments"):
                self.nextApptDate =  datetime.datetime.fromisoformat(self.checkSubkey("start_time_local", "futureAppointments"))
                self.nextApptDetail = self.checkSubkey("name", "futureAppointments")   
            
    class Install(Extraction):
        
        def __init__(self, installData):
            super().__init__(installData)
            
            self.id = self.checkKey("id")
            self.created = datetime.datetime.fromisoformat(self.checkKey("created_at"))
            self.status = self.checkKey("status_name")
            self.system_size = self.checkKey("system_size")
            
            # customerData = checkKey("customer")
            # closerData = checkKey("agent_user")
            
            # if customerData:
            #     self.customer = checkKey("name", customerData)
            #     self.lead_source = checkKey("lead_source", customerData)
            #     self.latLong = (checkKey("lat", customerData), checkKey("lng", customerData))
                
            # self.closer = checkKey("name", closerData) if closerData else None
                
    

                    
    # class Appointment:
        
    #     def __init__(self, data):
    #         data = data[list(data.keys())[0]]
    #         self.title = data["name"]
    #         self.status = data["status"]
    #         self.time = datetime.datetime.fromisoformat(data["start_time_local"])
            
if __name__ == "__main__":
    wrapper = EnerfloWrapper()    
    customers = wrapper.getCustomers()
    # installs = wrapper.getInstalls()
    # print(installs.head())
    