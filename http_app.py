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
import os, sys, shutil, platform, socket, random, time
from http.server import BaseHTTPRequestHandler, HTTPServer

import noti
import thyme_tas_mav as tas_mav
from http_adn import *

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
mqtt_flag = ''
noti_topic = ''
muv_sub_gcs_topic = ''

muv_sub_msw_topic = []

muv_pub_fc_gpi_topic = ''
muv_pub_fc_hb_topic = ''

msw_package = ''


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
        except Exception as e:
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
                conf.sub[i]['nu'] = 'http://' + socket.gethostbyname(socket.gethostname()) + ':' + conf['ae']['port'] + urlparse(conf['sub'][i]['nu'])['pathname']
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
                        conf['sub'][i]['nu'] = 'mqtt://' + conf['cse']['host'] + '/' + conf['ae']['id']
                        noti_topic = '/oneM2M/req/+/{}/#'.format(conf['ae']['id'])
                    elif urlparse(conf['sub'][i]['nu']).netloc == conf['cse']['host']:
                        noti_topic = '/oneM2M/req/+/{}/#'.format(conf['ae']['id'])
                    else:
                        noti_topic = '{}'.format(urlparse(conf['sub'][i]['nu']).path)

        mqtt_connect(conf['cse']['host'])

        muv_mqtt_connect('localhost', 1883)


def git_clone(mission_name, directory_name, repository_url):
    try:
        shutil.rmtree('./{}'.format(directory_name))
    except Exception as e:
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
    except Exception as e:
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

    except Exception as e:
        print('error')


def npm_install(mission_name, directory_name):
    print("Start npm_install")
    try:
        if platform.system() == 'Windows':
            cmd = 'npm.cmd'
        else:
            cmd = 'npm'
        print(os.getcwd() + '/' + directory_name)
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

    except Exception as e:
        print('error')


def fork_msw(mission_name, directory_name):
    executable_name = directory_name.replace(mission_name + '_', '')

    nodeMsw = subprocess.Popen(['node', executable_name], stdin=my_sortie_name, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, cwd=os.getcwd() + '/' + directory_name, text=True)

    (stdout, stderr) = nodeMsw.communicate()

    retcode = nodeMsw.returncode
    if retcode == 0:
        print('stdout: {}'.format(stdout))

    else:
        print('stderr: {}'.format(stdout))
        npm_install(mission_name, directory_name)


msw_directory = {}


def requireMsw(mission_name, directory_name):
    global msw_package
    global msw_directory

    require_msw_name = directory_name.replace(mission_name + '_', '')
    msw_directory[require_msw_name] = directory_name

    msw_package = './' + directory_name + '/' + require_msw_name


def ae_response_action(status, res_body):
    aeid = res_body['m2m:ae']['aei']
    conf['ae']['id'] = aeid

    return status, aeid


def create_cnt_all(count):
    if len(conf['cnt']) == 0:
        return 2001, count
    else:
        try:
            if conf['cnt'][count] is not None:
                parent = conf['cnt'][count]['parent']
                rn = conf['cnt'][count]['name']
                rsc, res_body, count = crtct(parent, rn, count)
                if rsc == 5106 or rsc == 2001 or rsc == 4105:
                    count += 1
                    status, count = create_cnt_all(count)
                    return status, count
                else:
                    return 9999, count
            else:
                return 2001, count
        except Exception as e:
            # print(e)
            return 2001, count

def delete_sub_all(count):
    if len(conf['sub']) == 0:
        return 2001, count
    else:
        if conf['sub'].get(count):
            target = conf['sub'][count]['parent'] + '/' + conf['sub'][count]['name']
            rsc, res_body, count = delsub(target, count)
            if rsc == 5106 or rsc == 2002 or rsc == 2000 or rsc == 4105 or rsc == 4004:
                count += 1
                status, count = delete_sub_all(count)
                return status, count
            else:
                return 9999, count
        else:
            return 2001, count


def create_sub_all(count):
    if len(conf['sub']) == 0:
        return 2001, count
    else:
        if conf['sub'].get(count):
            parent = conf['sub'][count]['parent']
            rn = conf['sub'][count]['name']
            nu = conf['sub'][count]['nu']
            rsc, res_body, count = crtsub(parent, rn, nu, count)
            if rsc == 5106 or rsc == 2001 or rsc == 4105:
                count += 1
                status, count = create_sub_all(count)
                return status, count
            else:
                return '9999', count
        else:
            return 2001, count


drone_info = {}
mission_parent = []
def retrieve_my_cnt_name():
    global sh_state
    global drone_info
    global mission_parent
    global MQTT_SUBSCRIPTION_ENABLE
    global muv_sub_gcs_topic
    global noti_topic
    global my_system_id
    global muv_pub_fc_gpi_topic
    global muv_pub_fc_hb_topic
    global muv_sub_msw_topic
    global my_drone_type

    res, res_body, count = rtvct('/Mobius/'+conf['ae']['approval_gcs']+'/approval/'+conf['ae']['name']+'/la', 0)
    if res == 2000:
        drone_info = res_body['m2m:cin']['con']

        conf['sub'] = []
        conf['cnt'] = []
        conf['fc'] = []

        my_gcs_name = drone_info['gcs']

        if drone_info.get('host'):
            conf['cse']['host'] = drone_info['host']

        print("gcs host is " + conf['cse']['host'])

        info = {}
        info['parent'] = '/Mobius/' + drone_info['gcs']
        info['name'] = 'Drone_Data'
        conf['cnt'].append(info)

        info = {}
        info['parent'] = '/Mobius/' + drone_info['gcs'] + '/Drone_Data'
        info['name'] = drone_info['drone']
        conf['cnt'].append(info)

        info['parent'] = '/Mobius/' + drone_info['gcs'] + '/Drone_Data/' + drone_info['drone']
        info['name'] = my_sortie_name
        conf['cnt'].append(info)

        my_parent_cnt_name = info['parent']
        my_cnt_name = my_parent_cnt_name + '/' + info['name']

        # set container for mission
        info = {}
        info['parent'] = '/Mobius/' + drone_info['gcs']
        info['name'] = 'Mission_Data'
        conf['cnt'].append(info)

        info = {}
        info['parent'] = '/Mobius/' + drone_info['gcs'] + '/Mission_Data'
        info['name'] = drone_info['drone']
        conf['cnt'].append(info)

        if drone_info.get('mission'):
            for mission_name in drone_info['mission']:
                if drone_info['mission'].get(mission_name):
                    info = {}
                    info['parent'] = '/Mobius/' + drone_info['gcs'] + '/Mission_Data/' + drone_info['drone']
                    info['name'] = mission_name
                    conf['cnt'].append(info)

                    chk_cnt = 'container'
                    if drone_info['mission'][mission_name].get(chk_cnt):
                        for i in range(len(drone_info['mission'][mission_name][chk_cnt])):
                            if drone_info['mission'][mission_name][chk_cnt][i] is not None:
                                container_name = drone_info['mission'][mission_name][chk_cnt][i].split(':')[0]
                                info = {}
                                info['parent'] = '/Mobius/' + drone_info['gcs'] + '/Mission_Data/' + drone_info['drone'] + '/' + mission_name
                                info['name'] = container_name
                                conf['cnt'].append(info)

                                info = {}
                                info['parent'] = '/Mobius/' + drone_info['gcs'] + '/Mission_Data/' + drone_info[
                                    'drone'] + '/' + mission_name + '/' + container_name
                                info['name'] = my_sortie_name
                                conf['cnt'].append(info)
                                mission_parent.append(info['parent'])

                                muv_sub_msw_topic.append(info['parent'] + '/#')

                                if len(drone_info['mission'][mission_name][chk_cnt][i].split(':')) > 1:
                                    info = {}
                                    info['parent'] = '/Mobius/' + drone_info['gcs'] + '/Mission_Data/' + drone_info[
                                        'drone'] + '/' + mission_name + '/' + container_name
                                    info['name'] = 'sub_msw'
                                    info['nu'] = 'mqtt://' + drone_info['gcs']['host'] + '/' + drone_info['mission'][mission_name][chk_cnt][i].split(':')[1] + '?ct=json'
                                    conf['cnt'].append(info)

                    chk_cnt = 'sub_container'
                    if drone_info['mission'][mission_name].get(chk_cnt):
                        for i in range(len(drone_info['mission'][mission_name][chk_cnt])):
                            if drone_info['mission'][mission_name][chk_cnt][i] is not None:
                                sub_container_name = drone_info['mission'][mission_name][chk_cnt][i]
                                info = {}
                                info['parent'] = '/Mobius/' + drone_info['gcs'] + '/Mission_Data/' + drone_info[
                                    'drone'] + '/' + mission_name
                                info['name'] = sub_container_name
                                conf['cnt'].append(info)

                                info = {}
                                info['parent'] = '/Mobius/' + drone_info['gcs'] + '/Mission_Data/' + drone_info[
                                    'drone'] + '/' + mission_name + '/' + sub_container_name
                                info['name'] = sub_container_name
                                info['nu'] = 'mqtt://' + drone_info['gcs']['host'] + '/' + conf['ae']['id'] + '?ct=json'
                                conf['cnt'].append(info)

                    chk_cnt = 'fc_container'
                    if drone_info['mission'][mission_name].get(chk_cnt):
                        for i in range(len(drone_info['mission'][mission_name][chk_cnt])):
                            if drone_info['mission'][mission_name][chk_cnt][i] is not None:
                                container_name = drone_info['mission'][mission_name][chk_cnt][i]
                                info = {}
                                info['parent'] = '/Mobius/' + drone_info['gcs'] + '/Mission_Data/' + drone_info['drone'] + '/' + mission_name
                                info['name'] = container_name
                                conf['fc'].append(info)

                    chk_cnt = 'git'
                    if drone_info['mission'][mission_name].get(chk_cnt):
                        repo_arr = drone_info['mission'][mission_name][chk_cnt].split('/')
                        directory_name = mission_name + '_' + repo_arr[len(repo_arr)-1].replace('.git', '')
                        try:
                            if os.path.isdir('./' + directory_name):
                                git_pull(mission_name, directory_name)
                            else:
                                git_clone(mission_name, directory_name, drone_info['mission'][mission_name][chk_cnt])
                        except Exception as e:
                            print(e)

        if drone_info.get('type'):
            my_drone_type = drone_info['type']
        else:
            my_drone_type = 'pixhawk'

        drone_type = {}
        drone_type['type'] = my_drone_type
        with open('./drone_type.json', 'w') as f:
            json.dump(drone_type, f, indent=4)

        if drone_info.get('system_id'):
            my_system_id = drone_info['system_id']
        else:
            my_system_id = 8

        muv_pub_fc_gpi_topic = '/Mobius/' + my_gcs_name + '/Drone_Data/' + drone_info['drone'] + '/global_position_int'
        muv_pub_fc_hb_topic = '/Mobius/' + my_gcs_name + '/Drone_Data/' + drone_info['drone'] + '/heartbeat'

        muv_sub_gcs_topic = '/Mobius/' + my_gcs_name + '/GCS_Data/' + drone_info['drone']
        MQTT_SUBSCRIPTION_ENABLE = 1
        sh_state = 'crtae'
        http_watchdog()
    else:
        print('x-m2m-rsc : ' + str(res) + ' <----' + str(res_body))
        time.sleep(0.25)
        http_watchdog()


def http_watchdog():
    global sh_state
    global return_count
    global request_count

    if sh_state == 'rtvct':
        print('[sh_state] : {}'.format(sh_state))
        retrieve_my_cnt_name()
    elif sh_state == 'crtae':
        print('[sh_state] : {}'.format(sh_state))
        status, res_body = crtae(conf['ae']['parent'], conf['ae']['name'], conf['ae']['appid'])
        print(res_body)
        if status == 2001:
            status, aeid = ae_response_action(status, res_body)
            print('x-m2m-rsc : ' + str(status) + ' - ' + aeid + ' <----')
            sh_state = 'rtvae'
            request_count = 0
            return_count = 0

            http_watchdog()
        elif status == 5106 or status == 4105:
            print('x-m2m-rsc : ' + str(status) + ' <----')
            sh_state = 'rtvae'

            http_watchdog()
        else:
            print('x-m2m-rsc : ' + str(status) + ' <----')
            http_watchdog()
    elif sh_state == 'rtvae':
        if conf['ae']['id'] == 'S':
            conf['ae']['id'] = 'S' + uuid.uuid1()

        print('[sh_state] : {}'.format(sh_state))
        status, res_body = rtvae(conf['ae']['parent'] + '/' + conf['ae']['name'])
        if status == 2000:
            aeid = res_body['m2m:ae']['aei']
            print('x-m2m-rsc : ' + str(status) + ' - ' + aeid + ' <----')

            if (conf['ae']['id'] != aeid) and (conf['ae']['id'] != ('/' + aeid)):
                print('AE-ID created is ' + aeid + ' not equal to device AE-ID is ' + conf['ae']['id'])
            else:
                sh_state = 'crtct'
                request_count = 0
                return_count = 0

                http_watchdog()
        else:
            print('x-m2m-rsc : ' + str(status) + ' <----')
            http_watchdog()
    elif sh_state == 'crtct':
        print('[sh_state] : {}'.format(sh_state))
        status, count = create_cnt_all(request_count)
        if status == 9999:
            http_watchdog()
        else:
            count += 1
            request_count = count
            return_count = 0
            if len(conf['cnt']) <= count:
                sh_state = 'delsub'
                request_count = 0
                return_count = 0

                http_watchdog()
    elif sh_state == 'delsub':
        print('[sh_state] : {}'.format(sh_state))
        status, count = delete_sub_all(request_count)
        if status == 9999:
            http_watchdog()
        else:
            count += 1
            request_count = count
            return_count = 0
            if len(conf['sub']) <= count:
                sh_state = 'crtsub'
                request_count = 0
                return_count = 0

                http_watchdog()
    elif sh_state == 'crtsub':
        print('[sh_state] : {}'.format(sh_state))
        status, count = create_sub_all(request_count)
        if status == 9999:
            http_watchdog()
        else:
            count += 1
            request_count = count
            return_count = 0
            if len(conf['sub']) <= count:
                sh_state = 'crtci'

                ready_for_notification()

                tas_mav.tas_ready(my_drone_type)

                http_watchdog()
    elif sh_state == 'crtci':
        # print('[sh_state] : {}'.format(sh_state))
        pass


def fc_on_connect(client,userdata,flags, rc):
    global mqtt_client
    global muv_sub_gcs_topic
    global noti_topic
    global muv_sub_msw_topic

    if muv_sub_gcs_topic != '':
        mqtt_client.subscribe(muv_sub_gcs_topic, 0)
        print('[mqtt_connect] muv_sub_gcs_topic is subscribed: ' + muv_sub_gcs_topic)

    if noti_topic != '':
        mqtt_client.subscribe(noti_topic, 0)
        print('[mqtt_connect] noti_topic is subscribed:  ' + noti_topic)



def fc_on_subscribe(client, userdata, mid, granted_qos):
    global mqtt_client
    global muv_mqtt_client
    print("muv_mqtt_client subscribed: " + str(mid) + " " + str(granted_qos))


def fc_on_message(client, userdata, msg):
    global mqtt_client
    global muv_sub_gcs_topic
    global noti_topic

    message = str(msg.payload.decode("utf-8"))
    print(message)

    if msg.topic == muv_sub_gcs_topic:
        tas_mav.gcs_noti_handler(message, my_drone_type)

    else:
        if msg.topic.includes('/oneM2M/req/'):
            jsonObj = json.dumps(message)

            if jsonObj['m2m:rqp'] is None:
                jsonObj['m2m:rqp'] = jsonObj

            noti.mqtt_noti_action(msg.topic.split('/'), jsonObj)


from thyme import mqtt_client
def mqtt_connect(serverip):
    global mqtt_client
    global muv_sub_gcs_topic
    global noti_topic

    if mqtt_client is None:
        if conf['usesecure'] == 'disable':
            mqtt_client = mqtt.Client()
            mqtt_client.on_connect = fc_on_connect
            mqtt_client.reconnect_delay_set(min_delay=2, max_delay=10)
            mqtt_client.on_subscribe = fc_on_subscribe
            mqtt_client.on_message = fc_on_message
            mqtt_client.connect(serverip, int(conf['cse']['mqttport']), keepalive=10)
            mqtt_client.loop_start()
            print('fc_mqtt is connected to {}'.format(serverip))

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


def muv_on_connect(client,userdata,flags, rc):
    global muv_mqtt_client
    global muv_sub_msw_topic

    for idx in range(len(muv_sub_msw_topic)):
        muv_mqtt_client.subscribe(muv_sub_msw_topic[idx], 0)
        print('[muv_mqtt_connect] muv_sub_msw_topic[{0}]: {1}'.format(str(idx), muv_sub_msw_topic[idx]))


def muv_on_subscribe(client, userdata, mid, granted_qos):
    global muv_mqtt_client

    print("muv_sub_msw_topic subscribed: " + str(mid) + " " + str(granted_qos))


def muv_on_message(client, userdata, msg):
    global muv_mqtt_client

    message = str(msg.payload.decode("utf-8"))
    print(message)

    try:
        msg_obj = json.loads(message)
        send_to_Mobius(msg.topic, msg_obj, int(random.random() * 10))
        # print(topic + ' - ' + JSON.stringify(msg_obj))

    except Exception as e:
        msg_obj = message
        send_to_Mobius(msg.topic, msg_obj, int(random.random() * 10))
        # print(topic + ' - ' + msg_obj)


from thyme import muv_mqtt_client
def muv_mqtt_connect(broker_ip, port):
    global muv_mqtt_client
    global muv_sub_msw_topic

    if muv_mqtt_client is None:
        if conf['usesecure'] == 'disable':
            muv_mqtt_client = mqtt.Client()
            muv_mqtt_client.on_connect = muv_on_connect
            muv_mqtt_client.reconnect_delay_set(min_delay=2, max_delay=10)
            muv_mqtt_client.on_subscribe = muv_on_subscribe
            muv_mqtt_client.on_message = muv_on_message
            muv_mqtt_client.connect(broker_ip, port, keepalive=10)
            muv_mqtt_client.loop_start()
            print('muv_mqtt is connected to {}'.format(broker_ip))

        else:
            """TBD mqtt secure"""


def send_to_Mobius(topic, content_each_obj, gap):
    gap, topic, content_each_obj = crtci(topic+'?rcn=0', 0, content_each_obj, None)
