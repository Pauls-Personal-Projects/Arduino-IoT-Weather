#!/usr/bin/env python3
# -*- coding: utf-8 -*-

####################################################################################################
#																								   #
#											ILMATEATAJA											   #
#																								   #
####################################################################################################
'''
Looja:		Paul J. Aru		-	https://github.com/paulpall
Kuupäev:	06/07/2021
Uuendatud:	13/06/2022
------------------------------------------------------------
Käsurealt kasutamiseks:
	$ ALGUS="2019-05-01T00:00Z" LÕPP="2019-06-01T00:00Z" \
		python Ilmateataja.py
------------------------------------------------------------
Tänud Adam Bachman, download_paged_data.py jagamise eest!
Link: https://gist.github.com/abachman/12df0b34503edd5692be22f6b9695539
'''



####################################################################################################
#	TEEGID																						   #
####################################################################################################
from datetime import datetime, timezone, timedelta	# Kuupäevade Teisendamiseks
from dateutil import tz								# Kuupäevade Teisendamiseks
import tweepy										# Twitteris Säutsumiseks
import matplotlib.pyplot as joonestus				# Näitude Joonestamiseks
import matplotlib.ticker as osuti					# Näitude Joonestamiseks
import matplotlib.dates as kuupäevad				# Näitude Joonestamiseks
import time
import os
import urllib.parse									# Adafruit IO'st Näitude Allalaadimiseks
import http.client									# Adafruit IO'st Näitude Allalaadimiseks
import json											# Adafruit IO'st Näitude Allalaadimiseks
import re



####################################################################################################
#	SÄTTED																						   #
####################################################################################################

### PEIDA ENNE GIT'i LAADIMIST ###
AIO_Kasutaja = ""
AIO_Võti = ""
Twitteri_API_Võti = ""
Twitteri_API_Saladus = ""
Twitteri_Ligipääsu_Token = ""
Twitteri_Ligipääsu_Saladus = ""
### PEIDA ENNE GIT'i LAADIMIST ###

#Ajavahemik Ilmanäitudest mida Adafruit'i Päringuks Kasutatakse (Viimase Kuu Näidud Saadaval)
lõppAeg = datetime.utcnow().astimezone().replace(tzinfo=tz.tzutc()).astimezone(tz.gettz('Europe/Tallinn'))
algAeg = lõppAeg-timedelta(days=13.5)
#Ajavahemik Millest Detailne Analüüs Vahetub Päeva-Keskmisele Üle:
analüüsiAjaPiirmäär = timedelta(days=2.5)
#Kõik Elemendid mis mu Ilmajaam Hetkel Mõõdab:
ilmaElemendid = ["temperature","humidity","pressure"]
#Piirmäärad Imelike Näitude Eemaldamiseks:
piirmäärad = {"ülem-temperature":100.00, "alam-temperature":-100.00,#°C
				"ülem-humidity":100.00, "alam-humidity":0.00,		#%
				"ülem-pressure":1100.00, "alam-pressure":900.00}	#hPa





####################################################################################################
#	TUGIFUNKTSIOONID																			   #
####################################################################################################



def säutsuTwitteris(tekst,pilt):
	autentsus = tweepy.OAuthHandler(Twitteri_API_Võti, Twitteri_API_Saladus)
	autentsus.set_access_token(Twitteri_Ligipääsu_Token, Twitteri_Ligipääsu_Saladus)
	twitter = tweepy.API(autentsus)
	üleslaetudPilt = twitter.media_upload(pilt)
	twitter.update_status(status=tekst, media_ids=[üleslaetudPilt.media_id])
	print("Twitterisse Säutsutud")



def ilmaStatistika(ilmaAndmed):
	'''
	Vaatab üle kõik näidud ja otsib välja huvitava!
	'''
	tekst=algAeg.strftime("%d.%m.%Y(%H:%M) - ")+lõppAeg.strftime("%d.%m.%Y(%H:%M)\n\n")
	tekst+="#Temperatuur\n"
	tekst+=("🔥 "+str(ilmaAndmed["temperature"]["statistika"]["kõrgeim"])+"°C ("+ilmaAndmed["temperature"]["statistika"]["kõrgeim-aeg"].strftime("%d.%m %H:%M")+")\n")
	tekst+=("❄️ "+str(ilmaAndmed["temperature"]["statistika"]["madalaim"])+"°C ("+ilmaAndmed["temperature"]["statistika"]["madalaim-aeg"].strftime("%d.%m %H:%M")+")\n")
	# Lühiajaline: Temperatuuri Keskmine
	if lõppAeg-algAeg < analüüsiAjaPiirmäär:
		tekst+=("📊 "+str(round((ilmaAndmed["temperature"]["statistika"]["summa"]/ilmaAndmed["temperature"]["statistika"]["summa-hulk"]),2))+"°C (keskmine)\n\n")
	# Pikaajaline: Keskmise Temperatuuri Muutus
	else:
		i=0
		esimeseOsaKeskmine=0
		teiseOsaKeskmine=0
		while i < (len(ilmaAndmed["temperature"]["aeg"])/2):
			esimeseOsaKeskmine += ilmaAndmed["temperature"]["näit"][i]
			i+=1
		esimeseOsaKeskmine=esimeseOsaKeskmine/(len(ilmaAndmed["temperature"]["aeg"])/2)
		if ((len(ilmaAndmed["temperature"]["aeg"])/2) % 2) != 0:
			i=i-1
		while i < (len(ilmaAndmed["temperature"]["aeg"])):
			teiseOsaKeskmine += ilmaAndmed["temperature"]["näit"][i]
			i+=1
		teiseOsaKeskmine=teiseOsaKeskmine/(len(ilmaAndmed["temperature"]["aeg"])/2)
		temperatuuriMuutus=teiseOsaKeskmine-esimeseOsaKeskmine
		if temperatuuriMuutus>0:
			tekst+=("📈 +"+str(round(temperatuuriMuutus,2))+"°C (viimasel "+str(round(len(ilmaAndmed["temperature"]["aeg"])/2))+". päeval)\n\n")
		else:
			tekst+=("📉 "+str(round(temperatuuriMuutus,2))+"°C (viimasel "+str(round(len(ilmaAndmed["temperature"]["aeg"])/2))+". päeval)\n\n")
	
	tekst+="#Niiskus\n"
	tekst+=("🌧 "+str(ilmaAndmed["humidity"]["statistika"]["kõrgeim"])+"% ("+ilmaAndmed["humidity"]["statistika"]["kõrgeim-aeg"].strftime("%d.%m %H:%M")+")\n")
	tekst+=("☀️ "+str(ilmaAndmed["humidity"]["statistika"]["madalaim"])+"% ("+ilmaAndmed["humidity"]["statistika"]["madalaim-aeg"].strftime("%d.%m %H:%M")+")\n")
	if lõppAeg-algAeg < analüüsiAjaPiirmäär:
		tekst+=("📊 "+str(round((ilmaAndmed["humidity"]["statistika"]["summa"]/ilmaAndmed["humidity"]["statistika"]["summa-hulk"]),2))+"% (keskmine)\n\n")
	else:
		i=0
		esimeseOsaKeskmine=0
		teiseOsaKeskmine=0
		while i < (len(ilmaAndmed["humidity"]["aeg"])/2):
			esimeseOsaKeskmine += ilmaAndmed["humidity"]["näit"][i]
			i+=1
		esimeseOsaKeskmine=esimeseOsaKeskmine/(len(ilmaAndmed["humidity"]["aeg"])/2)
		if ((len(ilmaAndmed["humidity"]["aeg"])/2) % 2) != 0:
			i=i-1
		while i < (len(ilmaAndmed["humidity"]["aeg"])):
			teiseOsaKeskmine += ilmaAndmed["humidity"]["näit"][i]
			i+=1
		teiseOsaKeskmine=teiseOsaKeskmine/(len(ilmaAndmed["humidity"]["aeg"])/2)
		temperatuuriMuutus=teiseOsaKeskmine-esimeseOsaKeskmine
		if temperatuuriMuutus>0:
			tekst+=("📈 +"+str(round(temperatuuriMuutus,2))+"% (viimasel "+str(round(len(ilmaAndmed["humidity"]["aeg"])/2))+". päeval)\n\n")
		else:
			tekst+=("📉 "+str(round(temperatuuriMuutus,2))+"% (viimasel "+str(round(len(ilmaAndmed["humidity"]["aeg"])/2))+". päeval)\n\n")
	
	tekst+="#Õhurõhk\n"
	tekst+=("🌫 "+str(ilmaAndmed["pressure"]["statistika"]["madalaim"])+"-"+str(ilmaAndmed["pressure"]["statistika"]["kõrgeim"])+"hPa\n")
	tekst+=("📊 "+str(round((ilmaAndmed["pressure"]["statistika"]["summa"]/ilmaAndmed["pressure"]["statistika"]["summa-hulk"]),2))+"hPa (keskmine)")

	return tekst



def joonestaNäidud(ilmaAndmed):
	'''
	Joonestab visuaalse ülevaate näitudest
	'''
	# Tugi Funktsioonid:
	def temperatuuriVorming(x, pos):
		return '{:1.0f}°C'.format(x)
	def niiskuseVorming(x, pos):
		return '{:1.0f}%'.format(x)
	def õhurõhuVorming(x, pos):
		return '{:1.0f}hPa'.format(x)
	def ajaVorming(x, pos=None):
		x = kuupäevad.num2date(x).astimezone(tz.gettz('Europe/Tallinn'))
		label = x.strftime('%H:%M.%f')
		label = label.rstrip("0")
		label = label.rstrip(".")
		return label
	def kuupäevaVorming(x, pos=None):
		x = kuupäevad.num2date(x).astimezone(tz.gettz('Europe/Tallinn'))
		label = x.strftime('%d.%m')
		return label
	
	# Joonestuste Loomine ja Vormimine:
	ilmaJoonestused, (temperatuuriJoonestus, niiskusJoonestus, õhurõhuJoonestus) = joonestus.subplots(3, 1)
	ilmaJoonestused.tight_layout(pad=3)
	temperatuuriJoonestus.yaxis.set_major_formatter(osuti.FuncFormatter(temperatuuriVorming))
	temperatuuriJoonestus.set_title('Temperatuur')
	niiskusJoonestus.yaxis.set_major_formatter(osuti.FuncFormatter(niiskuseVorming))
	niiskusJoonestus.set_title('Niiskus')
	õhurõhuJoonestus.yaxis.set_major_formatter(osuti.FuncFormatter(õhurõhuVorming))
	õhurõhuJoonestus.set_title('Õhurõhk')
	
	joonestusAndmed = {"temperature":{
							"aeg":[],			# Kuupäev ja Aeg Millal Temperatuuri Mõõdeti
							"näit":[],			# Temperatuuri Näit Kraadides/ Temperatuuri Keskmine Päevas
							"näit-hulk":[],		# Päeva Keskmise Arvutamiseks, Näitude Hulk
							"näit-kõrge":[],	# Päeva Keskmise Joonestamiseks, Kõrgeim Näit Igal Päeval
							"näit-madal":[],	# Päeva Keskmise Joonestamiseks, Madalaim Näit Igal Päeval
							"statistika":{		# Statistika Trükkimiseks, Erinevad Faktid
								"kõrgeim":piirmäärad["alam-temperature"],
								"kõrgeim-aeg":datetime(1970, 1, 1, tzinfo=timezone.utc),
								"madalaim":piirmäärad["ülem-temperature"],
								"madalaim-aeg":datetime(1970, 1, 1, tzinfo=timezone.utc),
								"summa":0.00,
								"summa-hulk":0,}},
						"humidity":{
							"aeg":[],
							"näit":[],
							"näit-hulk":[],
							"näit-kõrge":[],
							"näit-madal":[],
							"statistika":{
								"kõrgeim":piirmäärad["alam-humidity"],
								"kõrgeim-aeg":datetime(1970, 1, 1, tzinfo=timezone.utc),
								"madalaim":piirmäärad["ülem-humidity"],
								"madalaim-aeg":datetime(1970, 1, 1, tzinfo=timezone.utc),
								"summa":0.00,
								"summa-hulk":0,}},
						"pressure":{
							"aeg":[],
							"näit":[],
							"näit-hulk":[],
							"näit-kõrge":[],
							"näit-madal":[],
							"statistika":{
								"kõrgeim":piirmäärad["alam-pressure"],
								"kõrgeim-aeg":datetime(1970, 1, 1, tzinfo=timezone.utc),
								"madalaim":piirmäärad["ülem-pressure"],
								"madalaim-aeg":datetime(1970, 1, 1, tzinfo=timezone.utc),
								"summa":0.00,
								"summa-hulk":0,}}}
	
	# Detailsete Joonestuste Visandamine:
	if lõppAeg-algAeg < analüüsiAjaPiirmäär:
		for aeg in ilmaAndmed:
			for näidutüüp in ilmaAndmed[aeg]:
				if (ilmaAndmed[aeg][näidutüüp] <= piirmäärad["ülem-"+näidutüüp] and ilmaAndmed[aeg][näidutüüp] >= piirmäärad["alam-"+näidutüüp]):
					eiraNäitu = False
					if joonestusAndmed[näidutüüp]["aeg"] != []:
						if joonestusAndmed[näidutüüp]["aeg"][-1] - aeg >timedelta(minutes=0):
							print("HOIATUS: Eiran "+näidutüüp+" näitu vales asukohas "+joonestusAndmed[näidutüüp]["aeg"][-1].strftime("(eelmine aeg '%d(%H:%M)', ")+aeg.strftime("järgnev aeg '%d(%H:%M)')"))
							eiraNäitu = True
						elif aeg - joonestusAndmed[näidutüüp]["aeg"][-1] >timedelta(minutes=5):
							print("HOIATUS: Puuduvad "+näidutüüp+" näidud ajavahemikus "+joonestusAndmed[näidutüüp]["aeg"][-1].strftime("%d.%m.%Y(%H:%M) - ")+aeg.strftime("%d.%m.%Y(%H:%M)"))
					if not eiraNäitu:
						joonestusAndmed[näidutüüp]["aeg"].append(aeg)
						joonestusAndmed[näidutüüp]["näit"].append(ilmaAndmed[aeg][näidutüüp])
						if ilmaAndmed[aeg][näidutüüp] > joonestusAndmed[näidutüüp]["statistika"]["kõrgeim"]:
							joonestusAndmed[näidutüüp]["statistika"]["kõrgeim"] = ilmaAndmed[aeg][näidutüüp]
							joonestusAndmed[näidutüüp]["statistika"]["kõrgeim-aeg"] = aeg
						if ilmaAndmed[aeg][näidutüüp] < joonestusAndmed[näidutüüp]["statistika"]["madalaim"]:
							joonestusAndmed[näidutüüp]["statistika"]["madalaim"] = ilmaAndmed[aeg][näidutüüp]
							joonestusAndmed[näidutüüp]["statistika"]["madalaim-aeg"] = aeg
						joonestusAndmed[näidutüüp]["statistika"]["summa"] += ilmaAndmed[aeg][näidutüüp]
						joonestusAndmed[näidutüüp]["statistika"]["summa-hulk"] += 1
				else:
					print("HOIATUS: Eiran kahtlast "+näidutüüp+" näitu '"+str(ilmaAndmed[aeg][näidutüüp])+"' ajal "+aeg.strftime("%d.%m.%Y kell %H:%M"))
		
		for detailneJoonis in (temperatuuriJoonestus, niiskusJoonestus, õhurõhuJoonestus):
			detailneJoonis.xaxis.set_major_formatter(osuti.FuncFormatter(ajaVorming))
		temperatuuriJoonestus.set_xlabel(joonestusAndmed["temperature"]["aeg"][-1].strftime("Ajavahemikus %d.%m.%Y(%H:%M) - ")+joonestusAndmed["temperature"]["aeg"][0].strftime("%d.%m.%Y(%H:%M)"))
		niiskusJoonestus.set_xlabel(joonestusAndmed["humidity"]["aeg"][-1].strftime("Ajavahemikus %d.%m.%Y(%H:%M) - ")+joonestusAndmed["humidity"]["aeg"][0].strftime("%d.%m.%Y(%H:%M)"))
		õhurõhuJoonestus.set_xlabel(joonestusAndmed["pressure"]["aeg"][-1].strftime("Ajavahemikus %d.%m.%Y(%H:%M) - ")+joonestusAndmed["pressure"]["aeg"][0].strftime("%d.%m.%Y(%H:%M)"))	
		temperatuuriJoonestus.plot(joonestusAndmed["temperature"]["aeg"], joonestusAndmed["temperature"]["näit"], marker='', color='red', linewidth=1)
		niiskusJoonestus.plot(joonestusAndmed["humidity"]["aeg"], joonestusAndmed["humidity"]["näit"], marker='', color='blue', linewidth=1)
		õhurõhuJoonestus.plot(joonestusAndmed["pressure"]["aeg"], joonestusAndmed["pressure"]["näit"], marker='', color='grey', linewidth=1)
		
	# Päeva-Keskmise Joonestuste Visandamine:
	else:
		for element in ("temperature","humidity"):
			joonestusAndmed[element]["aeg"].append(list(ilmaAndmed.keys())[0])
			joonestusAndmed[element]["näit-kõrge"].append(piirmäärad["alam-"+element])
			joonestusAndmed[element]["näit-madal"].append(piirmäärad["ülem-"+element])
			joonestusAndmed[element]["näit"].append(0)
			joonestusAndmed[element]["näit-hulk"].append(0)
		for aeg in ilmaAndmed:
			if (aeg.year == joonestusAndmed["temperature"]["aeg"][-1].year) and (aeg.month == joonestusAndmed["temperature"]["aeg"][-1].month) and (aeg.day == joonestusAndmed["temperature"]["aeg"][-1].day) and ("temperature" in ilmaAndmed[aeg]):
				if (ilmaAndmed[aeg]["temperature"] <= piirmäärad["ülem-temperature"]) and (ilmaAndmed[aeg]["temperature"] >= piirmäärad["alam-temperature"]):
					if ilmaAndmed[aeg]["temperature"] > joonestusAndmed["temperature"]["näit-kõrge"][-1]:
						joonestusAndmed["temperature"]["näit-kõrge"][-1]=ilmaAndmed[aeg]["temperature"]
					if ilmaAndmed[aeg]["temperature"] < joonestusAndmed["temperature"]["näit-madal"][-1]:
						joonestusAndmed["temperature"]["näit-madal"][-1]=ilmaAndmed[aeg]["temperature"]
					joonestusAndmed["temperature"]["näit"][-1]+= ilmaAndmed[aeg]["temperature"]
					joonestusAndmed["temperature"]["näit-hulk"][-1]+=1
					#Statistika
					if ilmaAndmed[aeg]["temperature"] > joonestusAndmed["temperature"]["statistika"]["kõrgeim"]:
						joonestusAndmed["temperature"]["statistika"]["kõrgeim"] = ilmaAndmed[aeg]["temperature"]
						joonestusAndmed["temperature"]["statistika"]["kõrgeim-aeg"] = aeg
					if ilmaAndmed[aeg]["temperature"] < joonestusAndmed["temperature"]["statistika"]["madalaim"]:
						joonestusAndmed["temperature"]["statistika"]["madalaim"] = ilmaAndmed[aeg]["temperature"]
						joonestusAndmed["temperature"]["statistika"]["madalaim-aeg"] = aeg
					joonestusAndmed["temperature"]["statistika"]["summa"] += ilmaAndmed[aeg]["temperature"]
					joonestusAndmed["temperature"]["statistika"]["summa-hulk"] += 1
				else:
					print("HOIATUS: Eiran kahtlast temperatuuri näitu '"+str(ilmaAndmed[aeg]["temperature"])+"' ajal "+aeg.strftime("%d.%m.%Y kell %H:%M"))
			elif ("temperature" in ilmaAndmed[aeg]):
				joonestusAndmed["temperature"]["aeg"].append(aeg)
				if joonestusAndmed["temperature"]["näit-hulk"][-1] > 1:
					joonestusAndmed["temperature"]["näit"][-1]=joonestusAndmed["temperature"]["näit"][-1]/joonestusAndmed["temperature"]["näit-hulk"][-1]
				joonestusAndmed["temperature"]["näit-kõrge"][-1]=joonestusAndmed["temperature"]["näit-kõrge"][-1]-joonestusAndmed["temperature"]["näit"][-1]
				joonestusAndmed["temperature"]["näit-madal"][-1]=joonestusAndmed["temperature"]["näit"][-1]-joonestusAndmed["temperature"]["näit-madal"][-1]
				joonestusAndmed["temperature"]["näit"].append(ilmaAndmed[aeg]["temperature"])
				joonestusAndmed["temperature"]["näit-kõrge"].append(ilmaAndmed[aeg]["temperature"])
				joonestusAndmed["temperature"]["näit-madal"].append(ilmaAndmed[aeg]["temperature"])
				joonestusAndmed["temperature"]["näit-hulk"].append(1)
				#Statistika
				if ilmaAndmed[aeg]["temperature"] > joonestusAndmed["temperature"]["statistika"]["kõrgeim"]:
					joonestusAndmed["temperature"]["statistika"]["kõrgeim"] = ilmaAndmed[aeg]["temperature"]
					joonestusAndmed["temperature"]["statistika"]["kõrgeim-aeg"] = aeg
				if ilmaAndmed[aeg]["temperature"] < joonestusAndmed["temperature"]["statistika"]["madalaim"]:
					joonestusAndmed["temperature"]["statistika"]["madalaim"] = ilmaAndmed[aeg]["temperature"]
					joonestusAndmed["temperature"]["statistika"]["madalaim-aeg"] = aeg
				joonestusAndmed["temperature"]["statistika"]["summa"] += ilmaAndmed[aeg]["temperature"]
				joonestusAndmed["temperature"]["statistika"]["summa-hulk"] += 1
				
			if (aeg.year == joonestusAndmed["humidity"]["aeg"][-1].year) and (aeg.month == joonestusAndmed["humidity"]["aeg"][-1].month) and (aeg.day == joonestusAndmed["humidity"]["aeg"][-1].day) and ("humidity" in ilmaAndmed[aeg]):
				if (ilmaAndmed[aeg]["humidity"] <= piirmäärad["ülem-humidity"]) and (ilmaAndmed[aeg]["humidity"] >= piirmäärad["alam-humidity"]):
					if ilmaAndmed[aeg]["humidity"] > joonestusAndmed["humidity"]["näit-kõrge"][-1]:
						joonestusAndmed["humidity"]["näit-kõrge"][-1]=ilmaAndmed[aeg]["humidity"]
					if ilmaAndmed[aeg]["humidity"] < joonestusAndmed["humidity"]["näit-madal"][-1]:
						joonestusAndmed["humidity"]["näit-madal"][-1]=ilmaAndmed[aeg]["humidity"]
					joonestusAndmed["humidity"]["näit"][-1]+= ilmaAndmed[aeg]["humidity"]
					joonestusAndmed["humidity"]["näit-hulk"][-1]+=1
					#Statistika
					if ilmaAndmed[aeg]["humidity"] > joonestusAndmed["humidity"]["statistika"]["kõrgeim"]:
						joonestusAndmed["humidity"]["statistika"]["kõrgeim"] = ilmaAndmed[aeg]["humidity"]
						joonestusAndmed["humidity"]["statistika"]["kõrgeim-aeg"] = aeg
					if ilmaAndmed[aeg]["humidity"] < joonestusAndmed["humidity"]["statistika"]["madalaim"]:
						joonestusAndmed["humidity"]["statistika"]["madalaim"] = ilmaAndmed[aeg]["humidity"]
						joonestusAndmed["humidity"]["statistika"]["madalaim-aeg"] = aeg
					joonestusAndmed["humidity"]["statistika"]["summa"] += ilmaAndmed[aeg]["humidity"]
					joonestusAndmed["humidity"]["statistika"]["summa-hulk"] += 1
				else:
					print("HOIATUS: Eiran kahtlast niiskuse näitu '"+str(ilmaAndmed[aeg]["humidity"])+"' ajal "+aeg.strftime("%d.%m.%Y kell %H:%M"))
			elif ("humidity" in ilmaAndmed[aeg]):
				joonestusAndmed["humidity"]["aeg"].append(aeg)
				if joonestusAndmed["humidity"]["näit-hulk"][-1] > 1:
					joonestusAndmed["humidity"]["näit"][-1]=joonestusAndmed["humidity"]["näit"][-1]/joonestusAndmed["humidity"]["näit-hulk"][-1]
				joonestusAndmed["humidity"]["näit-kõrge"][-1]=joonestusAndmed["humidity"]["näit-kõrge"][-1]-joonestusAndmed["humidity"]["näit"][-1]
				joonestusAndmed["humidity"]["näit-madal"][-1]=joonestusAndmed["humidity"]["näit"][-1]-joonestusAndmed["humidity"]["näit-madal"][-1]
				joonestusAndmed["humidity"]["näit"].append(ilmaAndmed[aeg]["humidity"])
				joonestusAndmed["humidity"]["näit-kõrge"].append(ilmaAndmed[aeg]["humidity"])
				joonestusAndmed["humidity"]["näit-madal"].append(ilmaAndmed[aeg]["humidity"])
				joonestusAndmed["humidity"]["näit-hulk"].append(1)
				#Statistika
				if ilmaAndmed[aeg]["humidity"] > joonestusAndmed["humidity"]["statistika"]["kõrgeim"]:
					joonestusAndmed["humidity"]["statistika"]["kõrgeim"] = ilmaAndmed[aeg]["humidity"]
					joonestusAndmed["humidity"]["statistika"]["kõrgeim-aeg"] = aeg
				if ilmaAndmed[aeg]["humidity"] < joonestusAndmed["humidity"]["statistika"]["madalaim"]:
					joonestusAndmed["humidity"]["statistika"]["madalaim"] = ilmaAndmed[aeg]["humidity"]
					joonestusAndmed["humidity"]["statistika"]["madalaim-aeg"] = aeg
				joonestusAndmed["humidity"]["statistika"]["summa"] += ilmaAndmed[aeg]["humidity"]
				joonestusAndmed["humidity"]["statistika"]["summa-hulk"] += 1
				
			if "pressure" in ilmaAndmed[aeg]:
				if (ilmaAndmed[aeg]["pressure"] <= piirmäärad["ülem-pressure"]) and (ilmaAndmed[aeg]["pressure"] >= piirmäärad["alam-pressure"]):
					joonestusAndmed["pressure"]["aeg"].append(aeg)
					joonestusAndmed["pressure"]["näit"].append(ilmaAndmed[aeg]["pressure"])
					#Statistika
					if ilmaAndmed[aeg]["pressure"] > joonestusAndmed["pressure"]["statistika"]["kõrgeim"]:
						joonestusAndmed["pressure"]["statistika"]["kõrgeim"] = ilmaAndmed[aeg]["pressure"]
						joonestusAndmed["pressure"]["statistika"]["kõrgeim-aeg"] = aeg
					if ilmaAndmed[aeg]["pressure"] < joonestusAndmed["pressure"]["statistika"]["madalaim"]:
						joonestusAndmed["pressure"]["statistika"]["madalaim"] = ilmaAndmed[aeg]["pressure"]
						joonestusAndmed["pressure"]["statistika"]["madalaim-aeg"] = aeg
					joonestusAndmed["pressure"]["statistika"]["summa"] += ilmaAndmed[aeg]["pressure"]
					joonestusAndmed["pressure"]["statistika"]["summa-hulk"] += 1
				else:
					print("HOIATUS: Eiran kahtlast õhurõhu näitu '"+str(ilmaAndmed[aeg]["pressure"])+"' ajal "+aeg.strftime("%d.%m.%Y kell %H:%M"))
		
		if joonestusAndmed["temperature"]["näit-hulk"][-1] > 1:
			joonestusAndmed["temperature"]["näit"][-1]=joonestusAndmed["temperature"]["näit"][-1]/joonestusAndmed["temperature"]["näit-hulk"][-1]
		if joonestusAndmed["humidity"]["näit-hulk"][-1] > 1:
			joonestusAndmed["humidity"]["näit"][-1]=joonestusAndmed["humidity"]["näit"][-1]/joonestusAndmed["humidity"]["näit-hulk"][-1]						
		joonestusAndmed["temperature"]["näit-kõrge"][-1]=joonestusAndmed["temperature"]["näit-kõrge"][-1]-joonestusAndmed["temperature"]["näit"][-1]; joonestusAndmed["humidity"]["näit-kõrge"][-1]=joonestusAndmed["humidity"]["näit-kõrge"][-1]-joonestusAndmed["humidity"]["näit"][-1]
		joonestusAndmed["temperature"]["näit-madal"][-1]=joonestusAndmed["temperature"]["näit"][-1]-joonestusAndmed["temperature"]["näit-madal"][-1]; joonestusAndmed["humidity"]["näit-madal"][-1]=joonestusAndmed["humidity"]["näit"][-1]-joonestusAndmed["humidity"]["näit-madal"][-1]
		
		for pikaajalineJoonis in (temperatuuriJoonestus, niiskusJoonestus, õhurõhuJoonestus):
			pikaajalineJoonis.xaxis.set_major_formatter(osuti.FuncFormatter(kuupäevaVorming))
		temperatuuriJoonestus.set_xlabel(joonestusAndmed["temperature"]["aeg"][-1].strftime("Ajavahemikus %d.%m.%Y(%H:%M) - ")+joonestusAndmed["temperature"]["aeg"][0].strftime("%d.%m.%Y(%H:%M)"))
		niiskusJoonestus.set_xlabel(joonestusAndmed["humidity"]["aeg"][-1].strftime("Ajavahemikus %d.%m.%Y(%H:%M) - ")+joonestusAndmed["humidity"]["aeg"][0].strftime("%d.%m.%Y(%H:%M)"))
		õhurõhuJoonestus.set_xlabel(joonestusAndmed["pressure"]["aeg"][-1].strftime("Ajavahemikus %d.%m.%Y(%H:%M) - ")+joonestusAndmed["pressure"]["aeg"][0].strftime("%d.%m.%Y(%H:%M)"))
		temperatuuriJoonestus.errorbar(joonestusAndmed["temperature"]["aeg"], joonestusAndmed["temperature"]["näit"], yerr=[joonestusAndmed["temperature"]["näit-madal"],joonestusAndmed["temperature"]["näit-kõrge"]], ecolor='red')
		niiskusJoonestus.errorbar(joonestusAndmed["humidity"]["aeg"], joonestusAndmed["humidity"]["näit"], yerr=[joonestusAndmed["humidity"]["näit-madal"],joonestusAndmed["humidity"]["näit-kõrge"]], ecolor='red')
		õhurõhuJoonestus.plot(joonestusAndmed["pressure"]["aeg"], joonestusAndmed["pressure"]["näit"], marker='', color='grey', linewidth=1)
	# Näita Joonestusi:
	joonestus.show()
	# Salvesta Joonestused:
	joonestus.savefig('joonestused.jpg',bbox_inches='tight', dpi=150)
	return joonestusAndmed



def teisendaTekstAjaks(tekst):
	'''
	Adafruit Kasutab ISO 8601 Aja Vormingut, UTC Ajatsoonis.
	aasta-kuu-päevTtund:minut:sekundZ
	Näide: 2021-07-06T20:46:48Z
	'''
	return datetime(int(tekst[:4]),int(tekst[5:7]),int(tekst[8:10]),int(tekst[11:13]),int(tekst[14:16]),int(tekst[17:19]), tzinfo=timezone.utc).astimezone()
	


def salvestaNäit(jsonNäit, ilmaAndmed):
	'''
	Teisendab ja Salvestab Adafruit'i JSON-formaadis näidud Mällu.
	'''
	if teisendaTekstAjaks(jsonNäit["created_at"]) in ilmaAndmed:
		if jsonNäit["feed_key"] in ilmaAndmed[teisendaTekstAjaks(jsonNäit["created_at"])]:
			print("VIGA: Topelt",jsonNäit["feed_key"],"andmed",teisendaTekstAjaks(jsonNäit["created_at"]).strftime("%d.%m.%Y kell %H:%M"), "[salvestan", ilmaAndmed[teisendaTekstAjaks(jsonNäit["created_at"])][jsonNäit["feed_key"]], "ja", jsonNäit["value"], "keskmise:", str((float(jsonNäit["value"])+ilmaAndmed[teisendaTekstAjaks(jsonNäit["created_at"])][jsonNäit["feed_key"]])/2)+"]")
			ilmaAndmed[teisendaTekstAjaks(jsonNäit["created_at"])][jsonNäit["feed_key"]] = (float(jsonNäit["value"])+ilmaAndmed[teisendaTekstAjaks(jsonNäit["created_at"])][jsonNäit["feed_key"]])/2
		else:
			ilmaAndmed[teisendaTekstAjaks(jsonNäit["created_at"])][jsonNäit["feed_key"]] = float(jsonNäit["value"])
	else:
		ilmaAndmed[teisendaTekstAjaks(jsonNäit["created_at"])] = {jsonNäit["feed_key"]:float(jsonNäit["value"])}



def järgmiseLeheAadress(päis):
	'''
	Adafruit'i Rakendusliides Piirab Ligipääsu 1000. Andmepunktile Korraga.
	Antud funktsioon analüüsib päisest kas järgnev leht on olemas.
	'''
	if not päis:
		return None
	for link in [h.strip() for h in päis.split(";")]:
		if re.match('rel="next"', link):
			aadressiTulemus = re.search("<(.+)>", link)
			if aadressiTulemus:
				uusAadress = aadressiTulemus[1]
				return uusAadress
	return None
	
	
	
def laadiAndmeLeht(aadress, ilmaAndmed, aadressiPäised=None, jubaLaetudAndmeteHulk=0):
	'''
	Laeb alla ühe lehe andmeid Adafruit IO'st (Kuni 1000 Andmepunkti)
	 ja vastab järgmise lehe aadressiga, kui see on olemas (vastasel juhul 'None')
	'''
	ühenduseAllikas = urllib.parse.urlparse(aadress)
	#Turvaline ühendus, kui võimalik:
	if ühenduseAllikas.port == 443:
		ühendus = http.client.HTTPSConnection(ühenduseAllikas.hostname, ühenduseAllikas.port)
	else:
		ühendus = http.client.HTTPConnection(ühenduseAllikas.hostname, ühenduseAllikas.port)
	ühendus.request("GET", aadress, headers=aadressiPäised)
	vastus = ühendus.getresponse()
	sisu = vastus.read()
	jsonSisu = json.loads(sisu)
	if vastus.status != 200:
		print("VIGA: Ühenduse vastus ei vastanud ootustele - ", vastus.status, jsonSisu)
	elif jsonSisu:
		for näit in jsonSisu:
			salvestaNäit(näit, ilmaAndmed)
		if (teisendaTekstAjaks(jsonSisu[0]["created_at"]).strftime("%d.%m")==teisendaTekstAjaks(jsonSisu[-1]["created_at"]).strftime("%d.%m")):
			print(
				"{}/{} näitu laetud ({}-{})".format(
					len(jsonSisu)+jubaLaetudAndmeteHulk,
					vastus.getheader("X-Pagination-Total"),
					teisendaTekstAjaks(jsonSisu[0]["created_at"]).strftime("%d.%m %H:%M"),
					teisendaTekstAjaks(jsonSisu[-1]["created_at"]).strftime("%H:%M"),
				)	
			)
		else:
			print(
				"{}/{} näitu laetud ({} - {})".format(
					len(jsonSisu)+jubaLaetudAndmeteHulk,
					vastus.getheader("X-Pagination-Total"),
					teisendaTekstAjaks(jsonSisu[0]["created_at"]).strftime("%d.%m %H:%M"),
					teisendaTekstAjaks(jsonSisu[-1]["created_at"]).strftime("%d.%m %H:%M"),
				)	
			)
		uusLaetudAndmeteHulk=jubaLaetudAndmeteHulk+len(jsonSisu)
		return järgmiseLeheAadress(vastus.getheader("Link")),uusLaetudAndmeteHulk
	return None



def laadiTerveVoog(algAadress, ilmaAndmed, algAadressiPäised=None):
	"""
	Laeb kõik andmed ühest infovoost, ühelt Adafruit'i lehelt järgmisele hüpates.
	"""
	laetudAndmeteStatistika = 0
	allalaadimine = lambda u: laadiAndmeLeht(u, ilmaAndmed, algAadressiPäised, laetudAndmeteStatistika)
	järgmineLeht,laetudAndmeteStatistika = allalaadimine(algAadress)
	while järgmineLeht:
		time.sleep(1)
		järgmineLeht,laetudAndmeteStatistika = allalaadimine(järgmineLeht)

def laadiIlmaAndmed(ilmaVood):
	"""
	Laeb kõik ilma andmed, ühelt infovoolt/elemendilt järgmisele hüpates.
	"""
	ilmaAndmed = {}
	''' Näide:
	ilmaAndmed = { 07/07/21-21:16: {'temperature': 15,'humidity':97,'pressure':1020},
				   07/07/21-21:17: {'temperature': 16,...}
				 }
	'''
	for voog in ilmaVood:
		päringuAadress = aadressiMall % (AIO_Kasutaja, voog)
		if parameetrid:
			päringuAadress += "?" + urllib.parse.urlencode(parameetrid)
		#print(datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"), "laen", päringuAadress, "(", päised, "päisetega)")
		laadiTerveVoog(päringuAadress, ilmaAndmed, päised)
		print(voog,"andmed laetud!")
	return ilmaAndmed




####################################################################################################
#	PÕHI KOOD																					   #
####################################################################################################
if __name__ == "__main__":
	print("\nTere tulemast Ilmateatajasse!\n")
	aadressiMall = "https://io.adafruit.com/api/v2/%s/feeds/%s/data"
	parameetrid = {}
	
	if os.getenv("ALGUS"):
		parameetrid["start_time"] = os.getenv("ALGUS")
	elif algAeg:
		parameetrid["start_time"] = algAeg.isoformat(sep='T',timespec='seconds')
	if os.getenv("LÕPP"):
		parameetrid["end_time"] = os.getenv("LÕPP")
	elif lõppAeg:
		parameetrid["end_time"] = lõppAeg.isoformat(sep='T',timespec='seconds')

	if not (AIO_Kasutaja and AIO_Võti):
		print("VIGA: Adafruit IO Kasutajatunnus ja Võti on puudu! Palun määra need koodis.")
		exit(1)
		
	päised = {"X-AIO-Key": AIO_Võti}

	print("ANDMETE KOGUMINE",algAeg.strftime("[%d.%m.%Y(%H:%M) -"),lõppAeg.strftime("%d.%m.%Y(%H:%M)"), "ajavahemikust]")
	print("------------------------------------------------------------")
	ilmaNäidud = laadiIlmaAndmed(ilmaElemendid)
	sorteeritudIlmaNäidud = dict(sorted(ilmaNäidud.items(), key=lambda date:date[0]))
	print("------------------------------------------------------------")
	print("ANDMETE ANALÜÜS ["+str(len(ilmaNäidud)),"näitu, viimane", str((datetime.utcnow().astimezone().replace(tzinfo=tz.tzutc()).astimezone(tz.gettz('Europe/Tallinn'))-list(sorteeritudIlmaNäidud.keys())[0]).seconds), "sekundit tagasi]")
	print("------------------------------------------------------------")
	kontrollitudIlmaNäidud = joonestaNäidud(sorteeritudIlmaNäidud)
	print("------------------------------------------------------------")
	print("ANDMETE STATISTIKA")
	print("------------------------------------------------------------")
	print(ilmaStatistika(kontrollitudIlmaNäidud))
	print("------------------------------------------------------------")
	print("ANDMETE JAGAMINE")
	print("------------------------------------------------------------")
	säutsuTwitteris(ilmaStatistika(kontrollitudIlmaNäidud),"joonestused.jpg")
