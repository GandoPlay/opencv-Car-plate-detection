import string
import pytesseract

# pytesseract
custom_config = r'-l eng --oem 3 --psm 10 -c ' \
                fr'tessedit_char_whitelist="1234567890{string.ascii_uppercase}{string.ascii_lowercase}"'
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# image processing variables
GAUSSIAN_SMOOTH_FILTER_SIZE = (5, 5)
ADAPTIVE_THRESH_BLOCK_SIZE = 19
ADAPTIVE_THRESH_WEIGHT = 9
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
RED = (0, 0, 255)
FONT_SIZE = 0.75
THICKNESS = 2
DISTANCE_FROM_BOX = 15
KEEP = 100
STRUCTURING_ELEMENT_FILTER = (6, 6)
RESIZE_IMAGE = 2
MINSIZE = 250
MIN_RATIO = 0.5
MIN_AREA = 40
MAX_AREA = 10000
# STRING  variables
IRRELEVANT_STR = 'IRRELEVANT_STR'
MIN_LETTERS = 4
MIN_CERTAINTY = 0.5
