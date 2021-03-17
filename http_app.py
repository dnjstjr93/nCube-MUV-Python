# -*-coding:utf-8 -*-

"""
 Created by Wonseok Jung in KETI on 2021-03-16.
"""

import http
import json
import uuid
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import ssl
import subprocess
import os, sys, shutil, platform, socket, random
from http.server import BaseHTTPRequestHandler, HTTPServer

import http_adn as sh_adn
import noti
import thyme_tas_mav as tas_mav

from conf import conf
from thyme import sh_state

HTTP_SUBSCRIPTION_ENABLE = 0
MQTT_SUBSCRIPTION_ENABLE = 0

my_gcs_name = ''
my_parent_cnt_name = ''
my_cnt_name = ''
pre_my_cnt_name = ''
my_mission_parent = ''
my_mission_name = ''
my_sortie_name = 'disarm'

my_drone_type = 'pixhawk'
my_secure = 'off'
my_system_id = 8

Req_auth = ''
Res_auth = ''
Result_auth = ''
Certification = ''

retry_interval = 2500
normal_interval = 100

authResult = 'yet'

server = None
noti_topic = ''
muv_sub_gcs_topic = ''

muv_sub_msw_topic = []

muv_pub_fc_gpi_topic = ''
muv_pub_fc_hb_topic = ''


def getType(p):
    type = 'string'
    if (isinstance(p, list)):
        type = 'list'
    elif (isinstance(p, str)):
        try:
            if (isinstance(p, dict)):
                type = 'string_dictionary'
            else:
                type = 'string'
        except:
            type = 'string'
            return type
    elif (p is not None) and (isinstance(p, dict)):
        type = 'dictionary'
    else:
        type = 'other'
    return type


# ready for mqtt
for i in range(0, len(conf['sub'])):
    if conf['sub'][i]['name'] is not None:
        if urlparse(conf['sub'][i]['nu']).scheme == 'http:':
            HTTP_SUBSCRIPTION_ENABLE = 1
            if urlparse(conf['sub'][i]['nu']).netloc == 'autoset':
                conf.sub[i]['nu'] = 'http://' + socket.gethostbyname(socket.gethostname()) + ':' + conf.ae.port + url.parse(conf.sub[i]['nu']).pathname
        elif urlparse(conf['sub'][i]['nu']).scheme == 'mqtt:':
            MQTT_SUBSCRIPTION_ENABLE = 1
        else:
            print('notification uri of subscription is not supported')


return_count = 0
request_count = 0


def ready_for_notification():
    global noti_topic
    global mqtt_client

    if HTTP_SUBSCRIPTION_ENABLE == 1:
        server = HTTPServer(('0.0.0.0', int(conf['ae']['port'])), BaseHTTPRequestHandler)
        print('http_server running at {} port'.format(conf['ae']['port']))
        server.serve_forever()

    if MQTT_SUBSCRIPTION_ENABLE == 1:
        for i in range(0, len(conf['sub'])):
            if conf['sub'][i]['name'] is not None:
                if urlparse(conf['sub'][i]['nu']).scheme == 'mqtt:':
                    if urlparse(conf['sub'][i]['nu']).netloc == 'autoset':
                        conf.sub[i]['nu'] = 'mqtt://' + conf.cse.host + '/' + conf.ae.id
                        noti_topic = '/oneM2M/req/+/{}/#'.format(conf.ae.id)
                    elif urlparse(conf['sub'][i]['nu']).netloc == conf.cse.host:
                        noti_topic = '/oneM2M/req/+/{}/#'.format(conf.ae.id)
                    else:
                        noti_topic = '{}'.format(urlparse(conf['sub'][i]['nu']).path)

        mqtt_connect(conf['cse']['host'], muv_sub_gcs_topic, noti_topic)

        # muv_mqtt_connect('localhost', 1883, muv_sub_msw_topic)


def git_clone(mission_name, directory_name, repository_url):
    try:
        shutil.rmtree('./{}'.format(directory_name))
    except (FileNotFoundError, OSError) as e:
        print(e)

    gitClone = subprocess.Popen(['git', 'clone', repository_url, directory_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    try:
        stdout, stderr = gitClone.communicate()
        retcode = gitClone.returncode
        if retcode == 0:
            print('stdout: {}'.format(stdout))
            print('cloning finish...')
            requireMsw(mission_name, directory_name)
        else:
            print('stderr: {}'.format(stdout))
    except:
        print("Error: ", sys.exc_info()[0])


def git_pull(mission_name, directory_name):
    try:
        if platform.system() == 'Windows':
            cmd = 'git'
        else:
            cmd = 'git'

        gitPull = subprocess.Popen([cmd, 'pull'], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, cwd=os.getcwd() + '/' + directory_name, text=True)

        (stdout, stderr) = gitPull.communicate()

        retcode = gitPull.returncode
        if retcode == 0:
            print('stdout: {}'.format(stdout))
            requireMsw(mission_name, directory_name)
        else:
            print('stderr: {}'.format(stdout))

    except:
        print('error')


def npm_install(mission_name, directory_name):
    try:
        if platform.system() == 'Windows':
            cmd = 'npm.cmd'
        else:
            cmd = 'npm'

        npmInstall = subprocess.Popen([cmd, 'install'], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, cwd=os.getcwd() + '/' + directory_name, text=True)

        (stdout, stderr) = npmInstall.communicate()

        retcode = npmInstall.returncode
        if retcode == 0:
            print('stdout: {}'.format(stdout))
            fork_msw(mission_name, directory_name)
        else:
            print('stderr: {}'.format(stdout))
            npm_install(mission_name, directory_name)

    except:
        print('error')

# npm_install('msw_timesync', 'msw_timesync_msw_timesync')

def fork_msw(mission_name, directory_name):
    executable_name = directory_name.replace(mission_name + '_', '')

    nodeMsw = subprocess.Popen(['node', executable_name], stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, cwd=os.getcwd() + '/' + directory_name, text=True)

    (stdout, stderr) = nodeMsw.communicate()

    retcode = nodeMsw.returncode
    if retcode == 0:
        print('stdout: {}'.format(stdout))

    else:
        print('stderr: {}'.format(stdout))
        npm_install(mission_name, directory_name)

# fork_msw('msw_timesync', 'msw_timesync_msw_timesync')

msw_directory = {}
def requireMsw(mission_name, directory_name):
    global msw_directory
    require_msw_name = directory_name.replace(mission_name + '_', '')
    msw_directory[require_msw_name] = directory_name

    msw_package = './' + directory_name + '/' + require_msw_name
    # import msw_package


def ae_response_action(status, res_body, callback):
    aeid = res_body['m2m:ae']['aei']
    conf.ae.id = aeid
    callback(status, aeid)


drone_info = {}
mission_parent = []
def retrieve_my_cnt_name(callback):
    global sh_state
    print('[sh_state] : {}'.format(sh_state))
    sh_state = 'crtae'
    http_watchdog()

def http_watchdog():
    global sh_state

    if sh_state == 'rtvct':
        retrieve_my_cnt_name(1)
    elif sh_state == 'crtae':
        print('[sh_state] : {}'.format(sh_state))
        sh_state = 'rtvae'
        http_watchdog()
    elif sh_state == 'rtvae':
        print('[sh_state] : {}'.format(sh_state))
        sh_state = 'crtct'
        http_watchdog()
    elif sh_state == 'crtct':
        print('[sh_state] : {}'.format(sh_state))
        sh_state = 'delsub'
        http_watchdog()
    elif sh_state == 'delsub':
        print('[sh_state] : {}'.format(sh_state))
        sh_state = 'crtsub'
        http_watchdog()
    elif sh_state == 'crtsub':
        print('[sh_state] : {}'.format(sh_state))
        sh_state = 'crtci'
        http_watchdog()
    elif sh_state == 'crtci':
        print('[sh_state] : {}'.format(sh_state))


def on_connect(client,userdata,flags, rc):
    print("Connected with result code" + str(rc))

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    message = str(msg.payload.decode("utf-8"))
    if (msg.topic == muv_sub_gcs_topic):
        tas_mav.gcs_noti_handler(message)

    else:
        if (msg.topic.includes('/oneM2M/req/')):
            jsonObj = json.dumps(message)

            if (jsonObj['m2m:rqp'] is None):
                jsonObj['m2m:rqp'] = jsonObj

            noti.mqtt_noti_action(msg.topic.split('/'), jsonObj)

    try:
        msg_obj = json.dumps(message)
        send_to_Mobius((msg.topic), msg_obj, int(random.random() * 10))
        # print(topic + ' - ' + JSON.stringify(msg_obj))

    except:
        msg_obj = message
        send_to_Mobius((msg.topic), msg_obj, int(random.random() * 10))
        # print(topic + ' - ' + msg_obj)

from thyme import mqtt_client
def mqtt_connect(serverip, sub_gcs_topic, noti_topic):
    global mqtt_client

    if mqtt_client is None:
        print('mqtt_client is None')
        if conf['usesecure'] == 'disable':
            mqtt_client = mqtt.Client()
            mqtt_client.on_connect = on_connect
            mqtt_client.reconnect_delay_set(min_delay=2, max_delay=10)
            mqtt_client.on_disconnect = on_disconnect
            mqtt_client.on_subscribe = on_subscribe
            mqtt_client.on_message = on_message
            print('fc_mqtt is connected')
            if (sub_gcs_topic is not ''):
                print(sub_gcs_topic)
                mqtt_client.subscribe(sub_gcs_topic, 0)
                print('[mqtt_connect] sub_gcs_topic is subscribed: ' + sub_gcs_topic)

            if (noti_topic is not ''):
                mqtt_client.subscribe(noti_topic, 0)
                print('[mqtt_connect] noti_topic is subscribed:  ' + noti_topic)
            mqtt_client.connect(serverip, int(conf['cse']['mqttport']), keepalive=10)
            mqtt_client.loop_start()

        else:
            """TBD mqtt secure"""
            # mqtt_client = mqtt.Client()
            # mqtt_client.on_connect = on_connect
            # mqtt_client.reconnect_delay_set(min_delay=2, max_delay=10)
            # mqtt_client.on_disconnect = on_disconnect
            # mqtt_client.on_subscribe = on_subscribe
            # mqtt_client.on_message = on_message
            # print('fc_mqtt is connected')
            # if (sub_gcs_topic is not ''):
            #     print(sub_gcs_topic)
            #     mqtt_client.subscribe(sub_gcs_topic, 0)
            #     print('[mqtt_connect] sub_gcs_topic is subscribed: ' + sub_gcs_topic)
            #
            # if (noti_topic is not ''):
            #     mqtt_client.subscribe(noti_topic, 0)
            #     print('[mqtt_connect] noti_topic is subscribed:  ' + noti_topic)
            # mqtt_client.tls_set(certfile='./server-crt.pem', keyfile='./server-key.pem')
            # mqtt_client.connect(serverip, int(conf['cse']['mqttport']), keepalive=10)
            # mqtt_client.loop_start()
            # print(mqtt_client)


from thyme import muv_mqtt_client
def muv_mqtt_connect(broker_ip, port, noti_topic):
    global muv_mqtt_client
    print(muv_mqtt_client)
    if muv_mqtt_client is None:
        if conf['usesecure'] == 'disable':
            mqtt_client = mqtt.Client()
            mqtt_client.on_connect = on_connect
            mqtt_client.reconnect_delay_set(min_delay=2, max_delay=10)
            mqtt_client.on_disconnect = on_disconnect
            mqtt_client.on_subscribe = on_subscribe
            mqtt_client.on_message = on_message
            print('muv_mqtt connected to ' + broker_ip)
            for i in range(len(noti_topic)):
                muv_mqtt_client.subscribe(noti_topic[i])
                print('[muv_mqtt_connect] noti_topic[' + i + ']: ' + noti_topic[i])
            mqtt_client.connect(broker_ip, port, keepalive=10)
            mqtt_client.loop_start()

        else:
            """TBD mqtt secure"""


def send_to_Mobius(topic, content_each_obj, gap):
    print('send_to_Mobius')
#     setTimeout(function (topic, content_each_obj):
#         sh_adn.crtci(topic+'?rcn=0', 0, content_each_obj, null, function ():
#         });
#     }, gap, topic, content_each_obj);
# }
muv_mqtt_connect('localhost', 1883, noti_topic)