# -*-coding:utf-8 -*-

"""
 Created by Wonseok Jung in KETI on 2021-03-16.
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

