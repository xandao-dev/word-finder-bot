from pathlib import Path
from enum import Enum  

import cv2
import glob
from pathlib import Path
alphabetPath = str(Path(__file__).parent / 'alphabet')


class Alphabet():
	imagesPath = [img for img in glob.glob(alphabetPath + "/*.png")]
	imagesPath.sort() #Sort in alphabet order
	IMAGES = [cv2.imread(img) for img in imagesPath]
	IMAGES_NAMES = [Path(img).stem for img in imagesPath]
	IMAGES_DICT = dict(zip(IMAGES_NAMES, IMAGES))
	IMAGES_THRESHOLD = {
		'A': 0.83,
		'B': 0.91,
		'C': 0.86,
		'D': 0.9,
		'E': 0.9,
		'F': 0.9,
		'G': 0.9,
		'H': 0.9,
		'I': 0.9,
		'J': 0.9,
		'K': 0.9,
		'L': 0.9,
		'M': 0.9,
		'N': 0.9,
		'O': 0.9,
		'P': 0.9,
		'Q': 0.9,
		'R': 0.9,
		'S': 0.9,
		'T': 0.9,
		'U': 0.9,
		'V': 0.9,
		'W': 0.9,
		'X': 0.9,
		'Y': 0.9,
		'Z': 0.9,
	}
	def __init__(self):
		pass

#abc = Alphabet()
#print(abc.IMAGES_DICT)