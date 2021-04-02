# nCube-MUV-Python

Start Guide
<br /><br />
***
## Install Dependencies
### Install MQTT-broker
    sh install_mqtt_broker.sh

### Install python library
    pip3 install -r requirements.txt


### Install chromedriver for WebRTC
#### on Linux (Raspberry Pi, NVIDIA Jetson TX2, ETC..)
    sh ready_to_WebRTC.sh

#### on macOS
    sh ready_to_WebRTC.sh
    sudo spctl --master-disable

#### on Windows 

Download drivers compatible with the Chrome version from the [ChromeDriver official website](https://chromedriver.chromium.org/downloads).

Move the downloaded ChromeDriver to the nCube-MUV-python folder.
<br /><br />
***
## Run
    python3 thyme.py
