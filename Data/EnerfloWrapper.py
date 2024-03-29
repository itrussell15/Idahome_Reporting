# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 22:45:21 2022

@author: Schmuck
"""

import sys

import requests
import datetime
import pandas as pd
import logging

sys.path.append("..")

from global_functions import resource_path, resource_base

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

    # Get customers
    def getCustomers(self, pageSize = 200, previous_weeks = 6):
        
        url = self._getURL(self._endpoints["GET"]["all_customers"])
        date_cutoff = datetime.date.today() - datetime.timedelta(weeks = 6, days = 1)
        # Print the time period of the date collection

        # Get the number of data points to collect for next time.
        r = self._get(url)
        numLeads = r["dataCount"]
        # Get the number of pages we need to run through to get all the leads
        numPages = numLeads//pageSize
        # If there is the division isn't spot on, then add an extra page
        if numLeads % pageSize != 0:
            numPages += 1
        logging.info("{} pages available at {} leads per page".format(numPages, pageSize))
        
        df = pd.DataFrame()
        print("Requesting Data from Enerflo")
        for i in range(numPages, 0, -1):
            # print("Requesting Page -{}-".format(i))
            params = {"pageSize": pageSize, "page": i}
            page = self._get(url, params, as_json = False)
            remainingReqs = page.headers["X-RateLimit-Remaining"]
            # print("Received Page -{}-, {} Remaining Requests".format(i, remainingReqs))
            pageLeads = self.extractLeadData(page.json()["data"])
            df = pd.concat([df, pageLeads])
            if df["created"].min().to_pydatetime().date() < date_cutoff:
                break
        logging.info("{} requests made".format(self.requestCount))
        logging.info("{} requests remaining after complete".format(remainingReqs))
        df.set_index("custID", inplace = True)
 
        return df.sort_values(by = "created", ascending = False)
            
    def extractLeadData(self, pageData):
        leads = []
        for lead in pageData:
            thisLead = self.Lead(lead)
            leads.append(vars(thisLead))
        df = pd.DataFrame.from_records(leads)
        return df
 
    class Lead:
        
        def __init__(self, leadData):
            self.data = leadData
            
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
            self.owner = "{} {}".format(self.data["owner"]["first_name"], self.data["owner"]["last_name"]) \
                if "owner" in self.data.keys() else None                
            self.setter = "{} {}".format(leadData["setter"]["first_name"], self.data["setter"]["last_name"]) \
                if "setter" in self.data.keys() else None     

            self.nexApptDate = None
            self.nextApptDetail = None

            if leadData["futureAppointments"]:
                appt = leadData["futureAppointments"][list(leadData["futureAppointments"].keys())[0]]
                self.nextApptDate =  datetime.datetime.fromisoformat(self.checkSubkey("start_time_local", appt))
                self.nextApptDetail = self.checkSubkey("name", appt)   
            
        def checkKey(self, key):
            return self._rCheckKey(key, self.data)
        
        def checkSubkey(self, key, data):
            return self._rCheckKey(key, data)
        
        def _rCheckKey(self, key, data):
            if type(key) != list:
                try:
                    if data[key]:
                        return data[key]
                    else:
                        return None
                except:
                    logging.warning("Expected key of {} was not found and corrected to None".format(key))
                    return None
            else:
                subset = self._rCheckKey(key[0], data)
                for i in key[1:]:
                    if i != key[-1]:
                        subset = self._rCheckKey(i, subset)
                    else:
                        break
                try:
                    return subset[i]
                except:
                    return None
            
class Appointment:
    
    def __init__(self, data):
        data = data[list(data.keys())[0]]
        self.title = data["name"]
        self.status = data["status"]
        self.time = datetime.datetime.fromisoformat(data["start_time_local"])
            
if __name__ == "__main__":
    wrapper = EnerfloWrapper()    
    customers = wrapper.getCustomers()