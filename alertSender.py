import pickle
import time
from datetime import datetime
import cmcAPI
import requests

import os
from dotenv import load_dotenv
load_dotenv()

###########################################################
def main() -> None:
	print("alertSender started.")

	trendlines = {}
	strippedCoinNameList = []
	strippedCoinNameString = ''

	while True:
		try:
			trendlinesFile = open("trendlinesFile.pkl", "rb")
			trendlines = pickle.load(trendlinesFile)
		except:
			trendlinesFile = open("trendlinesFile.pkl", "wb")
			pickle.dump(trendlines, trendlinesFile)
			trendlinesFile.close()

		for coin in trendlines:
			strippedCoinName = coin.split("-")[0]
			if strippedCoinName not in strippedCoinNameList:
				strippedCoinNameList.append(strippedCoinName)
		strippedCoinNameString = ",".join(strippedCoinNameList)

		prices = cmcAPI.getPrices(strippedCoinNameString)

		for coin in trendlines:
			coinName = coin
			price = prices['data'][coinName.split("-")[0]]['quote']['USD']['price'] #Fetch price of coinName from exchange/some api
			print(price)
			for i in trendlines[coinName]:
				# print(i)
				m, b, direction = i[0], i[1], i[2]
				y=(m*(datetime.now().timestamp()))+b

				msg=f'{coinName.split("-")[0] + " is at a trendline!"}'

				if direction == "Above":
					if price >= y:
						requests.get(f'https://api.telegram.org/bot{os.environ.get("telegramBotToken")}/sendMessage?chat_id={os.environ.get("telegramChatID")}&parse_mode=Markdown&text={msg}')
				elif direction == "Below":
					if price <= y:
						requests.get(f'https://api.telegram.org/bot{os.environ.get("telegramBotToken")}/sendMessage?chat_id={os.environ.get("telegramChatID")}&parse_mode=Markdown&text={msg}')


		time.sleep(900) #Check every 15 minutes

if __name__ == '__main__':
    main()