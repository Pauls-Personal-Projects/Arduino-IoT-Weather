#!/usr/bin/env python3
# -*- coding: utf-8 -*-

############################################################
#                                                          #
#                       ILMATEATAJA                        #
#                                                          #
############################################################
'''
Looja:		Paul J. Aru		-	https://github.com/paulpall
Kuupäev:	06/07/2021
Uuendatud:	09/07/2021
------------------------------------------------------------
Käsurealt kasutamiseks:
	$ ALGUS="2019-05-01T00:00Z" LÕPP="2019-06-01T00:00Z" \
		python Ilmateataja.py
------------------------------------------------------------
Tänud Adam Bachman, download_paged_data.py jagamise eest!
Link: https://gist.github.com/abachman/12df0b34503edd5692be22f6b9695539
'''



# TEEGID
from datetime import datetime, timezone, timedelta
import time
import os
import urllib.parse
import http.client
import json
import re



# SÄTTED
AIO_Kasutaja = ""
AIO_Võti = ""
lõppAeg = datetime.utcnow() # Testimiseks: "2021-07-07T21:05:00Z"
algAeg = lõppAeg-timedelta(days=28) # Testimiseks: "2021-07-07T21:00:00Z" # UTC AJAS, Eestis Tegelikult 00:00
infoVood = ["temperature","humidity","pressure"]
ilmaNäidud = {}
''' Näide:
ilmaNäidud = { 07/07/21-21:16: {'temperature': 15,'humidity':97,'pressure':1020},
			   07/07/21-21:17: {'temperature': 16,...}
			 }
'''





# TUGIFUNKTSIOONID

def teisendaTekstAjaks(tekst):
	'''
	Adafruit Kasutab ISO 8601 Aja Vormingut, UTC Ajatsoonis.
	aasta-kuu-päevTtund:minut:sekundZ
	Näide: 2021-07-06T20:46:48Z
	'''
	return datetime(int(tekst[:4]),int(tekst[5:7]),int(tekst[8:10]),int(tekst[11:13]),int(tekst[14:16]),int(tekst[17:19]), tzinfo=timezone.utc).astimezone()
	


def salvestaNäit(jsonNäit):
	'''
	Teisendab ja Salvestab Adafruit'i JSON-formaadis näidud Mällu.
	'''
	if teisendaTekstAjaks(jsonNäit["created_at"]) in ilmaNäidud:
		if jsonNäit["feed_key"] in ilmaNäidud[teisendaTekstAjaks(jsonNäit["created_at"])]:
			print("VIGA: Topelt",jsonNäit["feed_key"],"andmed",teisendaTekstAjaks(jsonNäit["created_at"]).strftime("%d.%m.%Y kell %H:%M"))
			print("Hoiul Näit:",ilmaNäidud[teisendaTekstAjaks(jsonNäit["created_at"])][jsonNäit["feed_key"]])
			print("Leitud Näit:",jsonNäit["value"])
			exit(1)
		else:
			ilmaNäidud[teisendaTekstAjaks(jsonNäit["created_at"])][jsonNäit["feed_key"]] = float(jsonNäit["value"])
	else:
		ilmaNäidud[teisendaTekstAjaks(jsonNäit["created_at"])] = {jsonNäit["feed_key"]:float(jsonNäit["value"])}



def analüüsiNäidud():
	'''
	Vaatab üle kõik näidud ja otsib välja huvitava!
	'''
	kõrgeimadNäidud = {
		'temperature':-100.00, 'temperature-date':datetime(1970, 1, 1, tzinfo=timezone.utc),
		'humidity':-1.00, 'humidity-date':datetime(1970, 1, 1, tzinfo=timezone.utc),
		'pressure':900.00, 'pressure-date':datetime(1970, 1, 1, tzinfo=timezone.utc)
	}
	madalaimadNäidud = {
		'temperature':100.00, 'temperature-date':datetime(1970, 1, 1, tzinfo=timezone.utc),
		'humidity':101.00, 'humidity-date':datetime(1970, 1, 1, tzinfo=timezone.utc),
		'pressure':1100.00, 'pressure-date':datetime(1970, 1, 1, tzinfo=timezone.utc)
	}
	keskmisedNäidud = {
		'temperature':0.00, 'temperature-count':0,
		'humidity':0.00, 'humidity-count':0,
		'pressure':0.00, 'pressure-count':0
	}
	
	for aeg in ilmaNäidud:
		for näidutüüp in ilmaNäidud[aeg]:
			if ilmaNäidud[aeg][näidutüüp] > kõrgeimadNäidud[näidutüüp]:
				kõrgeimadNäidud[näidutüüp] = ilmaNäidud[aeg][näidutüüp]
				kõrgeimadNäidud[näidutüüp+"-date"] = aeg
			if ilmaNäidud[aeg][näidutüüp] < madalaimadNäidud[näidutüüp]:
				madalaimadNäidud[näidutüüp] = ilmaNäidud[aeg][näidutüüp]
				madalaimadNäidud[näidutüüp+"-date"] = aeg
			keskmisedNäidud[näidutüüp] += ilmaNäidud[aeg][näidutüüp]
			keskmisedNäidud[näidutüüp+"-count"] += 1
	for näidutüüp in infoVood:
		keskmisedNäidud[näidutüüp] = keskmisedNäidud[näidutüüp]/keskmisedNäidud[näidutüüp+"-count"]
	
	print("Kõrgeim Temperatuur: "+str(kõrgeimadNäidud["temperature"])+"C ("+kõrgeimadNäidud["temperature-date"].strftime("%d.%m.%Y kell %H:%M")+")")
	print("Madalaim Temperatuur: "+str(madalaimadNäidud["temperature"])+"C ("+madalaimadNäidud["temperature-date"].strftime("%d.%m.%Y kell %H:%M")+")")
	print("Keskmine Temperatuur: "+str(round(keskmisedNäidud["temperature"],2))+"C")
	print()
	print("Kõrgeim Niiskustase: "+str(kõrgeimadNäidud["humidity"])+"% ("+kõrgeimadNäidud["humidity-date"].strftime("%d.%m.%Y kell %H:%M")+")")
	print("Madalaim Niiskustase: "+str(madalaimadNäidud["humidity"])+"% ("+madalaimadNäidud["humidity-date"].strftime("%d.%m.%Y kell %H:%M")+")")
	print("Keskmine Niiskustase: "+str(round(keskmisedNäidud["humidity"],2))+"%")
	print()
	print("Kõrgeim Õhurõhk: "+str(kõrgeimadNäidud["pressure"])+"hPa ("+kõrgeimadNäidud["pressure-date"].strftime("%d.%m.%Y kell %H:%M")+")")
	print("Madalaim Õhurõhk: "+str(madalaimadNäidud["pressure"])+"hPa ("+madalaimadNäidud["pressure-date"].strftime("%d.%m.%Y kell %H:%M")+")")
	print("Keskmine Õhurõhk: "+str(round(keskmisedNäidud["pressure"],2))+"hPa")



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
	
	
	
def laadiAndmeLeht(aadress, aadressiPäised=None):
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
		viimaneNäit = {}
		for näit in jsonSisu:
			salvestaNäit(näit)
			viimaneNäit = näit
		print(
			"{}/{} näitu laetud (viimane neist: {} - {})".format(
				len(jsonSisu),
				vastus.getheader("X-Pagination-Total"),
				teisendaTekstAjaks(viimaneNäit["created_at"]).strftime("%d/%m/%Y %H:%M"),
				viimaneNäit["value"],
			)
		)
		return järgmiseLeheAadress(vastus.getheader("Link"))
	return None



def laadiTerveVoog(algAadress, algAadressiPäised=None):
	"""
	Laeb kõik andmed ühest infovoost, ühelt Adafruit'i lehelt järgmisele hüpates.
	"""
	allalaadimine = lambda u: laadiAndmeLeht(u, algAadressiPäised)
	järgmineLeht = allalaadimine(algAadress)
	while järgmineLeht:
		time.sleep(1)
		järgmineLeht = allalaadimine(järgmineLeht)





# PÕHI KOOD

if __name__ == "__main__":
	print("Tere tulemast Ilmateatajasse!\n")
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

	print("ANDMETE KOGUMINE",algAeg.strftime("(%d.%m.%Y %H:%M -"),lõppAeg.strftime("%d.%m.%Y %H:%M"), "ajavahemikust)")
	print("------------------------------------------------------------")
	for voog in infoVood:
		päringuAadress = aadressiMall % (AIO_Kasutaja, voog)
		if parameetrid:
			päringuAadress += "?" + urllib.parse.urlencode(parameetrid)
		#print(datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M"), "laen", päringuAadress, "(", päised, "päisetega)")
		laadiTerveVoog(päringuAadress, päised)
		print(voog,"andmed laetud!")
	print("------------------------------------------------------------")
	print("ANDMETE ANALÜÜS ("+str(len(ilmaNäidud))+" näitu kokku)")
	print("------------------------------------------------------------")
	analüüsiNäidud()





# VANA ADAFRUIT TEEGI KAUDU ÜHENDAMINE

'''
# ÜHENDA ADAFRUIT.IO TEENUSEGA
aio = Client(AIOKasutaja,AIOVõti)
print("\nJärgnevad Infovood Leiti Adafruit IO'st:")
infoVood = aio.feeds()
for voog in infoVood:
	print(voog.name)


# LAADI ALLA ILMAJAAMA ANDMED
print("\nAlustan Ilmajaama Andmete Allalaadimist...")
temperatuuriAndmed = aio.data('temperature')
print("33% - Laadisin " + str(len(temperatuuriAndmed)) + ". temperatuuri näitu")
niiskuseAndmed = aio.data('humidity')
print("66% - Laadisin " + str(len(niiskuseAndmed)) + ". niiskuse näitu")
õhurõhuAndmed = aio.data('pressure')
print("100% - Laadisin " + str(len(õhurõhuAndmed)) + ". õhurõhu näitu")


# SORTEERI ILMA ANDMED
print("\nAlustan Andmete Sorteerimist...")
uusimAeg = teisendaTekstAjaks(temperatuuriAndmed[0].created_at)
vanimAeg = teisendaTekstAjaks(temperatuuriAndmed[-1].created_at)
print("Viimasest Näidust on Möödunud: " + str(datetime.now(timezone.utc)-uusimAeg) + " (temperatuur oli siis: " + temperatuuriAndmed[0].value + "C)")
print("Temperatuuri Andmete Ajaperiood: " + uusimAeg.strftime("%d/%m/%Y %H:%M") + " - " + vanimAeg.strftime("%d/%m/%Y %H:%M"))
#for temperatuur in temperatuuriAndmed:
#	date = temperatuur.created_at
'''

