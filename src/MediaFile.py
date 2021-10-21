import sys
import traceback
from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtGui import QTransform
import logging

from src import config

class MediaFile:
    label = None
    rotation = None
    to_delete = False

    def __init__(self, filePath, label=None):
        self.filePath = filePath
        self.label = label

    def reset_label(self):
        self.label = None

    def mark_as_delete(self, flag=True):
        self.to_delete = flag

    def get_pixmap(self):

        img = Image.open(self.filePath)
        # img.verify()
        pixmap = QtGui.QPixmap(self.filePath)

        # rotate image according to exif orientation tag
        if self.image_has_exif(img):

            logging.debug(f"Image has orientation exif. Analyzing {self.filePath}")

            exif_data = img._getexif()
            orientation = exif_data[config.EXIF_ORIENTATION_TAG_CODE]
            transform = QTransform()

            if orientation == 1:
                # Normal image - nothing to do!
                logging.debug(f"Normal orientation. Nothing to do.")
                pass
            elif orientation == 2:
                # Mirrored left to right
                logging.debug(f"Mirrored left to right.")
                transform.scale(-1, 1)
                # img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 3:
                # Rotated 180 degrees
                logging.debug(f"Rotated 180 degrees.")
                transform.rotate(-180)
                # img = img.rotate(180)
            elif orientation == 4:
                # Mirrored top to bottom
                logging.debug(f"Mirrored top to bottom")
                transform.rotate(-180).scale(-1, 1)
                # img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 5:
                # Mirrored along top-left diagonal
                logging.debug(f"Mirrored along top-left diagonal")
                transform.rotate(-90).scale(-1, 1)
                # img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 6:
                # Rotated 90 degrees
                logging.debug(f"Rotated 90 degrees")
                transform.rotate(90)
                # img = img.rotate(-90, expand=True)
            elif orientation == 7:
                # Mirrored along top-right diagonal
                logging.debug(f"Mirrored along top-right diagonal")
                transform.rotate(90).scale(-1, 1)
                # img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
            elif orientation == 8:
                # Rotated 270 degrees
                logging.debug(f"Rotated -90 degrees")
                transform.rotate(-90)
                # img = img.rotate(90, expand=True)

            # img_qt = QImage(img)
            # pixmap = QtGui.QPixmap(self.filePath)
            # pixmap = QtGui.QPixmap.fromImage(img_qt)

            pixmap = pixmap.transformed(transform)

        return pixmap

    def image_has_exif(self, img):
        has_exif = False
        try:
            if hasattr(img, "_getexif") \
                    and isinstance(img._getexif(), dict) \
                    and config.EXIF_ORIENTATION_TAG_CODE in img._getexif():
                has_exif = True
        except AttributeError as err:
            # img._getexif() raises error after img.verify() for .PNG
            logging.warning("Image doesn't have exif")
            has_exif = False
        except Exception as err:
            logging.error(f"Unexpected error! {traceback.print_exc()}")
            sys.exit("Unexpected error")

        return has_exif
