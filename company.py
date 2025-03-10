from PyQt5.QtWidgets import QListWidget
from PyQt5 import QtCore, QtGui, QtWidgets
import socket
from pyexpat.errors import messages
import _pickle as cPickle
import os
import threading
import sys, time
import psutil


HOST = 'localhost'
PORT_phone = 5000
PORT_car = 8000
stop_thread = False
response = False

class Car:
    def __init__(self, car):
        self.brand = car[0]
        self.VIN = car[1]
        self.location = car[2]

    def __str__(self):
        return f'{self.brand} {self.VIN} {self.location}'

class Client:
    def __init__(self, client):
        self.name = client[0]
        self.CNP = client[1]
        self.card = client[2]

    def __str__(self):
        return f'{self.name}    {self.CNP}  {self.card}'

    def __eq__(self, other): # for checking if the client already exists
        if self.CNP == other.CNP and self.card == other.card:
            return True
        else:
            return False

class Ui_MainWindow(object):
    def __init__(self):
        self.phone_conn = None
        self.phone_server = None
        self.cars = []
        self.clients = []
        self.pause_event = threading.Event()  # Obiect pentru sincronizare
        with open('cars.txt', 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            for i in lines:
                self.cars.append(Car(i.split(' ')))


        with open('clients.txt', 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            for i in lines:
                self.clients.append(Client(i.split(' ')))


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600, 800)
        MainWindow.setWindowTitle('Company Backend')
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.centralwidget.setStyleSheet("background-color:white;")

        # start of UI elements:

        # approve request
        self.approve_request = QtWidgets.QPushButton(MainWindow)
        self.approve_request.setGeometry(QtCore.QRect(150, 550, 300, 50))
        self.approve_request.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignLeft;color: green")
        self.approve_request.setText("Approve Request")
        self.approve_request.clicked.connect(self.approve_req)
        self.approve_request.setVisible(False)

        # deny request
        self.deny_request = QtWidgets.QPushButton(MainWindow)
        self.deny_request.setGeometry(QtCore.QRect(150, 600, 300, 50))
        self.deny_request.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignLeft;color: red")
        self.deny_request.setText("Deny Request")
        self.deny_request.clicked.connect(self.deny_req)
        self.deny_request.setVisible(False)


        # phone app request
        self.request = QtWidgets.QLabel(self.centralwidget)
        self.request.setGeometry(QtCore.QRect(10, 100, 500, 300))
        self.request.setStyleSheet("font-size:18px;font:bold;qproperty-alignment: AlignLeft;")
        self.request.setText("Request: None")
        self.request.setVisible(False)

        # Start server button
        self.connect_to_phone_btn = QtWidgets.QPushButton(MainWindow)
        self.connect_to_phone_btn.setText("Connect to phone")
        self.connect_to_phone_btn.setStyleSheet("font: bold; font-size: 15px;")
        self.connect_to_phone_btn.setGeometry(QtCore.QRect(150, 600, 300, 50))
        self.connect_to_phone_btn.clicked.connect(self.connect_to_phone)

        # Connected label
        self.connected_label = QtWidgets.QLabel(self.centralwidget)
        self.connected_label.setGeometry(QtCore.QRect(50, 700, 500, 40))
        self.connected_label.setStyleSheet("font-size:15px;font:bold;qproperty-alignment: AlignCenter;")

        # end of UI elements;

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.show()

        self.connect_to_cars()

    def on_car_selected(self, item):
        car_text = item.text()
        for car in self.cars:
            if str(car) == car_text:
                self.selected_car = car
                break
        print(f"masina selectata: {self.selected_car}")

    def approve_req(self):
        global response
        response= True
        self.pause_event.set()

    def deny_req(self):
        global response
        response = False
        self.pause_event.set()

    # start of code
    def connect_to_phone(self):
        self.phone_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.phone_server.bind((HOST, PORT_phone))
        self.phone_server.listen(1)
        self.phone_conn, addr = self.phone_server.accept()

        if self.phone_conn is not None:
            self.connected_label.setText('Cars and Phone app connected')
            self.approve_request.setVisible(True)
            self.deny_request.setVisible(True)
            self.request.setVisible(True)
            self.connect_to_phone_btn.setVisible(False)
            self.recv_messages_phone()

    def recv_messages_phone(self):
        self.stop_event = threading.Event()
        self.c_thread = threading.Thread(target=self.recv_handler_phone, args=(self.stop_event,))
        self.c_thread.start()

    def recv_handler_phone(self, stop_event):
        global stop_thread
        global response
        while not stop_event.is_set() and stop_thread == False:
            msg = self.phone_conn.recv(1)
            print(msg)
            if msg == b'0':
                self.request.setText('Request: Client wants to connect to company')

                client_data = (self.phone_conn.recv(1024)).decode('utf-8')
                self.pause_event.clear()
                self.pause_event.wait()
                if response:
                    temp_client = Client(client_data.split(' '))
                    if temp_client not in self.clients:
                        self.clients.append(temp_client)
                        print('Client added successfully.')
                        # save the client into the database
                        with open('clients.txt', 'a') as f:
                            f.write(f'{client_data}\n')
                    else:
                        print('The client already exists.')
                    self.phone_conn.send(b'8')
                else:
                    self.phone_conn.send(b'9')

                self.request.setText('Request: ')

            elif msg == b'1':
                location = (self.phone_conn.recv(1024)).decode()
                self.request.setText(f'Request: all cars from {location}')

                self.pause_event.clear()
                self.pause_event.wait()

                if response:
                    temp_car_list = ''
                    for car in self.cars:
                        if car.location == location:
                            temp_car_list += car.__str__() + '|'

                    self.phone_conn.send(b'1')
                    print(temp_car_list)
                    self.phone_conn.sendall(bytes(temp_car_list, 'ascii'))
                else:
                    self.phone_conn.send(b'9')

                self.request.setText('Request: ')

            elif msg == b'2':
                VIN = self.phone_conn.recv(1024).decode()
                self.request.setText(f'Request: start rental for VIN: {VIN}')

                self.pause_event.clear()
                self.pause_event.wait()

                if response:
                    if self.cars_conn is not None:
                        self.cars_conn.sendall(b'2')
                else:
                    self.phone_conn.send(b'9')

                self.request.setText('Request: ')


            elif msg == b'3':
                VIN = self.phone_conn.recv(1024).decode()
                self.request.setText(f'Request: end rental for VIN: {VIN}')

                self.pause_event.clear()
                self.pause_event.wait()

                if response:
                    if self.cars_conn is not None:
                        self.cars_conn.sendall(b'3')
                else:
                    self.phone_conn.send(b'9')

                self.request.setText('Request: ')

            '''
         Message Identifier: unique per each message;
        o 0 – register client
        o 1 – query cars available for rental
        o 2 – start rental of the car chosen by the client
        o 3 – end rental of the car previously rented by the client
        o 4 – notification of success in execution of request (start rental, end rental, etc.)
        o 5 – notification of errors in execution of request (start rental, end rental, etc.)
            '''

    def connect_to_cars(self):
        self.cars_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cars_server.bind((HOST, PORT_car))
        self.cars_server.listen(1)
        self.cars_conn, addr = self.cars_server.accept()

        if self.cars_conn is not None:
            self.connected_label.setText('Cars connected')
            self.recv_messages_cars()


    def recv_messages_cars(self):
        self.stop_event = threading.Event()
        self.c_thread = threading.Thread(target=self.recv_handler_cars, args=(self.stop_event,))
        self.c_thread.start()

    def recv_handler_cars(self, stop_event):
        global stop_thread
        while not stop_event.is_set() and stop_thread == False:
            msg = self.cars_conn.recv(1)

            if msg == b'4':
                self.phone_conn.sendall(b'4')
            elif msg == b'5':
                self.phone_conn.sendall(b'5')


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


