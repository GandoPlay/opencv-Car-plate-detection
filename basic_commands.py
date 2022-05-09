import threading
import tkinter
from tkinter import *
from tkinter import  messagebox

from guiGlobals import *
import os

from image_viewer import ImageViewer
from network_module import recive_msg_header, create_msg_with_header


class BasicCommandsApp(tkinter.Tk):
    def __init__(self, socket, state='Show'):
        super().__init__()
        self.options = [
            'Israel',
            'Jordan',
            'Syria',
            'Palestine',
            'Saudi arabia'
        ]
        self.state = state
        self.imgs = []
        self.filenames = []
        self.labels = []
        self.set_screen()
        self.client_socket = socket
        self.client_socket.send(bytes(create_msg_with_header(self.state), "utf-8"))
        self.title(CLIENT_TITLE)
        self['bg'] = BACKGROUND_COLOR
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_screen(self, flag=False):
        """
        Set the screen of The application.
        :param flag:
        :return:
        """
        self.imgs = []
        self.filenames = []
        self.labels = []
        label = Label(self, text='Choose country', fg='black', bg=BACKGROUND_COLOR, font='david 40 bold')
        label.grid(row=0, column=0, columnspan=3)
        if not flag:
            self.clicked = StringVar()
            self.clicked.set(self.options[0])
        drop = OptionMenu(self, self.clicked, *self.options)
        drop.grid(row=1, column=0, columnspan=3)
        but = Button(self, text='show', command=self.create_new_screen).grid(row=2, column=0, columnspan=3)

    def writeTofile(self, data, filename):
        """
        Convert binary data to proper format and write it on Hard Disk
        :param data: binary data of the image
        :param filename: the Location of the file.
        :return:
        """

        with open(filename, 'wb') as file:
            file.write(data)

    def create_new_screen(self):
        """
        send the server which country we want. based on the action we chose
        the screen will behavior in accordingly.
        :return:
        """
        self.reset()
        # send the country
        self.client_socket.send(bytes(create_msg_with_header(self.clicked.get()), "utf-8"))
        # Get all the cars from this country
        data = recive_msg_header(self.client_socket)

        self.download_images_to_folder(data)

        self.perform_operation(self.state)

    def download_images_to_folder(self, data):
        """
        Using the giving data, convert it to an image and save it in a folder
        the data contains a list of images in this format:
        ('numPlate, country, Image's representation in binary string, oid'
        :param data: String that contains all the data of the images
        :return:
        """
        # turn string into a list.

        lst = eval(data)
        mone = 1
        self.imgs = []
        for car in lst:
            filename = os.getcwd() + fr'\database_photo\car{car[1]}{mone}.png'
            self.filenames.append(filename)
            self.writeTofile(car[2], filename)
            self.append_to_list(filename, car[0], car[3])

            mone += 1

    def handle_show(self):
        self.destroy()
        child = ImageViewer(self.imgs, self.clicked.get())
        child.mainloop()
        self.client_socket.send(bytes(create_msg_with_header('Back'), "utf-8"))
        self.__init__(self.client_socket, self.state)

    def handle_update(self):
        self.destroy()
        child = ImageViewer(self.imgs, self.clicked.get(), state='Update')
        child.mainloop()
        data = child.car_data()
        msg = f'{data[0]}\n{data[2]}'
        self.client_socket.send(bytes(create_msg_with_header(msg), "utf-8"))
        self.client_socket.send(bytes(create_msg_with_header('Back'), "utf-8"))
        self.__init__(self.client_socket, self.state)

    def handle_delete(self):
        self.destroy()
        child = ImageViewer(self.imgs, self.clicked.get(), state='Delete')
        child.mainloop()
        msg = str(child.car_data())
        if msg != 'None':
            self.client_socket.send(bytes(create_msg_with_header(msg), "utf-8"))
        self.client_socket.send(bytes(create_msg_with_header('Back'), "utf-8"))
        self.__init__(self.client_socket, self.state)

    def invalid_op(self, name):
        raise Exception("Invalid operation")

    def perform_operation(self, chosen_operation):
        """
        perform the action that the client chose.
        :param chosen_operation:  the operation ('Delete','Update','Insert','Show')
        :return:
        """
        ops = {
            "Delete": self.handle_delete,
            "Update": self.handle_update,
            "Show": self.handle_show
        }
        chosen_operation_function = ops.get(chosen_operation, self.invalid_op)
        return chosen_operation_function()

    def append_to_list(self, location, num_plate, oid):
        """
        append to self.img as a tuple
        :param location: the location of the image
        :param num_plate: numPlate of the image
        :param oid:
        :return:
        """
        tup = (location, num_plate, oid)
        self.imgs.append(tup)

    # def set_size(self, height, scr, width):
    #
    #     """
    #     resize an image.
    #     :param height: height
    #     :param scr: source image
    #     :param width: width
    #     :return: resized image.
    #     """
    #     return scr.resize((int(width * 0.25), int(height * 0.25)))

    def reset(self):
        """
        reset the entire GUI of the screen.
        :return:
        """
        for widgets in self.winfo_children():
            widgets.destroy()
        self.set_screen(True)

    def on_closing(self):
        """
        closes the Screen, send the server That the communication is over and closed the socket.
        :return:
        """
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            self.client_socket.send(bytes(create_msg_with_header('Quit'), "utf-8"))
            self.client_socket.close()
