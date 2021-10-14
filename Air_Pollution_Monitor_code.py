import requests
import config
import json
import time
import tele_config

from boltiot import Bolt,Sms
thresh_per=70
mybolt=Bolt(config.API_KEY,config.DEVICE_ID)
sms=Sms(config.SID,config.AUTH_TOKEN,config.To_num,config.From_num)

def sensor_value(pin):
   try:
    response=mybolt.analogRead(pin)
    data=json.loads(response)
    print(data)
    mybolt.digitalWrite(0,'LOW')
    if data['success']!=1:
      print("Request failed!")
      print("Here is the response",data)
      return -999
    val=int(data['value'])
    return val
   except Exception as e:
    print("There is some error")
    print(e)
    return -999


def snd_tele_msg(msg):
   url="https://api.telegram.org/" + tele_config.tele_bot_id + "/sendMessage"
   data={"chat_id":tele_config.tele_chat_id,"text":msg}
   try:
    response=requests.request("POST",url,params=data)
    print("This is the telegram response")
    print(response.text)
    tele_data=json.loads(response.text)
    return tele_data["ok"]
   except Exception as e:
    print("Error occured while sending msg via telegram!")
    print(e)
while True:
    print("Getting Sensor Value...")
    res = sensor_value("A0")
    poll_per = (res/1024)*100
    print("The Pollution percentage in the surrounding area is: "+str(poll_per)+ "%")
    if res == -999:
      print("Oops!Error occured while getting the sensor value")

    elif res>=thresh_per:
      mybolt.digitalWrite(0,'HIGH')
      response=sms.send_sms("ALERT!The Current gas sensor Value is:"+str(res)+". The Pollution Percentage is:"+str(poll_per)+". Has Exceeded the threshold level!")
      print("Response received from Twilio -->",str(response))
      print("Check the status of the SMS -->",str(response.status))
      message="ALERT!The Current gas sensor Value is:"+str(res)+". The Pollution Percentage is:"+str(poll_per)+". Has Exceeded the threshold level!"
      tele_status=snd_tele_msg(message)
      print("The Status of Telegram message:",tele_status)
    time.sleep(10)
