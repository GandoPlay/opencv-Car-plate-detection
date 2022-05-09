
import cv2
import easyocr

from countryDetection import CountryDetection
from stringOperators import *

cnts = []


class CarPlateDetection:
    # private functions

    def __init__(self, minAR=2, maxAR=5, debug=False):
        # store the minimum and maximum rectangular aspect ratio
        # values along with whether or not we are in debug mode
        self.__minAR = minAR
        self.__maxAR = maxAR
        self.__debug = debug
        self.__cd = CountryDetection()
        self.__process = []

    def __locate_license_plate_candidates(self, imgGrayscale, tresh_img, keep=KEEP):
        """
          this function.
          :param imgGrayscale: A gray Scale of the image.
          :param keep: A number that says how many rectangles we want.
          :return: A list of contours that could represent the car's plate.
          """
        height, width = imgGrayscale.shape
        if tresh_img is None:

            imgThresh = self.__image_filtering(imgGrayscale)
        else:
            imgThresh = tresh_img
        cnts,h = cv2.findContours(imgThresh.copy(), cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)

        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:keep]

        # return the list of contours
        return self.__locate_rectangles(cnts)

    def __image_filtering(self, imgGrayscale):
        """
         use image processing techniques on the image so we take data more
         if debug==True then all the process to a list.
        :param imgGrayscale: A gray Scale of the image.
        :return: Threshold image
        """
        structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, STRUCTURING_ELEMENT_FILTER)

        imgTopHat = cv2.morphologyEx(imgGrayscale, cv2.MORPH_TOPHAT, structuringElement)
        imgBlackHat = cv2.morphologyEx(imgGrayscale, cv2.MORPH_BLACKHAT, structuringElement)
        imgGrayscalePlusTopHat = cv2.add(imgGrayscale, imgTopHat)
        imgGrayscalePlusTopHatMinusBlackHat = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)
        imgBlurred = cv2.GaussianBlur(imgGrayscalePlusTopHatMinusBlackHat, GAUSSIAN_SMOOTH_FILTER_SIZE, 0)
        imgThresh = cv2.adaptiveThreshold(imgBlurred, 255.0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                                          ADAPTIVE_THRESH_BLOCK_SIZE, ADAPTIVE_THRESH_WEIGHT)
        if self.__debug:
            self.__process.append(imgGrayscalePlusTopHat)
            self.__process.append(imgGrayscalePlusTopHatMinusBlackHat)
            self.__process.append(imgBlurred)
            self.__process.append(imgThresh)
        return imgThresh

    def __is_aspect_ratio(self, c):
        """
            Return if th contour is in the aspect_ratio.
            :param c: A contour.
            :return: boolean.
                """
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        # check to see if the aspect ratio is rectangular
        return self.__minAR <= ar <= self.__maxAR

    def __locate_rectangles(self, candidates):
        """
          Return the rectangles that are more likely to be the car's plate.
          :param candidates: the contours of the rectangles in the image.
          :return: rectangles.
          """
        # loop over the license plate candidate contours
        return [c for c in candidates if self.__is_aspect_ratio(c)]

    def __locate_license_plate(self, gray, candidate):
        """
           This function extract the car's plate from the image.
            :param candidate:   rectangle.
            :param gray:  gray Scale of the image.
            :return: tuple(carPlate's image, carPlate's contour).
            """
        # initialize the license plate contour and ROI
        lpCnt = None
        roi = None
        # store the license plate contour and extract the
        # license plate from the grayscale image and then
        # threshold it
        (x, y, w, h) = cv2.boundingRect(candidate)
        lpCnt = candidate
        licensePlate = gray[y:y + h, x:x + w]
        roi = cv2.threshold(licensePlate, 0, 255,
                            cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        height, width = roi.shape
        if height + width < MINSIZE:
            roi = cv2.resize(roi, (0, 0), fx=RESIZE_IMAGE, fy=RESIZE_IMAGE)
        return roi, lpCnt

    def __extract_data(self, candidates, gray):
        """
              Take all the information from the image.
               :param candidates:   rectangles from the image.
               :param gray:  gray Scale of the image.
               :return:  tuple(country's name, number_plate, contour of the plate, rectangles from the image)
               """
        lp_number_plate = 'NO NUMBER'
        lp_country = 'NO COUNTRY'
        for c in candidates:
            (lp, lpCnt) = self.__locate_license_plate(gray, c)
            reader = easyocr.Reader(['en'])
            lpText = relevant_data(reader, lp)
            if lpText == IRRELEVANT_STR:
                continue
            country = self.__cd.detect_country(lp, lpText)
            print(country)
            # lp_number_plate = f'The number plate is: {extract_number_sequence(lpText)}'
            lp_number_plate = extract_number_sequence(lpText)
            if country == IRRELEVANT_STR:
                continue
            lp_country = country
            # lp_country = f'The country is {country}'
            break

        return lp_country, lp_number_plate, lpCnt, candidates

    # public functions
    def get_car_plate_data(self, image, thresh_img=None):
        """
              This function extract the data from the image and give us the car's number and country.
               :param image:   image of a car.
               :param thresh_img: *optional* A threshHold img.
               :return:  country's name, number_plate, contour of the plate, rectangles from the image.
               """
        # initialize the license plate text
        lpText = None
        # convert the input image to grayscale, locate all candidate
        # license plate regions in the image, and then process the
        # candidates, leaving us with the *actual* license plate
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        candidates = self.__locate_license_plate_candidates(gray, thresh_img)
        return self.__extract_data(candidates, gray)

    def show_process(self, img):
        """
        Showing the entire process of the image processing.
        :param img: The image.
        :return: A list of images in order of the processing.
        """
        self.__debug = True
        if self.__debug:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.__image_filtering(gray)
            proces = self.__process.copy()
            self.__process.clear()
            self.__debug = False
            return proces.copy()

    def debug_imshow(self, title, image):
        """
        Crates a window with the image.
        :param title: The title of the window.
        :param image: the image that we want to show.
        :return: void.
        """
        cv2.namedWindow(title)  # Create a named window
        cv2.moveWindow(title, 500, 250)
        cv2.imshow(title, image)
        cv2.waitKey(0)

    def draw_image(self, image, lpCnt, lp_country, lp_number_plate):
        """
                   This function draws a rectangle on the car's plate also put text:
                   above ==> the car's country  below==> the car's number
                    :param image:   rectangle.
                    :param lpCnt:  gray Scale of the image.
                    :param lp_country:  gray Scale of the image.
                    :param lp_number_plate:  gray Scale of the image.

                    :return: void.
                    """

        box = cv2.boxPoints(cv2.minAreaRect(lpCnt))
        box = box.astype("int")
        cv2.drawContours(image, [box], -1, GREEN, THICKNESS)
        # compute a normal (unrotated) bounding box for the license
        # plate and then draw the OCR'd license plate text on the
        # image
        (x, y, w, h) = cv2.boundingRect(lpCnt)
        cv2.putText(image, lp_country, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, FONT_SIZE, GREEN, THICKNESS)
        cv2.putText(image, lp_number_plate, (x, y + h + DISTANCE_FROM_BOX),
                    cv2.FONT_HERSHEY_SIMPLEX, FONT_SIZE, BLUE, THICKNESS)
