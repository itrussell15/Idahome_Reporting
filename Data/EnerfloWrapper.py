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

    def getCustomers(self, previous_weeks = 6):
        all_data = self._gatherAllPageData(self._endpoints["GET"]["all_customers"],
                                self.Lead,
                                previous_weeks)
        return all_data
    
    def getInstalls(self, previous_weeks = 1):
        all_data = self._gatherAllPageData(self._endpoints["GET"]["installs"],
                                       self.Install,
                                       previous_weeks)
        return all_data
    
    def _gatherAllPageData(self, url, extractionObject, previous_weeks):
        this_url = self._getURL(url)
        r = self._get(this_url)
        date_cutoff = datetime.date.today() - datetime.timedelta(weeks = previous_weeks, days = 1)
        datetime_cutoff = datetime.datetime(date_cutoff.year, date_cutoff.month, date_cutoff.day)
        
        # Different queries have seen different key name. This will be the first key value in the response.
        r_keys = list(r.keys())
        numLeads = r[r_keys[0]]
        numPages = numLeads//self.perPage
        
        # Adds another page if there is any leftover data in the last page
        if numLeads % self.perPage != 0:
            numPages += 1
        logging.info("{pages} pages available on {query} query @ {perPage} pages per lead".format(
            pages = numPages, query = url, perPage = self.perPage))
        
        df = pd.DataFrame()
        for i in range(numPages, 0, -1):
            print("Requesting page {}".format(i))
            params = {"pageSize": self.perPage, "page": i}
            page = self._get(this_url, params, as_json = False)
            rRemaining = page.headers["X-RateLimit-Remaining"]
            data = page.json()[r_keys[1]]
            pageLeads = self._extractData(data, extractionObject)       
            df = pd.concat([df, self.correctDatetime(pageLeads)])

            if df["created"].min() < date_cutoff:
                df = df[df['created'] < datetime_cutoff]
                break

        logging.info("{} requests made".format(self.requestCount))
        logging.info("{} requests remaining after complete".format(rRemaining))
        df.set_index("id", inplace = True)
        return df.sort_values(by = "created", ascending = True)
    
    def correctDatetime(self, data):
        data["created"] = data["created"].apply(self._toPyDatetime)
        return data
    
    _toPyDatetime = lambda self, x: pd.to_datetime(x).tz_localize(None)
        

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
        
        # def checkKey(self, key):
        #     if self.data[key]:
        #         return self.data[key]
        #     else:
        #         return None
        
        def checkKey(self, key):
            return self._rCheckKey(key, self.data)
        
        def checkSubkey(self, key, data):
            return self._rCheckKey(key, data)
        
        # TODO Make this so that it can take a list of keys to dig into
        def _rCheckKey(self, key, data):
            if type(key) != list:
                if data[key]:
                    return data[key]
                else:
                    return None
            else:
                subset = self._rCheckKey(key[0], data)
                for i in key[1:]:
                    if i != key[-1]:
                        subset = self._rCheckKey(i, data)
                    else:
                        break
                return subset[i]        

    class Lead(Extraction):
        
        def __init__(self, leadData):
            super().__init__(leadData)
            
            self.id = self.checkKey("id")
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
                
            # TODO Check if this section works with only the new CheckKey method
            self.nexApptDate = None
            self.nextApptDetail = None
            
            if self.checkKey("futureAppointments"):
                apptNum = list(leadData["futureAppointments"].keys())[0]
                apptDetails = self.checkKey(apptNum, "futureAppointments")
                self.nextApptDate = datetime.datetime.fromisoformat(apptDetails["start_time_local"])
                self.nextApptDate = apptDetails["name"]
            
    class Install(Extraction):
        
        def __init__(self, installData):
            super().__init__(installData)
            
            self.id = self.checkKey("id")
            self.customer = self.checkKey(["customer", "name"])
            self.created = datetime.datetime.fromisoformat(self.checkKey("created_at"))
            self.status = self.checkKey("status_name")
            self.system_size = self.checkKey("system_size")
            self.system_offset = self.checkKey("system_offset")
            self.closer = self.checkKey(["agent_user", "name"])
            self.panel_count = self.checkKey("panel_count")
            self.system_cost = self.checkKey(["cost", "system_cost_base"])
            
            self.milestone = self.getMilestone()
            print("{} milestone {}".format(self.customer, self.milestone))
            

        def getMilestone(self):
            latest = (None, datetime.datetime(1999, 1, 1))
            for i in self.checkKey("milestones"):
                date = self.checkSubkey(["install_milestone", "completed_on"], i)
                if date:
                    date = datetime.datetime.strptime(date, "%Y-%m-%d")
                    title = self.checkSubkey("title", i)
                    if date > latest[1]:
                        latest = (title, date)
            return latest[0]

                    
    # class Appointment:
        
    #     def __init__(self, data):
    #         data = data[list(data.keys())[0]]
    #         self.title = data["name"]
    #         self.status = data["status"]
    #         self.time = datetime.datetime.fromisoformat(data["start_time_local"])
            
if __name__ == "__main__":
    wrapper = EnerfloWrapper()    
    # customers = wrapper.getCustomers()
    installs = wrapper.getInstalls()
    # print(customers.head())
    