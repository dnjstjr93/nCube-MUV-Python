#-*-coding:utf-8 -*-

"""
 Created by Wonseok Jung in KETI on 2021-03-16.
"""

import conf
import http_app

conf = conf.conf
sh_state = 'rtvct'
mqtt_client = None
muv_mqtt_client = None

if __name__ == '__main__':
    # while True:
    http_app.http_watchdog()