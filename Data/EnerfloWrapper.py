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
    def getCustomers(self, pageSize = 200, previous_weeks = 6):
        
        url = self._getURL(self._endpoints["GET"]["all_customers"])
        date_cutoff = datetime.date.today() - datetime.timedelta(weeks = 6, days = 1)

        # Get the number of data points to collect for next time.
        # numLeads = requests.get(url, headers = self._headers).json()["dataCount"]
        r = self._get(url)
        numLeads = r["dataCount"]
        # Get the number of pages we need to run through to get all the leads
        numPages = numLeads//pageSize
        # If there is the division isn't spot on, then add an extra page
        if numLeads % pageSize != 0:
            numPages += 1
        
        df = pd.DataFrame()
        for i in range(numPages, 0, -1):
            print("Requesting Page -{}-".format(i))
            params = {"pageSize": pageSize, "page": i}
            page = self._get(url, params, as_json = False)
            remainingReqs = page.headers["X-RateLimit-Remaining"]
            print("Received Page -{}-, {} Remaining Requests".format(i, remainingReqs))
            # Info needed Name, Lead Source, Lead Status, Setter, Lead Owner, Next Appointment, Added
            pageLeads = self.extractLeadData(page.json()["data"])
            df = pd.concat([df, pageLeads])
            if df["created"].min().to_pydatetime().date() < date_cutoff:
                break
            
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
            self.name = leadData["fullName"]
            self.email = leadData["email"]
            self.phone = leadData["mobile"]
            self.address = f"""{leadData["address"]} {leadData["city"]}, {leadData["state"]} {leadData["zip"]}"""
            self.latLong = (leadData["lat"], leadData["lng"])
            self.lead_source = leadData["lead_source"]
            self.lead_status = leadData["status_name"] if leadData["status_name"] else None
            self.owner = "{} {}".format(leadData["owner"]["first_name"], leadData["owner"]["last_name"]) \
                if "owner" in leadData.keys() else None                
            self.setter = "{} {}".format(leadData["setter"]["first_name"], leadData["setter"]["last_name"]) \
                if "setter" in leadData.keys() else None     
            self.notes = leadData["customer_notes"] if leadData["customer_notes"] else None
            self.created = datetime.datetime.fromisoformat(leadData["created"])
            
            if leadData["futureAppointments"]:
                appt = leadData["futureAppointments"][list(leadData["futureAppointments"].keys())[0]]
                self.nexApptDate =  datetime.datetime.fromisoformat(appt["start_time_local"])
                self.nextApptDetail = appt["name"]
            else:
                self.nextAppointment = None
                self.nextApptDetail = None
                
            self.portal = leadData["customer_portal_url"]
            
            
class Appointment:
    
    def __init__(self, data):
        data = data[list(data.keys())[0]]
        self.title = data["name"]
        self.status = data["status"]
        self.time = datetime.datetime.fromisoformat(data["start_time_local"])
            
if __name__ == "__main__":
    wrapper = EnerfloWrapper()    
    customers = wrapper.getCustomers()