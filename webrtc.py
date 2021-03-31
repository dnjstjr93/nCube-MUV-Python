# -*-coding:utf-8 -*-

"""
 Created by Wonseok Jung in KETI on 2021-03-16.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import http_app


def openWeb():
    opt = Options()
    opt.add_argument("--disable-infobars")
    opt.add_argument("start-maximized")
    opt.add_argument("--disable-extensions")
    # Pass the argument 1 to allow and 2 to block
    opt.add_experimental_option("prefs", { \
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.geolocation": 1,
        "profile.default_content_setting_values.notifications": 1
    })

    driver = webdriver.Chrome(chrome_options=opt, executable_path='/usr/lib/chromium-browser/chromedriver')
    # driver.get("http://www.google.com")
    driver.get("https://203.253.128.177/videoroomtest.html")
    control_web(driver)


def control_web(driver):
    global display_name

    button_id = driver.find_element_by_id('start')
    button_id.click()

    driver.implicitly_wait(5)

    username_id = driver.find_element_by_id('username')
    username_id.send_keys(display_name)
    username_id.send_keys(Keys.RETURN)

    register_id = driver.find_element_by_id('register')
    register_id.click()


def webrtc():
    global display_name

    display_name = http_app.drone_info["drone"]
    display_name
    if display_name.isalnum():
        pass
    else:
        display_name = ''.join(char for char in display_name if char.isalnum())
    openWeb()


"""
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
# from PyQt5.QtCore import QUrl
# from PyQt5 import QtNetwork, QtWebEngineWidgets

import json
import threading
import time

import pyautogui

from PySide2.QtWidgets import QApplication
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PySide2.QtCore import QUrl
from PySide2 import QtNetwork, QtWebEngineWidgets

import http_app


def set_ssl_protocol():
    default_config = QtNetwork.QSslConfiguration.defaultConfiguration()
    default_config.setProtocol(QtNetwork.QSsl.TlsV1_2)
    QtNetwork.QSslConfiguration.setDefaultConfiguration(default_config)


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)
        self.featurePermissionRequested.connect(self.onFeaturePermissionRequested)

    def onFeaturePermissionRequested(self, url, feature):
        if feature in (QWebEnginePage.MediaAudioCapture,
                       QWebEnginePage.MediaVideoCapture,
                       QWebEnginePage.MediaAudioVideoCapture):
            self.setFeaturePermission(url, feature, QWebEnginePage.PermissionGrantedByUser)
        else:
            self.setFeaturePermission(url, feature, QWebEnginePage.PermissionDeniedByUser)

    def certificateError(self, certificateError):
        # print(certificateError.errorDescription(), certificateError.url(), certificateError.isOverridable())
        error = certificateError.error()
        if error == QtWebEngineWidgets.QWebEngineCertificateError.SslPinnedKeyNotInCertificateChain: # -150
            print("{} - SslPinnedKeyNotInCertificateChain".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateCommonNameInvalid: # -200
            print("{} - CertificateCommonNameInvalid".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateDateInvalid: # -201
            print("{} - CertificateDateInvalid".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateAuthorityInvalid: # -202
            # print("{} - CertificateAuthorityInvalid".format(error))
            certificateError.ignoreCertificateError()
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateContainsErrors: # -203
            print("{} - CertificateContainsErrors".format(error))
        if error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateNoRevocationMechanism: # -204
            print("{} - CertificateNoRevocationMechanism".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateUnableToCheckRevocation: # -205
            print("{} - CertificateUnableToCheckRevocation".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateRevoked: # -206
            print("{} - CertificateRevoked".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateInvalid: # -207
            print("{} - CertificateAuthorityInvalid".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateWeakSignatureAlgorithm: # -208
            print("{} - CertificateWeakSignatureAlgorithm".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateNonUniqueName: # -210
            print("{} - CertificateNonUniqueName".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateWeakKey: # -211
            print("{} - CertificateWeakKey".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateNameConstraintViolation: # -212
            print("{} - CertificateNameConstraintViolation".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateValidityTooLong: # -213
            print("{} - CertificateValidityTooLong".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateTransparencyRequired: # -214
            print("{} - CertificateTransparencyRequired".format(error))
        elif error == QtWebEngineWidgets.QWebEngineCertificateError.CertificateKnownInterceptionBlocked: # -217
            print("{} - CertificateKnownInterceptionBlocked".format(error))

        return super(WebEnginePage, self).certificateError(certificateError)


def auto_control():
    try:
        display_name = http_app.drone_info["drone"]
        if display_name.isalnum():
            pass
        else:
            display_name = ''.join(char for char in display_name if char.isalnum())
        print(display_name)

        pyautogui.moveTo(938, 430)
        time.sleep(3)
        pyautogui.click()
        pyautogui.typewrite(display_name, interval=0.1)
        pyautogui.keyDown('enter')
        pyautogui.keyUp('enter')
    except Exception as e:
        print(e)


def webrtc():
    # 좌표 객체 얻기
    position = pyautogui.position()

    # 화면 전체 크기 확인하기
    print('Monitor Size: ', pyautogui.size())
    # 현재 마우스 커서 위치 확인
    print('cur_cursor_position: ', pyautogui.position())

    app = QApplication([])

    view = QWebEngineView()
    page = WebEnginePage()
    view.setPage(page)
    view.load(QUrl("https://203.253.128.177/videoroomtest.html"))
    view.setGeometry(300, 300, 1500, 1200)
    view.setWindowTitle('Drone Broadcast')
    t = threading.Thread(target=auto_control)
    t.start()
    view.show()
    app.exec_()
"""
