from PyQt5 import QtCore, QtGui, QtWidgets
import socket
from pyexpat.errors import messages
import _pickle as cPickle
import os
import threading
import sys, time
import psutil

# flags:
# 2 - start rental
# 3 - end rental
# 4 - succes in request
# 5 - error in request


global conn
HOST = 'localhost'
PORT = 8000
stop_thread = False

flag_connect = 6
car_rented = False

lights_off = True

class Ui_MainWindow(object):
    def __init__(self):
        self.conn = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600, 800)
        MainWindow.setWindowTitle('Car')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.centralwidget.setStyleSheet("background-color:white;")

        # start of UI elements:

        # car name label
        self.car_name = QtWidgets.QLabel(self.centralwidget)
        self.car_name.setGeometry(QtCore.QRect(50, 10, 500, 50))
        self.car_name.setStyleSheet("font-size: 20px;font:bold;qproperty-alignment: AlignLeft;")
        self.car_name.setText("Car: placeholderVIN, placeholderLocation")

        # car rented label
        self.car_rented_label = QtWidgets.QLabel(self.centralwidget)
        self.car_rented_label.setGeometry(QtCore.QRect(10, 100, 300, 50))
        self.car_rented_label.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignLeft;")
        self.car_rented_label.setText("Rented state: Not rented")

        # start rental label
        self.rental_label = QtWidgets.QLabel(self.centralwidget)
        self.rental_label.setGeometry(QtCore.QRect(10, 150, 200, 50))
        self.rental_label.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignLeft;")
        self.rental_label.setText("Start rental:")
        # start rental led
        self.rental_led = QtWidgets.QLabel(self.centralwidget)
        self.rental_led.setGeometry(QtCore.QRect(125, 150, 25, 25))
        self.rental_led.setStyleSheet("background-color:red;font-size:18px;font:bold;qproperty-alignment: AlignLeft;")

        # unlocked car label
        self.car_state = QtWidgets.QLabel(self.centralwidget)
        self.car_state.setGeometry(QtCore.QRect(10, 200, 250, 50))
        self.car_state.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignLeft;")
        self.car_state.setText("Car state: Locked")

        # Connected label
        self.connected_label = QtWidgets.QLabel(self.centralwidget)
        self.connected_label.setGeometry(QtCore.QRect(10, 700, 200, 40))
        self.connected_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")


        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.show()
        # end of UI elements;

        self.start_server()

        #end of ui_mainwindow

    # start of code
    def start_server(self):
        global conn
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((HOST, PORT))

        if conn is not None:
            conn.send(b'sal')
            self.connected_label.setText("Company connected")
            self.recv_messages()

    def recv_messages(self):
        self.stop_event = threading.Event()
        self.c_thread = threading.Thread(target=self.recv_handler, args=(self.stop_event,))
        self.c_thread.start()

    def recv_handler(self, stop_event):
        global stop_thread
        global conn
        global car_rented, lights_off
        while not stop_event.is_set() and stop_thread == False:
            message = int(conn.recv(1024))
            # message = cPickle.loads(message)
            # check if car is already rented
            if car_rented == True and message == 2:
                conn.sendall(b"5")
                message = 0
            elif car_rented == False and message == 3:
                conn.sendall(b"6")
                message = 0

            # start rental message
            if message == 2:
                car_rented = True
                self.rental_led.setStyleSheet("background-color: green")
                self.car_rented_label.setText("Rented state: Rented")
                self.car_state.setText("Car state: Unlocked")
                conn.sendall(b"4")
            # end rental message
            if message == 3:
                if not lights_off:
                    conn.sendall(b"5")
                else:
                    car_rented = False
                    self.rental_led.setStyleSheet("background-color: red")
                    self.car_rented_label.setText("Rented state: Not rented")
                    self.car_state.setText("Car state: Locked")
                    conn.sendall(b"4")


def kill_proc_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    if including_parent:
        parent.kill()


class MyWindow(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        global stop_thread
        # uncomment for confirming if the user did not misclick on close
        # result = QtWidgets.QMessageBox.question(self,
        #                                         "Confirm Exit",
        #                                         "Are you sure you want to exit ?",
        #                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        #
        # if result == QtWidgets.QMessageBox.Yes:
        #     event.accept()
        #     stop_thread = True
        # elif result == QtWidgets.QMessageBox.No:
        #     event.ignore()
        stop_thread = True
        event.accept()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.center()
    sys.exit(app.exec_())