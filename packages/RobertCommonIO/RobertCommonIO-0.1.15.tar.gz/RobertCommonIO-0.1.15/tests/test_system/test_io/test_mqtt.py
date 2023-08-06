import time
from robertcommonio.system.io.mqtt import MQTTConfig, MQTTAccessor
from datetime import datetime

HOST = '47.103.96.35'
PORT = 11883
client_id = 'aiot_webapi_hqyc_client'
TOPIC = 'SUBSTATION/MASTER/101121-1/S_SNT_DAT1' #'SUBSTATION/MASTER/200120-1/S_SNT_DA' #'SUBSTATION/MASTER/200120-1/S_SNT_DAT'
USER = 'admin'
PSW = '!Abc@123'

def call_back(data):
    print(data)

def test_pub():
    accessor = MQTTAccessor(MQTTConfig(HOST=HOST, PORT=PORT, USER=USER, PSW=PSW, TOPIC=TOPIC, CLIENT_ID=client_id, KEEP_ALIVE=60))
    while True:
        accessor.publish_topic(TOPIC, datetime.now().strftime('%H:%M:%S'), 0)
        time.sleep(2)

def test_sub():
    accessor = MQTTAccessor(MQTTConfig(HOST=HOST, PORT=PORT, USER=USER, PSW=PSW, TOPIC=TOPIC, CLIENT_ID=client_id, KEEP_ALIVE=60, ENABLE_LOG=True))
    accessor.subscribe_topics(TOPIC, 0, 10, call_back)

test_pub()
