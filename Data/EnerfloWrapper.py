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
    
    def __init__(self, previous_weeks, perPageRequest = 200):
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
        self.previous_weeks = previous_weeks
        
    @staticmethod
    def _loadToken():
        with open(resource_path("Data/Secret.txt"), "r") as f:
            data = f.readlines()[0]
        return data

    def _getURL(self, endpoint):
        return self.BASE_URL.format(endpoint)
    
    def _getUnique(self, column):
        data = self._data[column].dropna()
        
        # data = data[column].unique()
        return data.unique()
    
    # Put get request with pages here
    def _getRequest(self, url, params = None, as_json = True):
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
    
    def _gatherAllPageData(self, url, extractionObject, previous_weeks):
        this_url = self._getURL(url)
        r = self._getRequest(this_url)
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
            page = self._getRequest(this_url, params, as_json = False)
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
        
        df.drop("data", inplace = True, axis = 1)
        
        return df.sort_values(by = "created", ascending = True)
    
    def correctDatetime(self, data):
        data["created"] = data["created"].apply(self._toPyDatetime)
        return data
    
    _toPyDatetime = lambda self, x: pd.to_datetime(x).tz_localize(None)
    
    def _extractData(self, pageData, object_type):
        data = []
        for lead in pageData:
            thisData = object_type(lead)
            data.append(vars(thisData))
        df = pd.DataFrame.from_records(data)
        return df
    
    def get(self, url, obj, previous_weeks = None):
        if previous_weeks !=  self.previous_weeks or "_data" not in self.__dict__:
            if previous_weeks:
                logging.info("New week range requested. Data now for {} weeks".format(self.previous_weeks))
                previous_weeks = self.previous_weeks
            
                data = self._gatherAllPageData(url = url,
                                                extractionObject = obj,
                                                previous_weeks = previous_weeks)
                return data
            else:
                return self._data
        else:
            logging.info("Gathering same data previously requested. Returning previous data")
            return self._data

    class Extraction:
        def __init__(self, data):
            self.data = data
        
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


class CustomerData(EnerfloWrapper):
        
    def __init__(self, perPageRequest = 200, previous_weeks = 6):
        super().__init__(perPageRequest = perPageRequest, previous_weeks = 6)
        
        self._data = self.get(previous_weeks)
        self.setters = self._getUnique("setter")
        self.closers = self._getUnique("closer")
        
        
    def get(self, weeks = None):
        self._data = EnerfloWrapper.get(self,
            url = self._endpoints["GET"]["all_customers"],
            obj = self.Lead,
            previous_weeks = weeks)
        return self._data
        
        
    # # TODO Put this in parent class
    # def get(self, previous_weeks = None):
    #     if previous_weeks !=  self.previous_weeks or "_data" not in self.__dict__:
    #         if not previous_weeks:
    #             previous_weeks = self.previous_weeks
            
    #         data = self._gatherAllPageData(url = self._endpoints["GET"]["all_customers"],
    #                                        extractionObject = self.Lead,
    #                                        previous_weeks = previous_weeks)
    #         self.previous_weeks = previous_weeks
    #         return data
    #     else:
    #         logging.info("Gathering same data previously requested. Returning previous data")
    #         return self._data
                
    class Lead(EnerfloWrapper.Extraction):
        
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
            self.closer = "{} {}".format(leadData["owner"]["first_name"], leadData["owner"]["last_name"]) \
                if "owner" in leadData.keys() else None                
            self.setter = "{} {}".format(leadData["setter"]["first_name"], leadData["setter"]["last_name"]) \
                if "setter" in leadData.keys() else None     
            
            apptNum = list(leadData["futureAppointments"].keys())[0] if self.checkKey("futureAppointments") else None
            
            date = self.checkKey(["futureAppointments", str(apptNum), "start_time_local"])
            self.nexApptDate = datetime.datetime.fromisoformat(date) if date else None
            self.nextApptDetail = self.checkKey(["futureAppointments", str(apptNum), "name"])            

class InstallData(EnerfloWrapper):
    
    def __init__(self, perPageRequest = 200, previous_weeks = 6):
        super().__init__(perPageRequest = perPageRequest, previous_weeks = previous_weeks)
        self._data = self.get(previous_weeks)
        self.setters = self._getUnique("setter")
        self.closers = self._getUnique("closer")
        
    def get(self, weeks = None):
        self._data = EnerfloWrapper.get(self,
            url = self._endpoints["GET"]["installs"],
            obj = self.Install,
            previous_weeks = weeks)
        return self._data
    
    class Install(EnerfloWrapper.Extraction):
        
        def __init__(self, installData):
            super().__init__(installData)
            
            self.id = self.checkKey("id")
            self.customer = self.checkKey(["customer", "name"])
            self.created = datetime.datetime.fromisoformat(self.checkKey("created_at"))
            self.status = self.checkKey("status_name")
            self.system_size = self.checkKey("system_size")
            self.system_offset = self.checkKey("system_offset")
            self.closer = self.checkKey(["agent_user", "name"])
            self.setter = self.checkKey(["setter_user", "name"])
            self.panel_count = self.checkKey("panel_count")
            self.system_cost = self.checkKey(["cost", "system_cost_base"])
            self.milestone = self.getMilestone()
            
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
            
if __name__ == "__main__":
    # customers = CustomerData()
    installs = InstallData()
    data = installs.get()