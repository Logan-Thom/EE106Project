"""
Python script to call from an external API and create a forecast for the 
next 48 hours of carbon data in the UK.

Created By: Logan Thom, Ricardo Barrera
Created On: 26/01/24
Created For: EE106 Project report
Last Update: 09/02/24
Updated By: Logan Thom, Ricardo Barrera
"""

import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timezone, timedelta            #used to collect current date so as to not break API calls for previous data
import random


headers = {
    'Accept':'applications/json'
}



def InitialiseFile():
    file = open("data.csv","w")
    file.write("forecast,actual,index\n")
    file.close()



def GetPreviousDataAverages():
    today_date = datetime.now(timezone.utc)                                                                             #store current date in variable
    past_date = today_date - timedelta(days = 25)
    today_date = str(today_date)[0:10] + 'T' + str(today_date)[11:16] + 'Z'                                             #convert to ISO 8601 format
    past_date = str(past_date)[0:10] + 'T' + str(today_date)[11:16] + 'Z'

    api_request_string = 'https://api.carbonintensity.org.uk/intensity/stats/' + past_date + '/' + today_date + '/'     #create string for api request
    r = requests.get(api_request_string, params={}, headers=headers)

    data_str = ConvertFromJson(r)
    average_over_month = data_str.get('average')                                                  #store statistical data from request in object r
    

    return average_over_month


def ReadSmallPreviousData(num):
    file = open("data.csv","r")
    lines = (file.readlines() [-num:])
    previous_values = []
    for line in (lines [-num:]):
        line_data = line.split(',')
        previous_values.append(int(line_data[1]))

    return previous_values
        


def GetTestDataSet():
    r = requests.get('https://api.carbonintensity.org.uk/intensity/date/2024-01-10/24', params = {}, headers=headers)
    return r



#process JSON into python
def ConvertFromJson(req):
    data_string = str(req.json())[80:]
    data_string = data_string[:-3]
    new_temp_string = ''.join(['"' if char == "'" else char for char in data_string])
    data_string = json.loads(new_temp_string)

    return data_string




#store in file
def StoreInFile(data):
    file = open("data.csv","a")
    for value in data.values():
        file.write(str(value) + ',')
    file.write('\n')
    file.close()
    return




#method for collecting data
def CollectData():
    #take date from 25 days ago, cycle through 48 segments representing half hour times, then through all the days
    #do not take maximum amount of data, the server will hate that and the api call will fail
    start_date = datetime.now(timezone.utc) - timedelta(days = 25)
    for i in range(25):
        loop_date = str(start_date + timedelta(days = i))[0:10]
        for ii in range(48):
            request_string = 'https://api.carbonintensity.org.uk/intensity/date/' + loop_date + '/' + str(ii+1)
            r = requests.get(request_string, params={}, headers=headers)
            converted_r = ConvertFromJson(r)
            StoreInFile(converted_r)
        
    return


def CreateNumpyPlotArray(forecast):
    fs = open("data.csv","r")
    next(fs)
    y_axis = np.array([])
    for line in fs:
        a = line.split(",")
        b = a[1]
        y_axis = np.append(y_axis, int(b))
        
    y_axis = np.append(y_axis, forecast)
    return y_axis



def DataGraph(y_axis):

    x_axis = np.linspace(-25, 2, len(y_axis))
    fig, ax = plt.subplots()
    ax.plot(x_axis,y_axis)
    plt.xlabel("Days in Past")
    plt.ylabel("Carbon Intensity (gCO2/kWh)")
    plt.show()
    

    return


def MovingAverage(previous_data_set):
    #does nothing currently
    return
    
def SimplePlot():
    x = np.linspace(0,2 * np.pi, 200)
    y = np.sin(x)
    fig, ax = plt.subplots()
    ax.plot(x,y)
    plt.show()

def AutoRegression(constant_term):
    #value = const + coeff*y-1 + coeff*y-2 + err
    #error term is white noise and completely random
    #const is the average of the last 25 days because I say so
    #coeff2 less than 1, greater than -1
    #sum of coeffs is less than 1
    #difference of coeffs is less than one
    #perhaps usefule to have the sums of the magnitudes of coeffs to be 2
    #needs to run for 48 hours ahead, or 96 times
    
    return


def SimpleExponentialSmoothing():

    #general form of future_term = a*yt + (1-a)*yt-1 + (1-a)**2 * yt-2 and so on
    
    #its at this point I REALLY wish we were in C++ so I could use deques 
    past_values = ReadSmallPreviousData(6)
    #loop through the 96 times, saving values to an array or list, 
    #appending the past_values list as you go on
    
    forecast_terms = np.empty(96)
    
    #smoothing coefficient
    a = 0.89
    
    for i in range(96):
        future_term = (1-a)**5 * past_values[0] + (1-a)**4 * past_values[1] + (1-a)**3 * past_values[2] + (1-a)**2 * past_values[3] + (1-a)*past_values[4] + a*past_values[5]
        past_values.append(future_term)
        past_values.pop(0)
        
        forecast_terms[i] = future_term

    return forecast_terms


def main():
    #InitialiseFile()
    #CollectData()
    #y = CreateNumpyPlotArray()
    #PastDataGraph(y)
    #mean_data = GetPreviousDataAverages()
    #AutoRegression(mean_data)
    

    forecast = SimpleExponentialSmoothing()
    plot_data_values = CreateNumpyPlotArray(forecast)
    DataGraph(plot_data_values)
    return



#this is a script
if __name__=='__main__':
  main()
