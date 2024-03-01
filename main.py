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
from datetime import datetime, timezone, time,  timedelta            #used to collect current date so as to not break API calls for previous data
import random




headers = {
    'Accept':'applications/json'
}



def InitialiseFile():
    file = open("data.csv","w")
    file.write("")
    file.close()



def RegionSelector():
    try:
        selected_region = int(input("Please enter one of the following integers to select a specific region:\n1 - North Scotland,\n2 - South Scotland,\n3 - North West England,\n4 - North East England,\n5 - Yorkshire,\n6 - North Wales,\n7 - South Wales,\n8 - West Midlands,\n9 - East Midlands,\n10 - East England,\n11 - South West England,\n12 - South England,\n13 - London,\n14 - South East England,\n15 - England,\n16 - Scotland,\n17 - Wales\n\nRegion: "))
    except:
        selected_region = 0
    if selected_region < 1 or selected_region > 17:
        selected_region = 0

    days = 0
    
    days = int(input("debugging feature: "))
    


    return selected_region, days


def GetPreviousDataAverages(days_in_past):
    today_date = datetime.now(timezone.utc)                                                                             #store current date in variable
    past_date = today_date - timedelta(days = days_in_past)
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
    r = requests.get( 'https://api.carbonintensity.org.uk/regional/intensity/2024-01-27T23:30Z/2024-01-27T00', params = {}, headers=headers)
    return r



#process JSON into python
def ConvertNationalFromJson(req):
    data_string = str(req.json())[80:]
    data_string = data_string[:-3]
    new_temp_string = ''.join(['"' if char == "'" else char for char in data_string])
    data_string = json.loads(new_temp_string)

    return data_string



def ConvertRegionalFromJson(req):
    data_string = str(req.json())
    index_one = data_string.find("{'fore")
    data_string = data_string[index_one:]
    index_two = data_string.find('}')
    data_string = data_string[:(index_two+1)]
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
def CollectData(selected_region,days_in_past):
    #take date from 25 days ago, cycle through 48 segments representing half hour times, then through all the days
    #do not take maximum amount of data, the server will hate that and the api call will fail
    
    #iterate from 0 to 23 and every odd iteration variable = 30, else = 00?

    if days_in_past == 0:
        days_in_past= 20

    start_date = datetime.now(timezone.utc) - timedelta(days = days_in_past)
    
    #efficiency is a myth
    times = ['T00:00Z','T00:30Z','T01:00Z','T01:30Z','T02:00Z','T02:30Z','T03:00Z','T03:30Z','T04:00Z','T04:30Z','T05:00Z','T05:30Z','T06:00Z','T06:30Z','T07:00Z','T07:30Z','T08:00Z','T08:30Z','T09:00Z','T09:30Z','T10:00Z','T10:30Z','T11:00Z','T11:30Z','T12:00Z','T12:30Z','T13:00Z','T13:30Z','T14:00Z','T14:30Z','T15:00Z','T15:30Z','T16:00Z','T16:30Z','T17:00Z','T17:30Z','T18:00Z','T18:30Z','T19:00Z','T19:30Z','T20:00Z','T20:30Z','T21:00Z','T21:30Z','T22:00Z','T22:30Z','T23:00Z','T23:30Z','T00:00Z']
    
    if selected_region == 0:
    
        for i in range(days_in_past):
            loop_date = str(start_date + timedelta(days = i))[0:10]
            for ii in range(48):
                request_string = 'https://api.carbonintensity.org.uk/intensity/date/' + loop_date + '/' + str(ii+1)
                r = requests.get(request_string, params={}, headers=headers)
                converted_r = ConvertNationalFromJson(r)
                StoreInFile(converted_r)

    else:
        for i in range(days_in_past):
            loop_date = str(start_date + timedelta(days = i))[0:10]
            for ii in range(1,48):

                request_string = 'https://api.carbonintensity.org.uk/regional/intensity/' + loop_date + times[ii-1] + '/' + loop_date + times[ii] + '/regionid/' + str(selected_region)
                r = requests.get(request_string, params={}, headers=headers)
                converted_r = ConvertRegionalFromJson(r)
                StoreInFile(converted_r)


        
    print("data file complete")
    return




def CreateNumpyPlotArray():
    fs = open("data.csv","r")
    y_axis = np.array([])
    for line in fs:
        a = line.split(",")
        b = a[0]
        y_axis = np.append(y_axis, int(b))
        

    return y_axis



def DataGraph(y_axis,limit,days_in_past, colour):


    x_axis = np.linspace((-1)*(days_in_past), limit, len(y_axis))
    fig, ax = plt.subplots()
    ax.plot(x_axis,y_axis, color=colour)
    plt.xlabel("Days in Past")
    plt.ylabel("Carbon Intensity (gCO2/kWh)")
    plt.show()
    

    return

def MultiDataGraph(y_plot_one, y_plot_two, limit_one, limit_two, days_in_past):
    x_axis_one = np.linspace((-1)*(days_in_past), limit_one, len(y_plot_one))
    x_axis_two = np.linspace((-1)*(days_in_past), limit_two, len(y_plot_two))
    fig,ax = plt.subplots()
    ax.plot(x_axis_one,y_plot_one)
    ax.plot(x_axis_two,y_plot_two, color = 'm')
    plt.xlabel("Days in Past")
    plt.ylabel("Carbon Intensity (gCO2/kWh)")
    plt.show()


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

    #loop through the 96 times, saving values to an array or list, 
    #appending the past_values list as you go on
    
    

    #smoothing coefficient
    a = 0.5

    fs = open("data.csv","r")
    lines = fs.readlines()
    forecast_terms = np.empty(len(lines) + 96)
    predicted_term = (lines[0].split(","))[0]
    i = 0
    mean = 0
    
    for line in lines:
        current_line = line.split(",")
        current_value = current_line[0]
            
        predicted_term = a*(float(current_value)) + (1-a)*(float(predicted_term))
        forecast_terms[i] = predicted_term
        mean += float(current_value)
        i += 1
        
    inter_quartile_range = np.percentile(forecast_terms, 75) - np.percentile(forecast_terms, 25)
    semi_inter_quartile_range = inter_quartile_range/2
    mean = mean/i
    for ii in range(96):

        #error based on variance of previous data
        err = random.uniform((-1)*(semi_inter_quartile_range),(semi_inter_quartile_range))
        predicted_term = a*(mean + err) + (1 - a)*predicted_term
        
        forecast_terms[ii + i] = predicted_term

        
    fs.close()
    return forecast_terms


def main():
    InitialiseFile()
    selected_region,days_in_past = RegionSelector()
    CollectData(selected_region,days_in_past)        #most intensive operation, try to keep commented until needed
    #y = CreateNumpyPlotArray()
    #PastDataGraph(y)
    #mean_data = GetPreviousDataAverages()
    #AutoRegression(mean_data)
    

    forecast = SimpleExponentialSmoothing()
    plot_data_values = CreateNumpyPlotArray()
    #DataGraph(plot_data_values,0,days_in_past, 'b')
    #DataGraph(forecast,2,days_in_past, 'r')
    
    #more interesting one
    MultiDataGraph(plot_data_values, forecast, 0, 2, days_in_past)
    

    

    return



#this is a script
if __name__=='__main__':
    main()

