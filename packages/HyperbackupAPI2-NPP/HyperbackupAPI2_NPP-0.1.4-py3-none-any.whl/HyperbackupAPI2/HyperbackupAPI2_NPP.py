import json
from pickle import NONE
import time
from os.path import exists
import os
import datetime

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import argparse
import mysql.connector
import yaml
import wget

__version__ ="0.1.4"

def main(args=None):
	ruta = os.path.dirname(os.path.abspath(__file__))
	rutaJson = ruta+"/dadesHyperBackup2.json"
	parser = argparse.ArgumentParser(description="Api per saber status de les copies d'hyperbackup")
	parser.add_argument('-q', '--quiet', help='Nomes mostra els errors i el missatge de acabada per pantalla.', action="store_false")
	parser.add_argument('--json-file', help='La ruta(fitxer inclos) a on es guardara el fitxer de dades json. Per defecte es: '+rutaJson, default=rutaJson, metavar='RUTA')
	parser.add_argument('-g', '--graphicUI', help='Mostra el navegador graficament.', action="store_false")
	parser.add_argument('--portable-chrome-path', help="La ruta del executable de chrome", default=NONE, metavar="RUTA")
	parser.add_argument('-v', '--versio', help='Mostra la versio', action='version', version='HyperBackupAPI-NPP v'+__version__)
	args = parser.parse_args(args)
	conf = ruta +"/config/config.yaml"
	if not(os.path.exists(ruta+"/config")):
		os.mkdir(ruta+"/config")
	if not(os.path.exists(ruta+"/errorLogs")):
		os.mkdir(ruta+"/errorLogs")
	if not(os.path.exists(ruta+"/chromedriver.exe")):
		wget.download("https://github.com/NilPujolPorta/HyperbackupAPI2-NPP/blob/master/HyperBackupAPI2/chromedriver.exe?raw=true", ruta+"/chromedriver.exe")
		print()

	if not(exists(conf)):
		print("Emplena el fitxer de configuracio de Base de Dades a config/config.yaml")
		article_info = [
			{
				'BD': {
				'host' : 'localhost',
				'user': 'root',
				'passwd': 'patata'
				}
			}
		]

		with open(conf, 'w') as yamlfile:
			data = yaml.dump(article_info, yamlfile)

	with open(conf, "r") as yamlfile:
		data = yaml.load(yamlfile, Loader=yaml.FullLoader)

	servidor = data[0]['BD']['host']
	usuari = data[0]['BD']['user']
	contrassenya = data[0]['BD']['passwd']

	try:
		mydb =mysql.connector.connect(
			host=servidor,
			user=usuari,
			password=contrassenya,
			database="Hyperbackup2"
			)
		mycursor = mydb.cursor(buffered=True)
		print("Access BDD correcte")
	except:
		try:
			mydb =mysql.connector.connect(
				host=servidor,
				user=usuari,
				password=contrassenya
				)
			print("Base de dades no existeix, creant-la ...")
			mycursor = mydb.cursor(buffered=True)
			mycursor.execute("CREATE DATABASE Hyperbackup2")
			mydb =mysql.connector.connect(
				host=servidor,
				user=usuari,
				password=contrassenya,
				database="Hyperbackup2"
				)
			mycursor = mydb.cursor(buffered=True)
			mycursor.execute("CREATE TABLE credencials (usuari VARCHAR(255), contassenya VARCHAR(255), url VARCHAR(255));")
		except:
			print("Login BDD incorrecte")
			return

	mycursor.execute("SELECT * FROM credencials")
	resultatbd = mycursor.fetchall()


	options = Options()
	if args.portable_chrome_path != NONE:
		options.binary_location = args.portable_chrome_path
	if args.graphicUI:
		options.headless = True
		options.add_argument('--headless')
		options.add_argument('--disable-gpu')
		options.add_argument('window-size=1720x980')
	options.add_argument('log-level=3')#INFO = 0, WARNING = 1, LOG_ERROR = 2, LOG_FATAL = 3.
	browser = webdriver.Chrome(executable_path= ruta+"/chromedriver.exe", options = options)

	llistaNas = []
	#per cada nas fer login i accedir al hyperbackup
	for nas in resultatbd:
		try:
			browser.get(nas[2])
			time.sleep(10)
			usuari = browser.find_element(by="xpath", value='//*[@id="dsm-user-fieldset"]/div/div/div[1]/input')
			usuari.send_keys(nas[0])
			browser.find_element(by="xpath", value='//*[@id="sds-login-vue-inst"]/div/span/div/div[2]/div[2]/div/div[3]/div[2]/div/div[2]/div[3]').click()
			time.sleep(5)
			passwd = browser.find_element(by="xpath", value='//*[@id="dsm-pass-fieldset"]/div[1]/div/div[1]/input')
			passwd.send_keys(nas[1])
			browser.find_element(by="xpath", value='//*[@id="sds-login-vue-inst"]/div/span/div/div[2]/div[2]/div/div[3]/div[2]/div/div[2]/div[4]').click()
			time.sleep(20)
			hypericon=browser.find_element(by="xpath", value='//*[@id="sds-desktop-shortcut"]/div/li[7]')
			hypericon.click()
			time.sleep(10)
		except Exception as e:
			print("Error de connexio web")
			now = datetime.datetime.now()
			date_string = now.strftime('%Y-%m-%d--%H-%M-%S-json')
			f = open(ruta+"/errorLogs/"+date_string+".txt",'w')
			f.write("Error de connexio web\n"+str(e))
			f.close()



		#aconsegueix els noms de cada copia i els guarda en un array
		nomsCopies = []
		nomTots = browser.find_elements(by="class name", value="x-tree-node-anchor")
		for nom in nomTots:
			nomsCopies.append(nom.text)



		#prep de variables
		ultimaCorrecte = []
		statusCopies = []



		#aconsegueix els elements del menu de l'esquerra i els posa en un array
		roottreenode = browser.find_elements(by="class name", value="x-tree-node")



		#per cada element del menu de l'esquerra el clica i extreu les dades d'aquella copia
		y=1
		for treenode in roottreenode:
			treenode.click()
			time.sleep(2)
			statusCopies.append(browser.find_element(by="xpath", value='/html/body/div[11]/div[14]/div[3]/div[1]/div/div/div/div[2]/div['+str(y)+']/div/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div').text)
			if ((statusCopies[(y-1)]) != "Eliminando versiones de copia de seguridad...") and ((statusCopies[(y-1)]) !='Deleting backup versions...') and ((statusCopies[(y-1)]) !='Waiting...') and ((statusCopies[(y-1)]) !='Backing up...') and ((statusCopies[(y-1)]) !='Canceling...'):
				ultimaCorrecte.append(browser.find_element(by="xpath", value='/html/body/div[11]/div[14]/div[3]/div[1]/div/div/div/div[2]/div['+str(y)+']/div/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[1]/div[2]/div/div/div[1]/span').text)
			else:
				ultimaCorrecte.append("Es sabra cuan acabi la copia actual")
			y+=1
		
		#Mostra els resultats per pantalla 
		
		llistaCopies = []
		x = 0
		if args.quiet:
			print()
			print(nas[2])
			print("=================================")
			print()
		while x < len(nomsCopies):
			if args.quiet:
				print(nomsCopies[x])
				print("Status ultima copia: " + (statusCopies[x]))
				print("Ultima copia correcte: " + (ultimaCorrecte[x]))
				print()
			llistaCopies.append({"Nom":nomsCopies[x], "Status ultima copia":statusCopies[x], "Ultima copia correcte":ultimaCorrecte[x]})
			x+=1
		llistaNas.append({"nomNAS":nas[2], "copies":llistaCopies})




	#guardar resultats en un JSON
	try:
		with open(args.json_file, 'w') as f:
			json.dump(llistaNas, f, indent = 4)
	except Exception as e:
		print("Error d'escriptura de json")
		now = datetime.datetime.now()
		date_string = now.strftime('%Y-%m-%d--%H-%M-%S-json')
		f = open(ruta+"/errorLogs/"+date_string+".txt",'w')
		f.write("Error d'escriptura de json "+str(e))
		f.close()
	if not(args.quiet):
		print("Done")

if __name__ =='__main__':
    main()