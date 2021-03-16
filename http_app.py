# -*-coding:utf-8 -*-

"""
 Created by Wonseok Jung in KETI on 2021-03-16.
"""

import http
import socket
import json
import uuid
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import time
import subprocess
import os, sys, shutil, platform
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
            #process.exit()

return_count = 0
request_count = 0


def ready_for_notification():
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

        # mqtt_connect(conf['cse']['host'], muv_sub_gcs_topic, noti_topic)
        #
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


from thyme import mqtt_client
def mqtt_connect(serverip, sub_gcs_topic, noti_topic):
    if mqtt_client is None:
        if conf['usesecure'] == 'disable':
            connectOptions = {}
            connectOptions['host'] = serverip,
            connectOptions['port'] = conf.cse.mqttport,
            connectOptions['protocol'] = "mqtt",
            connectOptions['keepalive'] = 10,
            connectOptions['protocolId'] = "MQTT",
            connectOptions['protocolVersion'] = 4,
            connectOptions['clean'] = True,
            connectOptions['reconnectPeriod'] = 2000,
            connectOptions['connectTimeout'] = 2000,
            connectOptions['rejectUnauthorized'] = False
        else:
            connectOptions = {}
            connectOptions['host'] = serverip,
            connectOptions['port'] = conf.cse.mqttport,
            connectOptions['protocol'] = "mqtts",
            connectOptions['keepalive'] = 10,
            connectOptions['protocolId'] = "MQTT",
            connectOptions['protocolVersion'] = 4,
            connectOptions['clean'] = True,
            connectOptions['reconnectPeriod'] = 2000,
            connectOptions['connectTimeout'] = 2000,
            connectOptions['key'] = fs.readFileSync("./server-key.pem"),
            connectOptions['cert'] = fs.readFileSync("./server-crt.pem"),
            connectOptions['rejectUnauthorized'] = False