"""
Python script to create forecast of future carbon intensity
data for specified UK region using the carbon intensity api.

If you are reading this and concerned about the 'return' statements
at the end of every function despite return type void, it is purely
to make the code more readable for me as I am used to C syntax where
the end of each function is clearly marked by {}

I use 2 space indentation, I will not apologise.

Created By: Logan Thom (202306752)
Created On: 26/01/24
Created For: EE106 Project
Last Update: 13/03/24
Updated By: Logan Thom

This is an individual project with no other collaborators.
"""

#imported libraries
import requests
import json
import matplotlib.pyplot as plt
import numpy as np 
from datetime import datetime, timezone, timedelta
import random

#global variables
data_file_path = './data.csv'


headers = {
  'Accept':'applications/json'
}

#functions
#function to clear existing data file, returns void
def ClearExistingDataFile():
  f = open(data_file_path,"w")
  f.write("")
  f.close()
  return 

#function to select specific regional data to collect
#returns int, input validation and error catching default to 0
#creates 2 extra variables for file accessing due to differences 
#in layout of national and regional api responses
def SelectRegion():
  #catch errors on input
  try:
    selected_region = int(input("Please enter one of the following integers to select a specific region:\n 1 - North Scotland,\n 2 - South Scotland,\n 3 - North West England,\n 4 - North East England,\n 5 - Yorkshire,\n 6 - North Wales,\n 7 - South Wales,\n 8 - West Midlands,\n 9 - East Midlands,\n10 - East England,\n11 - South West England,\n12 - South England,\n13 - London,\n14 - South East England,\n15 - England,\n16 - Scotland,\n17 - Wales\n\nRegion: "))
    data_file_index = 0                     #1 for national data, 0 for regional
    intensity_index = 1
  except:
    selected_region = 0
    data_file_index = 1
    intensity_index = 2
    print("Invalid Region, National Data Selected")

  #validate input is in allowed region
  if selected_region < 1 or selected_region > 17:
    selected_region = 0
    data_file_index = 1
    intensity_index = 2
    print("Invalid Region, National Data Selected")


  return selected_region, data_file_index, intensity_index

#function to call the api and get data
#takes int region, returns void
#I know it is ineffcient
def CallApi(region):
  days_in_past = 5
  start_date = datetime.now(timezone.utc) - timedelta(days=days_in_past)
  #need to store strings of possible times within a day
  #I hate this but they decided to not use actual time codes
  #which would make this actually look a lot nicer
  times = ['T00:00Z','T00:30Z','T01:00Z','T01:30Z','T02:00Z','T02:30Z','T03:00Z','T03:30Z','T04:00Z','T04:30Z','T05:00Z','T05:30Z','T06:00Z','T06:30Z','T07:00Z','T07:30Z','T08:00Z','T08:30Z','T09:00Z','T09:30Z','T10:00Z','T10:30Z','T11:00Z','T11:30Z','T12:00Z','T12:30Z','T13:00Z','T13:30Z','T14:00Z','T14:30Z','T15:00Z','T15:30Z','T16:00Z','T16:30Z','T17:00Z','T17:30Z','T18:00Z','T18:30Z','T19:00Z','T19:30Z','T20:00Z','T20:30Z','T21:00Z','T21:30Z','T22:00Z','T22:30Z','T23:00Z','T23:30Z','T00:00Z']
  file = open(data_file_path,"a")
  if region == 0:    
    for i in range(days_in_past):
      loop_date = str(start_date + timedelta(days = i))[0:10]
      for ii in range(48):
        request_string = 'https://api.carbonintensity.org.uk/intensity/date/' + loop_date + '/' + str(ii+1)
        r = requests.get(request_string, params={}, headers=headers)
        converted_r = ConvertNationalFromJson(r)
        StoreInFile(file,converted_r)
    

  else:
    for i in range(days_in_past):
      loop_date = str(start_date + timedelta(days = i))[0:10]
      for ii in range(1,48):
        request_string = 'https://api.carbonintensity.org.uk/regional/intensity/' + loop_date + times[ii-1] + '/' + loop_date + times[ii] + '/regionid/' + str(region)
        r = requests.get(request_string, params={}, headers=headers)
        converted_r = ConvertJsonToDictionary(r)
        StoreInFile(file,converted_r)
        
  file.close()
    

  return


#function to take API data and format into usable state
#uses substring methods to cut unnessecary data
#takes api request, returns dictionary
def ConvertJsonToDictionary(req):
  data_string = str(req.json())
  index_one = data_string.find("{'fore")
  data_string = data_string[index_one:]
  index_two = data_string.find('}')
  data_string = data_string[:(index_two+1)]
  #change the type of quotation marks to make it work,
  #one by one join every character to an empty string but
  #if the character is a single quote, use a double quote
  temp_string = ''.join(['"' if char == "'" else char for char in data_string])
  data_string = json.loads(temp_string)

  return data_string

#same as previos ConvertJsonToDictionary but for national formatting
def ConvertNationalFromJson(req):
    data_string = str(req.json())[80:]
    data_string = data_string[:-3]
    new_temp_string = ''.join(['"' if char == "'" else char for char in data_string])
    data_string = json.loads(new_temp_string)

    return data_string

#function to store data dictionary to a file
#takes dictionary, returns void
def StoreInFile(file,data):
  for value in data.values():
    file.write(str(value) + ',')
  file.write('\n')
  return


#function to find distribution of carbon levels and graph
#returns void
def CreateDistributionGraph(intensity_index):
  distribution = {"very low": 0, "low": 0, "moderate": 0, "high": 0, "very high": 0}
  file = open(data_file_path,"r")
  lines = file.readlines()
  for line in lines:
    emmission_level = (line.split(","))[intensity_index]
    #python equivalent of a C switch statement, requires 3.10.x or higher
    match emmission_level:
      case "very low":
        distribution['very low'] += 1
      case "low":
        distribution['low'] += 1
      case "moderate":
        distribution['moderate'] += 1
      case "high":
        distribution['high'] += 1
      case "very high":
        distribution['very high'] += 1

  file.close()

  #make graph
  fig,ax = plt.subplots()
  bars = plt.barh(list(distribution.keys()),list(distribution.values()))
  bars[4].set_color('red')
  bars[3].set_color('orange')
  bars[2].set_color('yellow')
  bars[1].set_color('mediumseagreen')
  bars[0].set_color('green')

  ax.set_xlabel('Ocurrences of State')
  ax.set_ylabel("Intensity State")
  ax.set_title("Distribution of Intensity States")
  plt.show()
  return

#function to find semi-interquartile ranges
def GetSemiInterQuartileRange(data_set):
  q3 = np.percentile(data_set,75)
  q1 = np.percentile(data_set,25)
  iqr = q3 - q1
  siqr = iqr*0.5
  return siqr

#create forecast of data values
def SimpleExponentialSmoothing(data_file_index):
  #smoothing coefficient
  a = 0.5
  file = open(data_file_path,"r")
  lines = file.readlines()
  forecast_terms = np.empty([])
  predicted_term = (lines[0].split(","))[data_file_index]
  mean = 0
  i = 0
  #train on this data
  for line in lines:
    current_line = line.split(",")
    current_value = current_line[data_file_index]
    predicted_term = a*(float(current_value)) + (1-a)*(float(predicted_term)) + random.uniform(-1, 1)
    if predicted_term < 0:
      predicted_term = predicted_term * (-1)
    forecast_terms = np.append(forecast_terms,predicted_term)
    mean += float(current_value)
    i += 1
  file.close()
  mean = mean/i
  siqr = GetSemiInterQuartileRange(forecast_terms)
  error = random.uniform((-1)*(siqr/2),(siqr/2))
  # real predictions made here
  for ii in range(96):
    predicted_term = np.round((a*predicted_term + (1-a)*forecast_terms[i - 1 + ii] + error),3)
    if predicted_term < 0:
        predicted_term = predicted_term * (-1)
    error = random.uniform((-1)*(siqr/2),(siqr/2))
    forecast_terms = np.append(forecast_terms,predicted_term)

  return forecast_terms

#function to create numpy array of data to plot
#returns numpy array
def CreatePlotArray(data_file_index):
  file = open(data_file_path,"r")
  y_axis = np.array([])
  for line in file:
    a = line.split(",")
    b = a[data_file_index]
    y_axis = np.append(y_axis, int(b))

  return y_axis

#function to plot data on a matplotlib graph
#takes, numpy array, numpy array, int, int, int, returns void
def CreateGraph(y_plot_one, y_plot_two, limit_one, limit_two,days_in_past):
  x_axis_one = np.linspace((-1)*days_in_past, limit_one, len(y_plot_one))
  x_axis_two = np.linspace((-1)*days_in_past, limit_two, len(y_plot_two))
  fig,ax = plt.subplots()
  ax.plot(x_axis_one,y_plot_one)
  ax.plot(x_axis_two,y_plot_two, color="r")
  plt.xlabel("Days From Now")
  plt.ylabel("Carbon Intensity (gCO2/kWh)")
  plt.show()
  
  return

#function to create a benchmark
#returns void, places benchmark on the io stream
def BenchmarkForecast(forecast,data_file_index):
  #make a naive MAE benchmark and normal MAE benchmark to compute MASE
  file = open(data_file_path,"r")
  naive_value = ((file.readline()).split(','))[data_file_index]
  lines = file.readlines()
  naive_mean = 0
  actual_mean = 0
  i = 0
  for line in lines:
    current_value = line.split(',')[data_file_index]
    naive_mean += np.abs(float(naive_value) - float(current_value))
    actual_mean += np.abs(forecast[i] - float(current_value))
    i += 1
  naive_mean = naive_mean/i
  actual_mean = actual_mean/i
  mase = np.round((actual_mean / naive_mean),3)
  print("MASE benchmark: " + str(mase))
  
  return


#main function
def main():
  ClearExistingDataFile()
  region, dfi, inteni = SelectRegion()
  CallApi(region)
  forecast = SimpleExponentialSmoothing(dfi)
  api_data = CreatePlotArray(dfi)
  CreateGraph(api_data, forecast, 0, 2, 5)
  CreateDistributionGraph(inteni)
  BenchmarkForecast(forecast,dfi)
  return

#this is a script
if __name__=='__main__':
  main()

