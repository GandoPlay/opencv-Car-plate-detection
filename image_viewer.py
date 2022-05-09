import tkinter
from tkinter import *
from tkinter import messagebox

from PIL import ImageTk, Image

from guiGlobals import CLIENT_TITLE


class ImageViewer(tkinter.Tk):
    def __init__(self, imgs, country, state='Show'):
        super().__init__()

        self.imgs = self.set_images(imgs)
        self.str = 'None'
        self.state = state
        self.country = country
        self.title(CLIENT_TITLE)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.index = 0

        (self.current_img, self.text, self.oid) = self.imgs[0]
        self.label = Label(self, image=self.current_img)
        self.text_label = Label(self, text=self.text, fg='black', font='time 15 bold')
        self.back_button = Button(self, text='back', fg='white', bg='red', command=self.back, state=DISABLED,
                                  font='time 15 bold')
        self.forward_button = Button(self, text='next', fg='white', bg='red', command=self.forward, font='time 15 bold')
        if state == 'Update' or state == 'Delete':
            self.select_button = Button(self, text='Select', fg='black', bg='yellow', command=self.select,
                                        font='time 15 bold')
            self.select_button.grid(row=2, column=1)

        self.label.grid(row=0, column=0, columnspan=3)
        self.back_to_parent = Button(self, text='Go Back', fg='white', bg='blue',
                                     font='time 15 bold', command=self.back_to_father)

        self.text_label.grid(row=1, column=0, columnspan=3)

        self.back_button.grid(row=2, column=0)
        self.forward_button.grid(row=2, column=2)
        self.back_to_parent.grid(row=3, column=0)

    def back_to_father(self):
        self.destroy()

    def select(self):
        if self.state == 'Delete':
            self.destroy()
            self.str = self.oid

        elif self.state == 'Update':
            self.update_window()

    def update_window(self):
        # open new Window
        editor = Tk()
        editor.title('Update a Record')
        car_plate = Entry(editor, width=30)
        car_plate.grid(row=0, column=1)
        country = Entry(editor, width=30)
        country.grid(row=1, column=1)

        car_plate_label = Label(editor, text="""Car's plate number""")
        car_plate_label.grid(row=0, column=0)
        country_label = Label(editor, text="""Car's country""")
        country_label.grid(row=1, column=0)

        car_plate.insert(0, self.text)
        country.insert(1, self.country)

        self.save_btn = Button(editor, text='Save', command=lambda: self.save(editor, car_plate.get(), country.get()))
        self.save_btn.grid(row=2, columnspan=2, pady=10, padx=10, ipadx=100)
        editor.mainloop()

    def car_data(self):
        return self.str

    def save(self, root, car_plate, country):
        root.destroy()
        self.destroy()
        self.str = car_plate, country, self.oid

    def set_size(self, height, img, scr, width):

        if width >= 1000 and height >= 1000:
            img = scr.resize((int(width * 0.25), int(height * 0.25)))
        elif width >= 1000 or height >= 1000:
            if width >= 1000:
                img = scr.resize((int(width * 0.5), int(height * 0.5)))
            if height >= 1000:
                img = scr.resize((int(width * 0.5), int(height * 0.5)))

        return img

    def set_images(self, lst):
        img_lst = []
        for i in lst:
            img = Image.open(i[0])
            width, height = img.size
            img = self.set_size(height, img, img, width)
            tup = (ImageTk.PhotoImage(img), i[1], i[2])
            img_lst.append(tup)
        return img_lst

    def forward(self):
        if self.index + 1 < len(self.imgs):
            self.index += 1
        if self.index == len(self.imgs):
            self.forward_button = Button(self, text='next', fg='white', bg='red', state=DISABLED, font='time 15 bold')

        else:

            self.label.grid_forget()
            self.text_label.grid_forget()
            self.current_img, self.text, self.oid = self.imgs[self.index]
            self.label = Label(image=self.current_img)
            self.text_label = Label(self, text=self.text, fg='black', font='time 15 bold')
            self.forward_button = Button(self, text='next', fg='white', bg='red', command=self.forward,
                                         font='time 15 bold')
            self.back_button = Button(self, text='back', fg='white', bg='red', command=self.back, font='time 15 bold')
            self.back_to_parent = Button(self, text='Go Back', fg='white', bg='blue',
                                         font='time 15 bold', command=self.back_to_father)

            self.label.grid(row=0, column=0, columnspan=3)
            self.text_label.grid(row=1, column=0, columnspan=3)
            self.back_button.grid(row=2, column=0)
            self.forward_button.grid(row=2, column=2)
            self.back_to_parent.grid(row=3, column=0)

    def back(self):

        if self.index <= 0:
            self.back_button = Button(self, text='back', fg='white', bg='red', state=DISABLED, font='time 15 bold')
            self.index = 0
        else:
            self.index -= 1

            self.label.grid_forget()
            self.text_label.grid_forget()
            self.label.grid_forget()
            self.text_label.grid_forget()
            self.current_img, self.text, self.oid = self.imgs[self.index]
            self.label = Label(image=self.current_img)
            self.text_label = Label(self, text=self.text, fg='black', font='time 15 bold')
            self.forward_button = Button(self, text='next', fg='white', bg='red', command=self.forward,
                                         font='time 15 bold')
            self.back_button = Button(self, text='back', fg='white', bg='red', command=self.back, font='time 15 bold')
            self.back_to_parent = Button(self, text='Go Back', fg='white', bg='blue',
                                         font='time 15 bold', command=self.back_to_father)

            self.label.grid(row=0, column=0, columnspan=3)
            self.text_label.grid(row=1, column=0, columnspan=3)
            self.back_button.grid(row=2, column=0)
            self.forward_button.grid(row=2, column=2)
            self.back_to_parent.grid(row=3, column=0)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
