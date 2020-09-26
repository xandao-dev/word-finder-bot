# region Imports
import time
import re
import pprint
from pyfiglet import Figlet
from pynput.mouse import Listener as MouseListener
from pytesseract import image_to_string
from PIL import Image
import win32gui
import numpy as np
import cv2

from assets.Assets import Alphabet
from WindowCapture import WindowCapture
# endregion

#Confs & Paths
debug = True


def main():
	# Instances
	alphabet = Alphabet()
	pp = pprint.PrettyPrinter(indent=2)
	#hwnd = get_focused_window_handle()
	#window_capture = WindowCapture(hwnd)

	# start_countdown(3)

	screenshot = cv2.imread("assets/samples/mainSample.png", cv2.IMREAD_GRAYSCALE)
	keyword_chars = get_keyword_chars(screenshot, debug)
	matrix_chars = get_matrix_chars(screenshot, pp, debug)

	cv2.waitKey()


def get_keyword_chars(screenshot, debug=False):
	scrshot_w = screenshot.shape[1]
	scrshot_h = screenshot.shape[0]

	# Area where the keyword stand
	screenshot = screenshot[427:scrshot_h-272, 117:scrshot_w-90]

	img = cv2.threshold(screenshot, 185, 245, cv2.THRESH_BINARY)[1]  # Threshold to obtain binary image
	
	img = Image.fromarray(img)

	text_list = image_to_string(img, lang='por', config='--psm 8 --oem 3 -c tessedit_char_whitelist=QWERTYUIOPASDFGHJKLZXCVBNM').split('\n')  # get text and split in array
	# text_list = [i for i in text_list if i.strip()] # Delete empty strings
	keyword = max(text_list, key=len)  # Get the biggest string
	keyword_chars = [char.upper() for char in list(keyword)]
	#keyword_chars_set = set(keyword_chars)
	print("Keyword: ", keyword)
	print("Keyword Array: ", keyword_chars)
	#print("Keyword Set: ", keyword_chars_set)

	if debug:
		cv2.imshow('Keyword Position', screenshot)

	return keyword_chars


def get_matrix_chars(screenshot, pprint, debug=False):
	scrshot_w = screenshot.shape[1]
	scrshot_h = screenshot.shape[0]

	# Area where the letters stand
	screenshot = screenshot[58:scrshot_h-309, 45:scrshot_w-100]

	if debug:
		cv2.imshow('Keyword Position', screenshot)

	screenshot = Image.fromarray(screenshot)

	text_list = image_to_string(screenshot, lang='por', config='--psm 4 --oem 3 -c tessedit_char_whitelist=QWERTYUIOPASDFGHJKLZXCVBNM').split('\n')  # get text and split in array
	text_list = [i for i in text_list if i.strip()] # Delete empty strings

	text_matrix = []
	for i, text in enumerate(text_list):
		text_matrix.append([char for char in text])

	pprint.pprint(text_matrix)

	return text_matrix


# region Helpers
def start_countdown(sleep_time_sec=5):
	print('Starting', end='')
	for i in range(10):
		print('.', end='')
		time.sleep(sleep_time_sec/10)
	print('\nReady, forcing dwarves to work!')


def print_logo(text_logo: str):
	figlet = Figlet(font='slant')
	print(figlet.renderText(text_logo))


def get_focused_window_handle():
	print('\nSelecione a janela do tiktok')

	hwnd = []

	def on_click(x, y, button, pressed):
		if not pressed:
			hwnd.append(win32gui.GetForegroundWindow())
			return False

	with MouseListener(on_click=on_click) as mouse_listener:
		mouse_listener.join()

	print('Window Selected: ', win32gui.GetWindowText(hwnd[0]))
	time.sleep(0.5)
	return hwnd[0]
# endregion


if __name__ == '__main__':
	try:
		print_logo('Caca Palavra Bot')
		main()
	except Exception as e:
		print(str(e))
