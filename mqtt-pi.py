#
# pip install paho-mqtt
#

import paho.mqtt.client as mqtt
# from time import sleep
import time
import random
import json
import threading


broker = '172.23.20.187'
port = 1883
topic_publish_telemetry = 'v1/devices/me/telemetry'
#服務端rpc客戶端publish的topic
topic_publish_server_rpc = 'v1/devices/me/rpc/response/'
#客戶端rpc客戶端publish的topic
topic_publish_client_rpc = 'v1/devices/me/rpc/request/'

#服務端attribute變化，客戶端subscribe的topic
topic_subscribe_attributes = "v1/devices/me/attributes"
#服務端rpc客戶端subscribe的topic
topic_subscribe_server_prc = topic_publish_client_rpc
#客戶端rpc客戶端subscribe的topic
topic_subscribe_client_prc = topic_publish_server_rpc

clientId = "maskDevice"
username = "maskDevice"
password = "maskDevice"
uploadInterval = 60
switchOnOff = True

client = mqtt.Client(clientId)
client.username_pw_set(username, password)


def publish(topic,msg):
    msgStr = json.dumps(msg)
    print("publish   ==> Topic:" + topic + "     Payload:" + msgStr)
    client.publish(topic, msgStr)


def on_message(client, userdata, message):
    global uploadInterval
    global switchOnOff
    topic = message.topic
    messageJson = json.loads(message.payload)
    # str(message.payload) 會帶類型
    print("subscribe <== Topic:" + topic + "     Payload:" + str(messageJson) + "     QoS:" + str(message.qos))


    if (topic_subscribe_attributes == topic):
        if ("uploadInterval_target" in messageJson):
            uploadInterval = messageJson["uploadInterval_target"]
            publish(topic_publish_telemetry,{"uploadInterval_report": uploadInterval})
    elif (topic.startswith(topic_subscribe_server_prc)):
        method = messageJson["method"]
        params = messageJson["params"]
        requestId = topic[len(topic_subscribe_server_prc):]
        if (method == "setValue"):
            switchOnOff=params
            publish(topic_publish_server_rpc + requestId, {"switch":switchOnOff,"debugFlag":"debugFlagValue"})
        elif (method == "getValue"):
            publish(topic_publish_server_rpc + requestId, switchOnOff)



client.on_message = on_message

# 設備connect到MQTT服務器
# https://github.com/eclipse/paho.mqtt.python
client.connect(broker, port, 600)
print("connect to "+broker)
# 設備初始化subscribe需要接收的topics
client.subscribe( topic_subscribe_attributes)
client.subscribe( topic_subscribe_server_prc + "+")
client.subscribe( topic_subscribe_client_prc + "+")


publish( topic_publish_client_rpc + str(int(time.time())),{"method": "getCurrentTime"})


def repeat():
    if switchOnOff:
        x = random.randrange(60, 80)
        y = random.randrange(20, 40)

        msg = {"temperature": x, "speed": y}
        publish(topic_publish_telemetry,msg)

    t = threading.Timer(uploadInterval, repeat, [])  # [i] 是repeat参数
    t.start()


repeat()

client.loop_forever()
