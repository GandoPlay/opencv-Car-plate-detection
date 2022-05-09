import threading
import tkinter
from tkinter import *

from insert_image_app import InsertImageApp
from guiGlobals import *
import socket

import time

from network_module import create_msg_with_header
from basic_commands import BasicCommandsApp


class Client(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.title(CLIENT_TITLE)
        self['bg'] = BACKGROUND_COLOR2
        self.client_socket = None
        self.geometry(fr'{WIDTH}x{400}')
        self.connect_to_server()
        self.set_screen()

    def set_screen(self):
        """
        set up the entire Gui for the Client Application.
        Sets all The buttons of the actions the client can make.
        INSERT, SHOW, DELETE, UPDATE.
        :return:
        """
        label = Label(self, text=WELCOME, fg='Blue', bg=BACKGROUND_COLOR2, font='Arial 40 bold')
        label.place(x=350, y=10)
        # Insert button
        self.set_button(text='Insert', fg='white', bg='red', font='time 40 bold',
                        command=self.insert, x=100, y=200)
        # Update button
        self.set_button(text='Update', fg='black', bg='Yellow', font='time 40 bold',
                        command=self.update, x=350, y=200)
        # Delete button
        self.set_button(text='Delete', fg='black', bg='Cyan', font='time 40 bold',
                        command=self.delete, x=600, y=200)
        # Show button
        self.set_button(text='show', fg='white', bg='Green', font='time 40 bold',
                        command=self.show, x=850, y=200)

    def set_button(self, text, fg, bg, font, command, x, y):
        """
        Set up the button
        :param text: What is written on the button
        :param fg: Foreground color of the button
        :param bg: Background color of the button
        :param font: the font of the text
        :param command: what command will the button do
        :param x: x coord
        :param y: y coord
        :return:
        """
        but = Button(self, text=text, fg=fg, bg=bg, font=font,
                     command=command)
        but.place(x=x, y=y)

    def show(self):
        self.destroy()
        app = BasicCommandsApp(self.client_socket)
        app.mainloop()

    def insert(self):
        self.destroy()
        app = InsertImageApp(self.client_socket)
        app.mainloop()

    def delete(self):
        self.destroy()
        app = BasicCommandsApp(self.client_socket, 'Delete')
        app.mainloop()

    def update(self):
        self.destroy()
        app = BasicCommandsApp(self.client_socket, 'Update')
        app.mainloop()

    def reset(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        label = Label(self, text=WELCOME, fg='black', bg=BACKGROUND_COLOR2,
                      font='time 15 bold')
        label.pack()

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((IP, PORT))
            self.client_socket.send(bytes(create_msg_with_header('Start'), "utf-8"))
        except ConnectionRefusedError:
            print('trying again to connect..')
            time.sleep(2)
            self.connect_to_server()


def main():
    app = Client()
    app.mainloop()


if __name__ == '__main__':
    main()
