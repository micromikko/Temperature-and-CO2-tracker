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

#pyboard_main.py sisältää MicroPythonin päässä suoritettavan ohjelman, jonka vastuulla ovat lämpötila- ja hiilidioksidiantureiden
#lukeminen, niiden datan muuntaminen yleisesti käytettyihin yksikköihin, aikaleiman luominen, sekä näiden lähettäminen Raspberry Pi:lle.


import pyb
from pyb import Pin, ADC


def read_temp_step(adc_temp):
	"""Read and return temp data from pin X1."""
	temp_step = str(adc_temp.read())
	return temp_step


def read_CO2_step(adc_CO2):
	"""Read and return CO2 data from pin X2."""
	CO2_step = str(adc_CO2.read())
	return CO2_step


def temp_step_to_celcius(temp_step):
	"""Calculates and returns the step readings in Celcius."""
	R_kty = 1780*temp_step/(4095 - temp_step)
	temp_celcius = 25-((2000-R_kty)/16)
	return temp_celcius


def CO2_step_to_ppm(CO2_step):
	"""Calculates and returns a value in a similar fashion to out temp_step_to_celcius() function."""
	return CO2_ppm


def bletykki(datetime, temp_average, CO2_average):
	"""Gathers datetime (the timestamp), temp_average and CO2_average into a single 20 character string. Sends said string using BLE.""""
	packet = "{}{}{}".format(datetime, temp_average, CO2_average)
	#***send packet with BLE***


def get_time():
	"""Creates and return timestamp in format ddmmyyHHMMSS using pyb.RTC."""
	rtc = pyb.RTC()
	dt_year, dt_month, dt_day, dt_weekday, dt_hour, dt_min, dt_sec, dt_subsec = rtc.datetime()
	dt_year = int(str(dt_year)[2:4])
	timestamp = "{0:02d}{1:02d}{2:02d}{3:02d}{4:02d}{5:02d}".format(dt_day, dt_month, dt_year, dt_hour, dt_min, dt_sec)
	return timestamp


def main():
	adc_temp = pyb.ADC(Pin('X1'))									#Creates an ADC on pin X1 and assigns it to a variable
	adc_CO2 = pyb.ADC(Pin('X2'))									#Creates an ADC on pin X2 and assigns it to a variable
	temp_list = []													#Creates an empty list for temperature values
	CO2_list = []													#Creates and empty list for CO2 values
	while True:
		temp_step = read_temp_step(adc_temp)						#Read temp value from pin X1 and assign it to temp_step
		temp_now = temp_step_to_celcius(temp_step)					#Calculate the Celcius value from temp_step
		temp_list.append(temp_now)									#Add temp_now value to temp_list
		CO2_step = read_temp_step(adc_CO2)							#Read CO2 value from pin X2
		CO2_now = CO2_step_to_ppm(CO2_step)							#Calculate the CO2 ppm value from CO2_step
		CO2_list.append(CO2_now)									#Add CO2_now value to CO2_list
		pyb.delay(1000)												#1 second delay
		if len(temp_list) and len(CO2_list) == 60:					#The following block is excecuted when both lists are filled with 60 values
			datetime = get_time()									#Gets the current time using PyBoards Real Time Clock. Converts time to string formatted "ddmmyyHHMMSS"
			temp_average = sum(temp_list) / len(temp_list)			#Calculates the average temperature of the list (sum of values / 60)
			temp_average = "{0:4.1f}".format(temp_average)			#Temperature average to format xx.x
			CO2_average = sum(CO2_list) / len(CO2_list)				#Calculates the average temperature of the list (sum of values / 60)
			CO2_average = "{0:04d}".format(CO2_average)				#CO2 average to format xxxx
			bletykki(datetime, temp_average, CO2_average)			#Sends packet ("ddmmyyHHMMSSttttcccc") using BLE.
			temp_list = []
			CO2_list = []


if __name__ == "__main__":
	main()