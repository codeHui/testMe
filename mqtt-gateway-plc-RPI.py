#
# pip install paho-mqtt
#

import paho.mqtt.client as mqtt
# from time import sleep
import time
import random
import json
import threading
import RPi.GPIO as GPIO
broker = 'chariot-dev.'
port = 1883

Buzzer = 11

CL = [0, 131, 147, 165, 175, 196, 211, 248]		# Frequency of Low C notes

CM = [0, 262, 294, 330, 350, 393, 441, 495]		# Frequency of Middle C notes

CH = [0, 525, 589, 661, 700, 786, 882, 990]		# Frequency of High C notes

song_1 = [	CM[3], CM[5], CM[6], CM[3], CM[2], CM[3], CM[5], CM[6], # Notes of song1
              CH[1], CM[6], CM[5], CM[1], CM[3], CM[2], CM[2], CM[3],
              CM[5], CM[2], CM[3], CM[3], CL[6], CL[6], CL[6], CM[1],
              CM[2], CM[3], CM[2], CL[7], CL[6], CM[1], CL[5]	]

beat_1 = [	1, 1, 3, 1, 1, 3, 1, 1, 			# Beats of song 1, 1 means 1/8 beats
              1, 1, 1, 1, 1, 1, 3, 1,
              1, 3, 1, 1, 1, 1, 1, 1,
              1, 2, 1, 1, 1, 1, 1, 1,
              1, 1, 3	]

song_2 = [	CM[1], CM[1], CM[1], CL[5], CM[3], CM[3], CM[3], CM[1], # Notes of song2
              CM[1], CM[3], CM[5], CM[5], CM[4], CM[3], CM[2], CM[2],
              CM[3], CM[4], CM[4], CM[3], CM[2], CM[3], CM[1], CM[1],
              CM[3], CM[2], CL[5], CL[7], CM[2], CM[1]	]

beat_2 = [	1, 1, 2, 2, 1, 1, 2, 2, 			# Beats of song 2, 1 means 1/8 beats
              1, 1, 2, 2, 1, 1, 3, 1,
              1, 2, 2, 1, 1, 2, 2, 1,
              1, 2, 2, 1, 1, 3 ]

def setup():
    GPIO.setmode(GPIO.BOARD)		# Numbers GPIOs by physical location
    GPIO.setup(Buzzer, GPIO.OUT)	# Set pins' mode is output
    global Buzz						# Assign a global variable to replace GPIO.PWM
    Buzz = GPIO.PWM(Buzzer, 440)	# 440 is initial frequency.
    Buzz.start(50)



topic_publish_connect="v1/gateway/connect"
topic_publish_telemetry = 'v1/gateway/telemetry'
#客戶端rpc客戶端publish的topic
topic_publish_client_rpc = 'v1/devices/me/rpc/request/'

topic_publish_attributes_me = "v1/devices/me/attributes"
topic_publish_attributes  = "v1/gateway/attributes"
#服務端rpc客戶端publish的topic
topic_publish_server_rpc = 'v1/devices/me/rpc/response/'

#服務端attribute變化，客戶端subscribe的topic
topic_subscribe_attributes = "v1/gateway/attributes/response"
#服務端rpc客戶端subscribe的topic
topic_subscribe_server_prc = "v1/gateway/rpc"

#客戶端rpc客戶端subscribe的topic
topic_subscribe_client_prc = topic_publish_server_rpc

factoryNumber = 1
lineNumber = 1
entityId = "_"+str(factoryNumber)+"_" + str(lineNumber)

deviceName_incubation = "incubation"
deviceName_storage = "storage"
deviceName_temperature = "temperature"
device_incubation_1=deviceName_incubation+"_1"+entityId
device_incubation_2=deviceName_incubation+"_2"+entityId
device_incubation_3=deviceName_incubation+"_3"+entityId
device_incubation_4=deviceName_incubation+"_4"+entityId
device_incubation_5=deviceName_incubation+"_5"+entityId
device_storage_1=deviceName_storage+"_1"+entityId
# cooler
device_temperature_1=deviceName_temperature+"_1"+entityId
# heat exchanger
device_temperature_2=deviceName_temperature+"_2"+entityId

# sameDeviceId="warehouseGateway"
sameDeviceId="yogurt_line"+entityId
clientId = sameDeviceId
username = sameDeviceId
password = sameDeviceId
uploadInterval = 3
switchOnOff = True
targetTemp = 35.5
currentTemp = 35.5

setup()
client = mqtt.Client(clientId)
client.username_pw_set(username, password)


def startAlarm():
    print("start alarm")
    print ('\n    Playing song 1...')
    for i in range(1, len(song_1)):		# Play song 1
        Buzz.ChangeFrequency(song_1[i])	# Change the frequency along the song note
        time.sleep(beat_1[i] * 0.5)		# delay a note for beat * 0.5s




def publish(topic,msg):
    msgStr = json.dumps(msg)
    print("publish   ==> Topic:" + topic + "     Payload:" + msgStr)
    client.publish(topic, msgStr)


def on_message(client, userdata, message):
    global uploadInterval
    global switchOnOff
    global targetTemp
    topic = message.topic
    messageJson = json.loads(message.payload)
    # str(message.payload) 會帶類型
    print("subscribe <== Topic:" + topic + "     Payload:" + str(messageJson) + "     QoS:" + str(message.qos))


    if (topic_subscribe_attributes == topic):
        if ("uploadInterval_target" in messageJson):
            uploadInterval = messageJson["uploadInterval_target"]
            publish(topic_publish_telemetry,{"uploadInterval_report": uploadInterval})
    elif (topic.startswith(topic_subscribe_server_prc)):
        # method = messageJson["method"]
        # params = messageJson["params"]
        method = messageJson["data"]["method"]
        params = messageJson["data"]["params"]
        deviceSubStr = messageJson["device"]
        # requestId = topic[len(topic_subscribe_server_prc):]
        if (method == "setValue"):
            targetTemp=params
            # publish(topic_publish_server_rpc + requestId, {"switch":switchOnOff,"debugFlag":"debugFlagValue"})
        # elif (method == "getValue"):
        #     publish(topic_publish_server_rpc + requestId, switchOnOff)
# Topic:v1/gateway/rpc     Payload:{'device': 'incubation_2_1_1', 'data': {'id': 17, 'method': 'setGpio', 'params': {'pin': '23', 'value': 1}}}
        elif (method == "setAlarm"):
            if(deviceSubStr == 'incubation_2_1_1'):
                startAlarm()



client.on_message = on_message

# 設備connect到MQTT服務器
# https://github.com/eclipse/paho.mqtt.python
client.connect(broker, port, 600)
print("connect to "+broker+sameDeviceId)
# 設備初始化subscribe需要接收的topics
client.subscribe( topic_subscribe_attributes)
client.subscribe( topic_subscribe_server_prc + "/+")
# client.subscribe( topic_subscribe_client_prc + "+")
# 服務端rpc客戶端subscribe的topic,test
client.subscribe( "v1/devices/me/rpc/request/" + "+")



publish(topic_publish_connect,{"device":device_incubation_1})
publish(topic_publish_connect,{"device":device_incubation_2})
publish(topic_publish_connect,{"device":device_incubation_3})
publish(topic_publish_connect,{"device":device_incubation_4})
publish(topic_publish_connect,{"device":device_incubation_5})
publish(topic_publish_connect,{"device":device_storage_1})
publish(topic_publish_connect,{"device":device_temperature_1})
publish(topic_publish_connect,{"device":device_temperature_2})

initAttributes = {device_incubation_1: {"subDeviceType": "incubation"}
    ,device_incubation_2: {"subDeviceType": "incubation"}
    ,device_incubation_3: {"subDeviceType": "incubation"}
    ,device_incubation_4: {"subDeviceType": "incubation"}
    ,device_incubation_5: {"subDeviceType": "incubation"}
    ,device_storage_1: {"subDeviceType": "storage","alarm_type":"fail_to_collect","alarm_detail": "alarm_details"}
    ,device_temperature_1: {"subDeviceType": "temperature"}
    ,device_temperature_2: {"subDeviceType": "temperature"}
                  }
publish(topic_publish_attributes,initAttributes)


initAttributesMe = {"isWorking": True}
publish(topic_publish_attributes_me,initAttributesMe)


def repeat():
    global targetTemp
    global currentTemp

    # alarm
    # publish( topic_publish_client_rpc + str(int(time.time())),{"method": "gatewayAlarm","alarmMessage":"fail to connect XX sensor"})
    if switchOnOff:
        # temperature = random.randrange(20, 50)
        if(targetTemp > currentTemp):
           currentTemp = currentTemp+1
        elif(targetTemp < currentTemp):
            currentTemp = currentTemp-1

        temperature = currentTemp + random.randrange(-1, 1)
        level = random.randrange(1, 9)
        # todo
        ph = random.randrange(40, 70)/10
        # print("qqqqqqqq" + str(type(ph)))
        weight = random.randrange(10, 35)

        timestamp = int(time.time())*1000
        msg = {
            device_incubation_1: [
                {
                    "ts": timestamp,
                    "values": {
                        "temperature": temperature,
                        "ph": ph,
                        "level": level
                    }
                }
            ],
            device_incubation_2: [
                {
                    "ts": timestamp,
                    "values": {
                        "temperature": temperature+1,
                        "ph": round(ph-1, 1),
                        "level": level+1
                    }
                }
            ],
            device_incubation_3: [
                {
                    "ts": timestamp,
                    "values": {
                        "temperature": temperature+1,
                        "ph": round(ph-1, 1),
                        "level": level+1
                    }
                }
            ],
            device_incubation_4: [
                {
                    "ts": timestamp,
                    "values": {
                        "temperature": temperature-3,
                        "ph": ph,
                        "level": level+1
                    }
                }
            ],
            device_incubation_5: [
                {
                    "ts": timestamp,
                    "values": {
                        "temperature": temperature+1,
                        "ph": round(ph+1, 1),
                        "level": level
                    }
                }
            ],
            device_storage_1: [
                {
                    "ts": timestamp,
                    "values": {
                        "weight": weight,
                    }
                }
            ],
            device_temperature_1: [
                {
                    "ts": timestamp,
                    "values": {
                        "temperature": temperature+1,
                    }
                }
            ],
            device_temperature_2: [
                {
                    "ts": timestamp,
                    "values": {
                        "temperature": temperature-10,
                    }
                }
            ]
        }
        publish(topic_publish_telemetry,msg)

    t = threading.Timer(uploadInterval, repeat, [])  # [i] 是repeat参数
    t.start()


repeat()

client.loop_forever()
