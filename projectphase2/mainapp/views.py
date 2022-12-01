from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
from requests.api import request
import os
from django.core.files.storage import FileSystemStorage
import numpy as np
import pydeck as pdk
import pandas as pd
import sys
import math

# Create your views here.

def home(request):
    return render(request,'home.html')

def spatial(request):  
    return render(request,'spatial.html',{"max_lat":max_lat,"min_lat":min_lat,"max_lon":max_lon,"min_lon":min_lon,"step_lon":step_lon,"step_lat":step_lat,"mean_lon":mean_lon,"mean_lat":mean_lat})

def temporal(request):
    return render(request,'temporal.html',{"max_lat":max_lat,"min_lat":min_lat,"max_lon":max_lon,"min_lon":min_lon,"step_lon":step_lon,"step_lat":step_lat,"mean_lon":mean_lon,"mean_lat":mean_lat,"min_time":min_time,"max_time":max_time})

def knn(request):
    return render(request,'knn.html',{"max_id":max_id,"min_id":min_id,"k_range":max_id - min_id})

def trips(request):
    return render(request,"trips.html")
    
def step_finder(co1, co2):
    if len(str(co1).split(".")[1]) > len(str(co2).split(".")[1]):
        return 1 / math.pow(10, (len(str(co1).split(".")[1])))
    else:
        return 1 / math.pow(10, (len(str(co2).split(".")[1])))

def calculate_min_max_timestamp(json_data):
    min_time_result = sys.maxsize
    max_time_result = -sys.maxsize
    for i in json_data:
        for j in i['waypoints']:
            if j['timestamp'] < min_time_result:
                min_time_result = j['timestamp']
            if j['timestamp'] > max_time_result:
                max_time_result = j['timestamp']
    return [min_time_result, max_time_result]


def data(request):
    file=request.FILES['myfile']
    path=os.getcwd()+"\\input"
    fs = FileSystemStorage(location=path)
    if os.path.exists("input/input.json"):
        os.remove("input/input.json")
    filename = fs.save("input.json",file)
    f = open("input/input.json")
    global min_lon
    global min_lat
    global max_lon
    global max_lat
    global mean_lon
    global mean_lat
    global max_time
    global min_time
    global step_lon
    global step_lat
    global max_id
    global min_id
    min_lat = sys.maxsize
    max_lat = -sys.maxsize
    min_lon = sys.maxsize
    max_lon = -sys.maxsize
    min_time = sys.maxsize
    max_time = -sys.maxsize
    min_id = sys.maxsize
    max_id = -sys.maxsize

    #new_json = []
    for i in json.load(f):
        for j in i['trajectory']:
            if j['location'][0]>max_lat:
                max_lat=j['location'][0]
            if j['location'][1]>max_lon:
                max_lon=j['location'][1]
            if j['location'][0]<min_lat:
                min_lat=j['location'][0]
            if j['location'][1]<min_lon:
                min_lon=j['location'][1]
            if j['timestamp']<min_time:
                min_time=j['timestamp']
            if j['timestamp']>max_time:
                max_time=j['timestamp']
            #wp.append({"coordinates":[j['location'][1], j['location'][0]], "timestamp":j['timestamp']})
        #new_json.append({"waypoints":wp})
        if i['trajectory_id']>max_id:
            max_id=i['trajectory_id']
        if i['trajectory_id']<min_id:
            min_id=i['trajectory_id']
    #with open('json_data.json', 'w') as outfile:
        #outfile.write(json.dumps(new_json))
    
    mean_lon = (min_lon+max_lon)/2
    mean_lat = (min_lat+max_lat)/2
    step_lon = step_finder(min_lon, max_lon)
    step_lat = step_finder(min_lat, max_lat)
  
    df = pd.read_json("input/input.json")
    df["coordinates"] = df["trajectory"].apply(lambda f: [[item["location"][1], item["location"][0]] for item in f])
    df["timestamps"] = df["trajectory"].apply(lambda f: [item["timestamp"] - min_time for item in f])
    #df.drop([""], axis=1, inplace=True)

    color_lookup = pdk.data_utils.assign_random_colors(df['trajectory_id'])
    df['color'] = df.apply(lambda row: color_lookup.get(str(row['trajectory_id'])), axis=1)

    layer = pdk.Layer(
        "TripsLayer",
        df,
        get_path="coordinates",
        get_timestamps="timestamps",
        get_color="color",
        opacity=0.8,
        width_min_pixels=5,
        rounded=True,
        trail_length=max_time - min_time,
        current_time=max_time - min_time
    )

    view_state = pdk.ViewState(latitude=mean_lat, longitude=mean_lon, zoom=10, bearing=0, pitch=0)
    r = pdk.Deck(layers=[layer], initial_view_state=view_state)
    r.to_html("templates/trips_layer.html")
    return render(request,'trips.html')
    
def spatial_(request):
    file_path=os.getcwd()+"\\input\\input.json"
    lon1 = np.float64(request.POST['lon1rangevalue'])
    lon2 = np.float64(request.POST['lon2rangevalue'])
    lat1 = np.float64(request.POST['lat1rangevalue'])
    lat2 = np.float64(request.POST['lat2rangevalue'])
    x = {
        "latitude_minimum": lat1,
        "longitude_minimum": lon1,
        "latitude_maximum": lat2,
        "longitude_maximum": lon2,
        "path": file_path
	}
    x=json.dumps(x)
    header = {'Content-Type':'application/json'}
    response=requests.get('http://127.0.0.1:8080/get-spatial-range', headers=header, data=x)
    response_data=response.json()

    new_json=[]
    for i in response_data['ids']:
        k=[]
        for j in range(len(i['timestamp'])):
            k.append({"coordinates":[i['location'][j][1], i['location'][j][0]], "timestamp":i['timestamp'][j]})
        new_json.append({"id":i['trajectory_id'], "waypoints":k})
    
    min_time_stamp, max_time_stamp = calculate_min_max_timestamp(new_json)

    with open('json_data.json', 'w') as outfile:
        outfile.write(json.dumps(new_json))
    df = pd.read_json("json_data.json")
    if df.shape[0] != 0:
        df["coordinates"] = df["waypoints"].apply(lambda f: [item["coordinates"] for item in f])
        df["timestamps"] = df["waypoints"].apply(lambda f: [item["timestamp"] - min_time_stamp for item in f])
        color_lookup = pdk.data_utils.assign_random_colors(df['id'])
        df['color'] = df.apply(lambda row: color_lookup.get(str(row['id'])), axis=1)
        layer = pdk.Layer(
            "TripsLayer",
            df,
            get_path="coordinates",
            get_timestamps="timestamps",
            get_color="color",
            opacity=0.8,
            width_min_pixels=5,
            rounded=True,
            trail_length=max_time - min_time,
            current_time=max_time - min_time
        )

        view_state = pdk.ViewState(latitude=mean_lat, longitude=mean_lon, zoom=10, bearing=0, pitch=0)
        r = pdk.Deck(layers=[layer], initial_view_state=view_state)
        r.to_html("templates/trips_layer.html")
        return render(request,'trips.html')
    else:
        return render(request, 'spatial.html',{"max_lat":max_lat,"min_lat":min_lat,"max_lon":max_lon,"min_lon":min_lon,"step_lon":step_lon,"step_lat":step_lat,"mean_lon":mean_lon,"mean_lat":mean_lat})


def temporal_(request):
    file_path=os.getcwd()+"\\input\\input.json"
    lon3 = np.float64(request.POST['lon3rangevalue'])
    lon4 = np.float64(request.POST['lon4rangevalue'])
    lat3 = np.float64(request.POST['lat3rangevalue'])
    lat4 = np.float64(request.POST['lat4rangevalue'])
    st_time = int(request.POST['time1rangevalue'])
    en_time = int(request.POST['time2rangevalue'])
    x = {
        "latitude_minimum": lat3,
        "longitude_minimum": lon3,
        "latitude_maximum": lat4,
        "longitude_maximum": lon4,
        "start_time": st_time,
        "end_time": en_time,
        "path": file_path
	}
    x=json.dumps(x)
    header = {'Content-Type':'application/json'}
    response=requests.get('http://127.0.0.1:8080/get-spatiotemporal-range', headers=header, data=x)
    response_data=response.json()
    
    new_json=[]
    for i in response_data['ids']:
        k=[]
        for j in range(len(i['timestamp'])):
            k.append({"coordinates":[i['location'][j][1], i['location'][j][0]], "timestamp":i['timestamp'][j]})
        new_json.append({"id":i['trajectory_id'], "waypoints":k})

    min_time_stamp, max_time_stamp = calculate_min_max_timestamp(new_json)

    with open('json_data.json', 'w') as outfile:
        outfile.write(json.dumps(new_json))
    df = pd.read_json("json_data.json")
    if df.shape[0] != 0:
        df["coordinates"] = df["waypoints"].apply(lambda f: [item["coordinates"] for item in f])
        df["timestamps"] = df["waypoints"].apply(lambda f: [item["timestamp"] - min_time_stamp for item in f])
        df.drop(["waypoints"], axis=1, inplace=True)
        color_lookup = pdk.data_utils.assign_random_colors(df['id'])
        df['color'] = df.apply(lambda row: color_lookup.get(str(row['id'])), axis=1)

        layer = pdk.Layer(
            "TripsLayer",
            df,
            get_path="coordinates",
            get_timestamps="timestamps",
            get_color="color",
            opacity=0.8,
            width_min_pixels=5,
            rounded=True,
            trail_length=max_time_stamp - min_time_stamp,
            current_time=max_time_stamp - min_time_stamp
        )
        view_state = pdk.ViewState(latitude=mean_lat, longitude=mean_lon, zoom=10, bearing=0, pitch=0)
        r = pdk.Deck(layers=[layer], initial_view_state=view_state)
        r.to_html("templates/trips_layer.html")
        return render(request,'trips.html')
    else:
        return render(request, 'temporal.html', {"max_lat":max_lat,"min_lat":min_lat,"max_lon":max_lon,"min_lon":min_lon,"step_lon":step_lon,"step_lat":step_lat,"mean_lon":mean_lon,"mean_lat":mean_lat,"min_time":min_time,"max_time":max_time})   

def knn_(request):
    file_path=os.getcwd()+"\\input\\input.json"
    trac_id_1 = int(request.POST['trac1rangevalue'])
    k_1 = int(request.POST['kval1rangevalue'])
    x = {
        "trajectory_id":trac_id_1,
        "k_neighbours":k_1,
        "path":file_path
    }
    x=json.dumps(x)
    header = {'Content-Type':'application/json'}
    response=requests.get('http://127.0.0.1:8080/get-knn', headers=header, data=x)
    response_data=response.json()
    
    newn_json = []
    file = open(file_path)
    json_obj = json.load(file)
    for i in response_data['ids']:
        id = i['trajectory_id']
        for j in json_obj:
            if j['trajectory_id'] == id:
                newn_json.append(j)
    newn_json = {"ids":newn_json}

    new_json=[]
    for i in newn_json['ids']:
        k=[]
        for j in i['trajectory']:
            k.append({"coordinates":[j['location'][1], j['location'][0]], "timestamp":j['timestamp']})
        new_json.append({"id":i['trajectory_id'], "waypoints":k})

    min_time_stamp, max_time_stamp = calculate_min_max_timestamp(new_json)

    with open('json_data.json', 'w') as outfile:
        outfile.write(json.dumps(new_json))

    df = pd.read_json("json_data.json")
    df["coordinates"] = df["waypoints"].apply(lambda f: [item["coordinates"] for item in f])
    df["timestamps"] = df["waypoints"].apply(lambda f: [item["timestamp"] - min_time_stamp for item in f])
    
    df.drop(["waypoints"], axis=1, inplace=True)

    color_lookup = pdk.data_utils.assign_random_colors(df['id'])
    df['color'] = df.apply(lambda row: color_lookup.get(str(row['id'])), axis=1)

    layer = pdk.Layer(
        "TripsLayer",
        df,
        get_path="coordinates",
        get_timestamps="timestamps",
        get_color="color",
        opacity=0.8,
        width_min_pixels=5,
        rounded=True,
        trail_length=max_time - min_time,
        current_time=max_time - min_time
    )

    view_state = pdk.ViewState(latitude=mean_lat, longitude=mean_lon, zoom=10, bearing=0, pitch=0)
    r = pdk.Deck(layers=[layer], initial_view_state=view_state)
    r.to_html("templates/trips_layer.html")
    return render(request,'trips.html')
