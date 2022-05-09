from difflib import SequenceMatcher

# static functions
from Globals import *


def adjust_text(detected):
    """
        removing any duplicates from a string and Capitalize the letters.
        :param detected: string
        :return: string without duplicates and Capitalize.
              """
    detected = detected.upper()
    detected = ''.join(dict.fromkeys(detected))
    return ''.join(detected)


def remove_letters(msg):
    """
          removing letters from the A B C...... .
          :param msg: string that contains the letters we want to remove
          :return: A B C.... without the letters we input .
                """
    return ''.join(c for c in string.ascii_uppercase if c not in msg)


#
def order_letters_list(letters):
    """
          convert the list into a string
          :param letters: list of tuple (letter, x, y)
          :return: string .
                """
    txt = ''.join([l[0] for l in letters])
    return adjust_text(txt)


def letters_list_to_string(letters):
    txt = ''.join([l for l in letters])
    return adjust_text(txt)


def contains_digits(text):
    """
            counts how many digits there are in a string
            :param text: string
            :return: int
                  """
    return sum(c.isdigit() for c in text)


def similar(a, b):
    """
        calculating how similar a and b
        :param a: string
        :param b: string
        :return: float between 0.0 to 1.0 .
          """
    return SequenceMatcher(None, a, b).ratio()


def relevant_data(reader, lp):
    """
    return whether the text is relevant or not.
         :param reader: OCR Reader.
         :param lp: image.
         :return: string.
           """
    text = reader.readtext(lp, paragraph="False")
    if len(text) == 0:
        return IRRELEVANT_STR

    return text[0][1] if contains_digits(text[0][1]) > MIN_LETTERS else IRRELEVANT_STR


def contains_str(text, letters_dict):
    """
        return the key from the dict that is in the text.
        :param text: string
        :param letters_dict: dict
        :return: string.
          """
    return ''.join([country_name for country_name in letters_dict if country_name in text.upper()])


def clean_text_to_country(text, temp, letters_dict):
    """
        remove from text all the letters from the abc.. expect the letters in letters_dict[temp]
        :param text: string
        :param temp: string
        :param letters_dict: dict
        :return: string.
          """
    return ''.join(char for char in text if char not in letters_dict[temp][1])



def extract_number_sequence(lpText):
    """
        find the max sequence of numbers
        :param lpText: string
        :return: string.
          """
    max_sequence = 0
    cur_sequence = 0
    res = 'did not find any number'
    cur = ''
    for letter in lpText:
        if not letter.isalpha():
            cur += letter
            cur_sequence += 1
        else:
            if max_sequence < cur_sequence:
                res = cur
                max_sequence = cur_sequence
                cur_sequence = 0
                cur = ''
    if cur_sequence == len(lpText):
        res = lpText
    return res
