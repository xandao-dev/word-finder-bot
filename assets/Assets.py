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

	def __init__(self):
		pass

#abc = Alphabet()
#print(abc.IMAGES_DICT)