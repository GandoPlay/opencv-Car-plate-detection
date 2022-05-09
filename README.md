# opencv-Car-plate-detection
Running to project:
================================
To run this code in pycharm, download the following packages:
Pillow Version 9.1.0
easyocr  Version 1.4.2
pytesseract Version 0.3.9
numpy Version 1.22.3
opencv-python version 4.5.5.64
pip  Version 21.1.2

then, download the pytessract model (64 bits) from :
https://github.com/UB-Mannheim/tesseract/wiki
and then in Globals.py change the value of "pytesseract.pytesseract.tesseract_cmd" to the location of the file you just downloaded.
To run the code, simply run the server and then the client.
You can run another client or more from the cmd if you want.

You can also download from this drive link: (Github won't allow me to upload the entire project)
https://drive.google.com/drive/folders/172xGTOsD5j0oBdxNJVcrNHecevM_cmhg?usp=sharing
The application:
=================
As a client you got a few options:
-You can insert a png image to the database
-You can delete an image from the database
-You can Update information in the database
-You can see the database

This system is using image processing techniques to locate a license plate's number and country,these are the country it can detect:
Israel
Suadi arabia
Jordan
palestine
Syria
