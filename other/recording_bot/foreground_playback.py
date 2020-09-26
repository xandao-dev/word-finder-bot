import pyautogui
import os
import json
from time import sleep, time
from pyfiglet import Figlet


def main():
	initializePyAutoGUI()
	start_countdown(3)

	playActions("tower_b5.json")
	print("Done")


def initializePyAutoGUI():
	# Initialized PyAutoGUI
	# https://pyautogui.readthedocs.io/en/latest/introduction.html
	# When fail-safe mode is True, moving the mouse to the upper-left corner will abort your program.
	pyautogui.FAILSAFE = True


def playActions(filename):
	# Read the file
	script_dir = os.path.dirname(__file__)
	filepath = os.path.join(
		script_dir, 
		'recordings', 
		filename
	)
	with open(filepath, 'r') as jsonfile:
		# parse the json
		data = json.load(jsonfile)
		
		# loop over each action
		# Because we are not waiting any time before executing the first action, any delay before the initial
		# action is recorded will not be reflected in the playback.
		for index, action in enumerate(data):
			action_start_time = time()

			# look for escape input to exit
			if action['button'] == 'Key.esc':
				break

			# perform the action
			if action['type'] == 'keyDown':
				key = convertKey(action['button'])
				pyautogui.keyDown(key)
				print("keyDown on {}".format(key))
			elif action['type'] == 'keyUp':
				key = convertKey(action['button'])
				pyautogui.keyUp(key)
				print("keyUp on {}".format(key))
			elif action['type'] == 'click':
				pyautogui.click(action['pos'][0], action['pos'][1], duration=0.25)
				print("click on {}".format(action['pos']))

			# then sleep until next action should occur
			try:
				next_action = data[index + 1]
			except IndexError:
				# this was the last action in the list
				break
			elapsed_time = next_action['time'] - action['time']

			# if elapsed_time is negative, that means our actions are not ordered correctly. throw an error
			if elapsed_time < 0:
				raise Exception('Unexpected action ordering.')

			# adjust elapsed_time to account for our code taking time to run
			elapsed_time -= (time() - action_start_time)
			if elapsed_time < 0:
				elapsed_time = 0
			print('sleeping for {}'.format(elapsed_time))
			sleep(elapsed_time)


# convert pynput button keys into pyautogui keys
# https://pynput.readthedocs.io/en/latest/_modules/pynput/keyboard/_base.html#Key
# https://pyautogui.readthedocs.io/en/latest/keyboard.html
def convertKey(button):
	PYNPUT_SPECIAL_CASE_MAP = {
		'alt_l': 'altleft',
		'alt_r': 'altright',
		'alt_gr': 'altright',
		'caps_lock': 'capslock',
		'ctrl_l': 'ctrlleft',
		'ctrl_r': 'ctrlright',
		'page_down': 'pagedown',
		'page_up': 'pageup',
		'shift_l': 'shiftleft',
		'shift_r': 'shiftright',
		'num_lock': 'numlock',
		'print_screen': 'printscreen',
		'scroll_lock': 'scrolllock',
	}

	# example: 'Key.F9' should return 'F9', 'w' should return as 'w'
	cleaned_key = button.replace('Key.', '')

	if cleaned_key in PYNPUT_SPECIAL_CASE_MAP:
		return PYNPUT_SPECIAL_CASE_MAP[cleaned_key]

	return cleaned_key


# region Helpers
def start_countdown(sleep_time_sec=5):
    print('Starting', end='', flush=True)
    for i in range(10):
        print('.', end='', flush=True)
        sleep(sleep_time_sec/10)
    print('\nReady, forcing dwarves to work!')


def print_logo(text_logo: str):
    figlet = Figlet(font='slant')
    print(figlet.renderText(text_logo))
# endregion

if __name__ == "__main__":
    try:
        print_logo('Background Playback Bot')
        main()
    except Exception as e:
        print(str(e))
