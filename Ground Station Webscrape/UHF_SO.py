import time
start = time.time()
print('UHF_SO.py is running. It should take about 30 seconds to collect station info')

from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from array import *

#go to the main ground station list
my_url = 'https://network.satnogs.org/stations/'
#read the page, store data, and close it
uClient = uReq(my_url)
page_html = uClient.read()
uClient.close()
#pull out the data from page of the currently online ground stations
page_soup = soup(page_html, "html.parser")
containers = page_soup.findAll("span",{"class":"station label label-online"})
#loop that will print out each online ground station number
#FUTURE array (ideally CSV file, doesn not currently do that)
a = 0
b = len(containers)
stations = array('i',[len(containers)])
while a < b:

	station = containers[a].text
	station_array = station.split()
	station_num = ''.join(station_array)
	# print(station_num)
	station_num_int=int(station_num)
	stations.append(station_num_int)
	a += 1

#ground station array currently comes from s_n.py script by copying output, pasting in excel and transforming data from 1xn array to nx1 array with , added after each #
#FUTURE import/create an array from s_n CSV output

#loop that will go through the pages of each ground station 1 by 1
end = time.time()
print('It took ',int(end - start), 'seconds for scan to complete.')

if b==0:
	print('There are no stations online. Check https://status.libre.space/')
else:
	print('There are '+ str(b) + ' stations online! Do you want to use selection criteria? Y for yes, otherwise just hit enter.')
	selection=str(input())
	if 'y' in selection or 'Y' in selection:
		min_alt_selection=input('Min Alt AGL (m) [if none, hit enter]:')
		if min_alt_selection =='':
			min_alt_selection = 0
		else:
			min_alt_selection=int(min_alt_selection)
		min_horizon_selection=input('Min Horizion (°) [if none, hit enter]:')
		if min_horizon_selection =='':
			min_horizon_selection = 0
		else:
			min_horizon_selection=int(min_horizon_selection)
		ant_type_selection=input("Select antenna type (H/V/U/L/S) [if none, hit enter]:")
		if ant_type_selection =='':
			antenna_type=0
		elif ant_type_selection == 'H' or ant_type_selection == 'h':
			antenna_type = '(HF'
		elif ant_type_selection == 'V' or ant_type_selection == 'v':
			antenna_type = 'VHF'
		elif ant_type_selection == 'U' or ant_type_selection == 'u':
			antenna_type = 'UHF'
		elif ant_type_selection == 'L' or ant_type_selection == 'l':
			antenna_type = 'L'
		elif ant_type_selection == 'S' or ant_type_selection == 's':
			antenna_type = '(S'
		else:
			antenna_type=0
			print('Invalid input selected for antenna type. No antenna type selected.')
	else:
		min_alt_selection=0
		min_horizon_selection=0
		antenna_type=0
alt_skip_counter=0
hor_skip_counter=0
ant_skip_counter=0		
print('Station |Coordinates \t\t|Alt AGL m|Min Hor °|Antenna Type \t\t\t\t\t\t\t\t     |URL')
a=0
b=len(stations)
while a <= b:
	a += 1
	#need to convert integer to string for combining it with URL
	if a == len(stations):
		break
	sta_num=stations[a]
	sta_num_str=str(sta_num)
	
	#goes to the page for a particular ground station
	my_url = "https://network.satnogs.org/stations/"+sta_num_str+"/"

	#read the page, store data, and close it
	uClient = uReq(my_url)
	page_html = uClient.read()
	uClient.close()

	#pull out the data from page of the currently online ground stations
	page_soup = soup(page_html, "html.parser")
	containers = page_soup.findAll("span",{"class":"front-data"})

	#next 4 lines have been commented out, but were originally intended to be used for creating CSV file headers 
	#filename="gs.csv"
	#f = open(filename, "w")
	#headers = ("coordinates, altitude,min_horizon,success_rate,antenna1,antenna2,antenna3,antenna4,antenna5\n")
	#f.write(headers)

	#stores values from page for each variable, using text.strip to get rid of unneeded information
	coordinates = containers[2].text.strip()
	coordinates = coordinates.replace(',',"/")
	altitude = containers[3].text.strip()
	altitude = altitude.replace(" m","") #remove m
	altitude = int(altitude)
	if altitude < min_alt_selection:
		alt_skip_counter=alt_skip_counter+1
		print('Min altitude selection criteria skip',alt_skip_counter, end="\r")
		continue
	min_horizon = containers[4].text.strip()
	min_horizon = min_horizon.replace("°","") #remove degree symbol
	min_horizon = int(min_horizon)
	if min_horizon < min_horizon_selection:
		hor_skip_counter=hor_skip_counter+1
		print('Min horizon selection criteria skip',hor_skip_counter, end="\r")
		continue
	container=containers[6].text
	if container.find('%') != -1:
		container=containers[5].text
	container1=container.replace('\n','')
	container2=container1.replace(' ','')
	container3=container2.replace('(',' ')
	container4=container3.split(')')
	container4=container4[:-1]
	ant_str= ','.join(container4)
	if antenna_type != 0:
		if antenna_type in container:
			ant_str = ant_str
		else:
			ant_skip_counter=ant_skip_counter+1
			print('Antenna selection criteria skip',ant_skip_counter, end="\r")
			continue

	#next 5 lines have been commented out, print all the information in one line instead further down
	#print(coordinates)
	#print(altitude)
	#print(min_horizon)
	#print(success_rate)
	#print(ant_str)

	#next line was commented out, again was originally for storing data in CSV file but each successive ground station overwrote previous
	#f.write(coordinates + "," + altitude + "," + min_horizon + "," + ant_str+ "\n")
	#print out all the ground station info
	print ('{: <8}'.format(sta_num_str) + "|" + '{: <23}'.format(coordinates) + "|" + '{: <9}'.format(altitude) + "|" + '{: <9}'.format(min_horizon) + "|" + '{: <80}'.format(ant_str) + "|" + my_url)
	#end the loop when all ground stations have been run through
print('\n End of list.')
	
#next line was comment out, again was originally for closing CSV file
#f.close()