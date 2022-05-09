import socket
import sys
import threading
import time

import cv2

import struct

from DB import DBCars
from guiGlobals import *

from carPlateDetection import CarPlateDetection
from network_module import create_msg_with_header,send_cv2_image_as_png, decode_data, BUFFER_SIZE, receive_large_data, extract_image


class Server:
    def __init__(self):
        self.cpd = CarPlateDetection()
        self.server = None
        self.clients = {}
        self.client = None
        self.CLIENT_COUNTER = 1

        self.database = DBCars()
        self.payload_size = struct.calcsize(">L")

    def create_server(self):
        """
        Initialize the Server.
        :return:
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT))
        self.server.listen(10)
        print('The server is up')

    def recv_data_large(self, data, size, name):

        while len(data) < size:
            data += self.clients[name].recv(BUFFER_SIZE)
        return data

    def handleQuit(self, msg, name):
        """

        :param msg: the msg the client sent.
        :param name: the Name of the client.
        :return: True if the client is leaving the Server else False.
        """
        if msg == 'Quit':
            self.clients[name].close()
            self.clients.pop(name)
            print(f"{name} has left!")
            return True
        return False

    def session_with_client(self, client_socket, name):
        """
        The communication with the Client.
        The client send a request he need from the DataBase whether it is
        (Update, Insert, Delete, Show)

        :param client_socket: the socket with the client we are interacting with.
        :param name: the name of the client.
        :return:
        """
        self.clients[name] = client_socket
        self.CLIENT_COUNTER += 1
        while True:
            if name not in self.clients:
                break

            data = b"" + self.clients[name].recv(BUFFER_SIZE)
            msg = decode_data(data)

            if msg == 'Start':
                continue

            if self.handleQuit(msg, name):
                break

            self.perform_operation(msg, name)

    def handle_insert(self, name):
        """
        The client send to photo he want to process.
        While the image is being processed.
        The server send once a time a part of the process.
        When the Image is done.
        The server send back the image, The number plate and the Country.
        :param name: Name of the client.
        :return:
        """
        data = b"" + self.clients[name].recv(BUFFER_SIZE)
        frame = extract_image(data, self.clients[name])
        #frame = self.extract_image_from_client(data, name)
        # showing The process
        imgs = self.cpd.show_process(frame)
        self.clients[name].send(bytes(create_msg_with_header(f'{len(imgs)}'), "utf-8"))
        for i in imgs:
            send_cv2_image_as_png(i,self.clients[name])
            #self.send_response(i, name)
        (lp_country, lp_number_plate, lpCnt, c) = self.cpd.get_car_plate_data(frame, imgs[len(imgs) - 1])
        self.clients[name].send(bytes(create_msg_with_header(f'{lp_country} \n {lp_number_plate}'), "utf-8"))

        self.cpd.draw_image(frame, lpCnt, '', '')
        _, enc = cv2.imencode(".png", frame)

        self.database.insert(lp_number_plate, lp_country, enc)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #self.send_response(frame, name)
        send_cv2_image_as_png(frame, self.clients[name])

    def handle_delete(self, name):
        while True:
            data = self.clients[name].recv(BUFFER_SIZE)
            country = decode_data(data)

            if self.handleQuit(country, name):
                break

            if country == 'Back' or country == 'Delete':
                continue

            txt = str(self.database.show(country))
            self.clients[name].send(bytes(create_msg_with_header(txt), "utf-8"))
            data = self.clients[name].recv(BUFFER_SIZE)
            oid = decode_data(data)
            if oid == 'Back':
                continue
            self.database.delete(oid)

    def handle_update(self, name):
        while True:
            data = self.clients[name].recv(BUFFER_SIZE)
            country = decode_data(data)
            if self.handleQuit(country, name):
                break
            if country == 'Back' or country == 'Update':
                continue
            txt = str(self.database.show(country))

            self.clients[name].send(bytes(create_msg_with_header(txt), "utf-8"))
            data = self.clients[name].recv(BUFFER_SIZE)
            m = decode_data(data)
            lst = m.split('\n')
            self.database.update(lst[0], country, lst[1])

    def handle_show(self, name):
        while True:
            data = self.clients[name].recv(BUFFER_SIZE)
            msg = decode_data(data)
            data = b""
            if self.handleQuit(msg, name):
                break
            if msg == 'Back' or msg == 'Show':
                continue

            data_to_send = str(self.database.show(msg))
            self.clients[name].send(bytes(create_msg_with_header(data_to_send), "utf-8"))

    def invalid_op(self, name):
        raise Exception("Invalid operation")

    def perform_operation(self, chosen_operation, name):
        """
        perform the action that the client chose.
        :param chosen_operation:  the operation ('Delete','Update','Insert','Show')
        :param name: The name of the client
        :return:
        """
        ops = {
            "Delete": self.handle_delete,
            "Update": self.handle_update,
            "Insert": self.handle_insert,
            "Show": self.handle_show
        }
        chosen_operation_function = ops.get(chosen_operation, self.invalid_op)
        return chosen_operation_function(name)

    def start_server(self):
        """
        Start the connection with the clients.
        :return:
        """
        self.create_server()

        while True:
            client_socket, c = self.server.accept()
            name = f'client{self.CLIENT_COUNTER}'
            print(f'{name} has connected!')
            t1 = threading.Thread(target=self.session_with_client, args=(client_socket, f'{name}'))
            t1.start()


def main():
    s = Server()
    s.start_server()


if __name__ == '__main__':
    main()
