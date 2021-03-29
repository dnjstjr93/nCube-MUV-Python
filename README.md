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

	sudo apt-get install -y python3-pyside2.qt3dcore python3-pyside2.qt3dinput \
		python3-pyside2.qt3dlogic python3-pyside2.qt3drender python3-pyside2.qtcharts \
		python3-pyside2.qtconcurrent python3-pyside2.qtcore python3-pyside2.qtgui \
		python3-pyside2.qthelp python3-pyside2.qtlocation python3-pyside2.qtmultimedia \
		python3-pyside2.qtmultimediawidgets python3-pyside2.qtnetwork python3-pyside2.qtopengl \
		python3-pyside2.qtpositioning python3-pyside2.qtprintsupport python3-pyside2.qtqml \
		python3-pyside2.qtquick python3-pyside2.qtquickwidgets python3-pyside2.qtscript \
		python3-pyside2.qtscripttools python3-pyside2.qtsensors python3-pyside2.qtsql \
		python3-pyside2.qtsvg python3-pyside2.qttest python3-pyside2.qttexttospeech \
		python3-pyside2.qtuitools python3-pyside2.qtwebchannel python3-pyside2.qtwebsockets \
		python3-pyside2.qtwidgets python3-pyside2.qtx11extras python3-pyside2.qtxml \
		python3-pyside2.qtxmlpatterns python3-pyside2uic



## Run


    python3 thyme.py
