from src.MainWindow import MainWindow
from PyQt5 import QtWidgets
import sys

import logging.config

def initialise_loggegr():

    logging.config.fileConfig("config/logger.ini")
    logging.getLogger('PIL').setLevel(logging.WARNING) # set PIL to log only warning level
    logging.debug("Logger has been initialised")

if __name__ == "__main__":
    initialise_loggegr()

    logging.info("Starting media manager")

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
