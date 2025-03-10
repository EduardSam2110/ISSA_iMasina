import re
import time

from PyQt5.QtWidgets import QListWidget, QLineEdit, QWidget, QVBoxLayout
from PyQt5 import QtCore, QtGui, QtWidgets
import socket
import threading
import psutil


HOST = 'localhost'
PORT = 5000
stop_thread = False

locations= ["Alexandru", "Copou", "CUG", "Nicolina", "Pacurari", "Podu-Ros", "Tatarasi"]
rented = False


class Ui_MainWindow(object):
    def __init__(self):
        self.conn = None



    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600, 800)
        MainWindow.setWindowTitle('Phone App')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.centralwidget.setStyleSheet("background-color:white;")

        # start of UI elements:

        ##########################################    Application Title   ##############################################
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(225, 25, 200, 50))
        self.title.setStyleSheet("font-size:25px;font:bold;qproperty-alignment: AlignLeft;")
        self.title.setText("Rent-A-Car")

        ##########################################    Connection Part   ################################################
        # Start server button
        self.connect_to_company_btn = QtWidgets.QPushButton(MainWindow)
        self.connect_to_company_btn.setText("Connect to company")
        self.connect_to_company_btn.setStyleSheet("font: bold; font-size: 15px;")
        self.connect_to_company_btn.setGeometry(QtCore.QRect(200, 550, 200, 41))
        self.connect_to_company_btn.clicked.connect(self.connect_to_company)

        #Connected label
        self.connected_label = QtWidgets.QLabel(self.centralwidget)
        self.connected_label.setGeometry(QtCore.QRect(10, 700, 200, 40))
        self.connected_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        #User label
        self.user_label = QtWidgets.QLabel(self.centralwidget)
        self.user_label.setGeometry(QtCore.QRect(450, 700, 100, 40))
        self.user_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")
        self.user_label.setText("")
        ################################################    Login Form   ###############################################
        #form label
        self.form_label = QtWidgets.QLabel(self.centralwidget)
        self.form_label.setGeometry(QtCore.QRect(225, 100, 200, 50))
        self.form_label.setStyleSheet("font-size:20px;font:bold;qproperty-alignment: AlignLeft;")
        self.form_label.setText("Login Form")
        self.form_label.setVisible(False)

        # username label
        self.username_label = QtWidgets.QLabel(self.centralwidget)
        self.username_label.setGeometry(QtCore.QRect(100, 150, 400, 60))
        self.username_label.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignLeft;")
        self.username_label.setText("Username:")
        self.username_label.setVisible(False)

        #username text box
        self.username_input = QtWidgets.QLineEdit(self.centralwidget)
        self.username_input.setGeometry(QtCore.QRect(210, 140, 200, 40))
        self.username_input.setStyleSheet("font-size:16px;")
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setVisible(False)

        # CNP label
        self.cnp_label = QtWidgets.QLabel(self.centralwidget)
        self.cnp_label.setGeometry(QtCore.QRect(100, 200, 400, 60))
        self.cnp_label.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignLeft;")
        self.cnp_label.setText("CNP:")
        self.cnp_label.setVisible(False)

        # CNP text box
        self.cnp_input = QtWidgets.QLineEdit(self.centralwidget)
        self.cnp_input.setGeometry(QtCore.QRect(210, 190, 200, 40))
        self.cnp_input.setValidator(QtGui.QIntValidator())
        self.cnp_input.setStyleSheet("font-size:16px;")
        self.cnp_input.setPlaceholderText("Enter CNP")
        self.cnp_input.setVisible(False)

        # Card label
        self.card_label = QtWidgets.QLabel(self.centralwidget)
        self.card_label.setGeometry(QtCore.QRect(100, 250, 400, 60))
        self.card_label.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignLeft;")
        self.card_label.setText("Card:")
        self.card_label.setVisible(False)

        # Card text box
        self.card_input = QtWidgets.QLineEdit(self.centralwidget)
        self.card_input.setGeometry(QtCore.QRect(210, 240, 200, 40))
        self.card_input.setValidator(QtGui.QIntValidator())
        self.card_input.setStyleSheet("font-size:16px;")
        self.card_input.setPlaceholderText("Enter Card Number")
        self.card_input.setVisible(False)

        #submit
        self.submit_btn = QtWidgets.QPushButton(MainWindow)
        self.submit_btn.setText("Submit")
        self.submit_btn.setStyleSheet("font: bold; font-size: 15px;")
        self.submit_btn.setGeometry(QtCore.QRect(200, 300, 200, 41))
        self.submit_btn.clicked.connect(self.submit_login)
        self.submit_btn.setVisible(False)

        #submit error message
        self.resubmit_label = QtWidgets.QLabel(self.centralwidget)
        self.resubmit_label.setGeometry(QtCore.QRect(200, 300, 400, 60))
        self.resubmit_label.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignLeft;color: red")
        self.resubmit_label.setText("Please submit again")
        self.resubmit_label.setVisible(False)

        ################################################    Location List   ############################################
        self.location_list = QListWidget(self.centralwidget)
        self.location_list.setStyleSheet("font-size: 20px;font:bold;qproperty-alignment: AlignLeft;border: none")
        self.location_list.setGeometry(25, 75, 200, 300)
        self.location_list.setFixedSize(500, 400)

        for location in locations:
            self.location_list.addItem(location)

        self.location_list.itemClicked.connect(self.on_location_selected)
        self.location_list.setVisible(False)

        self.location_btn = QtWidgets.QPushButton(MainWindow)
        self.location_btn.setText("Query cars at ")
        self.location_btn.setStyleSheet("font: bold; font-size: 15px;")
        self.location_btn.setGeometry(QtCore.QRect(200, 550, 200, 40))
        self.location_btn.clicked.connect(self.query_request)
        self.location_btn.setVisible(False)
        self.location_btn.setEnabled(False)

        ################################################    Car List   #################################################
        self.car_list = QListWidget(self.centralwidget)
        self.car_list.setStyleSheet("font-size: 20px;font:bold;qproperty-alignment: AlignLeft;border: none")
        self.car_list.setGeometry(25, 75, 200, 300)
        self.car_list.setFixedSize(500, 400)

        self.car_list.itemClicked.connect(self.on_car_selected)
        self.car_list.setVisible(False)

        ##########################################    Rental Part   ####################################################
        #rent option label
        self.car_choosen = QtWidgets.QLabel(self.centralwidget)
        self.car_choosen.setGeometry(QtCore.QRect(100, 450, 400, 100))
        self.car_choosen.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignCenter")
        self.car_choosen.setText("Car selected:\nBrand:\nVIN:")
        self.car_choosen.setVisible(False)

        #company notification label
        self.notification= QtWidgets.QLabel(self.centralwidget)
        self.notification.setGeometry(QtCore.QRect(100, 200, 400, 100))
        self.notification.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignCenter;color:green")
        self.notification.setVisible(False)

        #start rental button
        self.start_rental_btn = QtWidgets.QPushButton(MainWindow)
        self.start_rental_btn.setText("Start rental")
        self.start_rental_btn.setStyleSheet("font: bold; font-size: 15px;color:green")
        self.start_rental_btn.setGeometry(QtCore.QRect(200, 550, 200, 41))
        self.start_rental_btn.clicked.connect(self.start_rental)
        self.start_rental_btn.setVisible(False)
        self.start_rental_btn.setEnabled(False)

        #end rental button
        self.end_rental_btn = QtWidgets.QPushButton(MainWindow)
        self.end_rental_btn.setText("End rental")
        self.end_rental_btn.setStyleSheet("font: bold; font-size: 15px;color:red")
        self.end_rental_btn.setGeometry(QtCore.QRect(200, 600, 200, 41))
        self.end_rental_btn.clicked.connect(self.end_rental)
        self.end_rental_btn.setVisible(False)
        self.end_rental_btn.setEnabled(False)
        ################################################################################################################
        # end of UI elements;

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.show()



    # start of code
    def recv_messages(self):
        self.stop_event = threading.Event()
        self.c_thread = threading.Thread(target=self.recv_handler, args=(self.stop_event,))
        self.c_thread.start()

    def recv_handler(self, stop_event):
        global stop_thread
        global rented
        while not stop_event.is_set() and stop_thread == False:
            if self.conn is not None:
                msg = self.conn.recv(1)

                if msg == b'1':
                    self.location_btn.setVisible(False)
                    self.location_list.setVisible(False)
                    self.car_list.setVisible(True)
                    self.car_choosen.setVisible(True)
                    self.start_rental_btn.setVisible(True)
                    self.end_rental_btn.setVisible(True)
                    car_data = self.conn.recv(1024)
                    car_data = car_data.decode("ascii")
                    car_data = car_data.split('|')
                    car_data = car_data[:len(car_data)-1]
                    for car in car_data:
                        if car != " ":
                            self.car_list.addItem(car)

                elif msg == b'4':
                    rented = ~rented
                    if rented:
                        self.notification.setText("The rental request has been approved!\nPlease enjoy your ride!")
                        self.car_choosen.setGeometry(QtCore.QRect(100, 75, 400, 100))
                        self.start_rental_btn.setGeometry(QtCore.QRect(200, 300, 200, 41))
                        self.end_rental_btn.setGeometry(QtCore.QRect(200, 350, 200, 41))
                        self.car_list.setVisible(False)
                        self.start_rental_btn.setEnabled(False)
                        self.end_rental_btn.setEnabled(True)
                        self.notification.setVisible(True)
                    else:
                        self.end_rental_btn.setEnabled(False)
                        self.notification.setText("Thank you for your time with us!")
                        self.car_choosen.setVisible(False)
                        time.sleep(2.5)
                        self.car_choosen.setGeometry(QtCore.QRect(100, 450, 400, 100))
                        self.start_rental_btn.setGeometry(QtCore.QRect(200, 550, 200, 41))
                        self.end_rental_btn.setGeometry(QtCore.QRect(200, 600, 200, 41))
                        #closing and hiding list of cars, start/end buttons
                        self.car_list.setVisible(False)
                        self.car_list.clear()
                        self.start_rental_btn.setEnabled(False)
                        self.start_rental_btn.setVisible(False)
                        self.end_rental_btn.setVisible(False)
                        self.notification.setVisible(False)
                        self.car_choosen.setText("Car selected:\nBrand:\nVIN:")
                        #restarting from location choosing
                        self.location_list.setVisible(True)
                        self.location_btn.setVisible(True)

                elif msg == b'5':
                    if rented:
                        self.notification.setVisible(True)
                        self.notification.setStyleSheet("font-size:16px;font:bold;qproperty-alignment: AlignCenter;color:red")
                        self.notification.setText("End rental request error!\nPlease check the lights and windows to be closed")
                        time.sleep(3)
                        self.notification.setVisible(False)
                    else:
                        self.notification.setVisible(True)
                        self.notification.setGeometry(QtCore.QRect(100, 400, 400, 50))
                        self.notification.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignCenter;color:red")
                        self.notification.setText("Rental request delayed!\nThe selected car is temporary unavailable.")
                        time.sleep(3)
                        self.notification.setVisible(False)
                        self.notification.setGeometry(QtCore.QRect(100, 200, 400, 100))

                elif msg == b'8':
                    self.lock_login()
                    self.user_label.setText("User: " + self.username)
                    self.location_list.setVisible(True)
                    self.location_btn.setVisible(True)
                elif msg == b'9':
                    self.resubmit_label.setVisible(True)
                    self.submit_btn.setEnabled(True)

            '''
                  Message Identifier: unique per each message;
                 o 0 – register client
                 o 1 – query cars available for rental
                 o 2 – start rental of the car chosen by the client
                 o 3 – end rental of the car previously rented by the client
                 o 4 – notification of success in execution of request (start rental, end rental, etc.)
                 o 5 – notification of errors in execution of request (start rental, end rental, etc.)
                 o 8 - confirm user login
                 o 9 - reject user login
                     '''

    def connect_to_company(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((HOST, PORT))

        if self.conn is not None:
            # self.conn.send(b'2')
            # self.conn.send(b'usern1ame cardnumber C1NP')
            self.connect_to_company_btn.setVisible(False)
            self.connected_label.setText("Company connected")
            self.unlock_login()
            self.recv_messages()

    def unlock_login(self):
        self.form_label.setVisible(True)
        self.username_label.setVisible(True)
        self.username_input.setVisible(True)
        self.cnp_label.setVisible(True)
        self.cnp_input.setVisible(True)
        self.card_label.setVisible(True)
        self.card_input.setVisible(True)
        self.submit_btn.setVisible(True)

    def lock_login(self):
        self.form_label.setVisible(False)
        self.username_label.setVisible(False)
        self.username_input.setVisible(False)
        self.cnp_label.setVisible(False)
        self.cnp_input.setVisible(False)
        self.card_label.setVisible(False)
        self.card_input.setVisible(False)
        self.submit_btn.setVisible(False)

    def submit_login(self):
        self.conn.send(b'0')
        self.conn.send((str(self.username_input.text() + " " + self.cnp_input.text() + " " + self.card_input.text())).encode('utf-8'))
        self.submit_btn.setEnabled(False)
        self.username = self.username_input.text()
        self.username_input.clear()
        self.card_input.clear()
        self.cnp_input.clear()

    def on_location_selected(self, item):
        global location_selected
        location_selected = item.text()
        self.location_btn.setText("Query cars at " + location_selected)
        self.location_btn.setEnabled(True)

    def on_car_selected(self, item):
        global car_selected
        car_selected = item.text()
        self.start_rental_btn.setText("Start rental")
        self.start_rental_btn.setEnabled(True)
        self.car_choosen.setText("Car selected:\nBrand: "+ car_selected.split(' ')[0] +"\nVIN: " +  car_selected.split(' ')[1])

    def query_request(self):
        global location_selected
        print(self.location_btn.text())
        self.conn.send(b'1')
        self.conn.send(location_selected.encode('utf-8'))

    def start_rental(self):
        self.conn.send(b'2')
        self.conn.send((car_selected.split(' ')[1]).encode('utf-8'))

    def end_rental(self):
        self.conn.send(b'3')
        self.conn.send((car_selected.split(' ')[1]).encode('utf-8'))


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




