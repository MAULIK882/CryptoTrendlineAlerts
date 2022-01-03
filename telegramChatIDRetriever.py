import requests
import os
from dotenv import load_dotenv
import json
load_dotenv()

###########################################################

responseContents = json.loads(requests.get(f'https://api.telegram.org/bot{os.environ.get("telegramBotToken")}/getUpdates').text)

try:
	if 'error_code' in responseContents:
		print("Set telegramBotToken in your .env file first.")
	else:
		print("Your telegram chat ID is: " + str(responseContents['result'][0]['message']['chat']['id']))
except IndexError:
	print("Send any message to your bot and run again.")