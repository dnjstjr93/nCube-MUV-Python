# nCube-MUV-Python
Start Guide

## Install Dependencies
### Install library 
- on Linux and Raspberry Pi
```
$ pip3 install -r requirements.txt
```

- on Windows and Mac
```
$ pip install -r requirements.txt
```

### Install MQTT-broker
```
$ wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
$ sudo apt-key add mosquitto-repo.gpg.key
$ cd /etc/apt/sources.list.d/
$ sudo wget http://repo.mosquitto.org/debian/mosquitto-buster.list 
$ sudo apt-get update
$ sudo apt-get install -y mosquitto
```

## Run
```
$ python3 thyme.py
```