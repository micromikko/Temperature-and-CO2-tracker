#L.Ä.H.I.A.P.U, eli
#LÄmpötilaa ja HIilidioksidia mittaava Anturoitu PUolinainen varoitusjärjestelmä

#Ryhmä 4, "Älykköjen liiga"
#Hyttinen, Simo
#Kontas, Joel
#Peltola, Mikko
#Virta, Juho

#Koodia tulisi tarkastella siitä näkökulmasta, että olisimme saaneet käyttöömme CO2-anturin ja toimivan BLE-järjestelmän.
#Olemme kuitenkin kirjoittaneet kyseisiä toimintoja ja osia varten funktioita, joiden kuvaukset kertovat niiden suorittamista tehtävistä
#ja jotta laitteen toiminnan yleiskuva hahmottuisi paremmin.

#raspi_main.py sisältää Raspberry Pi:n päässä suoritettavan ohjelman, jonka harteilla ovat sekä vastaanotetun datan tallentaminen
#että varoitussähköpostin lähettäminen lämpötila- tai hiilidioksidiarvojen kohotessa asettamiemme rajonen yläpuolelle.

#RRDtoolin käyttöä koskevat funktiot ovat sen dokumentoinnista lainattuja.
#http://oss.oetiker.ch/rrdtool/doc/index.en.html

#Sähköpostin lähettävä funktio on usean lähteen pohjalta kasattu.

#Lainattuja funktioita:
#createRRD()
#addData()
#tempgraph
#CO2graph


import subprocess
import time
import math
import random
import smtplib
import datetime
from email.mime.text import MIMEText


def catcher(packet):
	"""Recieves/intercepts a string from the bletykki function, slices it into bits and assigns it to 3 variables. Returns a tuple containing said variables."""
	#Recieves a 20 character string from PyBoard formatted "ddmmyyHHMMSSttttcccc"
	#assigns the string to a variable called "packet"
	p_datetime = packet[:12]
	p_temp = float(packet[12:16])
	p_CO2 = int(packet[16:])
	return (p_datetime, p_temp, p_CO2)


def check_level(p_temp, p_CO2):
	"""Checks temperature and CO2 and sets their levels accordingly. 0 = "green", 1 = "yellow", and 2 = "red"."""
	if p_temp < 23:
		temp_level = 0
	elif p_temp >= 23 and p_temp < 27:
		temp_level = 1
	elif p_temp >= 27:
		temp_level = 2

	if p_CO2 < 1500:
		CO2_level = 0
	elif p_CO2 >= 1500 and p_CO2 < 2000:
		CO2_level =1
	elif p_CO2 >= 2000:
		CO2_level = 2
	
	return (temp_level, CO2_level)

	
def temp_warning(p_temp, temp_level):
	"""Determines the level of temperature warning to send using the email() function."""
	if temp_level == 1:
		defcon = "Defcon Yellow"
		message = "Defcon: Yellow. The class' temperature is uncomfortably hot at {} degrees Celcius. Are you sweating yet?".format(str(p_temp))
		email(defcon, message)
		prev_level = temp_level
		return prev_level
	elif temp_level == 2:
		defcon = "Defcon Red"
		message = "Defcon: Red. The temperature is {} degrees Celcius... Kinda like a crematorium.".format(str(p_temp))
		email(defcon, message)
		prev_level = temp_level
		return prev_level


def CO2_warning(p_CO2, CO2_level):
	"""Determines the level of CO2 warning to send using the email() function."""
	if CO2_level == 1:
		defcon = "Defcon Yellow"
		message = "Defcon: Yellow. The carbon dioxide level is at {} ppm. Get ready for a sweet headache!".format(str(p_CO2))
		email(defcon, message)
		CO2_prev = CO2_level
		return CO2_prev
	elif CO2_level == 2:
		defcon = "Defcon Red"
		message = "Defcon: Red. The carbon dioxide level is at {} ppm. Blissful unconsciousness is just around the corner!".format(str(p_CO2))
		email(defcon, message)
		CO2_prev = CO2_level
		return CO2_prev
		

def email(defcon, message):
	"""Responsible for sending the warning in question."""
	addr_to = "ryhma4laitteet@gmail.com"
	addr_from = "mittari@diibaduu.asd"

	smtp_server = "smtp.metropolia.fi"

	msg = MIMEText(message)
	msg['To'] = addr_to
	msg['From'] = addr_from
	msg['Subject'] = defcon

	s = smtplib.SMTP(smtp_server)
	s.sendmail(addr_from, addr_to, msg.as_string())
	s.quit()


def createRRD():
	"""Creates the RRD database used in the program."""
	subprocess.call(['rrdtool', 'create', 'test.rrd', '--step', '60',
					'DS:temp:GAUGE:120:0:50',
					'DS:CO2:GAUGE:120:0:3000',
					'RRA:MAX:0.5:1:1440' ])

					 
def addData(time, temperature, CO2):
	"""Adds temperature and CO2 data to the database with a timestamp."""
	subprocess.call(['rrdtool', 'update', 'test.rrd',  
					str(time)+':'+ str(temperature)+':'+ str(CO2) ])


def tempgraph(startTime, endTime):
	"""Draws a temperature graph."""
	subprocess.call(['rrdtool', 'graph', 'temptest.png', 
					'-w', '1000', '-h', '400',
					'--start', str(int(startTime)), 
					'--end', str(int(endTime)), 
					'DEF:temperature=test.rrd:temp:MAX', 
					'LINE1:temperature#ff0000:Temp',] )

					 
def CO2graph(startTime, endTime):
	"""Draws a CO2 graph."""
	subprocess.call(['rrdtool', 'graph', 'CO2test.png', 
					'-w', '1000', '-h', '400',
					'--start', str(int(startTime)), 
					'--end', str(int(endTime)), 
					'DEF:CO2=test.rrd:CO2:MAX',
					'LINE2:CO2#00ff00:CO2'] )

					

					

def main():
	start = time.time()											#Assigns the start time
	end = start + 24 * 60 * 60									#Assigns the end time 24 hours from start
	createRRD()
	temp_prev = 0												#Sets the "previous" temp level to zero, even though this is the first run.
	CO2_prev = 0												#Sets the "previous" CO2 level to zero, even though this is the first run.
	while True:
		p_datetime, p_temp, p_CO2 = catcher(packet) 			#Assigns three variables from the sliced "packet" string.
		addData(datetime, temp, CO2)							#Adds the previously extracted variables to the RRD database
		temp_level, CO2_level = check_level(p_temp, p_CO2)		#Checkss and assigns the current levels to temp and CO2 (levels: 0 = green, 1 = yellow, 2 = red)
		if temp_level > temp_prev:								#If the temperature as increased to the next level, the warning function is excecuted (sending an email depending on the level)
			temp_prev = temp_warning(p_temp, temp_level)
		elif temp_level < temp_prev:							#If the level is smaller than before, it's assigned the appropriate value
			temp_prev = temp_level
		
		if CO2_level > CO2_prev:								#If the temperature as increased to the next level, the warning function is excecuted (sending an email depending on the level)
			CO2_prev = CO2_warning(p_CO2, CO2_level)
		elif CO2_level < CO2_prev:								#If the level is smaller than before, it's assigned the appropriate value
			CO2_prev = CO2_level
		
		if time.time() >= end:
			tempgraph(start, end)								#Draws a temperature graph of the previous 24 hours (1 sample per minute)
			CO2graph(start, end)								#Draws a CO2 graph of the previous 24 hours (1 sample per minute)
			start = time.time()									#Resets the "timer" that produces the graphs
			end = start + 24 * 60 * 60

if __name__ == "__main__":
	main()