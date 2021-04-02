#!/usr/bin/sh

CHECK_OS="`cat /etc/issue | head -n 1`"
OS="${CHECK_OS%% *}"

echo  ${OS}

if [[ "$OS" == "Raspbian" ]]; then
	wget http://ports.ubuntu.com/pool/universe/c/chromium-browser/chromium-chromedriver_65.0.3325.181-0ubuntu0.14.04.1_armhf.deb
	sudo dpkg -i chromium-chromedriver_65.0.3325.181-0ubuntu0.14.04.1_armhf.deb
elif [[ "$OS" == "Linux" ]]; then
	sudo apt-get purge -y chromium-browser
	sudo apt-get install -y chromium-browser
	sudo apt-get install -y chromium-chromedriver
