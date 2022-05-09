import cv2
import easyocr
import numpy as np

from stringOperators import *


class CountryDetection:
    def __init__(self):
        self.country_licence_plate = {
            "SYR": ('Syria', remove_letters('SYR')), "IL": ('Israel', remove_letters('IL')),
            "JORDAN": ('Jordan', remove_letters('JORDAN')),
            "KSA": ('Saudi arabia', remove_letters('KSA')), "P": ('Palestine', remove_letters('P'))
        }
        # self.country_dict = {"SYR": 'Syria', "IL": 'Israel', "JORDAN": 'Jordan',
        #                      "KSA": 'Saudi arabia', "P": 'Palestine'}
        # self.letters = {'SYR': remove_letters('SYR'), 'IL': remove_letters('IL'),
        #                 'JORDAN': remove_letters('JORDAN'),
        #                 'KSA': remove_letters('KSA'), 'P': remove_letters('P')}
        self.reader = easyocr.Reader(['en'])

    def __use_pytesseract(self, lp):
        """
            Text detection using pytesseract.
            :param lp: the image
            :return:  a list of the detected text from the image.
        """
        contours, j = cv2.findContours(lp.copy(), cv2.RETR_TREE,
                                       cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        detected = ''
        letters = []

        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            ratio = h / w
            area = cv2.contourArea(c)
            if ratio > MIN_RATIO and MIN_AREA < area < MAX_AREA:
                base = np.ones(lp.shape, dtype=np.uint8)

                base[y:y + h, x:x + w] = lp[y:y + h, x:x + w]

                c = pytesseract.image_to_string(base, config=custom_config)

                letter = c.split('\n')[0]
                # the pytesseract model detect 'I' as 'l'
                if letter == 'l':
                    letter = 'I'
                letter = adjust_text(letter)

                if letter.isalpha() and len(letter) == 1:
                    letters.append((letter, x, y))
        letters = sorted(letters, key=lambda k: k[1] + k[2])
        l = [x[0] for x in letters]

        return letters_list_to_string(l)
        # return order_letters_list(letters)

    def __text_detection(self, lp, mode):
        """
                using ocr, and pytesseract, this function determine which country
                 are more likely to appear in the image.
                  :param lp: the image
                :param mode: boolean => True - ocr False - pytesseract : .
                :return: tuple(max_certainty, max_country_name).
            """
        max_certainty = MIN_CERTAINTY
        max_country_name = IRRELEVANT_STR
        text = self.reader.readtext(lp, paragraph="False")[0][1] if mode else ''.join(self.__use_pytesseract(lp))
        saved_text = text

        for country_name in  self.country_licence_plate:
            text = clean_text_to_country(text, country_name,  self.country_licence_plate)
            res_country_name = country_name
            if not mode: res_country_name, text = ''.join(sorted(country_name)), ''.join(sorted(text))

            if similar(text, res_country_name) > max_certainty:
                max_certainty = similar(text, res_country_name)
                max_country_name = self.country_licence_plate[country_name][0]
            text = saved_text
        return max_certainty, max_country_name

    def detect_country(self, lp, try_text=''):
        """
                this function return the country from the image
                :param try_text: the first text that was scanned.
                :param lp: the image
                :return:  string
            """

        # a first check for luck
        if try_text != '':
            res = contains_str(try_text, self.country_licence_plate)
            if res != '':
                return self.country_licence_plate[res][0]

        # easy ocr text detection
        ocr_certainty, ocr_country_name = self.__text_detection(lp, True)
        # pytesseract text detection
        pytesseract_certainty, pytesseract_country_name = self.__text_detection(lp, False)

        tuple_lst = [(ocr_certainty, ocr_country_name), (pytesseract_certainty, pytesseract_country_name)]
        return ''.join(sorted(tuple_lst, key=lambda x: x[0], reverse=True)[0][1])
