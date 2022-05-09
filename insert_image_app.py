import threading
import tkinter
from tkinter import *
from tkinter import filedialog, ttk, messagebox

from PIL import Image, ImageTk
from guiGlobals import *
import cv2
import socket
import struct
import time

from network_module import recive_msg_header, create_msg_with_header, BUFFER_SIZE, extract_image, send_cv2_image_as_png


class InsertImageApp(tkinter.Tk):
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.title(CLIENT_TITLE)
        self['bg'] = BACKGROUND_COLOR
        self.geometry(fr'{WIDTH}x{HEIGHT}')
        self.label = Label(self, text=ENTER_LOC, fg='black', bg=BACKGROUND_COLOR,
                           font='time 15 bold')
        self.label.pack()
        self.button = Button(self, text='Select Image', fg='white', bg='red', font='time 15 bold',
                             command=self.open_file).pack()
        self.progress = None

        self.my_image = None
        self.filename = ''
        self.screen_img = None
        self.Thread = False
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((IP, PORT))

    def open_file(self):
        self.reset()
        self.filename = filedialog.askopenfilename(initialdir='photo', title='Select a file',
                                                   filetypes=(('PNG files', '*.png'), ('all files', '*.*')))
        if self.filename != '':
            self.label = Label(self, text='The location is: ' + self.filename, fg='black', bg=BACKGROUND_COLOR,
                               font='time 15 bold').pack()

            self.screen_img = Image.open(self.filename)
            img = self.screen_img
            width, height = self.screen_img.size
            img = self.set_size(height, img, self.screen_img, width)
            self.my_image = ImageTk.PhotoImage(img)
            self.label = Label(image=self.my_image)
            self.label.pack()
            button1 = Button(self, text='Analyze image', fg='white', bg='red', font='time 15 bold',
                             command=self.can_send).pack()

    def can_send(self):
        self.Thread = False
        if self.progress is None:
            self.progress = ttk.Progressbar(self, orient=HORIZONTAL, length=PROGRESS_BAR_LENGTH, mode='determinate')
            self.progress.pack(pady=20)
        threading.Thread(target=self.send_image).start()

    def send_image(self):
        if not self.Thread:
            #self.send_response()
            self.client_socket.send(bytes(create_msg_with_header('Insert'), "utf-8"))
            send_cv2_image_as_png(self.screen_img, self.client_socket)
            self.receive_image()
            self.receive_response()
            self.Thread = True

    def reset(self):
        for widgets in self.winfo_children():
            widgets.destroy()
        self.label = Label(self, text=ENTER_LOC, fg='black', bg=BACKGROUND_COLOR,
                           font='time 15 bold')
        self.label.pack()
        self.button = Button(self, text='Select Image', fg='white', bg='red', font='time 15 bold',
                             command=self.open_file).pack()
        self.my_image = None
        self.filename = ''
        self.screen_img = None
        self.Thread = False
        self.progress = None

    def send_response(self):
        """
        Send the server the type of the protocol is insert an image to the dataBASE.
        Then, send the image we want to process.
        :return:
        """
        self.client_socket.send(bytes(create_msg_with_header('Insert'), "utf-8"))
        send_cv2_image_as_png(self.screen_img, self.client_socket)

    def recv_data_large(self, data, size):
        while len(data) < size:
            data += self.client_socket.recv(BUFFER_SIZE)
        return data

    def receive_image(self, group=True):
        """
        The client receive from the server images and display them on screen
        :param group: True if the client receive a couple of image, False if only one image
        :return:
        """
        data = b""
        # Return the size of the struct
        payload_size = struct.calcsize(">L")

        if group:
            size = int(recive_msg_header(self.client_socket))
            # You may need to convert the color.
            i = 0
            imgs = []
            while i < size:
                im_pil = self.get_image_convert_to_pill_image(data)
                imgs.append(im_pil)
                i += 1
            for im_pil in imgs:
                self.update_process_bar()
                self.display_image(im_pil)

        else:
            # You may need to convert the color.
            im_pil = self.get_image_convert_to_pill_image(data)
            self.display_image(im_pil)

    def get_image_convert_to_pill_image(self, data):
        frame = extract_image(data, self.client_socket)
        #frame = self.extract_image_from_client(data, payload_size)
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)
        return im_pil

    def update_process_bar(self):
        """
        Adds value to the process bar.
        :return:
        """
        self.progress['value'] += 20
        self.update_idletasks()
        time.sleep(1)

    def display_image(self, im_pil):
        """
        Display image on screen
        :param im_pil: Image
        :return:
        """
        width, height = im_pil.size
        img = im_pil
        img = self.set_size(height, img, im_pil, width)
        self.my_image = ImageTk.PhotoImage(img)
        self.label.configure(image=self.my_image)
        self.label.image = self.my_image

    def receive_response(self):
        data = recive_msg_header(self.client_socket)
        if data is not None:
            self.receive_image(False)
            self.label = Label(self, text=data, fg='yellow', bg=BACKGROUND_COLOR,
                               font='time 15 bold').pack()
            self.progress['value'] = PROGRESS_BAR_LENGTH
            self.update_idletasks()

    def set_size(self, height, img, scr, width):
        """
        resize the image if it is too small
        :param height: height
        :param img: temp image
        :param scr: source image
        :param width: width
        :return: resized image
        """
        if width >= 1000 and height >= 1000:
            img = scr.resize((int(width * 0.25), int(height * 0.25)))
        elif width >= 1000 or height >= 1000:
            if width >= 1000:
                img = scr.resize((int(width * 0.25), int(height * 0.25)))
            if height >= 1000:
                img = scr.resize((int(width * 0.25), int(height * 0.25)))

        return img

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            self.client_socket.send(bytes(create_msg_with_header('Quit'), "utf-8"))
            self.client_socket.close()
