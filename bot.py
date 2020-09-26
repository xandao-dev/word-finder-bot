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

	#char = 'D'
	#positions = get_char_positions(alphabet.IMAGES_DICT[char], screenshot, pp, 0.9, debug)
	#pp.pprint(positions)
	cv2.waitKey()
	""" 
	while True:
		#screenshot = window_capture.get_screenshot()
		#positions = get_keyword_position(alphabet.IMAGES_DICT, keyword_chars, screenshot, pp, 0.80, debug)
		char = 'A'
		positions = get_char_positions(alphabet.IMAGES_DICT[char], screenshot, pp, 0.80, debug)
		pp.pprint(positions)
		#break
		if cv2.waitKey(1) == ord('q'):
			cv2.destroyAllWindows()
			break 
	"""


def get_keyword_position(letters_dict, keyword_chars, screenshot, pprint, threshold=0.7, debug=False):
	filtered_letters = {k: letters_dict[k] for k in set(keyword_chars)}

	# Save the dimensions of the needle image and the screenshot
	needles_w = {k: letter.shape[1] for (k, letter) in filtered_letters.items()}
	needles_h = {k: letter.shape[0] for (k, letter) in filtered_letters.items()}
	scrshot_w = screenshot.shape[1]
	scrshot_h = screenshot.shape[0]

	# Area where the letters stand
	screenshot = screenshot[45:scrshot_h-300, 25:scrshot_w-100]
	scrshot_w = scrshot_w - 175
	scrshot_h = scrshot_h - 345

	# There are 6 methods to choose from:
	# TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
	method = cv2.TM_CCOEFF_NORMED
	results = {k: cv2.matchTemplate(screenshot, letter, method) for (k, letter) in filtered_letters.items()}

	# Get the all the positions from the match result that exceed our threshold
	locations = {k: np.where(result >= threshold) for (k, result) in results.items()}
	locations = {k: list(zip(*location[::-1])) for (k, location) in locations.items()}
	#pprint.pprint(locations)

	# You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
	# locations by using groupRectangles().
	# First we need to create the list of [x, y, w, h] rectangles
	#location {A: [(loc),(loc)], B: [(loc),(loc)], ...}
	rectangles = {}
	for k, letterLotations in locations.items():
		for loc in letterLotations:
			rect = [int(loc[0]), int(loc[1]), needles_w[k], needles_h[k]]
			# Add every box to the list twice in order to retain single (non-overlapping) boxes
			rectangles[k] = [rect, rect]
			#rectangles.append(rect)
			#rectangles.append(rect)
	# Apply group rectangles.
	# The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
	# done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
	# in the result. I've set eps to 0.5, which is:
	# "Relative difference between sides of the rectangles to merge them into a group."
	for k, rectanglesOfLetter in rectangles.items():
		rects, weights = cv2.groupRectangles(rectanglesOfLetter, groupThreshold=1, eps=0.5)
		rectangles[k] = rects
	# print(rectangles)

	points = {}
	if len(rectangles):
		#print('Found needle.')

		line_color = (0, 255, 0)
		line_type = cv2.LINE_4
		marker_color = (255, 0, 255)
		marker_type = cv2.MARKER_CROSS

		for (k,rectanglesOfLetter) in rectangles.items():
			points[k] = []
			for (x, y, w, h) in rectanglesOfLetter:
				# Determine the center position
				center_x = x + int(w/2)
				center_y = y + int(h/2)
				# Save the points
				points[k].append((center_x, center_y))

				if debug:
					# Determine the box position
					top_left = (x, y)
					bottom_right = (x + w, y + h)
					# Draw the box
					cv2.rectangle(screenshot, top_left, bottom_right, color=line_color,
								lineType=line_type, thickness=2)
					#screenshot = cv2.resize(screenshot, (scrshot_w/2, scrshot_h/2))
					cv2.imshow('Letters Position', screenshot)

	return points


def get_char_positions(char, screenshot, pprint, threshold=0.7, debug=False):
	# Save the dimensions of the needle image and the screenshot
	needle_w = char.shape[1]
	needle_h = char.shape[0]
	scrshot_w = screenshot.shape[1]
	scrshot_h = screenshot.shape[0]

	# Area where the letters stand
	screenshot = screenshot[45:scrshot_h-300, 25:scrshot_w-100]
	scrshot_w = scrshot_w - 125
	scrshot_h = scrshot_h - 345

	# There are 6 methods to choose from:
	# TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
	method = cv2.TM_CCOEFF_NORMED
	results = cv2.matchTemplate(screenshot, char, method)

	# Get the all the positions from the match result that exceed our threshold
	locations = np.where(results >= threshold)
	locations = list(zip(*locations[::-1]))
	#pprint.pprint(locations)

	# You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
	# locations by using groupRectangles().
	# First we need to create the list of [x, y, w, h] rectangles
	#location {A: [(loc),(loc)], B: [(loc),(loc)], ...}
	rectangles = []
	for loc in locations:
		rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
		# Add every box to the list twice in order to retain single (non-overlapping) boxes
		rectangles.append(rect)
		rectangles.append(rect)
	# Apply group rectangles.
	# The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
	# done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
	# in the result. I've set eps to 0.5, which is:
	# "Relative difference between sides of the rectangles to merge them into a group."
	rects, weights = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
	# print(rectangles)

	points = []
	if len(rectangles):
		#print('Found needle.')

		line_color = (0, 255, 0)
		line_type = cv2.LINE_4
		marker_color = (255, 0, 255)
		marker_type = cv2.MARKER_CROSS
		for (x, y, w, h) in rectangles:
			# Determine the center position
			center_x = x + int(w/2)
			center_y = y + int(h/2)
			# Save the points
			points.append((center_x, center_y))

			if debug:
				# Determine the box position
				top_left = (x, y)
				bottom_right = (x + w, y + h)
				# Draw the box
				cv2.rectangle(screenshot, top_left, bottom_right, color=line_color,
							lineType=line_type, thickness=2)
				#screenshot = cv2.resize(screenshot, (scrshot_w/2, scrshot_h/2))
				cv2.imshow('Letters Position', screenshot)

	return points


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
