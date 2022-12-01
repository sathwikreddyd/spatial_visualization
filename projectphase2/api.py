from flask import Flask, jsonify, request
import subprocess, os, json, re

app = Flask(__name__)

@app.route('/')
def intitialize():
	return 'Welcome to PyDeck Visualization API for specific queries. Submit your queries using commands'

@app.route('/get-knn')
def  get_knn():

	'''
	{
    "trajectory_id": 0,
    "k_neighbours": 6,
    "path": "C:\\Users\\sdontham\\Documents\\College\\Assignments\\Rough\\CSE594\\proj 2\\sdse\\data"
	}
	'''

	data = request.get_json()
	trajectory_id = data['trajectory_id']
	k = data['k_neighbours']
	path_to_input = data['path']
	'''spark_args = {
		'name': 'spark_job_client',
		'main_file_args': '"' + os.getcwd().replace('\\\\','\\') + '/sdse/target/scala-2.12/SDSE-Phase-1-assembly-0.1.jar"'
	}'''
	
	job = ('spark-submit "' + re.sub(r"\\\\",r"\\",os.getcwd()) 
			+ '\\sdse\\target\\scala-2.12\\SDSE-Phase-1-assembly-0.1.jar" "' 
			+ path_to_input + '" "' + re.sub(r"\\\\",r"\\",os.getcwd()) 
			+ '\\sdse\\data\\output"' + ' get-knn ' + str(trajectory_id) 
			+ ' ' + str(k))
	
	subprocess.Popen(job, shell=True).wait()
	out_file = 0
	for file in os.listdir('sdse/data/output/get-knn'):
		if file.endswith(".json"):
			out_file = open('sdse/data/output/get-knn/' + file)
			break
	jsons = []
	for i in out_file:
		json_ = json.loads(i)
		jsons.append(json_)
	return jsonify({'ids':jsons})

@app.route('/get-spatial-range')
def get_spatial_range():

	'''
	{
    "latitude_minimum": 33.41415667570768,
    "longitude_minimum": -111.92518396810091,
    "latitude_maximum": 33.414291502635706,
    "longitude_maximum": -111.92254858414022,
    "path": "C:\\Users\\sdontham\\Documents\\College\\Assignments\\Rough\\CSE594\\proj 2\\sdse\\data\\simulated_trajectories.json"
	}
	'''

	data = request.get_json()
	lat_min = data['latitude_minimum']
	lat_max = data['latitude_maximum']
	lon_min = data['longitude_minimum']
	lon_max = data['longitude_maximum']
	path_to_input = data['path']

	job = ('spark-submit "' + re.sub(r"\\\\",r"\\",os.getcwd()) 
			+ '\\sdse\\target\\scala-2.12\\SDSE-Phase-1-assembly-0.1.jar" "' 
			+ path_to_input + '" "' + re.sub(r"\\\\",r"\\",os.getcwd()) 
			+ '\\sdse\\data\\output"' + " get-spatial-range "
			+ str(lat_min) + ' ' + str(lon_min) + ' '
			+ str(lat_max) + ' ' + str(lon_max))
	
	subprocess.Popen(job, shell=True).wait()
	out_file = 0
	for file in os.listdir('sdse/data/output/get-spatial-range'):
		if file.endswith(".json"):
			out_file = open('sdse/data/output/get-spatial-range/' + file)
			break
	jsons = []
	for i in out_file:
		json_ = json.loads(i)
		jsons.append(json_)
	return jsonify({'ids':jsons})

@app.route('/get-spatiotemporal-range')
def get_spatiotemporal_range():

	'''
	{
    "start_time": 1664511371,
    "end_time": 1664512676,
    "latitude_minimum": 33.41415667570768,
    "longitude_minimum": -111.92518396810091,
    "latitude_maximum": 33.414291502635706,
    "longitude_maximum": -111.92254858414022,
    "path": "C:\\Users\\sdontham\\Documents\\College\\Assignments\\Rough\\CSE594\\proj 2\\sdse\\data\\simulated_trajectories.json"
	}
	'''

	data = request.get_json()
	start_time = data['start_time']
	end_time = data['end_time']
	lat_min = data['latitude_minimum']
	lat_max = data['latitude_maximum']
	lon_min = data['longitude_minimum']
	lon_max = data['longitude_maximum']
	path_to_input = data['path']

	job = ('spark-submit "' + re.sub(r"\\\\",r"\\",os.getcwd()) 
			+ '\\sdse\\target\\scala-2.12\\SDSE-Phase-1-assembly-0.1.jar" "' 
			+ path_to_input + '" "' + re.sub(r"\\\\",r"\\",os.getcwd()) 
			+ '\\sdse\\data\\output"' + " get-spatiotemporal-range "
			+ str(start_time) + ' ' + str(end_time) + ' '
			+ str(lat_min) + ' ' + str(lon_min) + ' '
			+ str(lat_max) + ' ' + str(lon_max))
	
	subprocess.Popen(job, shell=True).wait()
	out_file = 0
	for file in os.listdir('sdse/data/output/get-spatiotemporal-range'):
		if file.endswith(".json"):
			out_file = open('sdse/data/output/get-spatiotemporal-range/' + file)
			break
	jsons = []
	for i in out_file:
		json_ = json.loads(i)
		jsons.append(json_)
	return jsonify({'ids':jsons})

	
if __name__ == '__main__':
	app.run(debug = True, port = 8080)