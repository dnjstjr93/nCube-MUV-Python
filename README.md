# nCube-MUV-Python

Start Guide

## Install Dependencies
### Install MQTT-broker
    wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key
    sudo apt-key add mosquitto-repo.gpg.key
    cd /etc/apt/sources.list.d/
    sudo wget http://repo.mosquitto.org/debian/mosquitto-buster.list 
    sudo apt-get update
    sudo apt-get install -y mosquitto


### Install python library
    pip3 install -r requirements.txt


### Install chromedriver for WebRTC
    dpkg -l | grep chromium    # check the chrominum package
    wget http://ports.ubuntu.com/pool/universe/c/chromium-browser/chromium-chromedriver_65.0.3325.181-0ubuntu0.14.04.1_armhf.deb
    sudo dpkg -i chromium-chromedriver_65.0.3325.181-0ubuntu0.14.04.1_armhf.deb


## Run
    python3 thyme.py
