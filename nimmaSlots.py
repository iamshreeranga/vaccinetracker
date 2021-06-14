#Nimmaslot here

import requests
from datetime import datetime
import schedule
import time
import os

base_district_url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict" 
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.02 Safari/537.36'}
kar_district_ids = [287,273]
group_id="nimmaslots"
now = datetime.now()
today_date = now.strftime("%d-%m-%Y")
api_url_telegram = "https://api.telegram.org/__API_KEY__/sendMessage?chat_id=@__idhere__&text="
api_url_telegram = api_url_telegram.replace("__API_KEY__",os.environ['API_KEY'])
List = []
count=0

def send_message_telegram(message):
	final_url_telegram = api_url_telegram.replace("__idhere__",group_id)
	final_url_telegram = final_url_telegram + message
	response = requests.get(final_url_telegram)
	print(response)
	if response.status_code != 200 : 
		List.clear()
	
  

def extract_availability_data(response):
	response_json = response.json()
	for center in response_json["centers"]:
		#print(center["name"] , center["address"])
		message =""
		details = "\n*Name : {},\n PinCode : {},\n Address : {}\n \n".format(
					center["name"] , center["pincode"], center["address"])
		for session in center["sessions"] :
			#slot = str(center["name"])+str(session["date"])
			slot = str(center["center_id"])+str(session["session_id"])
			if session["available_capacity_dose1"] > 0  and session["min_age_limit"] < 45 and slot not in List:
				List.append(slot)
				message+= " 18y Dose I : {},\n Date : {},\n Vaccine : {}\n \n".format(
					session["available_capacity_dose1"] , session["date"],session["vaccine"]) 
			if session["available_capacity_dose2"] > 0  and session["min_age_limit"] > 18 and slot not in List:
				List.append(slot)
				message += " [45y Dose II] : {},\n Date : {},\n Vaccine : {}\n \n".format(
					 session["available_capacity_dose2"] , session["date"],session["vaccine"]) 
		if len(message) != 0 : 
			#print(details+message)
			send_message_telegram(details+message)
	print("Count: {}, Date: {}".format(count,datetime.now()))

def fetch_data_from_district(district_id):
	query_params = "?district_id={}&date={}".format(district_id,today_date)
	final_url = base_district_url+query_params
	response = requests.get(final_url,headers=headers)
	#print(response.text)
	extract_availability_data(response)

def fetch_data_from_states(district_ids):
	clear_counter_notify_all()
	for district_id in district_ids :
		fetch_data_from_district(district_id)

def clear_counter_notify_all():
  global count
  count += 1
  if count > 8640 : #clears every day .. and sends latest availability
    count = 0
    List.clear()


	
if __name__ == "__main__":
	schedule.every(10).seconds.do(fetch_data_from_states,kar_district_ids)
	while True:
		schedule.run_pending()
		time.sleep(1)
