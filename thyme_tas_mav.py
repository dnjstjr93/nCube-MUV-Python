# -*-coding:utf-8 -*-

"""
 Created by Wonseok Jung in KETI on 2021-03-16.
"""

import datetime, serial, json, binascii, threading

import http_adn
import http_app
import thyme

_server = None

socket_mav = None
mavPort = None

mavPortNum = '/dev/ttyAMA0'
mavBaudrate = '57600'

mavstr = None


def tas_ready():
    global _server
    global mavPortNum
    global mavBaudrate

    if http_app.my_drone_type == 'dji':
        if _server is None:
            pass
            """TBD socket connect with DJI"""
            # _server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # print('socket connected')
    elif http_app.my_drone_type == 'pixhawk':
        mavPortNum = '/dev/tty.usbmodem143201'
        mavBaudrate = '57600'
        mavPortOpening()


aggr_content = {}


def send_aggr_to_Mobius(topic, content_each, gap):
    if aggr_content.get(topic):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%f')[:-3]
        aggr_content[topic][timestamp] = content_each
    else:
        aggr_content[topic] = {}
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%f')[:-3]
        aggr_content[topic][timestamp] = content_each

        http_adn.crtci(topic+'?rcn=0', 0, aggr_content[topic], None)
        del aggr_content[topic]

        return gap, topic
#
#
# function mavlinkGenerateMessage(sysId, type, params) {
#     const mavlinkParser = new MAVLink(null/*logger*/, sysId, 0);
#     try {
#         var mavMsg = null;
#         var genMsg = null;
#         //var targetSysId = sysId;
#         var targetCompId = (params.targetCompId == undefined)?
#             0:
#             params.targetCompId;
#
#         switch( type ) {
#             // MESSAGE ////////////////////////////////////
#             case mavlink.MAVLINK_MSG_ID_PING:
#                 mavMsg = new mavlink.messages.ping(params.time_usec, params.seq, params.target_system, params.target_component);
#                 break;
#             case mavlink.MAVLINK_MSG_ID_HEARTBEAT:
#                 mavMsg = new mavlink.messages.heartbeat(params.type,
#                     params.autopilot,
#                     params.base_mode,
#                     params.custom_mode,
#                     params.system_status,
#                     params.mavlink_version);
#                 break;
#             case mavlink.MAVLINK_MSG_ID_GPS_RAW_INT:
#                 mavMsg = new mavlink.messages.gps_raw_int(params.time_usec,
#                     params.fix_type,
#                     params.lat,
#                     params.lon,
#                     params.alt,
#                     params.eph,
#                     params.epv,
#                     params.vel,
#                     params.cog,
#                     params.satellites_visible,
#                     params.alt_ellipsoid,
#                     params.h_acc,
#                     params.v_acc,
#                     params.vel_acc,
#                     params.hdg_acc);
#                 break;
#             case mavlink.MAVLINK_MSG_ID_ATTITUDE:
#                 mavMsg = new mavlink.messages.attitude(params.time_boot_ms,
#                     params.roll,
#                     params.pitch,
#                     params.yaw,
#                     params.rollspeed,
#                     params.pitchspeed,
#                     params.yawspeed);
#                 break;
#             case mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT:
#                 mavMsg = new mavlink.messages.global_position_int(params.time_boot_ms,
#                     params.lat,
#                     params.lon,
#                     params.alt,
#                     params.relative_alt,
#                     params.vx,
#                     params.vy,
#                     params.vz,
#                     params.hdg);
#                 break;
#             case mavlink.MAVLINK_MSG_ID_SYS_STATUS:
#                 mavMsg = new mavlink.messages.sys_status(params.onboard_control_sensors_present,
#                     params.onboard_control_sensors_enabled,
#                     params.onboard_control_sensors_health,
#                     params.load,
#                     params.voltage_battery,
#                     params.current_battery,
#                     params.battery_remaining,
#                     params.drop_rate_comm,
#                     params.errors_comm,
#                     params.errors_count1,
#                     params.errors_count2,
#                     params.errors_count3,
#                     params.errors_count4);
#                 break;
#         }
#     }
#     catch( e ) {
#         console.log( 'MAVLINK EX:' + e );
#     }
#
#     if (mavMsg) {
#         genMsg = Buffer.from(mavMsg.pack(mavlinkParser));
#         //console.log('>>>>> MAVLINK OUTGOING MSG: ' + genMsg.toString('hex'));
#     }
#
#     return genMsg;
# }
#
# function sendDroneMessage(type, params) {
#     try {
#         var msg = mavlinkGenerateMessage(my_system_id, type, params);
#         if (msg == null) {
#             console.log("mavlink message is null");
#         }
#         else {
#             // console.log('msg: ', msg);
#             // console.log('msg_seq : ', msg.slice(2,3));
#             //mqtt_client.publish(my_cnt_name, msg.toString('hex'));
#             //_this.send_aggr_to_Mobius(my_cnt_name, msg.toString('hex'), 1500);
#             mavPortData(msg);
#         }
#     }
#     catch( ex ) {
#         console.log( '[ERROR] ' + ex );
#     }
# }
#
# var dji = {};
# var params = {};
#
# function dji_handler(data) {
#     socket_mav = this;
#
#     var data_arr = data.toString().split(',');
#
#     dji.flightstatus = data_arr[0].replace('[', '');
#     dji.timestamp = data_arr[1].slice(1, data_arr[1].length);
#     dji.lat = data_arr[2];
#     dji.lon = data_arr[3];
#     dji.alt = data_arr[4];
#     dji.relative_alt = data_arr[5];
#     dji.roll = data_arr[6];
#     dji.pitch = data_arr[7];
#     dji.yaw = data_arr[8];
#     dji.vx = data_arr[9];
#     dji.vy = data_arr[10];
#     dji.vz = data_arr[11];
#     dji.bat_percentage = data_arr[12];
#     dji.bat_voltage = data_arr[13];
#     dji.bat_current = data_arr[14];
#     dji.bat_capacity = data_arr[15].replace(']', '');
#
#     // Debug
#     var debug_string = dji.lat + ', ' + dji.lon + ', ' + dji.alt + ', ' + dji.relative_alt;
#     mqtt_client.publish(my_parent_cnt_name + '/Debug', debug_string);
#
#     // #0 PING
#     params.time_usec = dji.timestamp;
#     params.seq = 0;
#     params.target_system = 0;
#     params.target_component = 0;
#     setTimeout(sendDroneMessage, 1, mavlink.MAVLINK_MSG_ID_PING, params);
#
#     // #1 HEARTBEAT
#     params.type = 2;
#     params.autopilot = 3;
#
#     if(dji.flightstatus == '0') {
#         params.base_mode = 81;
#     }
#     else {
#         params.base_mode = (81 | 0x80);
#     }
#
#     params.system_status = 4;
#     params.mavlink_version = 3;
#     setTimeout(sendDroneMessage, 1, mavlink.MAVLINK_MSG_ID_HEARTBEAT, params);
#
#     // #2 MAVLINK_MSG_ID_GPS_RAW_INT
#     params.time_usec = dji.timestamp;
#     params.fix_type = 3;
#     params.lat = parseFloat(dji.lat) * 1E7;
#     params.lon = parseFloat(dji.lon) * 1E7;
#     params.alt = parseFloat(dji.alt) * 1000;
#     params.eph = 175;
#     params.epv = 270;
#     params.vel = 7;
#     params.cog = 0;
#     params.satellites_visible = 7;
#     params.alt_ellipsoid = 0;
#     params.h_acc = 0;
#     params.v_acc = 0;
#     params.vel_acc = 0;
#     params.hdg_acc = 0;
#     setTimeout(sendDroneMessage, 1, mavlink.MAVLINK_MSG_ID_GPS_RAW_INT, params);
#
#     // #3 MAVLINK_MSG_ID_ATTITUDE
#     params.time_boot_ms = dji.timestamp;
#     params.roll = dji.roll;
#     params.pitch = dji.pitch;
#     params.yaw = dji.yaw;
#     params.rollspeed = -0.00011268721573287621;
#     params.pitchspeed = 0.0000612109579378739;
#     params.yawspeed = -0.00031687552109360695;
#     setTimeout(sendDroneMessage, 1, mavlink.MAVLINK_MSG_ID_ATTITUDE, params);
#
#     // #4 MAVLINK_MSG_ID_GLOBAL_POSITION_INT
#     params.time_boot_ms = dji.timestamp;
#     params.lat = parseFloat(dji.lat) * 1E7;
#     params.lon = parseFloat(dji.lon) * 1E7;
#     params.alt = parseFloat(dji.alt) * 1000;
#     params.relative_alt = parseFloat(dji.relative_alt) * 1000;
#     params.vx = parseFloat(dji.vx) * 100;
#     params.vy = parseFloat(dji.vy) * 100;
#     params.vz = parseFloat(dji.vz) * 100;
#     params.hdg = 0;
#     setTimeout(sendDroneMessage, 1, mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, params);
#
#     // #5 MAVLINK_SYS_STATUS(#1)
#     params.onboard_control_sensors_present = mavlink.MAV_SYS_STATUS_SENSOR_3D_GYRO & mavlink.MAV_SYS_STATUS_SENSOR_GPS;
#     params.onboard_control_sensors_enabled = mavlink.MAV_SYS_STATUS_SENSOR_3D_GYRO & mavlink.MAV_SYS_STATUS_SENSOR_GPS;
#     params.onboard_control_sensors_health = mavlink.MAV_SYS_STATUS_SENSOR_3D_GYRO & mavlink.MAV_SYS_STATUS_SENSOR_GPS;
#     params.load = 500;
#     params.voltage_battery = dji.bat_voltage;
#     params.current_battery = dji.bat_current;
#     params.battery_remaining = dji.bat_percentagea;
#     params.drop_rate_comm = 8;
#     params.errors_comm = 0;
#     params.errors_count1 = 0;
#     params.errors_count2 = 0;
#     params.errors_count3 = 0;
#     params.errors_count4 = 0;
#     setTimeout(sendDroneMessage, 1, mavlink.MAVLINK_MSG_ID_SYS_STATUS, params);
# }


def noti(path_arr, cinObj, socket):
    cin = {}
    cin['ctname'] = path_arr[len(path_arr)-2]
    if cinObj['con'] is not None: cin['con'] = cinObj['con']
    else: cin['con'] = cinObj['content']

    if cin['con'] == '':
        print('---- is not cin message')
    else:
        socket.write(json.dumps(cin))


def gcs_noti_handler(message):
    global socket_mav
    global mavPort

    if http_app.my_drone_type == 'dji':
        com_msg = str(message)
        com_message = com_msg.split(":")
        msg_command = com_message[0]

        if msg_command == 't' or msg_command == 'h' or msg_command == 'l':
            socket_mav.wrtie(message)
        elif msg_command == 'g':
            if len(com_message) < 5:
                for i in range(5-len(com_message)):
                    com_msg += ':0'
                message = bytes(com_msg, 'utf-8')
            socket_mav.write(message)

            msg_lat = com_message[1][0:7]
            msg_lon = com_message[2][0:7]
            msg_alt = com_message[3][0:3]
        elif msg_command == 'm' or msg_command == 'a':
            socket_mav.write(message)
    elif http_app.my_drone_type == 'pixhawk':
        if mavPort is not None:
            if mavPort.isOpen():
                mavPort.write(message)
    else:
        pass


def mavPortOpening():
    global mavPort
    global mavPortNum
    global mavBaudrate

    # try:
    if mavPort is None:
        mavPort = serial.Serial(mavPortNum, int(mavBaudrate), timeout=10)
        mavPortOpen()
    else:
        if mavPort.isOpen():
            pass
        else:
            mavPort.open()

    # except Exception as e:
    #     mavPortError(e)


def mavPortOpen():
    global mavPort

    print('mavPort open. ' + mavPortNum + ' Data rate: ' + mavBaudrate)
    # print(mavPort.readlines())
    while True:
        mavPortData()
    # try:
    #     mav_thread = threading.Thread(target=mavPortData)
    #     # mav_thread.daemon = True
    #     mav_thread.start()
    # except Exception as e:
    #     print(e)


def mavPortClose():
    global mavPort

    print('mavPort closed..')
    mavPort.close()
    mavPortOpening()


def mavPortError(error):
    global mavPort

    print('[mavPort error]: {}'.format(error))
    mavPortOpening()


mav_ver = 1

byteToHex = []

for n in range(0xff+0x01):
    hexOctet = str(hex(n))[2:].zfill(2)
    byteToHex.append(hexOctet)


def Hex(arrayBuffer):
    global hexOctet

    buff = bytearray(arrayBuffer)
    hexOctet = []

    for i in range(len(buff)):
        hexOctet.append(byteToHex[buff[i]])

    return "".join(hexOctet)


mavStrFromDrone = ''
mavStrFromDroneLength = 0


def mavPortData():
    global mavPort
    global mavStrFromDroneLength
    global mavStrFromDrone

    if mavStrFromDroneLength > 0:
        mavStrFromDrone = mavStrFromDrone[mavStrFromDroneLength:]
        mavStrFromDroneLength = 0

    data = mavPort.readline()

    mavStrFromDrone += Hex(data)
    while len(mavStrFromDrone) > 12:
        stx = mavStrFromDrone[0:2]
        if stx == 'fe':
            if stx == 'fe':
                length = int(mavStrFromDrone[2:4], 16)
                mavLength = (6 * 2) + (length * 2) + (2 * 2)
            else:
                length = int(mavStrFromDrone[2:4], 16)
                mavLength = (10 * 2) + (length * 2) + (2 * 2)

            if (len(mavStrFromDrone) - mavStrFromDroneLength) >= mavLength:
                mavStrFromDroneLength += mavLength
                mavPacket = mavStrFromDrone[0:mavLength]
                # print(bytearray(bytes(mavPacket, encoding='utf-8')))
                hex = ":".join(mavPacket[i:i + 2] for i in range(0, len(mavPacket), 2))
                mavarr = []
                arr = hex.split(":")
                for i in arr:
                    mavarr.append(int("0x" + i, 0))
                thyme.mqtt_client.publish(http_app.my_cnt_name, bytearray(mavarr))
                send_aggr_to_Mobius(http_app.my_cnt_name, mavPacket, 1500)
                parseMavFromDrone(mavPacket)
            else:
                break
        else:
            mavStrFromDrone = mavStrFromDrone[2:]


fc = {}
try:
    with open('./fc_data_model.json', 'r') as f:
        fc = json.load(f)
except:
    fc['heartbeat'] = {}
    fc['heartbeat']['type'] = 2
    fc['heartbeat']['autopilot'] = 3
    fc['heartbeat']['base_mode'] = 0
    fc['heartbeat']['custom_mode'] = 0
    fc['heartbeat']['system_status'] = 0
    fc['heartbeat']['mavlink_version'] = 1

    fc['attitude'] = {}
    fc['attitude']['time_boot_ms'] = 123456789
    fc['attitude']['roll'] = 0.0
    fc['attitude']['pitch'] = 0.0
    fc['attitude']['yaw'] = 0.0
    fc['attitude']['rollspeed'] = 0.0
    fc['attitude']['pitchspeed'] = 0.0
    fc['attitude']['yawspeed'] = 0.0

    fc['global_position_int'] = {}
    fc['global_position_int']['time_boot_ms'] = 123456789
    fc['global_position_int']['lat'] = 0
    fc['global_position_int']['lon'] = 0
    fc['global_position_int']['alt'] = 0
    fc['global_position_int']['vx'] = 0
    fc['global_position_int']['vy'] = 0
    fc['global_position_int']['vz'] = 0
    fc['global_position_int']['hdg'] = 65535

    fc['battery_status'] = {}
    fc['battery_status']['id'] = 0
    fc['battery_status']['battery_function'] = 0
    fc['battery_status']['type'] = 3
    fc['battery_status']['temperature'] = 32767
    fc['battery_status']['voltages'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    fc['battery_status']['current_battery'] = -1
    fc['battery_status']['current_consumed'] = -1
    fc['battery_status']['battery_remaining'] = -1
    fc['battery_status']['time_remaining'] = 0
    fc['battery_status']['charge_state'] = 0

    with open('./fc_data_model.json', 'w') as f:
        json.dump(fc, f, indent=4)


flag_base_mode = 0
start_arm_time = 0
cal_flag = 0
cal_sortiename = ''

from pymavlinklib import common


def parseMavFromDrone(mavPacket):
    global flag_base_mode
    global start_arm_time
    global cal_sortiename
    global cal_flag

    try:
        ver = mavPacket[0:2]
        if ver == 'fd':
            sysid = mavPacket[10:12].lower()
            msgid = mavPacket[14:20].lower()
        else:
            sysid = mavPacket[6:8].lower()
            msgid = mavPacket[10:12].lower()

        sys_id = int(sysid, 16)
        msg_id = int(msgid, 16)

        cur_seq = int(mavPacket[4:6], 16)

        if msg_id == common.mavlink['GLOBAL_POSITION_INT']: # 33
            if ver == 'fd':
                base_offset = 20
                time_boot_ms = mavPacket[base_offset:base_offset+8].lower()
                base_offset += 8
                lat = mavPacket[base_offset:base_offset + 8].lower()
                base_offset += 8
                lon = mavPacket[base_offset:base_offset + 8].lower()
                base_offset += 8
                alt = mavPacket[base_offset:base_offset + 8].lower()
                base_offset += 8
                relative_alt = mavPacket[base_offset:base_offset + 8].lower()
            else:
                base_offset = 12
                time_boot_ms = mavPacket[base_offset:base_offset + 8].lower()
                base_offset += 8
                lat = mavPacket[base_offset:base_offset + 8].lower()
                base_offset += 8
                lon = mavPacket[base_offset:base_offset + 8].lower()
                base_offset += 8
                alt = mavPacket[base_offset:base_offset + 8].lower()
                base_offset += 8
                relative_alt = mavPacket[base_offset:base_offset + 8].lower()

            print(time_boot_ms)
            # fc['global_position_int']['time_boot_ms'] =
            # fc['global_position_int']['lat'] =
            # fc['global_position_int']['lon'] =
            # fc['global_position_int']['alt'] =
            # fc['global_position_int']['relative_alt'] =
            #
            # thyme.muv_mqtt_client.publish(http_app.muv_pub_fc_gpi_topic, json.loads)

        elif msg_id == common.mavlink['HEARTBEAT']: # 00
            if ver == 'fd':
                base_offset = 20
                custom_mode = mavPacket[base_offset:base_offset+8].lower()
                base_offset += 8
                type = mavPacket[base_offset:base_offset+2].lower()
                base_offset += 2
                autopilot = mavPacket[base_offset:base_offset + 2].lower()
                base_offset += 2
                base_mode = mavPacket[base_offset:base_offset + 2].lower()
                base_offset += 2
                system_status = mavPacket[base_offset:base_offset + 2].lower()
                base_offset += 2
                mavlink_version = mavPacket[base_offset:base_offset + 2].lower()
            else:
                base_offset = 12
                custom_mode = mavPacket[base_offset:base_offset + 8].lower()
                base_offset += 8
                type = mavPacket[base_offset:base_offset + 2].lower()
                base_offset += 2
                autopilot = mavPacket[base_offset:base_offset + 2].lower()
                base_offset += 2
                base_mode = mavPacket[base_offset:base_offset + 2].lower()
                base_offset += 2
                system_status = mavPacket[base_offset:base_offset + 2].lower()
                base_offset += 2
                mavlink_version = mavPacket[base_offset:base_offset + 2].lower()

            # fc['heartbeat']['type'] =
            # fc['heartbeat']['autopilot'] =
            # fc['heartbeat']['base_mode'] =
            # fc['heartbeat']['custom_mode'] =
            # fc['heartbeat']['system_status'] =
            # fc['heartbeat']['mavlink_version'] =

            # thyme.muv_mqtt_client.publish(http_app.muv_pub_fc_hb_topic, json.loads(fc['heartbeat']))

            if fc['heartbeat']['base_mode'] & 0x80:
                if flag_base_mode == 3:
                    start_arm_time = datetime.datetime.now()
                    flag_base_mode += 1
                    http_app.my_sortie_name = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S%f')[:-3]
                    http_app.my_cnt_name = http_app.my_parent_cnt_name + '/' + http_app.my_sortie_name
                    rsc, res_body, count = http_adn.crtct(http_app.my_parent_cnt_name + '?rcn=0', http_app.my_sortie_name, 0)
                    cal_flag = 1
                    cal_sortiename = http_app.my_sortie_name

                    for idx in http_app.mission_parent:
                        createMissionContainer(idx)
                else:
                    flag_base_mode += 1
                    if flag_base_mode > 16:
                        flag_base_mode = 16
            else:
                flag_base_mode = 0
                if cal_flag == 1:
                    cal_flag = 0
                    calculateFlightTime(cal_sortiename)
                http_app.my_sortie_name = 'disarm'
                http_app.my_cnt_name = http_app.my_parent_cnt_name + '/' + http_app.my_sortie_name

    except Exception as e:
        print(e)


end_arm_time = 0
arming_time = 0
flight_time = {}


def calculateFlightTime(cal_sortiename):
    global start_arm_time
    global end_arm_time
    global arming_time
    global flight_time

    end_arm_time = datetime.datetime.now()
    start_arm_time = datetime.datetime.now()
    arming_time = (end_arm_time - start_arm_time).seconds
    print('/Mobius/Life_Prediction/History/' + thyme.conf['ae']['name'] + '/la')
    rsc, res_body, count = http_adn.rtvct('/Mobius/Life_Prediction/History/' + thyme.conf['ae']['name'] + '/la', 0)
    if rsc == 2000:
        flight_time = res_body['m2m:cin']['con']
        if flight_time['total_flight_time'] == 0:
            flight_time['total_flight_time'] = arming_time
        else:
            flight_time['total_flight_time'] += arming_time

        flight_time['arming_time'] = arming_time
        flight_time['sortie_time'] = cal_sortiename

        http_adn.crtci('/Mobius/Life_Prediction/History/' + thyme.conf['ae']['name'] + '?rcn=0', 0, flight_time, None)

    else:
        rsc, res_body, count = http_adn.crtct('/Mobius/Life_Prediction/History' + '?rcn=0', thyme.conf['ae']['name'], 0)

        flight_time.total_flight_time = arming_time
        flight_time.arming_time = arming_time
        flight_time.sortie_name = cal_sortiename
        http_adn.crtci('/Mobius/Life_Prediction/History/' + thyme.conf['ae']['name'] + '?rcn=0', 0, flight_time, None)

    cal_sortiename = ''


def createMissionContainer(idx):
    mission_parent_path = idx
    rsc, res_body, count = http_adn.crtct(mission_parent_path + '?rcn=0', http_app.my_sortie_name, 0)