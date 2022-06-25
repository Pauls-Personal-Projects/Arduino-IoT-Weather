#!/usr/bin/env python3
# -*- coding: utf-8 -*-

####################################################################################################
#																								   #
#											INFOLIIN											   #
#																								   #
####################################################################################################
'''
Looja:		Paul J. Aru		-	https://github.com/paulpall
Kuupäev:	16/07/2021
'''



####################################################################################################
#	TEEGID																						   #
####################################################################################################
import tweepy										# Säutsumiseks
import os.path										# Säutsude ID Salvestamiseks
import Ilmateataja
from datetime import datetime, timezone, timedelta	# Kuupäevade Teisendamiseks
from dateutil import tz								# Kuupäevade Teisendamiseks



####################################################################################################
#	SÄTTED																						   #
####################################################################################################

### PEIDA ENNE GIT'i LAADIMIST ###
AIO_Võti = ""
Twitteri_API_Võti = ""
Twitteri_API_Saladus = ""
Twitteri_Ligipääsu_Token = ""
Twitteri_Ligipääsu_Saladus = ""
### PEIDA ENNE GIT'i LAADIMIST ###

#Kõik Elemendid mis mu Ilmajaam Hetkel Mõõdab:
ilmaElemendid = ["temperature","humidity","pressure"]
laadimisParameetrid = {}

#Piirmäärad Imelike Näitude Eemaldamiseks:
seatudPiirmäärad = {"ülem-temperature":100.00, "alam-temperature":-100.00,#°C
				"ülem-humidity":100.00, "alam-humidity":0.00,		#%
				"ülem-pressure":1100.00, "alam-pressure":900.00,	#hPa
				"analüüsiKeskmist":timedelta(days=2.5),	#Min. Aeg Päeva-Keskmise Analüüsiks Detailse Asemel
				"puuduvadNäidud":timedelta(minutes=30)} #Max. Aeg Ilma Andmeteta Vea Teateks



####################################################################################################
#	TUGIFUNKTSIOONID																			   #
####################################################################################################



def säutsuTwitteris(kellele, tekst, pilt):
	üleslaetudPilt = twitter.media_upload(pilt)
	twitter.update_status(status=tekst, in_reply_to_status_id=kellele.id, media_ids=[üleslaetudPilt.media_id], auto_populate_reply_metadata=True)
	print("Vastasin "+ kellele.user.name + "(i) säutsule “" + kellele.text + "”, ülevaatega “"+tekst+"”.")
	kirjutaViimaseSäutsuID(kellele.id)
	
	

def säutsuVeateade(kellele, sõnum):
	twitter.update_status(status=sõnum, in_reply_to_status_id=kellele.id, auto_populate_reply_metadata=True)
	print("Vastasin "+ kellele.user.name + "(i) säutsule “" + kellele.text + "”, veateatega “"+sõnum+"”.")
	kirjutaViimaseSäutsuID(kellele.id)



def kirjutaViimaseSäutsuID(id):
	if os.path.exists("Twitteri_viimase_säutsu_ID.txt"):
		tekstiFail = open("Twitteri_viimase_säutsu_ID.txt", "r")
		vanaID = int(tekstiFail.read())
		if vanaID < id:
			tekstiFail = open("Twitteri_viimase_säutsu_ID.txt", "w")
			tekstiFail.write(str(id))
			tekstiFail.close()
	else:
		tekstiFail = open("Twitteri_viimase_säutsu_ID.txt", "w")
		tekstiFail.write(str(id))
		tekstiFail.close()



def loeViimaseSäutsuID():
	id = 1
	if os.path.exists("Twitteri_viimase_säutsu_ID.txt"):
		tekstiFail = open("Twitteri_viimase_säutsu_ID.txt", "r")
		id = int(tekstiFail.read())
	return id



def kuulaSäutse():
	id = loeViimaseSäutsuID()
	
	if (list(tweepy.Cursor(twitter.mentions_timeline, since_id=1).items(1))[0].id) > id:
		print()
		print("Roboti Viimati Kuuldud Säutsud:")
		count=1
		for säuts in tweepy.Cursor(twitter.mentions_timeline, since_id=id).items():
			print(str(count)+"(ID:"+str(säuts.id)+") - "+säuts.text)
			if "@ArukasPilv Näita ilma vahemikus".lower() in säuts.text.lower():
				potensiaalnePäring = säuts.text.lower()
				potensiaalnePäring = potensiaalnePäring.replace("@ArukasPilv Näita ilma vahemikus".lower(),"")
				potensiaalnePäring = potensiaalnePäring.replace(" ","")
				kõikArvudOlemas = True
				try:
					algPäev=int(potensiaalnePäring[0:2])
				except ValueError:
					säutsuVeateade(säuts, "“"+potensiaalnePäring[0:2]+"” ei ole oodatud päeva formaadis! Kasuta PP.KK.AAAA(TT:MM) - PP.KK.AAAA(TT:MM) vormingut, nt. 31.<-.2021(23:59) - 01.01.2022(11:59).")
					kõikArvudOlemas = False
				try:
					algKuu=int(potensiaalnePäring[3:5])
				except ValueError:
					säutsuVeateade(säuts, "“"+potensiaalnePäring[3:5]+"” ei ole oodatud kuu formaadis! Kasuta PP.KK.AAAA(TT:MM) - PP.KK.AAAA(TT:MM) vormingut, nt. ->.12.<---(23:59) - 01.01.2022(11:59).")
					kõikArvudOlemas = False
				try:
					algAasta=int(potensiaalnePäring[6:10])
				except ValueError:
					säutsuVeateade(säuts, "“"+potensiaalnePäring[6:10]+"” ei ole oodatud aasta formaadis! Kasuta PP.KK.AAAA(TT:MM) - PP.KK.AAAA(TT:MM) vormingut, nt. 31.->.2021(<-:59) - 01.01.2022(11:59).")
					kõikArvudOlemas = False
				try:
					algTund=int(potensiaalnePäring[11:13])
				except ValueError:
					säutsuVeateade(säuts, "“"+potensiaalnePäring[11:13]+"” ei ole oodatud tunni formaadis! Kasuta PP.KK.AAAA(TT:MM) - PP.KK.AAAA(TT:MM) vormingut, nt. 31.12.--->(23:<-) - 01.01.2022(11:59).")
					kõikArvudOlemas = False
				try:
					algMinut=int(potensiaalnePäring[14:16])
				except ValueError:
					säutsuVeateade(säuts, "“"+potensiaalnePäring[14:16]+"” ei ole oodatud minuti formaadis! Kasuta PP.KK.AAAA(TT:MM) - PP.KK.AAAA(TT:MM) vormingut, nt. 31.12.2021(->:59) - 01.01.2022(11:59).")
					kõikArvudOlemas = False
				try:
					lõppPäev=int(potensiaalnePäring[18:20])
				except ValueError:
					säutsuVeateade(säuts, "“"+potensiaalnePäring[18:20]+"” ei ole oodatud päeva formaadis! Kasuta PP.KK.AAAA(TT:MM) - PP.KK.AAAA(TT:MM) vormingut, nt. 31.12.2021(23:59) - 01.<-.2022(11:59).")
					kõikArvudOlemas = False
				try:
					lõppKuu=int(potensiaalnePäring[21:23])
				except ValueError:
					säutsuVeateade(säuts, "“"+potensiaalnePäring[21:23]+"” ei ole oodatud kuu formaadis! Kasuta PP.KK.AAAA(TT:MM) - PP.KK.AAAA(TT:MM) vormingut, nt. 31.12.2021(23:59) - ->.01.<---(11:59).")
					kõikArvudOlemas = False
				try:
					lõppAasta=int(potensiaalnePäring[24:28])
				except ValueError:
					säutsuVeateade(säuts, "“"+potensiaalnePäring[24:28]+"” ei ole oodatud aasta formaadis! Kasuta PP.KK.AAAA(TT:MM) - PP.KK.AAAA(TT:MM) vormingut, nt. 31.12.2021(23:59) - 01.->.2022(<-:59).")
					kõikArvudOlemas = False
				try:
					lõppTund=int(potensiaalnePäring[29:31])
				except ValueError:
					säutsuVeateade(säuts, "“"+potensiaalnePäring[29:31]+"” ei ole oodatud tunni formaadis! Kasuta PP.KK.AAAA(TT:MM) - PP.KK.AAAA(TT:MM) vormingut, nt. 31.12.2021(23:59) - 01.01.--->(11:<-).")
					kõikArvudOlemas = False
				try:
					lõppMinut=int(potensiaalnePäring[32:34])
				except ValueError:
					säutsuVeateade(säuts, "“"+potensiaalnePäring[32:34]+"” ei ole oodatud minuti formaadis! Kasuta PP.KK.AAAA(TT:MM) - PP.KK.AAAA(TT:MM) vormingut, nt. 31.12.2021(23:59) - 01.01.2022(->:59).")
					kõikArvudOlemas = False
				if kõikArvudOlemas:
				
					laadimisParameetrid["start_time"] = datetime(algAasta,algKuu,algPäev,algTund,algMinut,00, tzinfo=tz.gettz('Europe/Tallinn')).isoformat(sep='T',timespec='seconds')
					laadimisParameetrid["end_time"] = datetime(lõppAasta,lõppKuu,lõppPäev,lõppTund,lõppMinut,00, tzinfo=tz.gettz('Europe/Tallinn')).isoformat(sep='T',timespec='seconds')
					aadressiMall = "https://io.adafruit.com/api/v2/%s/feeds/%s/data"
					laadimisPäised = {"X-AIO-Key": AIO_Võti}
					ilmaNäidud = Ilmateataja.laadiIlmaAndmed(ilmaElemendid, laadimisParameetrid, aadressiMall, laadimisPäised)
					sorteeritudIlmaNäidud = dict(sorted(ilmaNäidud.items(), key=lambda date:date[0]))
					kontrollitudIlmaNäidud = Ilmateataja.joonestaNäidud(sorteeritudIlmaNäidud, seatudPiirmäärad)
					säutsuTwitteris(säuts, Ilmateataja.ilmaStatistika(kontrollitudIlmaNäidud, seatudPiirmäärad), "joonestused.jpg")
				
				
			
			else:
				säutsuVeateade(säuts, "Kui soovid ilma ülevaadet viimase kuu andmetest, siis säutsu mulle “Näita ilma vahemikus PP.KK.AAAA(TT:MM) - PP.KK.AAAA(TT:MM)”. Tähed vaheta oma eelistatud ajaperioodiga, nt. 31.12.2021(23:59) - 01.01.2022(11:59).")
			print()
			count=count+1
	else:
		print()
		print("Uusi Säutse Pole!")





####################################################################################################
#	PÕHI KOOD																					   #
####################################################################################################



if __name__ == '__main__':
	autentsus = tweepy.OAuthHandler(Twitteri_API_Võti, Twitteri_API_Saladus)
	autentsus.set_access_token(Twitteri_Ligipääsu_Token, Twitteri_Ligipääsu_Saladus)
	twitter = tweepy.API(autentsus)
	kuulaSäutse()
