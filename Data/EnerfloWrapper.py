# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 22:45:21 2022

@author: Schmuck
"""

import sys, os

import requests, json
import datetime
import pandas as pd
import logging
from types import SimpleNamespace
from enum import Enum

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
    
    # Main data access point 
    @property
    def data(self):
        return self._data

    def _getURL(self, endpoint):
        return self.BASE_URL.format(endpoint)
    
    def _getUnique(self, column):
        data = self._data[column].dropna()
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
        
        if url.split("/")[0] == "v3":
            pageSizeParam = "per_page"
        else:
            pageSizeParam = "pageSize"
        
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
            params = {pageSizeParam: self.perPage, "page": i}
            page = self._getRequest(this_url, params = params, as_json = False)
            rRemaining = page.headers["X-RateLimit-Remaining"]
            data = page.json()[r_keys[1]]
            pageLeads = self._extractData(data, extractionObject)
            df = pd.concat([df, self.correctDatetime(pageLeads)])
            
            if previous_weeks:

                date_cutoff = datetime.date.today() - datetime.timedelta(weeks = previous_weeks, days = 1)
                datetime_cutoff = datetime.datetime(date_cutoff.year, date_cutoff.month, date_cutoff.day)
                if df["created"].min() < date_cutoff:
                    df = df[df['created'] > datetime_cutoff]
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
            logging.info("New week range requested. Data now for {} weeks".format(self.previous_weeks))
            previous_weeks = self.previous_weeks
            data = self._gatherAllPageData(url = url,
                                            extractionObject = obj,
                                            previous_weeks = previous_weeks)
            return data
            # if previous_weeks or "previous_weeks" not in self.__dict__:
            #     logging.info("New week range requested. Data now for {} weeks".format(self.previous_weeks))
            #     previous_weeks = self.previous_weeks
            
            #     data = self._gatherAllPageData(url = url,
            #                                     extractionObject = obj,
            #                                     previous_weeks = previous_weeks)
            #     return data
            # else:
            #     return self._data
        else:
            logging.info("Gathering same data previously requested. Returning previous data")
            return self._data
        
    def export(self):
        out = self._data
        
        for i in out.columns:
            if out[i].dtype not in [float, int, str]:
                out[i] = out[i].astype(str)
        import json
        
        temp = os.makedirs(os.getcwd() + "/cache") if not os.path.exists(os.getcwd() + "/cache") else None
        with open(os.getcwd() + "/cache/{}_data.json".format(self.__class__.__name__), "w") as f:
            json.dump(out.to_dict(), f, indent = 2)

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
                    # logging.warning("Expected key of {} was not found and corrected to None".format(key))
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
            
        @staticmethod
        def strToDate(x):
            return datetime.datetime.strptime(x, "%Y-%m-%d") if x else None
        


class Customers(EnerfloWrapper):
        
    def __init__(self, perPageRequest = 200, previous_weeks = 6):
        super().__init__(perPageRequest = perPageRequest, previous_weeks = previous_weeks)
        
        self.collect(previous_weeks)
        # self.setters = self._getUnique("setter")
        
    def collect(self, weeks = None):
        print("Gathering Customer Data")
        logging.info("Gathering Customer Data")
        if "_data" not in self.__dict__:
            self._data = EnerfloWrapper.get(self,
                url = self._endpoints["GET"]["all_customers"],
                obj = self.Lead,
                previous_weeks = weeks)
                
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
            
            # Add checkKey around these.
            self.address = f"""{leadData["address"]} {leadData["city"]}, {leadData["state"]} {leadData["zip"]}"""
            self.closer = "{} {}".format(leadData["owner"]["first_name"], leadData["owner"]["last_name"]) \
                if "owner" in leadData.keys() else None                
            self.setter = "{} {}".format(leadData["setter"]["first_name"], leadData["setter"]["last_name"]) \
                if "setter" in leadData.keys() else None    
            self.setter = self.setter if self.setter != self.closer else None
            
            apptNum = list(leadData["futureAppointments"].keys())[0] if self.checkKey("futureAppointments") else None
            
            date = self.checkKey(["fu˜tureAppointments", str(apptNum), "start_time_local"])
            self.nextApptDate = datetime.datetime.fromisoformat(date) if date else None
            self.nextApptDetail = self.checkKey(["futureAppointments", str(apptNum), "name"])            

class Installs(EnerfloWrapper):
    def __init__(self, perPageRequest = 150):
        super().__init__(perPageRequest = perPageRequest, previous_weeks = None)
        self.collect()
        self.setters = self._getUnique("setter")
        
    def collect(self):
        print("Gathering Install Data")
        logging.info("Gathering Install Data")
        self._data = EnerfloWrapper.get(self,
            url = self._endpoints["GET"]["installs"],
            obj = self.Install,
            previous_weeks = None)
        
        # self._data["current_milestone"].replace(to_replace = "Net Meter Meter Install", value = "PTO", inplace = True)
        self._data.sort_values(by = "agreement", ascending = False, inplace = True)
        self.export()
        
    # def getUpcomingInstalls(self, weeks):
    #     today = datetime.datetime.today()
    #     out = self._data[self._data["install_date"].between(today, today + datetime.timedelta(weeks = weeks))]
    #     if not out.empty:
    #         logging.info("{} upcoming installs for the next {} weeks".format(len(out), weeks))
    #         return out
    #     else:
    #         logging.info("No upcoming installs for the next {} weeks".format(weeks))
    #         return None
    
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
            self.setter = self.setter if self.setter != self.closer else None
            
            self.panel_count = self.checkKey("panel_count")
            self.gross_cost = self.checkKey(["cost", "system_cost_gross"])
            self.milestone = self.getMilestone("Net Meter Meter Install")
            self.agreement = self.getMilestone("Agreement")
            self.install_date = self.InstallDate()
            self.PTO = self.PTO_Date()
            self.current_milestone = self.getCurrentMilestone() if not self.PTO else "PTO"
        
            # if self.customer == "Trisha Anderson":
            #     self.install_date = self.InstallDate()
        
        def getMilestone(self, name, startDate = False):
            for milestone in self.checkKey("milestones"):
                if name == self.checkSubkey("title", milestone):
                    if not startDate:
                        out = self.checkSubkey(["install_milestone", "completed_on"], milestone)
                    else:
                        out = self.checkSubkey(["install_milestone", "start_date"], milestone)
                    
                    return self.strToDate(out) if out else out
                    
        def getCurrentMilestone(self):
            return self.checkKey(["last_completed_milestone", "title"])
        
        def PTO_Date(self):
            data = self._getCustomField(674)
            value = self.checkSubkey("fields", data)[-1]
            if self.checkSubkey("value", value):
                return datetime.datetime.strptime(value["value"]["value"], "%Y-%m-%d")
            else:
                return None
        
        def InstallDate(self):
            data = self._getCustomField(742)
            # print(data.keys())
            for i in self.checkSubkey("fields", data):
                if i["key"] == "scheduled_install_date":
                    date = self.checkSubkey(["value", "value"], i)
                    if date:
                        return datetime.datetime.strptime(date, "%Y-%m-%d")
            return None
                
            # for i in self.checkSubkey("fields", data):
            #     print(i)
            #     if i["id"] == 738:
            #         date = self.checkSubkey(["value", "value"], i)
            #         # print(date)
            #         return datetime.datetime.strptime(date, "%Y-%m-%d") if date else None
            #     else:
            #         return None
        
        # TODO fix this for both PTO and scheduled date
        def _getCustomField(self, thisID):
            custom_fields = self.checkKey("custom_fields")
            if custom_fields:
                for field in custom_fields:
                    if field["id"] == thisID:
                        return field
                        # value = self.checkSubkey("fields", field)[-1]
                        # print(value)
                        # try:
                        #     if self.checkSubkey("value", value):
                        #         return datetime.datetime.strptime(value["value"]["value"], "%Y-%m-%d")
    
                        #     else:
                        #         return None
                        # except:
                        #     print(value)
                        
class VirtualEnerfloWrapper(EnerfloWrapper):
    
    def __init__(self, file):
        super().__init__(previous_weeks = 0)
        self._data = pd.read_json(str(os.path.join(os.getcwd(), "cache", file)))
        
            
    
if __name__ == "__main__":
    
    
    customers = VirtualEnerfloWrapper("Customers_data.json")
    # customers = Customers(previous_weeks = 6)
    # installs = Installs()
    # installs.export()   
    # data = installs.get()