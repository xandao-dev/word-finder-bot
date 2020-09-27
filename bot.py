# region Imports
import time
import re
import pprint
from pyfiglet import Figlet
from pynput.mouse import Listener as MouseListener
from pytesseract import image_to_string
from fuzzywuzzy import fuzz, process
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
	hwnd = win32gui.FindWindow(None, 'BlueStacks')
	window_capture = WindowCapture(hwnd)

	#start_countdown(3)
	
	#screenshot = cv2.imread("assets/samples/mainSample.png", cv2.IMREAD_GRAYSCALE)
	screenshot = window_capture.get_screenshot()
	keyword = get_keyword(screenshot, debug)
	matrix_chars = get_matrix_chars(screenshot, pp, debug)

	fuzzyFinder = FuzzyFinder()
	fuzzyFinder.find(matrix_chars, keyword)
	cv2.waitKey()

class FuzzyFinder:
	def __init__(self):
		self.COLUMNS_INDEX = ['-','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


	def __get_possible_words(self, matrix, word):
		lword = len(word)
		nrows = len(matrix)
		ncols = len(matrix[0])
		
		# dir left to right
		words_left_to_right = []
		for i in range(nrows):
			for j in range(ncols - lword + 1):
				words_left_to_right.append(((i+1, j+1),(i + 1, j + lword), matrix[i][j:j+lword]))

		# Transpose Matrix
		matrix_trans = list(zip(*matrix))
		for i, row in enumerate(matrix_trans):
			matrix_trans[i] = ''.join(row)
		nrows = len(matrix_trans)
		ncols = len(matrix_trans[0])

		# dir up to down
		words_up_to_down = []
		for i in range(nrows):
			for j in range(ncols - lword + 1):
				words_up_to_down.append(((j + 1, i + 1), (j + lword, i + 1), matrix_trans[i][j:j+lword]))

		return words_left_to_right + words_up_to_down


	def find(self, matrix, word):
		possible_words = self.__get_possible_words(matrix, word)
		best_result = process.extractOne(word, [possible_word for (start, end, possible_word) in possible_words])
		for start, end, possible_word in possible_words:
			if best_result[0] == possible_word:
				start_pos = f'{self.COLUMNS_INDEX[start[1]]}{start[0]}'
				end_pos = f'{self.COLUMNS_INDEX[end[1]]}{end[0]}'
				print(f'Found word with {best_result[1]}% of accuracy: "{possible_word}", start: {start_pos}, end: {end_pos}')
				return (start_pos, end_pos, possible_word)
		else:
			print('Word not found')
			return False


def get_keyword(screenshot, debug=False):
	scrshot_w = screenshot.shape[1]
	scrshot_h = screenshot.shape[0]

	# Area where the keyword stand
	screenshot = screenshot[427:scrshot_h-272, 117:scrshot_w-90]

	img = cv2.threshold(screenshot, 185, 245, cv2.THRESH_BINARY)[1]  # Threshold to obtain binary image
	
	img = Image.fromarray(img)

	text_list = image_to_string(img, config='--psm 8 --oem 3 -c tessedit_char_whitelist=QWERTYUIOPASDFGHJKLZXCVBNM').split('\n')  # get text and split in array
	# text_list = [i for i in text_list if i.strip()] # Delete empty strings
	keyword = max(text_list, key=len)  # Get the biggest string
	#keyword_chars = [char.upper() for char in list(keyword)]
	print("Keyword: ", keyword)

	if debug:
		cv2.imshow('Keyword Position', screenshot)

	return keyword


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

	pprint.pprint(text_list)

	return text_list


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
	print_logo('Word Finder')
	main()
