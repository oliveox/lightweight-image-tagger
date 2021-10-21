import logging

from PyQt5 import QtCore
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMainWindow

from src.UiActions import RotateDirection
from src.UiRenderer import UiRenderer


class MainWindow(QMainWindow, UiRenderer):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent=parent)
        self.ui_actions = self.setupUi(self)

    def keyPressEvent(self, e):

        if e.key() \
                and not e.modifiers():
            try:
                letterString = QKeySequence(e.key()).toString()
                self.ui_actions.label_current_media(letterString)
            except Exception:
                logging.warning(f"Can't read key: {e.key()}")

        if e.key() == QtCore.Qt.Key_Left \
                and not e.modifiers():
            logging.info(f"Pressed <-")
            self.ui_actions.dispaly_previous_media_file()

        if e.key() == QtCore.Qt.Key_Right \
                and not e.modifiers():
            logging.info(f"Pressed ->")
            self.ui_actions.display_next_media_file()

        if e.modifiers() \
                and QtCore.Qt.ShiftModifier \
                and e.key() == QtCore.Qt.Key_Left:
            logging.info(f"Pressed SHIFT + <-")
            self.ui_actions.rotate_image(RotateDirection.LEFT)

        if e.modifiers() \
                and QtCore.Qt.ShiftModifier \
                and e.key() == QtCore.Qt.Key_Right:
            logging.info(f"Pressed SHIFT + ->")
            self.ui_actions.rotate_image(RotateDirection.RIGHT)

        if e.modifiers() \
                and QtCore.Qt.ShiftModifier \
                and e.key() == QtCore.Qt.Key_T:
            logging.info(f"Pressed SHIFT + T")
            self.ui_actions.create_new_label()

        if e.modifiers() \
                and QtCore.Qt.CTRL \
                and e.key() == QtCore.Qt.Key_S:
            logging.info(f"Pressed CTRL + S")
            self.ui_actions.save_media_changes_to_file()

        if e.modifiers() \
                and QtCore.Qt.CTRL \
                and e.key() == QtCore.Qt.Key_F1:
            logging.info(f"Pressed CTRL + F1")
            self.ui_actions.apply_actions_on_media_folder()

        if e.key() == QtCore.Qt.Key_Delete:
            logging.info(f"Pressed DELETE key")
            self.ui_actions.toggle_media_delete_status()
